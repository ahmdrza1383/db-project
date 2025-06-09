import redis
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, DatabaseError, IntegrityError, transaction
from django.utils.decorators import method_decorator
from datetime import datetime, date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.tasks import expire_reservation
import json
import random
import string
import re
from rest_framework.decorators import api_view
from datetime import datetime
import json

from .auth_utils import *
from .tasks import expire_reservation


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
        sql_query_find_user = f"SELECT username, user_role, email, phone_number, name, wallet_balance FROM users WHERE {db_field_name_for_query} = %s LIMIT 1"

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
            'role': user_database_info.get('user_role', 'USER'),
            'wallet_balance': user_database_info.get('wallet_balance')
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
            RETURNING username, user_role, email, name, wallet_balance; 
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
            'role': inserted_user_info.get('user_role', 'USER'),
            'wallet_balance': inserted_user_info.get('wallet_balance', 0)
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
    Updates profile information for the authenticated user, and allows adding to wallet balance.

    This API endpoint allows an authenticated user to update their profile details.
    All fields in the request body are optional. To keep a field unchanged,
    simply omit it from the request payload.

    A new field 'add_to_wallet_balance' is introduced. If provided, the specified
    amount will be added to the user's current wallet balance in the 'users' table ONLY.
    No record will be created in the 'payments' table for this operation.

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
        "city_id": 10,           // Integer ID referencing locations table
        "new_authentication_method": "PHONE_NUMBER", // 'EMAIL' or 'PHONE_NUMBER'
        "add_to_wallet_balance": 50000 // Integer: amount to add to wallet
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
            "city_id": 10,
            "authentication_method": "PHONE_NUMBER",
            "role": "USER",
            "wallet_balance": 1500000 // Updated wallet balance
        }
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON, missing required fields for sensitive operations,
                       invalid data format (e.g., email, phone),
                       negative or invalid amount for wallet top-up,
                       explicitly sending 'null' for certain fields.
    - 401 Unauthorized: Token missing or invalid.
    - 404 Not Found: User not found.
    - 409 Conflict: Username, email, or phone number already exists.
    - 500 Internal Server Error: Database or other unexpected server errors.
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
        add_to_wallet_amount = 0

        if 'add_to_wallet_balance' in data_payload:
            wallet_amount_input = data_payload['add_to_wallet_balance']
            try:
                add_to_wallet_amount = int(wallet_amount_input)
                if add_to_wallet_amount <= 0:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Amount to add to wallet must be a positive integer.'},
                        status=400)
            except (ValueError, TypeError):
                return JsonResponse(
                    {'status': 'error', 'message': 'Invalid amount for wallet balance. Must be an integer.'},
                    status=400)

            data_payload.pop('add_to_wallet_balance')

        optional_fields_no_explicit_null = {
            'name': 'Name',
            'phone_number': 'Phone number',
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

        if not fields_to_update_in_db and add_to_wallet_amount == 0:
            return JsonResponse({'status': 'error', 'message': 'No valid fields or changes provided for update.'},
                                status=400)

        updated_user_data_from_db = None
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT username,
                           name,
                           email,
                           phone_number,
                           date_of_sign_in,
                           city,
                           user_role,
                           authentication_method,
                           profile_status,
                           wallet_balance
                    FROM users
                    WHERE username = %s FOR UPDATE;
                    """,
                    [current_username_from_token]
                )
                current_user_data = cursor.fetchone()
                if not current_user_data:
                    return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)

                current_user_columns = [col[0] for col in cursor.description]
                current_user_dict = dict(zip(current_user_columns, current_user_data))
                current_wallet_balance = current_user_dict.get('wallet_balance', 0)

                final_username_for_db_ops = current_user_dict['username']
                update_set_clauses = []
                update_params = []

                if fields_to_update_in_db:
                    for db_column, value in fields_to_update_in_db.items():
                        update_set_clauses.append(f"{db_column} = %s")
                        update_params.append(value)

                    if 'username' in fields_to_update_in_db:
                        final_username_for_db_ops = fields_to_update_in_db['username']

                if add_to_wallet_amount > 0:
                    new_wallet_balance = current_wallet_balance + add_to_wallet_amount
                    update_set_clauses.append("wallet_balance = %s")
                    update_params.append(new_wallet_balance)
                    current_user_dict['wallet_balance'] = new_wallet_balance

                if update_set_clauses:
                    update_sql_query = f"""
                        UPDATE users
                        SET {', '.join(update_set_clauses)}
                        WHERE username = %s;
                    """
                    update_params.append(current_username_from_token)
                    cursor.execute(update_sql_query, update_params)
                    if cursor.rowcount == 0:
                        print(f"Warning: User {current_username_from_token} not updated by main update query.")

                cursor.execute(
                    """
                    SELECT username,
                           name,
                           email,
                           phone_number,
                           date_of_sign_in,
                           city,
                           user_role,
                           authentication_method,
                           profile_status,
                           wallet_balance
                    FROM users
                    WHERE username = %s;
                    """,
                    [final_username_for_db_ops]
                )
                final_user_row_tuple = cursor.fetchone()
                if not final_user_row_tuple:
                    raise DatabaseError("Failed to retrieve final user data after update/wallet top-up.")

                final_user_columns = [col[0] for col in cursor.description]
                updated_user_data_from_db = dict(zip(final_user_columns, final_user_row_tuple))

        user_info_for_response_and_cache = updated_user_data_from_db.copy()

        if 'city' in user_info_for_response_and_cache:
            user_info_for_response_and_cache['city_id'] = user_info_for_response_and_cache.pop('city')

        if user_info_for_response_and_cache.get('date_of_sign_in') and \
                hasattr(user_info_for_response_and_cache['date_of_sign_in'], 'isoformat'):
            user_info_for_response_and_cache['date_of_sign_in'] = user_info_for_response_and_cache[
                'date_of_sign_in'].isoformat()

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
            if 'phone_number' in fields_to_update_in_db:
                return JsonResponse({'status': 'error', 'message': 'This phone number is already registered.'},
                                    status=409)
            else:
                print(f"Database IntegrityError (phone_number related but not directly provided): {e}")
                return JsonResponse(
                    {'status': 'error',
                     'message': 'A data integrity error occurred related to phone number. Check your inputs.'},
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
    including details about its associated vehicle (flight, train, or bus)
    AND limited details of its associated reservations (reservation_id, reservation_status, reservation_seat).

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
            },
            "reservations": [
                {
                    "reservation_id": 101,
                    "reservation_status": "TEMPORARY",
                    "reservation_seat": 5
                },
                // ... more reservations for this ticket
            ]
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
                            SELECT t.ticket_id, \
                                   t.vehicle_id, \
                                   t.departure_start, \
                                   t.departure_end, \
                                   t.price, \
                                   t.total_capacity, \
                                   t.remaining_capacity, \
                                   t.ticket_status, \
                                   t.is_round_trip, \
                                   t.return_start, \
                                   t.return_end, \
                                   origin_loc.city     AS origin_city, \
                                   origin_loc.province AS origin_province, \
                                   dest_loc.city       AS destination_city, \
                                   dest_loc.province   AS destination_province, \
                                   v.vehicle_type
                            FROM tickets t
                                     INNER JOIN locations origin_loc ON t.origin_location_id = origin_loc.location_id
                                     INNER JOIN locations dest_loc ON t.destination_location_id = dest_loc.location_id
                                     INNER JOIN vehicles v ON t.vehicle_id = v.vehicle_id
                            WHERE t.ticket_id = %s; \
                            """

        reservations_query = """
                             SELECT reservation_id, \
                                    reservation_status, \
                                    reservation_seat
                             FROM reservations
                             WHERE ticket_id = %s;
                             """

        vehicle_specific_details = {}
        ticket_base_data = None
        reservations_data = []

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
                                       SELECT airline_name, \
                                              flight_class, \
                                              number_of_stop, \
                                              flight_code,
                                              origin_airport, \
                                              destination_airport, \
                                              facility
                                       FROM flights \
                                       WHERE vehicle_id = %s; \
                                       """
                cursor.execute(flight_details_query, [current_vehicle_id])
                details_tuple = cursor.fetchone()
                if details_tuple:
                    detail_cols = [col[0] for col in cursor.description]
                    vehicle_specific_details = dict(zip(detail_cols, details_tuple))

            elif current_vehicle_type == 'TRAIN':
                train_details_query = """
                                      SELECT train_stars, choosing_a_closed_coupe, facility
                                      FROM trains \
                                      WHERE vehicle_id = %s; \
                                      """
                cursor.execute(train_details_query, [current_vehicle_id])
                details_tuple = cursor.fetchone()
                if details_tuple:
                    detail_cols = [col[0] for col in cursor.description]
                    vehicle_specific_details = dict(zip(detail_cols, details_tuple))

            elif current_vehicle_type == 'BUS':
                bus_details_query = """
                                    SELECT company_name, bus_type, number_of_chairs, facility
                                    FROM buses \
                                    WHERE vehicle_id = %s; \
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

            cursor.execute(reservations_query, [ticket_id])
            reservation_rows = cursor.fetchall()
            reservation_columns = [col[0] for col in cursor.description]

            for row in reservation_rows:
                reservation = dict(zip(reservation_columns, row))
                reservations_data.append(reservation)

        ticket_base_data['vehicle_details'] = vehicle_specific_details
        ticket_base_data['reservations'] = reservations_data

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
    Also, the temporary reservation details (including ticket_price) are cached in Redis for 10 minutes.

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
        expiry_minutes_setting = getattr(settings, 'RESERVATION_EXPIRY_MINUTES', 10)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT remaining_capacity, ticket_status, price FROM tickets WHERE ticket_id = %s FOR UPDATE;",
                    [ticket_id]
                )
                ticket_info = cursor.fetchone()

                if not ticket_info:
                    raise Http404(f"Ticket with ID {ticket_id} not found.")

                current_remaining_capacity, ticket_is_active, ticket_price_from_db = ticket_info

                if not ticket_is_active:
                    return JsonResponse({'status': 'error', 'message': f'Ticket ID {ticket_id} is currently inactive.'},
                                        status=409)

                if current_remaining_capacity < 1:
                    return JsonResponse(
                        {'status': 'error', 'message': f'No remaining capacity for ticket ID {ticket_id}.'}, status=409)

                find_specific_seat_query = """
                                           SELECT reservation_id, reservation_status, username
                                           FROM reservations
                                           WHERE ticket_id = %s \
                                             AND reservation_seat = %s
                                               FOR UPDATE; \
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
                    SET username                     = %s,
                        reservation_status           = 'TEMPORARY',
                        date_and_time_of_reservation = %s
                    WHERE reservation_id = %s RETURNING reservation_id, ticket_id, reservation_seat, reservation_status, username, date_and_time_of_reservation;
                    """,
                    [current_username, reservation_time_utc, reservation_id_for_seat]
                )
                if cursor.rowcount == 0:
                    raise DatabaseError(
                        f"Failed to update reservation status for reservation ID {reservation_id_for_seat}.")

                updated_reservation_row = cursor.fetchone()
                if not updated_reservation_row:
                    raise DatabaseError("Failed to retrieve updated reservation details after update.")

                updated_reservation_columns_from_db = [col[0] for col in cursor.description]
                reservation_outcome_details = dict(zip(updated_reservation_columns_from_db, updated_reservation_row))

                reservation_outcome_details['status'] = reservation_outcome_details.pop('reservation_status')
                reservation_outcome_details['reserved_at'] = reservation_outcome_details.pop(
                    'date_and_time_of_reservation')

                if reservation_outcome_details.get('reserved_at') and \
                        hasattr(reservation_outcome_details['reserved_at'], 'isoformat'):
                    reservation_outcome_details['reserved_at'] = reservation_outcome_details['reserved_at'].isoformat()

                new_remaining_capacity = current_remaining_capacity - 1
                cursor.execute(
                    "UPDATE tickets SET remaining_capacity = %s WHERE ticket_id = %s;",
                    [new_remaining_capacity, ticket_id]
                )
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Failed to update remaining capacity for ticket ID {ticket_id}.")

            if reservation_id_to_monitor:
                expiry_seconds = expiry_minutes_setting * 60
                transaction.on_commit(
                    lambda: expire_reservation.apply_async(
                        args=[reservation_id_to_monitor],
                        countdown=expiry_seconds
                    )
                )
                print(
                    f"Celery task scheduled for reservation_id {reservation_id_to_monitor} to run in {expiry_minutes_setting} minutes.")

            if redis_client:
                redis_key = f"temp_reservation:{reservation_id_to_monitor}"

                reservation_for_cache = reservation_outcome_details.copy()
                reservation_for_cache['expires_in_minutes'] = expiry_minutes_setting
                reservation_for_cache['ticket_price'] = ticket_price_from_db

                try:
                    redis_client.setex(
                        redis_key,
                        expiry_seconds,
                        json.dumps(reservation_for_cache)
                    )
                    print(
                        f"Temporary reservation {reservation_id_to_monitor} cached in Redis for {expiry_minutes_setting} minutes with price {ticket_price_from_db}.")
                except redis.exceptions.RedisError as re_cache_err:
                    print(f"Redis error during temporary reservation caching: {re_cache_err}")
                except Exception as e:
                    print(f"Error preparing reservation for Redis cache: {e}")

        reservation_outcome_details['expires_in_minutes'] = expiry_minutes_setting

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


