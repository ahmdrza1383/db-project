import redis
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, DatabaseError, IntegrityError, transaction
from datetime import datetime, date
import json
import random
import string
import re

from .auth_utils import *
from .tasks import check_and_revert_reservation_task


def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))


redis_client = None
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    print("Successfully connected to Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis: {e}. OTP functionality will be impaired.")
except AttributeError:
    print("Redis settings (REDIS_HOST, REDIS_PORT) not found in Django settings.")


@csrf_exempt
@require_http_methods(["POST"])
def request_otp_view(request):
    """
    Requests an OTP (One-Time Password) for an existing user to log in.

    This API first checks if an active OTP already exists for the provided
    identifier in Redis. If so, it informs the user to wait.
    If no active OTP is found, it then checks if a user with the given
    identifier (email or phone number) exists in the PostgreSQL database.
    If the user exists and no active OTP is pending, a new OTP is generated,
    stored in Redis with a TTL, and a success message is returned.
    If the user does not exist in the database, an OTP will not be sent.

    Request Body (JSON):
    {
        "identifier": "user@example.com or 09123456789"
    }

    Successful Response (JSON):
    {
        "status": "success",
        "message": "An OTP has been sent to {identifier} for login. It is valid for {X} minutes.",
        "otp_for_testing": "123456" // This should be removed in production
    }

    Error Responses (JSON):
    - Invalid JSON format:
      {"status": "error", "message": "Invalid JSON format in request body."} (Status Code: 400)
    - Missing identifier:
      {"status": "error", "message": "Identifier (email or phone_number) is required."} (Status Code: 400)
    - Redis service unavailable:
      {"status": "error", "message": "Redis service unavailable. Cannot request OTP."} (Status Code: 503)
    - Active OTP already exists for the identifier:
      {"status": "error", "message": "An OTP has already been sent. Please try again in approximately {Y} seconds."} (Status Code: 429)
    - User not found in the database:
      {"status": "error", "message": "User not found. Please register or check your identifier."} (Status Code: 404)
    - Database error during user check:
      {"status": "error", "message": "A database error occurred while checking user status."} (Status Code: 500)
    - Redis error during OTP processing:
      {"status": "error", "message": "Failed to process OTP due to a Redis issue."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected error occurred."} (Status Code: 500)
    """
    if not redis_client:
        return JsonResponse({'status': 'error', 'message': 'Redis service unavailable. Cannot request OTP.'},
                            status=503)  # Service Unavailable

    try:
        data = json.loads(request.body)
        identifier = data.get('identifier')

        if not identifier:
            return JsonResponse({'status': 'error', 'message': 'Identifier (email or phone_number) is required.'},
                                status=400)

        redis_key = f"otp:{identifier}"

        if redis_client.exists(redis_key):
            ttl = redis_client.ttl(redis_key)
            wait_time_seconds = ttl if ttl and ttl > 0 else getattr(settings, 'OTP_RESEND_WAIT_SECONDS',
                                                                    60)
            return JsonResponse({
                'status': 'error',
                'message': f'An OTP has already been sent to this identifier. Please try again in approximately {wait_time_seconds} seconds.'
            }, status=429)

        user_exists_in_db = False
        is_email_identifier = '@' in identifier
        db_field_to_query = 'email' if is_email_identifier else 'phone_number'
        sql_query_user_check = f"SELECT 1 FROM users WHERE {db_field_to_query} = %s LIMIT 1"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query_user_check, [identifier])
                if cursor.fetchone():
                    user_exists_in_db = True
        except DatabaseError as db_e:
            print(f"Database error during user check in request_otp_view: {db_e}")
            return JsonResponse({'status': 'error', 'message': 'A database error occurred while checking user status.'},
                                status=500)

        if not user_exists_in_db:
            return JsonResponse(
                {'status': 'error', 'message': 'User not found. Please register or check your identifier.'},
                status=404)

        otp_code = generate_otp()
        otp_ttl_seconds = getattr(settings, 'OTP_TTL_SECONDS', 300)

        redis_client.set(name=redis_key, value=otp_code, ex=otp_ttl_seconds)

        print(f"Generated OTP for {identifier} (User in DB: {user_exists_in_db}): {otp_code} (TTL: {otp_ttl_seconds}s)")

        return JsonResponse({
            'status': 'success',
            'message': f'An OTP has been sent to {identifier} for login. It is valid for {otp_ttl_seconds // 60} minutes.'
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except redis.exceptions.RedisError as e:
        print(f"Redis error during OTP request: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to process OTP due to a Redis issue.'}, status=500)
    except Exception as e:
        print(f"Unexpected error in request_otp_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_view(request):
    """
    Verifies the OTP provided by the user for login.

    This API receives the user's identifier (email or phone number) and the OTP code.
    It validates the OTP against the value stored in Redis.
    If the OTP is valid:
        1. The corresponding user is retrieved from the PostgreSQL database.
           (It is assumed that `request_otp_view` only sent an OTP if the user exists).
        2. A JWT Access Token and a JWT Refresh Token are generated.
        3. These tokens, along with basic user information, are returned to the client.

    Request Body (JSON):
    {
        "identifier": "user@example.com or 09123456789",
        "otp_code": "123456"
    }

    Successful Response (JSON):
    {
        "status": "success",
        "message": "Login successful! OTP verified.",
        "access_token": "<JWT_access_token_string>",
        "refresh_token": "<JWT_refresh_token_string>",
        "user_info": {
            "username": "<username>",
            "name": "<user_name or null>",
            "email": "<user_email or null>",
            "phone_number": "<user_phone_number or null>",
            "role": "<user_role>"
        }
    }

    Error Responses (JSON):
    - Invalid JSON format:
      {"status": "error", "message": "Invalid JSON format in request body."} (Status Code: 400)
    - Missing identifier or OTP code:
      {"status": "error", "message": "Identifier and OTP code are required."} (Status Code: 400)
    - Redis service unavailable:
      {"status": "error", "message": "Redis service unavailable. Cannot verify OTP."} (Status Code: 503)
    - OTP not found or expired in Redis:
      {"status": "error", "message": "OTP not found or has expired. Please request a new one."} (Status Code: 400)
    - Invalid OTP code provided:
      {"status": "error", "message": "Invalid OTP code."} (Status Code: 400)
    - Database error during user lookup:
      {"status": "error", "message": "A database error occurred."} (Status Code: 500)
    - User unexpectedly not found in DB after valid OTP (should not happen with current logic):
      {"status": "error", "message": "User not found, despite valid OTP. Please contact support."} (Status Code: 404)
    - Redis error during OTP verification process:
      {"status": "error", "message": "A Redis error occurred."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected server error occurred."} (Status Code: 500)
    """
    if not redis_client:
        return JsonResponse({'status': 'error', 'message': 'Redis service unavailable. Cannot verify OTP.'}, status=503)

    try:
        data = json.loads(request.body)
        identifier = data.get('identifier')
        otp_code_user = data.get('otp_code')

        if not identifier or not otp_code_user:
            return JsonResponse({'status': 'error', 'message': 'Identifier and OTP code are required.'}, status=400)

        redis_key = f"otp:{identifier}"
        stored_otp = redis_client.get(redis_key)

        if not stored_otp:
            return JsonResponse(
                {'status': 'error', 'message': 'OTP not found or has expired. Please request a new one.'}, status=400)

        if stored_otp != otp_code_user:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP code.'}, status=400)

        try:
            redis_client.delete(redis_key)
        except redis.exceptions.RedisError as rd_del_e:
            print(f"Warning: Could not delete OTP key {redis_key} from Redis after verification: {rd_del_e}")

        user_database_info = None
        is_email = '@' in identifier
        db_field_name_for_query = 'email' if is_email else 'phone_number'
        sql_query_find_user = f"SELECT username, user_role, email, phone_number, name FROM users WHERE {db_field_name_for_query} = %s LIMIT 1"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query_find_user, [identifier])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    user_database_info = dict(zip(columns, row))
                else:
                    print(f"Error: User {identifier} was not found in DB during OTP verification, but OTP was valid.")
                    return JsonResponse(
                        {'status': 'error', 'message': 'User not found, despite valid OTP. Please contact support.'},
                        status=404)
        except DatabaseError as db_error:
            print(f"Database error during user lookup in verify_otp_view: {db_error}")
            return JsonResponse({'status': 'error', 'message': 'A database error occurred.'}, status=500)

        token_payload = {
            "sub": user_database_info['username'],
            "role": user_database_info.get('user_role', 'USER')
        }
        access_token = create_access_token(data=token_payload)
        refresh_token = create_refresh_token(data=token_payload)

        user_info_for_response = {
            'username': user_database_info['username'],
            'name': user_database_info.get('name'),
            'email': user_database_info.get('email'),
            'phone_number': user_database_info.get('phone_number'),
            'role': user_database_info.get('user_role', 'USER')
        }

        return JsonResponse({
            'status': 'success',
            'message': 'Login successful! OTP verified.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_info': user_info_for_response
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except redis.exceptions.RedisError as redis_error:
        print(f"Redis error during OTP verification process: {redis_error}")
        return JsonResponse({'status': 'error', 'message': 'A Redis error occurred.'}, status=500)
    except Exception as general_error:
        print(f"Unexpected error in verify_otp_view: {general_error.__class__.__name__}: {general_error}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def user_signup_view(request):
    """
    Registers a new user in the system.

    This API endpoint accepts new user details. Username, password, and email
    are mandatory. Name and phone_number are optional.
    The 'city' for the user will be set to NULL by default upon registration
    via this API.
    It hashes the password, validates inputs, checks for uniqueness of
    username, email, and phone_number (if provided), and then creates
    the new user in the PostgreSQL database.
    Upon successful registration, JWT access and refresh tokens are generated
    and returned along with basic user information.

    Request Body (JSON):
    {
        "username": "newuser",
        "password": "SecurePassword123!",
        "email": "user@example.com",
        "name": "Test User",
        "phone_number": "09123456789" // Optional, must be unique if provided
    }

    Successful Response (JSON - Status Code: 201 Created):
    {
        "status": "success",
        "message": "User registered successfully!",
        "access_token": "<JWT_access_token_string>",
        "refresh_token": "<JWT_refresh_token_string>",
        "user_info": {
            "username": "newuser",
            "email": "user@example.com",
            "name": "Test User",
            "role": "USER"
        }
    }

    Error Responses (JSON):
    - Invalid JSON format:
      {"status": "error", "message": "Invalid JSON format in request body."} (Status Code: 400)
    - Missing required fields (username, password, email):
      {"status": "error", "message": "Missing required fields: [field_names]"} (Status Code: 400)
    - Username, email, or phone number already exists:
      {"status": "error", "message": "Username, email, or phone number already exists."} (Status Code: 409 - Conflict)
    - Database error during registration:
      {"status": "error", "message": "A database error occurred during registration."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected error occurred."} (Status Code: 500)
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')
        phone_number_input = data.get('phone_number')

        required_fields_dict = {'username': username, 'password': password, 'email': email, 'name': name}
        missing_fields = [key for key, value in required_fields_dict.items() if not value]
        if missing_fields:
            return JsonResponse({'status': 'error', 'message': f'Missing required fields: {", ".join(missing_fields)}'},
                                status=400)

        phone_number_to_store = None
        if phone_number_input and phone_number_input.strip():
            phone_number_to_store = phone_number_input.strip()

            phone_pattern = r"^09\d{9}$"
            if not re.match(phone_pattern, phone_number_to_store):
                return JsonResponse(
                    {'status': 'error', 'message': 'Invalid phone number format. It must be 09XXXXXXXXX.'},
                    status=400)

        hashed_password = generate_password_hash(password)

        insert_query = """
            INSERT INTO users (username, password, email, name, phone_number)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING username, user_role, email, name; 
        """

        inserted_user_info = None
        with connection.cursor() as cursor:
            cursor.execute(insert_query, [
                username,
                hashed_password,
                email,
                name,
                phone_number_to_store
            ])
            inserted_row = cursor.fetchone()
            if inserted_row:
                columns = [col[0] for col in cursor.description]
                inserted_user_info = dict(zip(columns, inserted_row))
            else:
                raise DatabaseError("User insertion succeeded but failed to return user information.")

        token_payload = {
            "sub": inserted_user_info['username'],
            "role": inserted_user_info.get('user_role', 'USER')
        }
        access_token = create_access_token(data=token_payload)
        refresh_token = create_refresh_token(data=token_payload)

        response_user_info = {
            'username': inserted_user_info['username'],
            'email': inserted_user_info['email'],
            'name': inserted_user_info.get('name'),
            'role': inserted_user_info.get('user_role', 'USER')
        }

        return JsonResponse({
            'status': 'success',
            'message': 'User registered successfully!',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_info': response_user_info
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except IntegrityError as e:
        error_detail_str = str(e).lower()
        if "users_pkey" in error_detail_str or "users_username_key" in error_detail_str or \
                (
                        "duplicate key value violates unique constraint" in error_detail_str and "username" in error_detail_str):
            return JsonResponse(
                {'status': 'error', 'message': 'This username is already taken. Please choose a different one.'},
                status=409)
        elif "users_email_key" in error_detail_str or \
                ("duplicate key value violates unique constraint" in error_detail_str and "email" in error_detail_str):
            return JsonResponse({'status': 'error',
                                 'message': 'This email address is already registered. Please use a different email.'},
                                status=409)
        elif "users_phone_number_key" in error_detail_str or \
                (
                        "duplicate key value violates unique constraint" in error_detail_str and "phone_number" in error_detail_str):
            if phone_number_to_store:
                return JsonResponse({'status': 'error',
                                     'message': 'This phone number is already registered. Please use a different phone number.'},
                                    status=409)
            else:
                print(
                    f"Database IntegrityError (phone_number related but no phone number provided to store, or other issue): {e}")
                return JsonResponse(
                    {'status': 'error', 'message': 'A data integrity error occurred. Please check your inputs.'},
                    status=409)
        else:
            print(f"Database IntegrityError during signup: {e}")
            print(f"Error details: {error_detail_str}")
            return JsonResponse({'status': 'error',
                                 'message': 'A data integrity error occurred. Please ensure your inputs are unique and valid.'},
                                status=409)

    except DatabaseError as e:
        print(f"DatabaseError during signup: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred during registration.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in user_signup_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
@token_required
def update_user_profile_view(request):
    """
    Updates profile information for the authenticated user.

    This API endpoint allows an authenticated user to update their profile details.
    All fields in the request body are optional. To keep a field unchanged,
    simply omit it from the request payload.
    For optional fields like 'name', 'phone_number', 'date_of_birth', and 'city_id',
    sending a 'null' value in the request payload will result in a 400 error;
    these fields cannot be explicitly set to null via this API if you mean to clear them.
    If these fields are already null in the database, sending 'null' might be accepted
    (effectively no change) or still rejected based on the strict interpretation below.
    The current stricter interpretation is to reject explicit 'null' for these.

    Sensitive fields like username, password, and email can be changed by providing
    'new_username', 'new_password', and 'new_email' respectively. Changing
    username or password will result in new JWTs being issued.

    After a successful database update, the user's profile cache in Redis
    will be updated or created. If the username changes, the cache for the
    old username will be deleted.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON - all fields are optional):
    {
        "name": "New Full Name",
        "new_username": "new_unique_username123",
        "new_password": "aVeryStrongPassword!@#",
        "new_email": "new.email.unique@example.com",
        "phone_number": "09123456780",
        "date_of_birth": "1990-01-01",
        "city_id": 10, // Integer ID referencing locations table
        "new_authentication_method": "PHONE_NUMBER" // 'EMAIL' or 'PHONE_NUMBER'
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Profile updated successfully.",
        "access_token": "<new_jwt_access_token_if_username_or_password_changed>",
        "refresh_token": "<new_jwt_refresh_token_if_username_or_password_changed>",
        "user_info": {
            "username": "current_or_new_username",
            "name": "New Full Name",
            "email": "current_or_new_email@example.com",
            "phone_number": "09123456780",
            "date_of_birth": "1990-01-01",
            "city_id": 10, // or null if it was set to null and DB allows
            "authentication_method": "PHONE_NUMBER",
            "role": "USER" // Or actual role
        }
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON, missing required fields for sensitive operations,
                       invalid data format (e.g., email, phone, date),
                       explicitly sending 'null' for 'name', 'phone_number', 'date_of_birth', 'city_id'.
    - 401 Unauthorized: Token missing or invalid.
    - 404 Not Found: User not found (should not happen if token is valid).
    - 409 Conflict: Username, email, or phone number already exists.
    - 500 Internal Server Error: Database or other unexpected server errors.
    - 503 Service Unavailable: Redis service unavailable (if it's critical for an operation).
    """
    try:
        current_username_from_token = request.user_payload.get('sub')
        if not current_username_from_token:
            return JsonResponse({'status': 'error', 'message': 'Invalid token: Username not found in token payload.'},
                                status=401)

        try:
            data_payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

        if not data_payload:
            return JsonResponse({'status': 'error',
                                 'message': 'No fields provided for update. Please provide at least one field to update.'},
                                status=400)

        fields_to_update_in_db = {}
        requires_new_jwt_token = False

        optional_fields_no_explicit_null = {
            'name': 'Name',
            'phone_number': 'Phone number',
            'date_of_birth': 'Date of birth',
            'city_id': 'City ID'
        }

        for field_key, field_name_display in optional_fields_no_explicit_null.items():
            if field_key in data_payload:
                value = data_payload[field_key]
                if value is None:
                    return JsonResponse({'status': 'error',
                                         'message': f'{field_name_display} cannot be set to null. Omit the field to keep the current value or provide a new value.'},
                                        status=400)

                if field_key == 'name':
                    if not isinstance(value, str) or not value.strip():
                        return JsonResponse({'status': 'error', 'message': 'Name cannot be empty if provided.'},
                                            status=400)
                    fields_to_update_in_db['name'] = value.strip()

                elif field_key == 'phone_number':
                    phone_to_validate = str(value).strip()
                    if not phone_to_validate:
                        return JsonResponse({'status': 'error', 'message': 'Phone number cannot be empty if provided.'},
                                            status=400)
                    phone_pattern = r"^09\d{9}$"
                    if not re.match(phone_pattern, phone_to_validate):
                        return JsonResponse(
                            {'status': 'error', 'message': 'Invalid phone number format (09XXXXXXXXX).'}, status=400)
                    fields_to_update_in_db['phone_number'] = phone_to_validate

                elif field_key == 'date_of_birth':
                    dob_str = str(value).strip()
                    if not dob_str:
                        return JsonResponse(
                            {'status': 'error', 'message': 'Date of birth cannot be empty if provided.'}, status=400)
                    try:
                        dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()
                        if dob_obj > date.today():
                            return JsonResponse(
                                {'status': 'error', 'message': 'Date of birth cannot be in the future.'}, status=400)
                        fields_to_update_in_db['date_of_birth'] = dob_obj
                    except ValueError:
                        return JsonResponse(
                            {'status': 'error', 'message': 'Invalid date format for date_of_birth (YYYY-MM-DD).'},
                            status=400)

                elif field_key == 'city_id':
                    if not isinstance(value, int):
                        return JsonResponse({'status': 'error', 'message': 'city_id must be an integer.'}, status=400)
                    fields_to_update_in_db['city'] = value

        if 'new_username' in data_payload:
            new_username_val = data_payload.get('new_username')
            if new_username_val is None or not str(new_username_val).strip():
                return JsonResponse({'status': 'error', 'message': 'New username cannot be null or empty.'}, status=400)
            new_username_val = str(new_username_val).strip()
            if new_username_val != current_username_from_token:
                fields_to_update_in_db['username'] = new_username_val
                requires_new_jwt_token = True

        if 'new_password' in data_payload:
            new_password_val = data_payload.get('new_password')
            if new_password_val is None or not str(new_password_val):
                return JsonResponse({'status': 'error', 'message': 'New password cannot be null or empty.'}, status=400)
            fields_to_update_in_db['password'] = generate_password_hash(str(new_password_val))
            requires_new_jwt_token = True

        if 'new_email' in data_payload:
            new_email_input = data_payload.get('new_email')
            if new_email_input is None or not str(new_email_input).strip():
                return JsonResponse({'status': 'error', 'message': 'New email cannot be null or empty.'}, status=400)

            email_to_validate = str(new_email_input).strip()
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email_to_validate):
                return JsonResponse({'status': 'error', 'message': 'Invalid new email format.'}, status=400)
            fields_to_update_in_db['email'] = email_to_validate

        if 'new_authentication_method' in data_payload:
            auth_method_val = data_payload.get('new_authentication_method')
            if auth_method_val is None or not str(auth_method_val).strip():
                return JsonResponse(
                    {'status': 'error', 'message': 'New authentication method cannot be null or empty.'}, status=400)

            auth_method_val = str(auth_method_val).upper().strip()
            if auth_method_val not in ['EMAIL', 'PHONE_NUMBER']:
                return JsonResponse(
                    {'status': 'error', 'message': "Invalid authentication_method. Must be 'EMAIL' or 'PHONE_NUMBER'."},
                    status=400)
            fields_to_update_in_db['authentication_method'] = auth_method_val

        if not fields_to_update_in_db:
            return JsonResponse({'status': 'error', 'message': 'No valid fields or changes provided for update.'},
                                status=400)

        set_clauses_list = [f"{db_column} = %s" for db_column in fields_to_update_in_db.keys()]
        params_for_sql_update = list(fields_to_update_in_db.values())
        params_for_sql_update.append(current_username_from_token)

        update_sql_query = f"""
            UPDATE users
            SET {', '.join(set_clauses_list)}
            WHERE username = %s
            RETURNING username, name, email, phone_number, date_of_birth, city, user_role, authentication_method;
        """

        updated_user_data_from_db = None
        with connection.cursor() as cursor:
            cursor.execute(update_sql_query, params_for_sql_update)
            if cursor.rowcount == 0:
                return JsonResponse({'status': 'error', 'message': 'User not found or no effective changes applied.'},
                                    status=404)

            updated_row_tuple = cursor.fetchone()
            if updated_row_tuple:
                db_columns_from_returning = [col[0] for col in cursor.description]
                updated_user_data_from_db = dict(zip(db_columns_from_returning, updated_row_tuple))
            else:
                raise DatabaseError(
                    "User update query executed (rowcount > 0) but failed to return updated information via RETURNING.")

        user_info_for_response_and_cache = updated_user_data_from_db.copy()
        if user_info_for_response_and_cache.get('date_of_birth') and isinstance(
                user_info_for_response_and_cache['date_of_birth'], date):
            user_info_for_response_and_cache['date_of_birth'] = user_info_for_response_and_cache[
                'date_of_birth'].isoformat()
        if 'city' in user_info_for_response_and_cache:
            user_info_for_response_and_cache['city_id'] = user_info_for_response_and_cache.pop('city')

        final_username_in_db = user_info_for_response_and_cache.get('username')

        if redis_client:
            try:
                if final_username_in_db != current_username_from_token:
                    old_username_cache_key = f"user_profile:{current_username_from_token}"
                    redis_client.delete(old_username_cache_key)
                    print(f"User profile cache DELETED for old username: {current_username_from_token}")

                profile_cache_key = f"user_profile:{final_username_in_db}"
                profile_cache_ttl_seconds = getattr(settings, 'USER_PROFILE_CACHE_TTL_SECONDS', 3600)
                profile_data_json_str = json.dumps(user_info_for_response_and_cache)

                redis_client.setex(
                    profile_cache_key,
                    profile_cache_ttl_seconds,
                    profile_data_json_str
                )
                print(
                    f"User profile UPDATED/ADDED in cache for username: {final_username_in_db} with TTL: {profile_cache_ttl_seconds}s")
            except redis.exceptions.RedisError as re_cache_err:
                print(f"Redis error during profile cache operation: {re_cache_err}")

        response_json_data = {
            'status': 'success',
            'message': 'Profile updated successfully.',
            'user_info': user_info_for_response_and_cache
        }

        if requires_new_jwt_token:
            new_jwt_payload = {
                "sub": final_username_in_db,
                "role": user_info_for_response_and_cache.get('user_role', 'USER')
            }
            response_json_data['access_token'] = create_access_token(data=new_jwt_payload)
            response_json_data['refresh_token'] = create_refresh_token(data=new_jwt_payload)

        return JsonResponse(response_json_data)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except IntegrityError as e:
        err_str = str(e).lower()
        if "users_pkey" in err_str or "users_username_key" in err_str or (
                "duplicate key" in err_str and "username" in err_str):
            return JsonResponse({'status': 'error', 'message': 'This username is already taken.'}, status=409)
        if "users_email_key" in err_str or ("duplicate key" in err_str and "email" in err_str):
            return JsonResponse({'status': 'error', 'message': 'This email address is already registered.'}, status=409)
        if "users_phone_number_key" in err_str or ("duplicate key" in err_str and "phone_number" in err_str):
            if 'phone_number' in fields_to_update_in_db and fields_to_update_in_db.get('phone_number') is not None:
                return JsonResponse({'status': 'error', 'message': 'This phone number is already registered.'},
                                    status=409)
        if "violates foreign key constraint" in err_str and (
                "users_city_fkey" in err_str or "users_city_id_fkey" in err_str):
            if 'city' in fields_to_update_in_db and fields_to_update_in_db.get('city') is not None:
                return JsonResponse({'status': 'error', 'message': 'Invalid city ID provided.'}, status=400)
        print(f"DB IntegrityError on profile update: {e}")
        return JsonResponse(
            {'status': 'error', 'message': 'Data integrity error. Check unique fields or foreign keys.'}, status=409)
    except DatabaseError as e:
        print(f"DB Error on profile update: {e}")
        return JsonResponse({'status': 'error', 'message': 'Database error during profile update.'}, status=500)
    except Exception as e:
        print(f"Unexpected error in update_user_profile_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_cities_list_view(request):
    """
    Retrieves a list of all cities and their corresponding provinces available in the system.

    This API endpoint is essential for users to select origin and destination
    locations when searching for tickets.

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "data": [
            {
                "location_id": 1,
                "city": "Tehran",
                "province": "Tehran"
            },
            {
                "location_id": 2,
                "city": "Mashhad",
                "province": "Razavi Khorasan"
            },
            // ... more cities
        ]
    }

    Error Responses (JSON):
    - Database error:
      {"status": "error", "message": "A database error occurred while fetching cities."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected error occurred."} (Status Code: 500)
    """
    try:
        sql_query = """
            SELECT location_id, city, province FROM locations ORDER BY province, city;
        """
        cities_data = []
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            for row in rows:
                cities_data.append(dict(zip(columns, row)))

        return JsonResponse({
            'status': 'success',
            'data': cities_data
        }, status=200)

    except DatabaseError as e:
        print(f"Database error in get_cities_list_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while fetching cities.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in get_cities_list_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def search_tickets_view(request):
    """
    Allows users to search for available tickets based on various criteria using a POST request.

    Users can search by origin, destination, travel date, and vehicle type.
    Results are cached in Redis to improve performance for frequent queries.
    Optional filters for price, transport company, departure time, and travel class
    are also supported.

    Request Body (JSON):
    {
        "origin_city": "Tehran",
        "destination_city": "Mashhad",
        "departure_date": "2025-06-15",
        "vehicle_type": "FLIGHT", // Optional: 'FLIGHT', 'TRAIN', 'BUS'
        "min_price": 100000,     // Optional
        "max_price": 500000,     // Optional
        "company_name": "Mahan Air", // Optional (for Flight/Bus)
        "min_departure_time": "08:00", // Optional: HH:MM for departure start
        "max_departure_time": "18:00", // Optional: HH:MM for departure start
        "flight_class": "Economy",   // Optional (for Flight)
        "train_stars": 4,          // Optional (for Train)
        "bus_type": "VIP"          // Optional (for Bus)
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "data": [
            {
                "ticket_id": 1,
                "origin_city": "Tehran",
                "destination_city": "Mashhad",
                "departure_start": "YYYY-MM-DDTHH:MM:SS",
                "departure_end": "YYYY-MM-DDTHH:MM:SS",
                "price": 500000,
                "remaining_capacity": 20,
                "vehicle_type": "FLIGHT",
                "airline_name": "Mahan Air",
                "flight_class": "Economy",
                "number_of_stop": 0,
                "flight_code": "IR-1234",
                "origin_airport": "Mehrabad",
                "destination_airport": "Mashhad",
                "facility": {"meal": true}
            },
            // ... more tickets
        ],
        "cached": true/false // Indicates if response was from cache
    }

    Error Responses (JSON):
    - Invalid JSON format:
      {"status": "error", "message": "Invalid JSON format in request body."} (Status Code: 400)
    - Missing required parameters:
      {"status": "error", "message": "Missing required parameters: [param_names]"} (Status Code: 400)
    - Invalid date format:
      {"status": "error", "message": "Invalid departure_date format. Please use YYYY-MM-DD."} (Status Code: 400)
    - Invalid time format:
      {"status": "error", "message": "Invalid time format for min/max_departure_time. Please use HH:MM."} (Status Code: 400)
    - Invalid price/star values:
      {"status": "error", "message": "Price or stars must be positive integers."} (Status Code: 400)
    - Invalid vehicle type:
      {"status": "error", "message": "Invalid vehicle_type. Must be 'FLIGHT', 'TRAIN', or 'BUS'."} (Status Code: 400)
    - Database error:
      {"status": "error", "message": "A database error occurred during ticket search."} (Status Code: 500)
    - Redis error:
      {"status": "error", "message": "A Redis error occurred during caching."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected error occurred."} (Status Code: 500)
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

    origin_city = data.get('origin_city')
    destination_city = data.get('destination_city')
    departure_date_str = data.get('departure_date')

    # Optional Filters
    vehicle_type = data.get('vehicle_type')
    min_price = data.get('min_price')
    max_price = data.get('max_price')
    company_name = data.get('company_name')
    min_departure_time_str = data.get('min_departure_time')
    max_departure_time_str = data.get('max_departure_time')
    flight_class = data.get('flight_class')
    train_stars = data.get('train_stars')
    bus_type = data.get('bus_type')

    required_params = {
        'origin_city': origin_city,
        'destination_city': destination_city,
        'departure_date': departure_date_str,
    }
    missing_params = [key for key, value in required_params.items() if not value]
    if missing_params:
        return JsonResponse({'status': 'error', 'message': f'Missing required parameters: {", ".join(missing_params)}'},
                            status=400)

    try:
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid departure_date format. Please use YYYY-MM-DD.'},
            status=400
        )

    def validate_time_format(time_str):
        if time_str:
            try:
                datetime.strptime(time_str, '%H:%M').time()
                return True
            except ValueError:
                return False
        return True

    if not validate_time_format(min_departure_time_str) or not validate_time_format(max_departure_time_str):
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid time format for min/max_departure_time. Please use HH:MM.'},
            status=400)

    numeric_params_validated = {}
    for param_name, param_value in {'min_price': min_price, 'max_price': max_price, 'train_stars': train_stars}.items():
        if param_value is not None:
            try:
                numeric_params_validated[param_name] = int(param_value)
                if numeric_params_validated[param_name] <= 0:
                    raise ValueError
                if param_name == 'train_stars' and not (1 <= numeric_params_validated[param_name] <= 5):
                    return JsonResponse({'status': 'error', 'message': 'train_stars must be between 1 and 5.'},
                                        status=400)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': f'{param_name} must be a positive integer.'},
                                    status=400)

    # Validate vehicle type
    valid_vehicle_types = ['FLIGHT', 'TRAIN', 'BUS']
    if vehicle_type and vehicle_type.upper() not in valid_vehicle_types:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid vehicle_type. Must be \'FLIGHT\', \'TRAIN\', or \'BUS\'.'},
            status=400)

    cache_key_data = {k: v for k, v in data.items() if v is not None}
    cache_key = f"search_tickets:{json.dumps(cache_key_data, sort_keys=True)}"

    cached_response = None
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                cached_response = json.loads(cached_data)
                print(f"Serving search results from cache for key: {cache_key}")
                return JsonResponse({
                    'status': 'success',
                    'data': cached_response,
                    'cached': True
                })
        except redis.exceptions.RedisError as e:
            print(f"Redis error during cache lookup for search_tickets_view: {e}")

    tickets_data = []
    try:
        with connection.cursor() as cursor:
            base_query = """
                SELECT
                    t.ticket_id,
                    origin_loc.city AS origin_city,
                    dest_loc.city AS destination_city,
                    t.departure_start,
                    t.departure_end,
                    t.price,
                    t.remaining_capacity,
                    v.vehicle_type,
                    f.airline_name, f.flight_class, f.number_of_stop, f.flight_code, f.origin_airport, f.destination_airport, f.facility AS flight_facility,
                    tr.train_stars, tr.choosing_a_closed_coupe, tr.facility AS train_facility,
                    b.company_name, b.bus_type, b.number_of_chairs, b.facility AS bus_facility
                FROM tickets t
                INNER JOIN locations origin_loc ON t.origin_location_id = origin_loc.location_id
                INNER JOIN locations dest_loc ON t.destination_location_id = dest_loc.location_id
                INNER JOIN vehicles v ON t.vehicle_id = v.vehicle_id
                LEFT JOIN flights f ON v.vehicle_id = f.vehicle_id AND v.vehicle_type = 'FLIGHT'
                LEFT JOIN trains tr ON v.vehicle_id = tr.vehicle_id AND v.vehicle_type = 'TRAIN'
                LEFT JOIN buses b ON v.vehicle_id = b.vehicle_id AND v.vehicle_type = 'BUS'
                WHERE
                    origin_loc.city ILIKE %s AND
                    dest_loc.city ILIKE %s AND
                    DATE(t.departure_start) = %s AND
                    t.ticket_status = TRUE
            """
            query_params = [origin_city, destination_city, departure_date]

            if vehicle_type:
                base_query += " AND v.vehicle_type = %s"
                query_params.append(vehicle_type.upper())

            if 'min_price' in numeric_params_validated:
                base_query += " AND t.price >= %s"
                query_params.append(numeric_params_validated['min_price'])
            if 'max_price' in numeric_params_validated:
                base_query += " AND t.price <= %s"
                query_params.append(numeric_params_validated['max_price'])

            if min_departure_time_str:
                base_query += " AND t.departure_start::time >= %s"
                query_params.append(min_departure_time_str)
            if max_departure_time_str:
                base_query += " AND t.departure_start::time <= %s"
                query_params.append(max_departure_time_str)

            if company_name:
                base_query += " AND (f.airline_name ILIKE %s OR b.company_name ILIKE %s)"
                query_params.extend([f"%{company_name}%", f"%{company_name}%"])

            if flight_class and (not vehicle_type or vehicle_type.upper() == 'FLIGHT'):
                base_query += " AND f.flight_class ILIKE %s"
                query_params.append(f"%{flight_class}%")

            if 'train_stars' in numeric_params_validated and (not vehicle_type or vehicle_type.upper() == 'TRAIN'):
                base_query += " AND tr.train_stars = %s"
                query_params.append(numeric_params_validated['train_stars'])

            if bus_type and (not vehicle_type or vehicle_type.upper() == 'BUS'):
                base_query += " AND b.bus_type ILIKE %s"
                query_params.append(f"%{bus_type}%")

            base_query += " ORDER BY t.departure_start ASC;"

            cursor.execute(base_query, query_params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            for row in rows:
                ticket = dict(zip(columns, row))

                if ticket.get('departure_start') and hasattr(ticket['departure_start'], 'isoformat'):
                    ticket['departure_start'] = ticket['departure_start'].isoformat()
                if ticket.get('departure_end') and hasattr(ticket['departure_end'], 'isoformat'):
                    ticket['departure_end'] = ticket['departure_end'].isoformat()

                vehicle_details = {}
                current_vehicle_type = ticket['vehicle_type']

                if current_vehicle_type == 'FLIGHT':
                    vehicle_details['airline_name'] = ticket.pop('airline_name')
                    vehicle_details['flight_class'] = ticket.pop('flight_class')
                    vehicle_details['number_of_stop'] = ticket.pop('number_of_stop')
                    vehicle_details['flight_code'] = ticket.pop('flight_code')
                    vehicle_details['origin_airport'] = ticket.pop('origin_airport')
                    vehicle_details['destination_airport'] = ticket.pop('destination_airport')
                    facility_json = ticket.pop('flight_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                elif current_vehicle_type == 'TRAIN':
                    vehicle_details['train_stars'] = ticket.pop('train_stars')
                    vehicle_details['choosing_a_closed_coupe'] = ticket.pop('choosing_a_closed_coupe')
                    facility_json = ticket.pop('train_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                elif current_vehicle_type == 'BUS':
                    vehicle_details['company_name'] = ticket.pop('company_name')
                    vehicle_details['bus_type'] = ticket.pop('bus_type')
                    vehicle_details['number_of_chairs'] = ticket.pop('number_of_chairs')
                    facility_json = ticket.pop('bus_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                ticket.pop('flight_facility', None)
                ticket.pop('train_facility', None)
                ticket.pop('bus_facility', None)

                ticket.pop('airline_name', None)
                ticket.pop('flight_class', None)
                ticket.pop('number_of_stop', None)
                ticket.pop('flight_code', None)
                ticket.pop('origin_airport', None)
                ticket.pop('destination_airport', None)
                ticket.pop('train_stars', None)
                ticket.pop('choosing_a_closed_coupe', None)
                ticket.pop('company_name', None)
                ticket.pop('bus_type', None)
                ticket.pop('number_of_chairs', None)

                ticket['vehicle_details'] = vehicle_details
                tickets_data.append(ticket)

        response_data = {
            'status': 'success',
            'data': tickets_data,
            'cached': False
        }

        if redis_client:
            try:
                cache_ttl_seconds = getattr(settings, 'TICKET_SEARCH_CACHE_TTL_SECONDS', 300)
                redis_client.setex(cache_key, cache_ttl_seconds, json.dumps(tickets_data))
                print(f"Cached search results for key: {cache_key} with TTL: {cache_ttl_seconds}s")
            except redis.exceptions.RedisError as e:
                print(f"Redis error during caching search results: {e}")

        return JsonResponse(response_data, status=200)

    except DatabaseError as e:
        print(f"DatabaseError in search_tickets_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred during ticket search.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in search_tickets_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_ticket_details_view(request, ticket_id):
    """
    Retrieves and displays detailed information for a specific ticket,
    including details about its associated vehicle (flight, train, or bus). [cite: 1]

    This API provides comprehensive details for a ticket including its origin,
    destination, departure and arrival times, price, special amenities/facilities,
    and remaining capacity. [cite: 1] If the ticket pertains to a flight, train, or bus,
    specific attributes of that mode of transport are also displayed. [cite: 1]

    Path Parameter:
        ticket_id (int): The unique identifier for the ticket.

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "data": {
            "ticket_id": 1,
            "departure_start": "YYYY-MM-DDTHH:MM:SSZ",
            "departure_end": "YYYY-MM-DDTHH:MM:SSZ",
            "price": 500000,
            "total_capacity": 50,
            "remaining_capacity": 25,
            "ticket_status": true,
            "is_round_trip": false,
            "return_start": null,
            "return_end": null,
            "origin_city": "Tehran",
            "origin_province": "Tehran",
            "destination_city": "Mashhad",
            "destination_province": "Razavi Khorasan",
            "vehicle_type": "TRAIN", // or "FLIGHT", "BUS"
            "vehicle_details": {
                // Fields specific to TRAIN, FLIGHT, or BUS
                // Example for TRAIN:
                // "train_stars": 4,
                // "choosing_a_closed_coupe": true,
                // "facility": {"wifi": true, "restaurant": true}
            }
        }
    }

    Error Responses (JSON):
    - Ticket not found:
      {"status": "error", "message": "Ticket not found."} (Status Code: 404)
    - Database error:
      {"status": "error", "message": "A database error occurred."} (Status Code: 500)
    - Unexpected server error:
      {"status": "error", "message": "An unexpected error occurred."} (Status Code: 500)
    """
    try:
        main_ticket_query = """
            SELECT
                t.ticket_id, t.vehicle_id, t.departure_start, t.departure_end,
                t.price, t.total_capacity, t.remaining_capacity, t.ticket_status,
                t.is_round_trip, t.return_start, t.return_end,
                origin_loc.city AS origin_city, origin_loc.province AS origin_province,
                dest_loc.city AS destination_city, dest_loc.province AS destination_province,
                v.vehicle_type
            FROM tickets t
            INNER JOIN locations origin_loc ON t.origin_location_id = origin_loc.location_id
            INNER JOIN locations dest_loc ON t.destination_location_id = dest_loc.location_id
            INNER JOIN vehicles v ON t.vehicle_id = v.vehicle_id
            WHERE t.ticket_id = %s;
        """

        vehicle_specific_details = {}
        ticket_base_data = None

        with connection.cursor() as cursor:
            cursor.execute(main_ticket_query, [ticket_id])
            main_ticket_row_tuple = cursor.fetchone()

            if not main_ticket_row_tuple:
                raise Http404("Ticket not found.")

            main_ticket_columns = [col[0] for col in cursor.description]
            ticket_base_data = dict(zip(main_ticket_columns, main_ticket_row_tuple))

            current_vehicle_id = ticket_base_data['vehicle_id']
            current_vehicle_type = ticket_base_data['vehicle_type']

            if current_vehicle_type == 'FLIGHT':
                flight_details_query = """
                    SELECT airline_name, flight_class, number_of_stop, flight_code, 
                           origin_airport, destination_airport, facility
                    FROM flights WHERE vehicle_id = %s;
                """
                cursor.execute(flight_details_query, [current_vehicle_id])
                details_tuple = cursor.fetchone()
                if details_tuple:
                    detail_cols = [col[0] for col in cursor.description]
                    vehicle_specific_details = dict(zip(detail_cols, details_tuple))

            elif current_vehicle_type == 'TRAIN':
                train_details_query = """
                    SELECT train_stars, choosing_a_closed_coupe, facility
                    FROM trains WHERE vehicle_id = %s;
                """
                cursor.execute(train_details_query, [current_vehicle_id])
                details_tuple = cursor.fetchone()
                if details_tuple:
                    detail_cols = [col[0] for col in cursor.description]
                    vehicle_specific_details = dict(zip(detail_cols, details_tuple))

            elif current_vehicle_type == 'BUS':
                bus_details_query = """
                    SELECT company_name, bus_type, number_of_chairs, facility
                    FROM buses WHERE vehicle_id = %s;
                """
                cursor.execute(bus_details_query, [current_vehicle_id])
                details_tuple = cursor.fetchone()
                if details_tuple:
                    detail_cols = [col[0] for col in cursor.description]
                    vehicle_specific_details = dict(zip(detail_cols, details_tuple))

            if 'facility' in vehicle_specific_details and \
                    isinstance(vehicle_specific_details['facility'], str):
                try:
                    vehicle_specific_details['facility'] = json.loads(vehicle_specific_details['facility'])
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse facility JSON for vehicle_id {current_vehicle_id}")
                    vehicle_specific_details['facility'] = None

        ticket_base_data['vehicle_details'] = vehicle_specific_details

        datetime_fields = ['departure_start', 'departure_end', 'return_start', 'return_end']
        for field_name in datetime_fields:
            if ticket_base_data.get(field_name) and hasattr(ticket_base_data[field_name], 'isoformat'):
                ticket_base_data[field_name] = ticket_base_data[field_name].isoformat()

        return JsonResponse({'status': 'success', 'data': ticket_base_data})

    except Http404:
        return JsonResponse({'status': 'error', 'message': 'Ticket not found.'}, status=404)
    except DatabaseError as e:
        print(f"DatabaseError in get_ticket_details_view for ticket_id {ticket_id}: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while fetching ticket details.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in get_ticket_details_view for ticket_id {ticket_id}: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def reserve_ticket_view(request):
    """
    Temporarily reserves a specific seat for a given ticket for an authenticated 'USER'.
    Admins are not allowed to reserve tickets via this endpoint.
    Upon successful temporary reservation, a Celery task is scheduled to check
    for reservation expiry after a defined period (e.g., 10 minutes).

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON):
    {
        "ticket_id": 123,  // Integer: ID of the ticket
        "seat_number": 5   // Integer: The specific seat number to reserve
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Seat successfully reserved temporarily. Expiry check scheduled.",
        "reservation": {
            "reservation_id": 101,
            "ticket_id": 123,
            "seat_number": 5,
            "status": "TEMPORARY",
            "username": "currentuser",
            "reserved_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
            "expires_in_minutes": 10
        }
    }
    // Error responses as previously defined
    """
    try:
        current_username = request.user_payload.get('sub')
        user_role = request.user_payload.get('role')

        if not current_username:
            return JsonResponse({'status': 'error', 'message': 'Invalid token: Username missing.'}, status=401)

        if user_role != 'USER':
            return JsonResponse({
                'status': 'error',
                'message': 'Forbidden: Only regular users can reserve tickets. Admins are not permitted.'
            }, status=403)

        try:
            data = json.loads(request.body)
            ticket_id_input = data.get('ticket_id')
            seat_number_input = data.get('seat_number')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

        if ticket_id_input is None or seat_number_input is None:
            return JsonResponse({'status': 'error', 'message': "Missing 'ticket_id' or 'seat_number'."}, status=400)

        try:
            ticket_id = int(ticket_id_input)
            seat_number = int(seat_number_input)
            if seat_number <= 0:
                raise ValueError("Seat number must be positive.")
        except ValueError:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid ticket_id or seat_number (must be positive integer).'},
                status=400)

        reservation_outcome_details = None
        reservation_id_to_monitor = None

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT remaining_capacity, ticket_status FROM tickets WHERE ticket_id = %s FOR UPDATE;",
                    [ticket_id]
                )
                ticket_status_info = cursor.fetchone()

                if not ticket_status_info:
                    raise Http404(f"Ticket with ID {ticket_id} not found.")

                current_remaining_capacity, ticket_is_active = ticket_status_info

                if not ticket_is_active:
                    return JsonResponse({'status': 'error', 'message': f'Ticket ID {ticket_id} is currently inactive.'},
                                        status=409)

                if current_remaining_capacity < 1:
                    return JsonResponse(
                        {'status': 'error', 'message': f'No remaining capacity for ticket ID {ticket_id}.'}, status=409)

                find_specific_seat_query = """
                    SELECT reservation_id, reservation_status, username
                    FROM reservations
                    WHERE ticket_id = %s AND reservation_seat = %s
                    FOR UPDATE; 
                """
                cursor.execute(find_specific_seat_query, [ticket_id, seat_number])
                seat_reservation_info = cursor.fetchone()

                if not seat_reservation_info:
                    raise Http404(f"Seat number {seat_number} not found for ticket ID {ticket_id}.")

                reservation_id_for_seat, current_seat_status, current_seat_user = seat_reservation_info
                reservation_id_to_monitor = reservation_id_for_seat

                if current_seat_status != 'NOT_RESERVED' or current_seat_user is not None:
                    return JsonResponse({'status': 'error',
                                         'message': f'Seat {seat_number} for ticket ID {ticket_id} is not available for reservation.'},
                                        status=409)

                reservation_time_utc = datetime.now(timezone.utc)
                cursor.execute(
                    """
                    UPDATE reservations
                    SET username = %s, reservation_status = 'TEMPORARY', date_and_time_of_reservation = %s
                    WHERE reservation_id = %s; 
                    """,
                    [current_username, reservation_time_utc, reservation_id_for_seat]
                )
                if cursor.rowcount == 0:
                    raise DatabaseError(
                        f"Failed to update reservation status for reservation ID {reservation_id_for_seat}.")

                new_remaining_capacity = current_remaining_capacity - 1
                cursor.execute(
                    "UPDATE tickets SET remaining_capacity = %s WHERE ticket_id = %s;",
                    [new_remaining_capacity, ticket_id]
                )
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Failed to update remaining capacity for ticket ID {ticket_id}.")

                expiry_minutes_setting = getattr(settings, 'RESERVATION_EXPIRY_MINUTES', 10)
                reservation_outcome_details = {
                    "reservation_id": reservation_id_for_seat,
                    "ticket_id": ticket_id,
                    "seat_number": seat_number,
                    "status": "TEMPORARY",
                    "username": current_username,
                    "reserved_at": reservation_time_utc.isoformat(),
                    "expires_in_minutes": expiry_minutes_setting
                }

            if reservation_id_to_monitor:
                expiry_seconds = expiry_minutes_setting * 60
                transaction.on_commit(
                    lambda: check_and_revert_reservation_task.apply_async(
                        args=[reservation_id_to_monitor],
                        countdown=expiry_seconds
                    )
                )
                print(
                    f"Celery task scheduled for reservation_id {reservation_id_to_monitor} to run in {expiry_minutes_setting} minutes.")

        return JsonResponse({
            'status': 'success',
            'message': f'Seat {seat_number} for ticket ID {ticket_id} reserved temporarily. Expiry check scheduled.',
            'reservation': reservation_outcome_details
        }, status=200)

    except Http404 as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=404)
    except DatabaseError as e:
        print(f"DatabaseError in reserve_ticket_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred during the reservation process.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in reserve_ticket_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)
