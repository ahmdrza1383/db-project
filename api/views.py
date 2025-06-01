import redis
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, DatabaseError, IntegrityError
from datetime import datetime, date
import json
import random
import string
import re

from .auth_utils import *


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
            "name": "Test User", // or null if not provided
            "role": "USER"       // Default role
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
    Updates the profile information for the authenticated user.

    This API endpoint allows an authenticated user to update their profile details
    such as name, phone number, date of birth, and city.
    Only the fields provided in the request body will be updated.
    After a successful database update, the user's profile cache in Redis
    (if exists) will be invalidated.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON - all fields are optional):
    {
        "name": "New Name",
        "phone_number": "09xxxxxxxxx", // Must be unique if changed
        "date_of_birth": "YYYY-MM-DD", // e.g., "1995-08-15"
        "city_id": 2 // New city_id
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Profile updated successfully.",
        "user_info": { // Updated user information
            "username": "currentuser",
            "name": "New Name",
            "email": "user@example.com", // Email is not updatable via this API
            "phone_number": "09xxxxxxxxx",
            "date_of_birth": "YYYY-MM-DD",
            "city_id": 2, // or null
            "role": "USER"
        }
    }

    Error Responses (JSON):
    - Invalid JSON format (400)
    - No fields provided for update (400)
    - Invalid phone number format (400)
    - Phone number already exists (409)
    - Invalid date of birth format or logical error (e.g., future date) (400)
    - Invalid city_id (foreign key violation if city_id is invalid) (400)
    - Database errors (500)
    - Unauthorized (if token is missing or invalid - handled by @token_required) (401)
    """
    try:
        username_from_token = request.user_payload.get('sub')
        if not username_from_token:
            return JsonResponse({'status': 'error', 'message': 'Invalid token: Username not found in token.'},
                                status=401)

        data = json.loads(request.body)
        if not data:
            return JsonResponse({'status': 'error',
                                 'message': 'No fields provided for update. Please provide at least one field to update.'},
                                status=400)

        fields_to_update = {}
        params = []

        if 'name' in data:
            fields_to_update['name'] = data['name']

        if 'phone_number' in data:
            phone_number_input = data['phone_number']
            if phone_number_input and phone_number_input.strip():
                phone_to_validate = phone_number_input.strip()
                phone_pattern = r"^09\d{9}$"
                if not re.match(phone_pattern, phone_to_validate):
                    return JsonResponse(
                        {'status': 'error', 'message': 'Invalid phone number format. It must be 09XXXXXXXXX.'},
                        status=400)
                fields_to_update['phone_number'] = phone_to_validate
            else:
                fields_to_update['phone_number'] = None

        if 'date_of_birth' in data:
            date_of_birth_str = data['date_of_birth']
            if date_of_birth_str:
                try:
                    dob_object = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                    if dob_object > date.today():
                        return JsonResponse({'status': 'error', 'message': 'Date of birth cannot be in the future.'},
                                            status=400)
                    fields_to_update['date_of_birth'] = dob_object
                except ValueError:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Invalid date format for date_of_birth. Please use YYYY-MM-DD.'},
                        status=400)
            else:
                fields_to_update['date_of_birth'] = None

        if 'city_id' in data:
            city_id_input = data['city_id']
            if city_id_input is not None:
                if not isinstance(city_id_input, int):
                    return JsonResponse({'status': 'error', 'message': 'city_id must be an integer or null.'},
                                        status=400)
                fields_to_update['city'] = city_id_input
            else:
                fields_to_update['city'] = None

        if not fields_to_update:
            return JsonResponse({'status': 'error', 'message': 'No valid fields provided for update.'}, status=400)

        set_clauses = [f"{field} = %s" for field in fields_to_update.keys()]
        params.extend(fields_to_update.values())
        params.append(username_from_token)

        update_query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}
            WHERE username = %s
            RETURNING username, name, email, phone_number, date_of_birth, city, user_role;
        """

        updated_user_info = None
        with connection.cursor() as cursor:
            cursor.execute(update_query, params)
            if cursor.rowcount == 0:
                return JsonResponse({'status': 'error', 'message': 'User not found or no changes made.'}, status=404)

            updated_row = cursor.fetchone()
            if updated_row:
                columns = [col[0] for col in cursor.description]
                updated_user_info = dict(zip(columns, updated_row))
            else:
                raise DatabaseError("User update succeeded but failed to return updated information.")

        # TODO : check
        """
        if redis_client:
            try:
                # فرض می‌کنیم کلید کش پروفایل به این صورت است. اگر متفاوت است، آن را تنظیم کنید.
                redis_cache_key = f"user_profile:{username_from_token}"
                deleted_count = redis_client.delete(redis_cache_key)
                if deleted_count > 0:
                    print(f"User profile cache invalidated for {username_from_token}")
            except redis.exceptions.RedisError as re_cache_err:
                # این خطا نباید باعث شکست کل عملیات شود، اما باید لاگ شود.
                print(f"Redis error during cache invalidation for user {username_from_token}: {re_cache_err}")
        """

        if updated_user_info.get('date_of_birth') and isinstance(updated_user_info['date_of_birth'], date):
            updated_user_info['date_of_birth'] = updated_user_info['date_of_birth'].isoformat()

        if 'city' in updated_user_info:
            updated_user_info['city_id'] = updated_user_info.pop('city')

        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully.',
            'user_info': updated_user_info
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except IntegrityError as e:
        error_detail_str = str(e).lower()
        if "users_phone_number_key" in error_detail_str or \
                (
                        "duplicate key value violates unique constraint" in error_detail_str and "phone_number" in error_detail_str):
            return JsonResponse(
                {'status': 'error', 'message': 'This phone number is already registered by another user.'}, status=409)
        elif ("violates foreign key constraint" in error_detail_str and (
                "users_city_id_fkey" in error_detail_str or "_city_fkey" in error_detail_str or "users_city" in error_detail_str)) and 'city' in fields_to_update and \
                fields_to_update['city'] is not None:
            return JsonResponse({'status': 'error', 'message': 'Invalid city ID provided. Location not found.'},
                                status=400)
        else:
            print(f"Database IntegrityError during profile update: {e}")
            return JsonResponse(
                {'status': 'error', 'message': 'A data integrity error occurred. Please check your inputs.'},
                status=409)
    except DatabaseError as e:
        print(f"DatabaseError during profile update: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while updating profile.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in update_user_profile_view: {e.__class__.__name__}: {e}")
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