class CancelReservationView(APIView):
    """
       Handles both checking cancellation policies (GET) and confirming the cancellation (POST)
       for a specific reservation identified by its ID.
    """

    @method_decorator(csrf_exempt)
    @method_decorator(token_required)
    def get(self, request, reservation_id):
        """
        Checks and returns the cancellation penalty for a specific reservation.

        This endpoint allows an authenticated user to preview the financial
        consequences of canceling a ticket before committing to the action. It
        verifies that the reservation belongs to the authenticated user and is
        in a cancellable state ('RESERVED'). The penalty is calculated based on
        the time remaining until departure.

        Path Parameter:
            reservation_id (int): The unique identifier for the reservation.

        Request Headers:
            Authorization: Bearer <JWT_access_token>

        Successful Response (JSON - Status Code: 200 OK):
        {
            "status": "success",
            "cancellation_info": {
                "reservation_id": 101,
                "ticket_price": 500000,
                "time_to_departure_hours": 25.5,
                "penalty_percentage": 10,
                "penalty_amount": 50000,
                "refund_amount": 450000
            }
        }

        Error Responses (JSON):
        - 401 Unauthorized: Token is missing or invalid.
        - 403 Forbidden: User does not own the reservation.
        - 404 Not Found: Reservation with the given ID does not exist.
        - 409 Conflict: Reservation is not in a 'RESERVED' state or departure time has passed.
        - 500 Internal Server Error: A database or unexpected server error occurred.
        """
        current_username = request.user_payload.get('sub')

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        r.username, r.reservation_status, t.departure_start, t.price
                    FROM reservations r
                    INNER JOIN tickets t ON r.ticket_id = t.ticket_id
                    WHERE r.reservation_id = %s;
                """
                cursor.execute(query, [reservation_id])
                reservation_data = cursor.fetchone()

                if not reservation_data:
                    return Response({'status': 'error', 'message': 'Reservation not found.'},
                                    status=status.HTTP_404_NOT_FOUND)

                res_username, res_status, departure_start, ticket_price = reservation_data

                if res_username != current_username:
                    return Response(
                        {'status': 'error', 'message': 'Forbidden: You can only check your own reservations.'},
                        status=status.HTTP_403_FORBIDDEN)

                if res_status != 'RESERVED':
                    return Response(
                        {'status': 'error', 'message': f'Reservation cannot be canceled. Current status: {res_status}'},
                        status=status.HTTP_409_CONFLICT)

                time_now = datetime.now()
                if departure_start <= time_now:
                    return Response({'status': 'error', 'message': 'Cannot cancel a ticket after its departure time.'},
                                    status=status.HTTP_409_CONFLICT)

                time_remaining_hours = (departure_start - time_now).total_seconds() / 3600
                penalty_percentage = 10 if time_remaining_hours > 1 else 50
                penalty_amount = (ticket_price * penalty_percentage) / 100
                refund_amount = ticket_price - penalty_amount

                response_data = {
                    "reservation_id": reservation_id,
                    "ticket_price": ticket_price,
                    "time_to_departure_hours": round(time_remaining_hours, 2),
                    "penalty_percentage": penalty_percentage,
                    "penalty_amount": int(penalty_amount),
                    "refund_amount": int(refund_amount)
                }

                return Response({'status': 'success', 'cancellation_info': response_data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in GET CancellationView: {e}")
            return Response({'status': 'error', 'message': 'An unexpected error occurred.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @method_decorator(csrf_exempt)
    @method_decorator(token_required)
    def post(self, request, reservation_id):
        """
        Confirms the cancellation of a reservation.

        This method performs the actual cancellation for the authenticated user.
        All database operations are executed within a single atomic transaction
        to ensure data integrity.
        The process involves:
        1. Verifying ownership and cancellable status of the reservation again.
        2. Re-calculating the penalty and the final refund amount.
        3. Adding the refund amount to the user's wallet balance.
        4. Reverting the reservation status to 'NOT_RESERVED' and clearing the user link.
        5. Incrementing the ticket's remaining capacity by one.
        6. Creating a 'CANCEL' record in the reservations_history table.

        Path Parameter:
            reservation_id (int): The unique identifier for the reservation to be canceled.

        Request Headers:
            Authorization: Bearer <JWT_access_token>

        Successful Response (JSON - Status Code: 200 OK):
        {
            "status": "success",
            "message": "Reservation successfully canceled.",
            "refund_details": {
                "refund_amount": 450000,
                "new_wallet_balance": 1500000
            }
        }

        Error Responses (JSON):
        - Same error responses as the GET method apply here.
        """
        current_username = request.user_payload.get('sub')

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    query = """
                        SELECT
                            r.username, r.ticket_id, r.reservation_status,
                            t.departure_start, t.price, u.wallet_balance
                        FROM reservations r
                        INNER JOIN tickets t ON r.ticket_id = t.ticket_id
                        INNER JOIN users u ON r.username = u.username
                        WHERE r.reservation_id = %s FOR UPDATE OF r, t, u;
                    """
                    cursor.execute(query, [reservation_id])
                    data_for_cancellation = cursor.fetchone()

                    if not data_for_cancellation:
                        return Response({'status': 'error', 'message': 'Reservation not found.'},
                                        status=status.HTTP_404_NOT_FOUND)

                    res_username, ticket_id, res_status, departure_start, ticket_price, current_wallet_balance = data_for_cancellation

                    if res_username != current_username:
                        return Response(
                            {'status': 'error', 'message': 'Forbidden: You can only cancel your own reservations.'},
                            status=status.HTTP_403_FORBIDDEN)

                    if res_status != 'RESERVED':
                        return Response({'status': 'error',
                                         'message': f'Reservation cannot be canceled. Current status: {res_status}'},
                                        status=status.HTTP_409_CONFLICT)

                    if departure_start <= datetime.now():
                        return Response(
                            {'status': 'error', 'message': 'Cannot cancel a ticket after its departure time.'},
                            status=status.HTTP_409_CONFLICT)

                    time_remaining_hours = (departure_start - datetime.now()).total_seconds() / 3600
                    penalty_percentage = 10 if time_remaining_hours > 1 else 50
                    penalty_amount = (ticket_price * penalty_percentage) / 100
                    refund_amount = ticket_price - penalty_amount

                    new_wallet_balance = current_wallet_balance + refund_amount
                    cursor.execute("UPDATE users SET wallet_balance = %s WHERE username = %s;",
                                   [new_wallet_balance, current_username])

                    cursor.execute(
                        "UPDATE reservations SET reservation_status = 'NOT_RESERVED', username = NULL, date_and_time_of_reservation = NULL WHERE reservation_id = %s;",
                        [reservation_id])

                    cursor.execute(
                        "UPDATE tickets SET remaining_capacity = remaining_capacity + 1 WHERE ticket_id = %s;",
                        [ticket_id])

                    cursor.execute(
                        """
                        INSERT INTO reservations_history (username, reservation_id, operation_type, cancel_by)
                        VALUES (%s, %s, 'CANCEL', %s);
                        """,
                        [current_username, reservation_id, current_username]
                    )
            return Response({
                'status': 'success',
                'message': 'Reservation successfully canceled.',
                'refund_details': {
                    'refund_amount': int(refund_amount),
                    'new_wallet_balance': int(new_wallet_balance)
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in POST CancellationView: {e}")
            return Response({'status': 'error', 'message': 'An unexpected error occurred during cancellation.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateRequestView(APIView):
    """
    Allows a user to submit a request to either cancel or change the date of their reservation.
    """

    @method_decorator(csrf_exempt)
    @method_decorator(token_required)
    def post(self, request, reservation_id):
        """
        Creates a new request for a specific reservation based on the existing 'requests' table schema.

        The user must own the reservation, and it must be in 'RESERVED' status.
        The request subject can be 'CANCEL' or 'CHANGE_DATE'. A text for the request must also be provided.
        The penalty calculation for cancellation by an admin will be based on the
        'date_and_time' this request is created.

        Path Parameter:
            reservation_id (int): The ID of the reservation to create a request for.

        Request Body (JSON):
        {
            "request_subject": "CANCEL", // or "CHANGE_DATE"
            "request_text": "I need to cancel this trip due to a family emergency."
        }

        Successful Response (JSON - Status Code: 201 Created):
        {
            "status": "success",
            "message": "Your request has been submitted successfully and is pending review.",
            "request_details": {
                "request_id": 1,
                "reservation_id": 101,
                "request_subject": "CANCEL",
                "request_text": "I need to cancel this trip due to a family emergency."
            }
        }

        Error Responses (JSON):
        - 400 Bad Request: Invalid or missing parameters in the request body.
        - 401 Unauthorized: Invalid or missing token.
        - 403 Forbidden: User does not own the reservation.
        - 404 Not Found: The specified reservation does not exist.
        - 409 Conflict: The reservation is not in a cancellable state, or departure has passed.
        """
        current_username = request.user_payload.get('sub')

        try:

            data = request.data
            request_subject = data.get('request_subject')
            request_text = data.get('request_text')

            if not all([request_subject, request_text]):
                return Response(
                    {'status': 'error', 'message': "Both 'request_subject' and 'request_text' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            request_subject_upper = request_subject.upper()
            if request_subject_upper not in ['CANCEL', 'CHANGE_DATE']:
                return Response(
                    {'status': 'error', 'message': "Invalid 'request_subject'. Must be 'CANCEL' or 'CHANGE_DATE'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                with connection.cursor() as cursor:
                    query = """
                        SELECT r.username, r.reservation_status, t.departure_start
                        FROM reservations r
                        JOIN tickets t ON r.ticket_id = t.ticket_id
                        WHERE r.reservation_id = %s FOR UPDATE OF r;
                    """
                    cursor.execute(query, [reservation_id])
                    reservation_info = cursor.fetchone()

                    if not reservation_info:
                        return Response({'status': 'error', 'message': 'Reservation not found.'},
                                        status=status.HTTP_404_NOT_FOUND)

                    res_username, res_status, departure_start = reservation_info

                    if res_username != current_username:
                        return Response({'status': 'error', 'message': 'Forbidden: You do not own this reservation.'},
                                        status=status.HTTP_403_FORBIDDEN)

                    if res_status != 'RESERVED':
                        return Response({'status': 'error',
                                         'message': f'Cannot create a request for this reservation. Current status is {res_status}.'},
                                        status=status.HTTP_409_CONFLICT)

                    if departure_start <= datetime.now():
                        return Response({'status': 'error',
                                         'message': 'Cannot create a request for a ticket whose departure time has passed.'},
                                        status=status.HTTP_409_CONFLICT)

                    insert_query = """
                        INSERT INTO requests (reservation_id, username, request_subject, request_text)
                        VALUES (%s, %s, %s, %s)
                        RETURNING request_id;
                    """
                    cursor.execute(insert_query,
                                   [reservation_id, current_username, request_subject_upper, request_text])
                    new_request_id = cursor.fetchone()[0]

            return Response({
                'status': 'success',
                'message': 'Your request has been submitted successfully and is pending review.',
                'request_details': {
                    'request_id': new_request_id,
                    'reservation_id': reservation_id,
                    'request_subject': request_subject_upper,
                    'request_text': request_text
                }
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            print(f"IntegrityError in CreateRequestView: {e}")
            return Response(
                {'status': 'error', 'message': 'A data integrity conflict occurred. The reservation might not exist.'},
                status=status.HTTP_409_CONFLICT)
        except Exception as e:
            print(f"Error in CreateRequestView: {e}")
            return Response({'status': 'error', 'message': 'An unexpected error occurred.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def pay_ticket_view(request):
    """
    Handles payment for a temporarily reserved ticket.

    Only regular 'USER' roles are permitted to perform payments. 'ADMIN' roles are forbidden.
    The system ONLY checks for the temporary reservation in Redis using its reservation_id.
    If it's not found in Redis, it implies the reservation has expired or was never created,
    and an error is returned.

    Users can pay using 'WALLET', 'CRYPTOCURRENCY', or 'CREDIT_CARD'.
    - If `payment_method` is 'WALLET', the system automatically determines
      if the payment is 'SUCCESSFUL' or 'UNSUCCESSFUL' based on wallet balance.
      The 'payment_status' field in the request body should NOT be provided for 'WALLET' payments.
    - If `payment_method` is 'CRYPTOCURRENCY' or 'CREDIT_CARD', the user MUST
      provide the 'payment_status' (either 'SUCCESSFUL' or 'UNSUCCESSFUL') in the request body.
      This simulates external payment gateway responses.

    Upon successful payment, the reservation status is confirmed to 'RESERVED',
    a payment record is created, and a 'BUY' entry is added to reservation history.
    If payment fails (e.g., insufficient wallet balance or user-provided 'UNSUCCESSFUL' status),
    the temporary reservation status remains 'TEMPORARY', allowing user to retry payment
    within the expiry window. The Celery task will eventually revert it if payment is not made.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON):
    {
        "reservation_id": 101,      // Integer: ID of the temporary reservation to pay for
        "payment_method": "WALLET", // String: "WALLET", "CRYPTOCURRENCY", or "CREDIT_CARD"
        "payment_status": "SUCCESSFUL" // Optional: MUST be "SUCCESSFUL" or "UNSUCCESSFUL" for non-WALLET methods
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Payment successful. Reservation confirmed.",
        "payment_details": {
            "payment_id": 101,
            "reservation_id": 101,
            "amount_paid": 500000,
            "payment_status": "SUCCESSFUL",
            "payment_method": "WALLET",
            "date_and_time_of_payment": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
        },
        "reservation_history": {
            "operation_type": "BUY",
            "history_status": "SUCCESSFUL",
            "date_and_time": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
        },
        "new_wallet_balance": 1500000 // Only present if payment_method was WALLET
    }

    Error Response (JSON - Status Code: 400 Bad Request - e.g., insufficient wallet balance):
    {
        "status": "error",
        "message": "Payment failed: Insufficient wallet balance.",
        "payment_details": {
            "payment_id": 102,
            "reservation_id": 102,
            "amount_paid": 500000,
            "payment_status": "UNSUCCESSFUL",
            "payment_method": "WALLET",
            "date_and_time_of_payment": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
        },
        "reservation_history": {
            "operation_type": "BUY",
            "history_status": "UNSUCCESSFUL",
            "date_and_time": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
        }
    }

    Error Responses (JSON - other common errors):
    - 400 Bad Request: Invalid JSON, missing required fields, invalid payment_method,
                       invalid/missing payment_status for non-wallet methods,
                       providing payment_status for WALLET method.
    - 401 Unauthorized: Token missing or invalid.
    - 403 Forbidden: User role is not 'USER' or reservation does not belong to the user.
    - 404 Not Found: Temporary reservation not found in Redis for the given reservation_id.
    - 409 Conflict: Reservation is not in TEMPORARY status (e.g., already paid or reverted by Celery).
    - 500 Internal Server Error: Database or unexpected server errors.
    """
    current_username = request.user_payload.get('sub')
    user_role = request.user_payload.get('role')

    if not current_username:
        return JsonResponse({'status': 'error', 'message': 'Invalid token: Username missing.'}, status=401)

    if user_role != 'USER':
        return JsonResponse({
            'status': 'error',
            'message': 'Forbidden: Only regular users can make payments. Admins are not permitted.'
        }, status=403)

    try:
        data = json.loads(request.body)
        reservation_id_input = data.get('reservation_id')  # New: Get reservation_id from body
        payment_method = data.get('payment_method')
        user_provided_payment_status = data.get('payment_status')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    if not all([reservation_id_input, payment_method]):  # Updated: check for reservation_id
        return JsonResponse({'status': 'error', 'message': 'Missing required fields: reservation_id, payment_method.'},
                            status=400)

    try:
        res_id = int(reservation_id_input)  # Convert reservation_id to int
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'reservation_id must be a valid integer.'}, status=400)

    valid_payment_methods = ['WALLET', 'CRYPTOCURRENCY', 'CREDIT_CARD']
    if payment_method.upper() not in valid_payment_methods:
        return JsonResponse(
            {'status': 'error', 'message': f'Invalid payment_method. Must be one of {valid_payment_methods}.'},
            status=400)

    payment_method_upper = payment_method.upper()
    payment_successful_outcome = False
    transaction_time = datetime.now(timezone.utc)

    payment_details_for_response = {}
    history_details_for_response = {}
    new_wallet_balance = None

    actual_ticket_price_for_transaction = None

    if payment_method_upper == 'WALLET':
        if user_provided_payment_status is not None:
            return JsonResponse({'status': 'error',
                                 'message': 'Payment status cannot be provided for WALLET payments. It is determined automatically.'},
                                status=400)
    else:  # CRYPTOCURRENCY or CREDIT_CARD
        if user_provided_payment_status is None:
            return JsonResponse(
                {'status': 'error', 'message': f'Payment status is required for {payment_method_upper} payments.'},
                status=400)
        user_provided_payment_status_upper = user_provided_payment_status.upper()
        if user_provided_payment_status_upper not in ['SUCCESSFUL', 'UNSUCCESSFUL']:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid payment_status. Must be SUCCESSFUL or UNSUCCESSFUL.'},
                status=400)

    # --- START: Logic to find reservation ONLY in Redis using direct key ---
    if not redis_client:
        return JsonResponse({'status': 'error', 'message': 'Redis service unavailable.'}, status=503)

    redis_key = f"temp_reservation:{res_id}"  # Direct key construction
    cached_data_json = redis_client.get(redis_key)

    if not cached_data_json:
        return JsonResponse({'status': 'error',
                             'message': 'Temporary reservation not found in Redis or has expired. Please reserve the ticket again.'},
                            status=404)

    try:
        cached_reservation_data = json.loads(cached_data_json)
    except json.JSONDecodeError:
        print(f"Error parsing Redis data for key {redis_key}: Invalid JSON.")
        return JsonResponse({'status': 'error', 'message': 'Corrupted temporary reservation data in Redis.'},
                            status=500)

    # Validate cached data matches current user and basic reservation details
    if cached_reservation_data.get('username') != current_username:
        return JsonResponse(
            {'status': 'error', 'message': 'Forbidden: This temporary reservation does not belong to you.'}, status=403)

    # Also validate ticket_id and seat_number from cached_data against expected values if they were provided in request body.
    # For now, we only need reservation_id to GET from Redis and trust that the cached data is correct for the user.
    # If ticket_id and reservation_seat are still provided in body, you could add checks here:
    # if cached_reservation_data.get('ticket_id') != ticket_id_from_request or cached_reservation_data.get('seat_number') != reservation_seat_from_request:
    #     return JsonResponse({'status': 'error', 'message': 'Temporary reservation details mismatch.'}, status=400)

    actual_ticket_price_for_transaction = cached_reservation_data.get('ticket_price')
    if actual_ticket_price_for_transaction is None:
        print(f"Error: Ticket price not found in Redis cache for reservation {res_id}.")
        return JsonResponse({'status': 'error',
                             'message': 'Ticket price missing from temporary reservation data in Redis. Cannot proceed.'},
                            status=500)

    # --- END: Logic to find reservation ONLY in Redis using direct key ---

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # 1. Fetch current user's wallet balance and current reservation status from DB
                # This is a crucial consistency check and fetches wallet balance.
                cursor.execute(
                    """
                    SELECT u.wallet_balance, r.reservation_status, r.ticket_id
                    FROM users u
                             INNER JOIN reservations r ON u.username = r.username
                    WHERE u.username = %s
                      AND r.reservation_id = %s
                        FOR UPDATE OF u, r;
                    """,
                    [current_username, res_id]
                )
                user_res_info = cursor.fetchone()

                if not user_res_info:
                    # This implies data inconsistency or reservation got reverted by Celery very recently
                    return JsonResponse({'status': 'error',
                                         'message': 'Reservation not found in DB or its status has changed unexpectedly. Please try again.'},
                                        status=404)

                current_wallet_balance, current_res_status_db, fetched_ticket_id_db = user_res_info

                if current_res_status_db != 'TEMPORARY':
                    return JsonResponse({'status': 'error',
                                         'message': f'Reservation status is {current_res_status_db}. Only TEMPORARY reservations can be paid. It might have expired or been processed.'},
                                        status=409)

                # Double-check ticket_id consistency from Redis with DB fetched ticket_id (optional but good)
                # Here, ticket_id from Redis is 'actual_ticket_price_for_transaction'.
                # Let's define ticket_id_from_redis for clarity
                ticket_id_from_redis_cache = cached_reservation_data.get('ticket_id')

                if fetched_ticket_id_db != ticket_id_from_redis_cache:
                    print(
                        f"Warning: Ticket ID mismatch between Redis Cache ({ticket_id_from_redis_cache}) and DB ({fetched_ticket_id_db}) for reservation {res_id}. Proceeding with DB's ticket_id for integrity.")
                    # Use DB's source of truth for ticket_id going forward in DB operations
                    ticket_id_for_db_ops = fetched_ticket_id_db
                else:
                    ticket_id_for_db_ops = fetched_ticket_id_db  # Or ticket_id_from_redis_cache, they are same

                # 2. Determine payment_successful_outcome based on method
                if payment_method_upper == 'WALLET':
                    if current_wallet_balance >= actual_ticket_price_for_transaction:  # Use the price from Redis
                        payment_successful_outcome = True
                        new_wallet_balance = current_wallet_balance - actual_ticket_price_for_transaction
                        # Update user's wallet balance
                        cursor.execute("UPDATE users SET wallet_balance = %s WHERE username = %s;",
                                       [new_wallet_balance, current_username])
                    else:
                        payment_successful_outcome = False
                        new_wallet_balance = current_wallet_balance  # Wallet balance remains unchanged

                else:  # CRYPTOCURRENCY or CREDIT_CARD
                    payment_successful_outcome = (user_provided_payment_status_upper == 'SUCCESSFUL')
                    # Wallet balance remains unchanged for these methods

                    # For non-wallet payments, actual_ticket_price_for_transaction should already be from Redis.
                    # No need to re-fetch from DB here.

                # 3. Insert into payments table
                payment_status_db = 'SUCCESSFUL' if payment_successful_outcome else 'UNSUCCESSFUL'

                cursor.execute(
                    """
                    INSERT INTO payments (username, reservation_id, amount_paid, payment_status,
                                          date_and_time_of_payment, payment_method)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING payment_id, amount_paid;
                    """,
                    [current_username, res_id, actual_ticket_price_for_transaction, payment_status_db, transaction_time,
                     payment_method_upper]
                )
                payment_id, inserted_amount_paid = cursor.fetchone()

                payment_details_for_response = {
                    "payment_id": payment_id,
                    "reservation_id": res_id,
                    "amount_paid": inserted_amount_paid,
                    "payment_status": payment_status_db,
                    "payment_method": payment_method_upper,
                    "date_and_time_of_payment": transaction_time.isoformat()
                }

                # 4. Update reservation status and details
                # Only update reservation status to RESERVED if payment is successful.
                # If payment fails, status remains TEMPORARY. Celery task will revert if time expires.
                if payment_successful_outcome:
                    new_reservation_status = 'RESERVED'
                    cursor.execute(
                        """
                        UPDATE reservations
                        SET reservation_status           = %s,
                            date_and_time_of_reservation = %s
                        WHERE reservation_id = %s;
                        """,
                        [new_reservation_status, transaction_time, res_id]
                    )

                # 5. Insert into reservations_history
                history_status_db = 'SUCCESSFUL' if payment_successful_outcome else 'UNSUCCESSFUL'
                cursor.execute(
                    """
                    INSERT INTO reservations_history (username, reservation_id, date_and_time, operation_type,
                                                      buy_status, cancel_by)
                    VALUES (%s, %s, %s, 'BUY', %s, NULL);
                    """,
                    [current_username, res_id, transaction_time, history_status_db]
                )
                history_details_for_response = {
                    "operation_type": "BUY",
                    "history_status": history_status_db,
                    "date_and_time": transaction_time.isoformat()
                }

                # 6. Delete from Redis (only if payment is successful for this reservation)
                if payment_successful_outcome and redis_client:
                    redis_key_to_delete = f"temp_reservation:{res_id}"
                    try:
                        redis_client.delete(redis_key_to_delete)
                        print(f"Temporary reservation {res_id} deleted from Redis due to successful payment.")
                    except redis.exceptions.RedisError as re_del_err:
                        print(f"Redis error during deletion of temp_reservation {res_id}: {re_del_err}")

        # Final Response
        response_message = "Payment successful. Reservation confirmed." if payment_successful_outcome else "Payment failed. Please try again or use another payment method."
        response_status_code = status.HTTP_200_OK if payment_successful_outcome else status.HTTP_400_BAD_REQUEST

        response_data = {
            'status': 'success' if payment_successful_outcome else 'error',
            'message': response_message,
            'payment_details': payment_details_for_response,
            'reservation_history': history_details_for_response
        }
        if payment_method_upper == 'WALLET':
            response_data['new_wallet_balance'] = int(new_wallet_balance)

        return JsonResponse(response_data, status=response_status_code)

    except Http404 as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=404)
    except DatabaseError as e:
        print(f"DatabaseError in pay_for_ticket_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred during the payment process.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in pay_for_ticket_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def admin_cancelled_reservations_view(request):
    """
    Retrieves a list of canceled reservations, with optional filters sent in the request body.

    This endpoint is restricted to admin users only. It allows filtering
    the results based on 'username' and 'ticket_id' provided in the POST request body.
    The results are ordered by the cancellation date in descending order.

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body (JSON - all fields are optional):
    {
        "username": "user123",      // Optional: Filters for a specific user.
        "ticket_id": 45             // Optional: Filters for a specific ticket.
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "count": 1,
        "data": [
            {
                "reservation_history_id": 1,
                "cancellation_time": "YYYY-MM-DDTHH:MM:SSZ",
                "canceled_by_user": "user123",
                "ticket_id": 45,
                "reservation_id": 101,
                "departure_start": "YYYY-MM-DDTHH:MM:SSZ"
            }
            // ... more canceled reservations
        ]
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON or if 'ticket_id' is not a valid integer.
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 500 Internal Server Error: A database or unexpected server error occurred.
    """

    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse(
            {'status': 'error', 'message': 'Forbidden: This action is restricted to admin users.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'},
                                status=status.HTTP_400_BAD_REQUEST)

        username_filter = data.get('username')
        ticket_id_filter = data.get('ticket_id')

        query = """
            SELECT
                rh.reservation_history_id,
                rh.date_and_time AS cancellation_time,
                rh.username AS canceled_by_user,
                r.ticket_id,
                rh.reservation_id,
                t.departure_start
            FROM reservations_history rh
            JOIN reservations r ON rh.reservation_id = r.reservation_id
            JOIN tickets t ON r.ticket_id = t.ticket_id
            WHERE
                rh.operation_type = 'CANCEL'
        """
        params = []

        if username_filter:
            query += " AND rh.username = %s"
            params.append(username_filter)

        if ticket_id_filter is not None:
            try:
                ticket_id_int = int(ticket_id_filter)
                query += " AND r.ticket_id = %s"
                params.append(ticket_id_int)
            except (ValueError, TypeError):
                return JsonResponse(
                    {'status': 'error', 'message': "Invalid 'ticket_id' format. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        query += " ORDER BY rh.date_and_time DESC;"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            canceled_reservations = []
            for row in rows:
                reservation_dict = dict(zip(columns, row))
                if reservation_dict.get('cancellation_time') and hasattr(reservation_dict['cancellation_time'],
                                                                         'isoformat'):
                    reservation_dict['cancellation_time'] = reservation_dict['cancellation_time'].isoformat()
                if reservation_dict.get('departure_start') and hasattr(reservation_dict['departure_start'],
                                                                       'isoformat'):
                    reservation_dict['departure_start'] = reservation_dict['departure_start'].isoformat()
                canceled_reservations.append(reservation_dict)

        return JsonResponse({
            'status': 'success',
            'count': len(canceled_reservations),
            'data': canceled_reservations
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in admin_cancelled_reservations_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def admin_request_list_view(request):
    """
    Retrieves a list of user requests, with optional filters sent in the POST request body.

    This endpoint is restricted to admin users only. It allows filtering
    the results based on 'username', 'ticket_id', and 'status' provided in the
    POST request body. The results are ordered by the request creation date in
    descending order.

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body (JSON - all fields are optional):
    {
        "username": "user123",      // Optional: Filters for a specific user.
        "ticket_id": 45,            // Optional: Filters for requests related to a specific ticket.
        "status": "PENDING"         // Optional: Filters by request status ('PENDING', 'APPROVED', 'REJECTED').
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "count": 1,
        "data": [
            {
                "request_id": 1,
                "username": "user123",
                "reservation_id": 101,
                "ticket_id": 45,
                "request_subject": "CANCEL",
                "request_text": "I need to cancel this trip.",
                "requested_at": "YYYY-MM-DDTHH:MM:SSZ",
                "is_checked": false,
                "is_accepted": false
            }
            // ... more requests
        ]
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON or if 'ticket_id' is not a valid integer.
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 500 Internal Server Error: A database or unexpected server error occurred.
    """
    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse(
            {'status': 'error', 'message': 'Forbidden: This action is restricted to admin users.'},
            status=403
        )

    try:
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

        username_filter = data.get('username')
        ticket_id_filter = data.get('ticket_id')
        status_filter = data.get('status')

        query = """
            SELECT
                req.request_id, req.username, req.reservation_id, res.ticket_id,
                req.request_subject, req.request_text, req.date_and_time AS requested_at,
                req.is_checked, req.is_accepted
            FROM requests req
            JOIN reservations res ON req.reservation_id = res.reservation_id
            WHERE 1=1
        """
        params = []

        if username_filter:
            query += " AND req.username = %s"
            params.append(username_filter)

        if ticket_id_filter is not None:
            try:
                query += " AND res.ticket_id = %s"
                params.append(int(ticket_id_filter))
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'ticket_id must be an integer.'}, status=400)

        if status_filter and status_filter.upper() in ['PENDING', 'APPROVED', 'REJECTED']:
            if status_filter.upper() == 'PENDING':
                query += " AND req.is_checked = FALSE"
            elif status_filter.upper() == 'APPROVED':
                query += " AND req.is_checked = TRUE AND req.is_accepted = TRUE"
            elif status_filter.upper() == 'REJECTED':
                query += " AND req.is_checked = TRUE AND req.is_accepted = FALSE"

        query += " ORDER BY req.date_and_time DESC;"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            requests_list = []
            for row in rows:
                req_dict = dict(zip(columns, row))
                if req_dict.get('requested_at'):
                    req_dict['requested_at'] = req_dict['requested_at'].isoformat()
                requests_list.append(req_dict)

        return JsonResponse({'status': 'success', 'count': len(requests_list), 'data': requests_list})

    except Exception as e:
        print(f"Error in admin_request_list_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def admin_approve_request_view(request, request_id):
    """
    Approves and processes a user request (e.g., for cancellation).

    This endpoint verifies that the ticket's departure time has not already passed
    at the moment of approval before processing the request.

    This endpoint is for admin use only. It processes a specific user request
    identified by its ID. All database operations are performed within a single
    atomic transaction to ensure data integrity.

    If the request is for 'CANCEL', it calculates the penalty based on the time
    the user submitted the request, refunds the appropriate amount to the user's
    wallet, frees up the reserved seat, and logs the action in the history.
    The logic for 'CHANGE_DATE' requests should also be handled here if implemented.

    Path Parameter:
        request_id (int): The unique identifier for the request to be approved.

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body:
        An empty body is expected.

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Cancellation approved. 450000 has been refunded to the user's wallet."
    }

    Error Responses (JSON):
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 404 Not Found: Request with the given ID does not exist.
    - 409 Conflict: The request has already been processed.
    - 500 Internal Server Error: A database or unexpected server error occurred during approval.
    """
    admin_username = request.user_payload.get('sub')
    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Admin access required.'}, status=403)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        req.request_id, req.request_subject, req.date_and_time AS requested_at,
                        req.is_checked, res.reservation_id, res.ticket_id, 
                        res.username AS user_username, t.departure_start, t.price, u.wallet_balance
                    FROM requests req
                    JOIN reservations res ON req.reservation_id = res.reservation_id
                    JOIN tickets t ON res.ticket_id = t.ticket_id
                    JOIN users u ON res.username = u.username
                    WHERE req.request_id = %s FOR UPDATE OF req, res, t, u;
                """
                cursor.execute(query, [request_id])
                request_data = cursor.fetchone()

                if not request_data:
                    return JsonResponse({'status': 'error', 'message': 'Request not found.'}, status=404)

                columns = [col[0] for col in cursor.description]
                data_dict = dict(zip(columns, request_data))

                if data_dict['is_checked']:
                    return JsonResponse({'status': 'error',
                                         'message': f"This request has already been processed (Accepted: {data_dict.get('is_accepted', 'N/A')})."},
                                        status=409)

                departure_start_time = data_dict['departure_start']
                if departure_start_time <= datetime.now():
                    cursor.execute(
                        "UPDATE requests SET is_checked = TRUE, is_accepted = FALSE, check_by = %s WHERE request_id = %s;",
                        [admin_username, request_id])
                    return JsonResponse(
                        {'status': 'error',
                         'message': 'Cannot approve request: The departure time for this ticket has already passed. The request has been automatically rejected.'},
                        status=409
                    )

                message = ""
                if data_dict['request_subject'] == 'CANCEL':
                    time_to_departure = data_dict['departure_start'] - data_dict['requested_at']
                    time_remaining_hours = time_to_departure.total_seconds() / 3600

                    penalty_percentage = 10 if time_remaining_hours > 1 else 50
                    penalty_amount = (data_dict['price'] * penalty_percentage) / 100
                    refund_amount = data_dict['price'] - penalty_amount

                    new_wallet_balance = data_dict['wallet_balance'] + refund_amount
                    cursor.execute("UPDATE users SET wallet_balance = %s WHERE username = %s;",
                                   [new_wallet_balance, data_dict['user_username']])
                    cursor.execute(
                        "UPDATE reservations SET reservation_status = 'NOT_RESERVED', username = NULL, date_and_time_of_reservation = NULL WHERE reservation_id = %s;",
                        [data_dict['reservation_id']])
                    cursor.execute(
                        "UPDATE tickets SET remaining_capacity = remaining_capacity + 1 WHERE ticket_id = %s;",
                        [data_dict['ticket_id']])
                    cursor.execute(
                        """
                        INSERT INTO reservations_history (username, reservation_id, operation_type, cancel_by)
                        VALUES (%s, %s, 'CANCEL', %s);
                        """,
                        [data_dict['user_username'], data_dict['reservation_id'], admin_username]
                    )

                    message = f"Cancellation approved. {int(refund_amount)} has been refunded to the user's wallet."

                elif data_dict['request_subject'] == 'CHANGE_DATE':
                    # TODO: Implement complex logic for changing date
                    message = "Change Date request approved. (Change date logic needs full implementation)."

                cursor.execute(
                    "UPDATE requests SET is_checked = TRUE, is_accepted = TRUE, check_by = %s WHERE request_id = %s;",
                    [admin_username, request_id])

        return JsonResponse({'status': 'success', 'message': message})

    except Exception as e:
        print(f"Error in admin_approve_request_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred during approval.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def admin_reject_request_view(request, request_id):
    """
    Rejects a pending user request.

    This endpoint is for admin use only. It marks a specific user request
    as checked and not accepted. This is a final action and cannot be undone
    via this API. The operation is performed within an atomic transaction.

    Path Parameter:
        request_id (int): The unique identifier for the request to be rejected.

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body:
        An empty body is expected.

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Request has been rejected."
    }

    Error Responses (JSON):
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 404 Not Found: Request with the given ID does not exist.
    - 409 Conflict: The request has already been processed.
    - 500 Internal Server Error: A database or unexpected server error occurred during rejection.
    """
    admin_username = request.user_payload.get('sub')
    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Admin access required.'}, status=403)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SELECT is_checked FROM requests WHERE request_id = %s FOR UPDATE;", [request_id])
                req_status = cursor.fetchone()

                if not req_status:
                    return JsonResponse({'status': 'error', 'message': 'Request not found.'}, status=404)

                if req_status[0]:  # is_checked
                    return JsonResponse({'status': 'error', 'message': 'This request has already been processed.'},
                                        status=409)

                cursor.execute(
                    "UPDATE requests SET is_checked = TRUE, is_accepted = FALSE, check_by = %s WHERE request_id = %s;",
                    [admin_username, request_id])

        return JsonResponse({'status': 'success', 'message': 'Request has been rejected.'})

    except Exception as e:
        print(f"Error in admin_reject_request_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred during rejection.'},
                            status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def get_user_bookings_view(request):
    """
    Retrieves a list of authenticated user's bookings with optional filters.

    This API allows an authenticated 'USER' to fetch their ticket reservations.
    Admins are forbidden from using this endpoint.
    It supports filtering by reservation status (e.g., 'RESERVED', 'CANCELED'),
    by a date range for the ticket's departure date, and by origin/destination cities.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON - all fields are optional):
    {
        "reservation_status": "RESERVED",
        "start_departure_date": "YYYY-MM-DD",
        "end_departure_date": "YYYY-MM-DD",
        "origin_city": "Tehran",
        "destination_city": "Mashhad"
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "count": 2,
        "data": [
            {
                "reservation_id": 101,
                "ticket_id": 123,
                "reservation_status": "RESERVED",
                "reserved_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
                "reservation_seat": 5,
                "ticket_details": {
                    "origin_city": "Tehran",
                    "destination_city": "Mashhad",
                    "departure_start": "YYYY-MM-DDTHH:MM:SS",
                    "departure_end": "YYYY-MM-DDTHH:MM:SS",
                    "price": 500000,
                    "vehicle_type": "FLIGHT",
                    "airline_name": "Mahan Air",
                    "vehicle_details": { ... }
                },
                "payment_info": {
                    "amount_paid": 500000,
                    "payment_status": "SUCCESSFUL",
                    "payment_method": "CREDIT_CARD",
                    "date_and_time_of_payment": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
                },
                "history_info": [
                    {
                        "operation_type": "BUY",
                        "history_status": "SUCCESSFUL",
                        "date_and_time": "YYYY-MM-DDTHH:MM:SS.ffffffZ"
                    }
                ]
            }
            // ... more bookings
        ]
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON, invalid date format, invalid reservation_status, invalid city names.
    - 401 Unauthorized: Token missing or invalid.
    - 403 Forbidden: User is an admin (only regular users can access).
    - 500 Internal Server Error: Database or unexpected server errors.
    """
    current_username = request.user_payload.get('sub')
    user_role = request.user_payload.get('role')

    if not current_username:
        return JsonResponse({'status': 'error', 'message': 'Invalid token: Username missing.'}, status=401)

    if user_role != 'USER':
        return JsonResponse({
            'status': 'error',
            'message': 'Forbidden: Only regular users can view their bookings.'
        }, status=403)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

    filter_status = data.get('reservation_status')
    start_date_str = data.get('start_departure_date')
    end_date_str = data.get('end_departure_date')
    origin_city = data.get('origin_city')
    destination_city = data.get('destination_city')

    if filter_status and filter_status.upper() not in ['RESERVED', 'NOT_RESERVED', 'TEMPORARY', 'CANCELED']:
        return JsonResponse({'status': 'error', 'message': 'Invalid reservation_status provided.'}, status=400)

    start_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid start_departure_date format. Please use YYYY-MM-DD.'},
                status=400
            )

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid end_departure_date format. Please use YYYY-MM-DD.'},
                status=400
            )

    query = """
        SELECT
            r.reservation_id,
            r.ticket_id,
            r.reservation_status,
            r.date_and_time_of_reservation AS reserved_at,
            r.reservation_seat,
            t.departure_start,
            t.departure_end,
            t.price,
            v.vehicle_type,
            loc_origin.city AS origin_city,
            loc_dest.city AS destination_city,
            f.airline_name, f.flight_class, f.number_of_stop, f.flight_code, f.origin_airport, f.destination_airport, f.facility AS flight_facility,
            tr.train_stars, tr.choosing_a_closed_coupe, tr.facility AS train_facility,
            b.company_name, b.bus_type, b.number_of_chairs, b.facility AS bus_facility,
            p.amount_paid, p.payment_status AS payment_current_status, p.payment_method, p.date_and_time_of_payment,
            rh.operation_type AS history_operation_type, rh.buy_status AS history_buy_status, rh.date_and_time AS history_date_and_time
        FROM reservations r
        JOIN tickets t ON r.ticket_id = t.ticket_id
        JOIN vehicles v ON t.vehicle_id = v.vehicle_id
        JOIN locations loc_origin ON t.origin_location_id = loc_origin.location_id
        JOIN locations loc_dest ON t.destination_location_id = loc_dest.location_id
        LEFT JOIN flights f ON v.vehicle_id = f.vehicle_id AND v.vehicle_type = 'FLIGHT'
        LEFT JOIN trains tr ON v.vehicle_id = tr.vehicle_id AND v.vehicle_type = 'TRAIN'
        LEFT JOIN buses b ON v.vehicle_id = b.vehicle_id AND v.vehicle_type = 'BUS'
        LEFT JOIN payments p ON r.reservation_id = p.reservation_id AND p.payment_status = 'SUCCESSFUL'
        LEFT JOIN (
            SELECT
                rh_inner.reservation_id,
                rh_inner.operation_type,
                rh_inner.buy_status,
                rh_inner.date_and_time,
                ROW_NUMBER() OVER (PARTITION BY rh_inner.reservation_id ORDER BY rh_inner.date_and_time DESC) as rn
            FROM reservations_history rh_inner
        ) rh ON r.reservation_id = rh.reservation_id AND rh.rn = 1
        WHERE r.username = %s
    """
    params = [current_username]

    if filter_status:
        if filter_status.upper() == 'CANCELED':
            query += " AND rh.operation_type = 'CANCEL' AND rh.buy_status = 'CANCELED'"
        else:
            query += " AND r.reservation_status = %s"
            params.append(filter_status.upper())

    if start_date:
        query += " AND DATE(t.departure_start) >= %s"
        params.append(start_date)

    if end_date:
        query += " AND DATE(t.departure_start) <= %s"
        params.append(end_date)

    if origin_city:
        query += " AND loc_origin.city ILIKE %s"
        params.append(f"%{origin_city}%")

    if destination_city:
        query += " AND loc_dest.city ILIKE %s"
        params.append(f"%{destination_city}%")

    query += " ORDER BY t.departure_start DESC, r.date_and_time_of_reservation DESC;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            user_bookings = []
            for row in rows:
                booking = dict(zip(columns, row))

                for key in ['reserved_at', 'departure_start', 'departure_end', 'date_and_time_of_payment',
                            'history_date_and_time']:
                    if booking.get(key) and hasattr(booking[key], 'isoformat'):
                        booking[key] = booking[key].isoformat()

                vehicle_details = {}
                current_vehicle_type = booking.pop('vehicle_type')

                if current_vehicle_type == 'FLIGHT':
                    vehicle_details['airline_name'] = booking.pop('airline_name')
                    vehicle_details['flight_class'] = booking.pop('flight_class')
                    vehicle_details['number_of_stop'] = booking.pop('number_of_stop')
                    vehicle_details['flight_code'] = booking.pop('flight_code')
                    vehicle_details['origin_airport'] = booking.pop('origin_airport')
                    vehicle_details['destination_airport'] = booking.pop('destination_airport')
                    facility_json = booking.pop('flight_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                elif current_vehicle_type == 'TRAIN':
                    vehicle_details['train_stars'] = booking.pop('train_stars')
                    vehicle_details['choosing_a_closed_coupe'] = booking.pop('choosing_a_closed_coupe')
                    facility_json = booking.pop('train_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                elif current_vehicle_type == 'BUS':
                    vehicle_details['company_name'] = booking.pop('company_name')
                    vehicle_details['bus_type'] = booking.pop('bus_type')
                    vehicle_details['number_of_chairs'] = booking.pop('number_of_chairs')
                    facility_json = booking.pop('bus_facility')
                    if facility_json:
                        try:
                            vehicle_details['facility'] = json.loads(facility_json)
                        except json.JSONDecodeError:
                            vehicle_details['facility'] = None
                    else:
                        vehicle_details['facility'] = None

                for key_to_remove in ['airline_name', 'flight_class', 'number_of_stop', 'flight_code', 'origin_airport',
                                      'destination_airport', 'flight_facility',
                                      'train_stars', 'choosing_a_closed_coupe', 'train_facility',
                                      'company_name', 'bus_type', 'number_of_chairs', 'bus_facility']:
                    booking.pop(key_to_remove, None)

                booking['ticket_details'] = {
                    'origin_city': booking.pop('origin_city'),
                    'destination_city': booking.pop('destination_city'),
                    'departure_start': booking.pop('departure_start'),
                    'departure_end': booking.pop('departure_end'),
                    'price': booking.pop('price'),
                    'vehicle_type': current_vehicle_type,
                    'vehicle_details': vehicle_details
                }

                payment_info = {}
                if booking.get('amount_paid') is not None:
                    payment_info = {
                        'amount_paid': booking.pop('amount_paid'),
                        'payment_status': booking.pop('payment_current_status'),
                        'payment_method': booking.pop('payment_method'),
                        'date_and_time_of_payment': booking.pop('date_and_time_of_payment')
                    }
                else:
                    booking.pop('amount_paid', None)
                    booking.pop('payment_current_status', None)
                    booking.pop('payment_method', None)
                    booking.pop('date_and_time_of_payment', None)

                booking['payment_info'] = payment_info

                history_info = {}
                if booking.get('history_operation_type') is not None:
                    history_info = {
                        'operation_type': booking.pop('history_operation_type'),
                        'history_status': booking.pop('history_buy_status'),
                        'date_and_time': booking.pop('history_date_and_time')
                    }
                else:
                    booking.pop('history_operation_type', None)
                    booking.pop('history_buy_status', None)
                    booking.pop('history_date_and_time', None)

                booking['history_info'] = history_info

                user_bookings.append(booking)

        return JsonResponse({
            'status': 'success',
            'count': len(user_bookings),
            'data': user_bookings
        }, status=200)

    except DatabaseError as e:
        print(f"DatabaseError in get_user_bookings_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while fetching bookings.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in get_user_bookings_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'},
                            status=500)
