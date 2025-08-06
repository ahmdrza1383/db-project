import os
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
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string
import re
from rest_framework.decorators import api_view
from datetime import datetime
import json
import smtplib
from email.message import EmailMessage
from elasticsearch import Elasticsearch, NotFoundError

from .auth_utils import *
from .tasks import expire_reservation
from .elastic_utils import update_ticket_in_elastic


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


def send_otp_email_html(recipient_email, otp_code):
    """
    Renders an HTML template with the OTP and sends it as a multipart email.
    Uses the smtplib configuration from settings.
    """
    try:
        context = {'otp_code': otp_code}
        html_content = render_to_string('api/otp_email.html', context)

        text_content = strip_tags(html_content)

        msg = EmailMessage()
        msg['Subject'] = 'کد تایید ورود'
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = recipient_email

        msg.set_content(text_content)
        msg.add_alternative(html_content, subtype='html')

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        print(f"HTML Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"[EMAIL WARNING] Failed to send HTML email to {recipient_email}: {e}")
        return False


@csrf_exempt
@require_http_methods(["POST"])
def request_otp_view(request):
    """
    Requests an OTP (One-Time Password) for an existing and active user to log in.

    This API endpoint initiates the OTP-based login process. It first checks for
    an active OTP in Redis to prevent spamming. If none exists, it verifies that
    the user associated with the provided identifier (email or phone number)
    exists in the database and that their account is active.

    Upon successful validation, a new OTP is generated, stored in Redis with a
    time-to-live (TTL), and sent to the user's email address if the identifier
    is an email.

    Request Body (JSON):
    {
        "identifier": "user@example.com"
    }
    // OR
    {
        "identifier": "09123456789"
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "An OTP has been sent to {identifier} for login. It is valid for 5 minutes."
    }

    Error Responses (JSON):
    - 400 Bad Request: Returned if the request body contains invalid JSON or if the
      'identifier' field is missing.
      {"status": "error", "message": "Identifier (email or phone_number) is required."}

    - 403 Forbidden: Returned if the user's account ('profile_status') is inactive.
      {"status": "error", "message": "Your account is currently inactive. Please contact support."}

    - 404 Not Found: Returned if no user is found with the provided identifier.
      {"status": "error", "message": "User not found. Please register or check your identifier."}

    - 429 Too Many Requests: Returned if an active OTP has already been sent to this
      identifier recently. The user must wait until the previous OTP expires.
      {"status": "error", "message": "An OTP has already been sent to this identifier..."}

    - 500 Internal Server Error: Returned for unexpected database errors or other
      server-side exceptions.
      {"status": "error", "message": "A database error occurred while checking user status."}

    - 503 Service Unavailable: Returned if the Redis service is not available.
      {"status": "error", "message": "Redis service unavailable. Cannot request OTP."}
    """
    if not redis_client:
        return JsonResponse({'status': 'error', 'message': 'Redis service unavailable. Cannot request OTP.'},
                            status=503)

    try:
        data = json.loads(request.body)
        identifier = data.get('identifier')

        if not identifier:
            return JsonResponse({'status': 'error', 'message': 'Identifier (email or phone_number) is required.'},
                                status=400)

        redis_key = f"otp:{identifier}"

        if redis_client.exists(redis_key):
            ttl = redis_client.ttl(redis_key)
            wait_time_seconds = ttl if ttl and ttl > 0 else getattr(settings, 'OTP_RESEND_WAIT_SECONDS', 60)
            return JsonResponse({
                'status': 'error',
                'message': f'An OTP has already been sent to this identifier. Please try again in approximately {wait_time_seconds} seconds.'
            }, status=429)

        user_info_from_db = None
        is_email_identifier = '@' in identifier
        db_field_to_query = 'email' if is_email_identifier else 'phone_number'
        sql_query_user_check = f"SELECT username, profile_status FROM users WHERE {db_field_to_query} = %s LIMIT 1"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query_user_check, [identifier])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    user_info_from_db = dict(zip(columns, row))
        except DatabaseError as db_e:
            print(f"Database error during user check in request_otp_view: {db_e}")
            return JsonResponse({'status': 'error', 'message': 'A database error occurred while checking user status.'},
                                status=500)

        if not user_info_from_db:
            return JsonResponse(
                {'status': 'error', 'message': 'User not found. Please register or check your identifier.'},
                status=404)

        if not user_info_from_db['profile_status']:
            return JsonResponse(
                {'status': 'error', 'message': 'Your account is currently inactive. Please contact support.'},
                status=403)

        otp_code = generate_otp()
        otp_ttl_seconds = getattr(settings, 'OTP_TTL_SECONDS', 300)

        redis_client.set(name=redis_key, value=otp_code, ex=otp_ttl_seconds)

        if is_email_identifier:
            send_otp_email_html(identifier, otp_code)

        print(
            f"Generated OTP for {identifier} (User Active: {user_info_from_db['profile_status']}): {otp_code} (TTL: {otp_ttl_seconds}s)")

        return JsonResponse({
            'status': 'success',
            'message': f'An OTP has been sent to {identifier} for login. It is valid for {otp_ttl_seconds // 60} minutes.',
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
        user_info = None
        is_email = '@' in identifier
        db_field_name_for_query = 'email' if is_email else 'phone_number'

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT username FROM users WHERE {db_field_name_for_query} = %s LIMIT 1", [identifier])
                user_row = cursor.fetchone()
                if not user_row:
                    print(f"Error: User {identifier} was not found in DB during OTP verification, but OTP was valid.")
                    return JsonResponse(
                        {'status': 'error', 'message': 'User not found, despite valid OTP. Please contact support.'},
                        status=404)
                username_from_db = user_row[0]
        except DatabaseError as db_error:
            print(f"Database error during username lookup in verify_otp_view: {db_error}")
            return JsonResponse({'status': 'error', 'message': 'A database error occurred.'}, status=500)

        if redis_client:
            try:
                invalidate_user_profile_cache(username_from_db)
            except redis.exceptions.RedisError as e:
                print(f"[CACHE WARNING] Failed to invalidate cache for '{username_from_db}' during login: {e}")

        user_database_info = get_user_profile(username_from_db)

        if not user_database_info:
            return JsonResponse({'status': 'error', 'message': 'Could not retrieve user profile after verification.'},
                                status=500)

        token_payload = {
            "sub": user_database_info['username'],
            "role": user_database_info.get('user_role', 'USER')
        }
        access_token = create_access_token(data=token_payload)
        refresh_token = create_refresh_token(data=token_payload)

        return JsonResponse({
            'status': 'success',
            'message': 'Login successful! OTP verified.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_info': user_database_info
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

            inserted_user_info = dict(zip(columns, inserted_row))

        if inserted_user_info and redis_client:
            print(f"Populating cache for new user: {inserted_user_info['username']}")
            get_user_profile(inserted_user_info['username'])

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

        A special field 'add_to_wallet_balance' is introduced. If provided, the specified
        amount will be added to the user's current wallet balance atomically in the database.
        No record will be created in the 'payments' table for this specific top-up operation.

        For optional fields like 'name', 'phone_number', 'date_of_birth', and 'city_id',
        sending a 'null' value will result in a 400 Bad Request error.

        Sensitive fields like username, password, and email can be changed by providing
        'new_username', 'new_password', and 'new_email' respectively. Changing the
        username or password will result in new JWTs being issued in the response.

        After a successful database update, the user's profile cache in Redis
        is forcefully updated to ensure data consistency.

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
            "city_id": 10,
            "new_authentication_method": "PHONE_NUMBER", // or "EMAIL"
            "add_to_wallet_balance": 50000
        }

        Successful Response (JSON - Status Code: 200 OK):
        {
            "status": "success",
            "message": "Profile updated successfully.",
            "access_token": "<new_jwt_access_token_if_needed>",
            "refresh_token": "<new_jwt_refresh_token_if_needed>",
            "user_info": {
                "username": "current_or_new_username",
                "name": "New Full Name",
                "email": "current_or_new_email@example.com",
                "phone_number": "09123456780",
                "date_of_birth": "1990-01-01",
                "city_id": 10,
                "authentication_method": "PHONE_NUMBER",
                "role": "USER",
                "wallet_balance": 1500000 // Updated wallet balance
            }
        }

        Error Responses (JSON):
        - 400 Bad Request: Returned for various input validation failures:
            * Invalid JSON format.
            * Providing 'null' or empty values for fields that do not support it.
            * Invalid data format (e.g., for email, phone number, date, city_id).
            * Providing a non-positive or non-integer value for 'add_to_wallet_balance'.
            * Sending an empty request body or no valid fields for an update.

        - 401 Unauthorized: Returned if the Authorization token is missing, malformed, or invalid.

        - 404 Not Found: Returned if the user associated with the token is not found in the database,
          or if an update query affects zero rows unexpectedly.

        - 409 Conflict: Returned if a new 'username', 'email', or 'phone_number' is provided
          and it already exists in the database for another user.

        - 500 Internal Server Error: Returned for unexpected database errors or other
          unhandled exceptions on the server side.
        """
    try:
        current_username_from_token = request.user_payload.get('sub')
        if not current_username_from_token:
            return JsonResponse({'status': 'error', 'message': 'Invalid token: Username not found in token payload.'},
                                status=401)

        try:
            data_payload = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

        if not data_payload:
            return JsonResponse({'status': 'error', 'message': 'No fields provided for update.'}, status=400)

        fields_to_set = {}
        add_to_wallet_amount = 0
        requires_new_jwt_token = False

        if 'add_to_wallet_balance' in data_payload:
            wallet_amount_input = data_payload.pop('add_to_wallet_balance')
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

        for field, value in data_payload.items():
            if field == 'name':
                if value is None or not str(value).strip():
                    return JsonResponse({'status': 'error', 'message': 'Name cannot be null or empty.'}, status=400)
                fields_to_set['name'] = str(value).strip()

            elif field == 'phone_number':
                if value is None:
                    return JsonResponse({'status': 'error', 'message': 'Phone number cannot be null.'}, status=400)
                phone_to_validate = str(value).strip()
                if not re.match(r"^09\d{9}$", phone_to_validate):
                    return JsonResponse({'status': 'error', 'message': 'Invalid phone number format (09XXXXXXXXX).'},
                                        status=400)
                fields_to_set['phone_number'] = phone_to_validate

            elif field == 'date_of_birth':
                if value is None:
                    return JsonResponse({'status': 'error', 'message': 'Date of birth cannot be null.'}, status=400)
                try:
                    dob_obj = datetime.strptime(str(value), '%Y-%m-%d').date()
                    if dob_obj > date.today():
                        return JsonResponse({'status': 'error', 'message': 'Date of birth cannot be in the future.'},
                                            status=400)
                    fields_to_set['date_of_birth'] = dob_obj
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid date format (YYYY-MM-DD).'}, status=400)

            elif field == 'city_id':
                if value is None:
                    return JsonResponse({'status': 'error', 'message': 'City ID cannot be null.'}, status=400)
                if not isinstance(value, int):
                    return JsonResponse({'status': 'error', 'message': 'city_id must be an integer.'}, status=400)
                fields_to_set['city'] = value

            elif field == 'new_username':
                if value is None or not str(value).strip():
                    return JsonResponse({'status': 'error', 'message': 'New username cannot be null or empty.'},
                                        status=400)
                new_username_val = str(value).strip()
                if new_username_val != current_username_from_token:
                    fields_to_set['username'] = new_username_val
                    requires_new_jwt_token = True

            elif field == 'new_password':
                if value is None or not str(value):
                    return JsonResponse({'status': 'error', 'message': 'New password cannot be null or empty.'},
                                        status=400)
                fields_to_set['password'] = generate_password_hash(str(value))
                requires_new_jwt_token = True

            elif field == 'new_email':
                if value is None or not str(value).strip():
                    return JsonResponse({'status': 'error', 'message': 'New email cannot be null or empty.'},
                                        status=400)
                email_to_validate = str(value).strip()
                if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_to_validate):
                    return JsonResponse({'status': 'error', 'message': 'Invalid new email format.'}, status=400)
                fields_to_set['email'] = email_to_validate

            elif field == 'new_authentication_method':
                if value is None or not str(value).strip():
                    return JsonResponse(
                        {'status': 'error', 'message': 'New authentication method cannot be null or empty.'},
                        status=400)
                auth_method_val = str(value).upper().strip()
                if auth_method_val not in ['EMAIL', 'PHONE_NUMBER']:
                    return JsonResponse({'status': 'error',
                                         'message': "Invalid authentication_method. Must be 'EMAIL' or 'PHONE_NUMBER'."},
                                        status=400)
                fields_to_set['authentication_method'] = auth_method_val

        if not fields_to_set and add_to_wallet_amount == 0:
            return JsonResponse({'status': 'error', 'message': 'No valid fields or changes provided for update.'},
                                status=400)

        set_clauses = []
        params = []

        for field, value in fields_to_set.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        if add_to_wallet_amount > 0:
            set_clauses.append("wallet_balance = wallet_balance + %s")
            params.append(add_to_wallet_amount)

        params.append(current_username_from_token)

        update_query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}
            WHERE username = %s
            RETURNING *;
        """

        updated_user_data_from_db = None
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(update_query, params)
                if cursor.rowcount == 0:
                    return JsonResponse(
                        {'status': 'error', 'message': 'User not found or no effective changes were applied.'},
                        status=404)

                updated_row = cursor.fetchone()
                columns = [col[0] for col in cursor.description]
                updated_user_data_from_db = dict(zip(columns, updated_row))

        final_username_in_db = updated_user_data_from_db.get('username')

        if redis_client:
            try:
                if final_username_in_db != current_username_from_token:
                    invalidate_user_profile_cache(current_username_from_token)

                invalidate_user_profile_cache(final_username_in_db)
                get_user_profile(final_username_in_db)
            except redis.exceptions.RedisError as re_cache_err:
                print(f"Redis error during profile cache update: {re_cache_err}")

        user_info_for_response = updated_user_data_from_db.copy()
        user_info_for_response.pop('password', None)

        if user_info_for_response.get('date_of_birth') and isinstance(user_info_for_response['date_of_birth'], date):
            user_info_for_response['date_of_birth'] = user_info_for_response['date_of_birth'].isoformat()
        if user_info_for_response.get('date_of_sign_in') and hasattr(user_info_for_response['date_of_sign_in'],
                                                                     'isoformat'):
            user_info_for_response['date_of_sign_in'] = user_info_for_response['date_of_sign_in'].isoformat()
        if 'city' in user_info_for_response:
            user_info_for_response['city_id'] = user_info_for_response.pop('city')

        response_json_data = {'status': 'success', 'message': 'Profile updated successfully.',
                              'user_info': user_info_for_response}

        if requires_new_jwt_token:
            new_jwt_payload = {"sub": final_username_in_db, "role": user_info_for_response.get('user_role', 'USER')}
            response_json_data['access_token'] = create_access_token(data=new_jwt_payload)
            response_json_data['refresh_token'] = create_refresh_token(data=new_jwt_payload)

        return JsonResponse(response_json_data)

    except IntegrityError as e:
        err_str = str(e).lower()
        if "users_pkey" in err_str or "users_username_key" in err_str:
            return JsonResponse({'status': 'error', 'message': 'This username is already taken.'}, status=409)
        if "users_email_key" in err_str:
            return JsonResponse({'status': 'error', 'message': 'This email address is already registered.'}, status=409)
        if "users_phone_number_key" in err_str:
            return JsonResponse({'status': 'error', 'message': 'This phone number is already registered.'}, status=409)
        if "violates foreign key constraint" in err_str and "city" in err_str:
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
@token_required
def get_user_profile_view(request):
    """
    Retrieves and returns the profile information for the authenticated user.
    """
    current_username = request.user_payload.get('sub')
    if not current_username:
        return JsonResponse({'status': 'error', 'message': 'Invalid token: Username not found in token payload.'},
                            status=401)

    try:
        user_profile = get_user_profile(current_username)
        if user_profile:
            return JsonResponse({'status': 'success', 'user_info': user_profile})
        else:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f"Error fetching user profile: {e}")
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
    Searches for tickets using Elasticsearch based on various criteria.

    This endpoint receives a JSON payload with search filters and constructs a
    dynamic query to search the 'tickets' index in Elasticsearch. It supports
    required fields like origin, destination, and date, as well as a wide
    range of optional filters for vehicle type, price, company, and specific
    vehicle attributes.

    Request Body (JSON):
    {
        "origin_city": "Tehran",
        "destination_city": "Mashhad",
        "departure_date": "2025-07-10",
        "vehicle_type": "BUS",           // Optional: 'FLIGHT', 'TRAIN', 'BUS'
        "min_price": 100000,             // Optional
        "max_price": 500000,             // Optional
        "company_name": "Hamsafar",      // Optional (for Flight/Bus)
        "flight_class": "Economy",       // Optional (for Flight)
        "train_stars": 4,                // Optional (for Train)
        "bus_type": "VIP"                // Optional (for Bus)
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "data": [
            {
                "ticket_id": 22,
                "origin_city": "Tehran",
                "destination_city": "Qazvin",
                // ... other ticket details
            }
        ],
        "cached": false
    }

    Error Responses (JSON):
    - 400 Bad Request: For invalid JSON, missing required fields, or bad data formats.
    - 500 Internal Server Error: For database or unexpected server errors.
    - 503 Service Unavailable: If the connection to Elasticsearch fails.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    if not all(k in data for k in ['origin_city', 'destination_city', 'departure_date']):
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required parameters: origin_city, destination_city, departure_date'
        }, status=400)

    try:
        es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
        es_client = Elasticsearch(
            hosts=[{"host": es_host, "port": 9200, "scheme": "http"}]
        )
        if not es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
    except Exception as e:
        print(f"Elasticsearch connection error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Search service is temporarily unavailable.'}, status=503)

    search_query = {
        "query": {
            "bool": {
                "must": [],
                "filter": [
                    {"term": {"ticket_status": True}}
                ]
            }
        }
    }

    search_query["query"]["bool"]["must"].append({"match": {"origin_city": data["origin_city"]}})
    search_query["query"]["bool"]["must"].append({"match": {"destination_city": data["destination_city"]}})

    try:
        date_str = data['departure_date']
        start_of_day = f"{date_str}T00:00:00"
        end_of_day = f"{date_str}T23:59:59"
        search_query["query"]["bool"]["filter"].append({
            "range": {
                "departure_start": {
                    "gte": start_of_day,
                    "lte": end_of_day,
                    "format": "yyyy-MM-dd'T'HH:mm:ss"
                }
            }
        })
    except (ValueError, KeyError):
        return JsonResponse({'status': 'error', 'message': 'Invalid date format for departure_date (YYYY-MM-DD).'},
                            status=400)

    if data.get("vehicle_type"):
        search_query["query"]["bool"]["filter"].append({"term": {"vehicle_type": data["vehicle_type"].upper()}})

    price_range_query = {}
    if data.get("min_price"):
        price_range_query["gte"] = data["min_price"]
    if data.get("max_price"):
        price_range_query["lte"] = data["max_price"]
    if price_range_query:
        search_query["query"]["bool"]["filter"].append({"range": {"price": price_range_query}})

    if data.get("company_name"):
        search_query["query"]["bool"]["must"].append({
            "multi_match": {
                "query": data["company_name"],
                "fields": ["airline_name", "company_name"],
                "fuzziness": "AUTO"
            }
        })

    if data.get("flight_class"):
        search_query["query"]["bool"]["filter"].append({"term": {"flight_class.keyword": data["flight_class"]}})

    if data.get("train_stars"):
        search_query["query"]["bool"]["filter"].append({"term": {"train_stars": data["train_stars"]}})

    if data.get("bus_type"):
        search_query["query"]["bool"]["filter"].append({"term": {"bus_type.keyword": data["bus_type"]}})

    try:
        response = es_client.search(index="tickets", body=search_query, size=100)  # Increase size to get more results
        results = [hit['_source'] for hit in response['hits']['hits']]
        return JsonResponse({"status": "success", "data": results, "cached": False})
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred during the search.'}, status=500)


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
    Also, the temporary reservation details (including ticket_price and ticket_departure_start)
    are cached in Redis for 10 minutes.

    ***ADDED CHECK: Cannot reserve if ticket departure time is in the past.***

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

        ticket_price_from_db = None
        departure_start_time = None

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT remaining_capacity, ticket_status, price, departure_start FROM tickets WHERE ticket_id = %s FOR UPDATE;",
                    [ticket_id]
                )
                ticket_info = cursor.fetchone()

                if not ticket_info:
                    raise Http404(f"Ticket with ID {ticket_id} not found.")

                current_remaining_capacity, ticket_is_active, ticket_price_from_db, departure_start_time = ticket_info

                now_utc = datetime.now(timezone.utc)
                if departure_start_time.tzinfo is None:
                    departure_start_time = departure_start_time.replace(tzinfo=timezone.utc)

                if departure_start_time <= now_utc:
                    return JsonResponse({'status': 'error',
                                         'message': 'Cannot reserve a ticket for a trip that has already started or passed.'},
                                        status=409)

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
                    return JsonResponse({'status': 'error',
                                         'message': f"Seat number {seat_number} not found for ticket ID {ticket_id}. Please check available seats."},
                                        status=404)

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

                transaction.on_commit(
                    lambda: update_ticket_in_elastic(ticket_id, {"remaining_capacity": new_remaining_capacity})
                )

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
                reservation_for_cache[
                    'ticket_departure_start'] = departure_start_time.isoformat()

                try:
                    redis_client.setex(
                        redis_key,
                        expiry_seconds,
                        json.dumps(reservation_for_cache)
                    )
                    print(
                        f"Temporary reservation {reservation_id_to_monitor} cached in Redis for {expiry_minutes_setting} minutes with price {ticket_price_from_db} and departure {departure_start_time.isoformat()}.")
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
       Handles checking cancellation policies (GET).
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

    ***ADDED CHECK: Cannot pay if ticket departure time is in the past (retrieved solely from Redis cache).***

    Users can pay using 'WALLET', 'CRYPTOCURRENCY', or 'CREDIT_CARD'.
    - If `payment_method` is 'WALLET', the system automatically determines
      if the payment is 'SUCCESSFUL' or 'UNSUCCESSFUL' based on wallet balance.
    - If `payment_method` is 'CRYPTOCURRENCY', or 'CREDIT_CARD', the user MUST
      provide the 'payment_status' (either 'SUCCESSFUL' or 'UNSUCCESSFUL') in the request body.

    Upon successful payment, the reservation status is confirmed to 'RESERVED',
    a payment record is created, and a 'BUY' entry is added to reservation history.
    If payment fails (e.g., insufficient wallet balance or user-provided 'UNSUCCESSFUL' status),
    the temporary reservation status remains 'TEMPORARY', allowing user to retry payment
    within the expiry window. The Celery task will eventually revert it if payment is not made.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON):
    {
        "reservation_id": 101,
        "payment_method": "WALLET",
        "payment_status": "SUCCESSFUL"
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Payment successful. Reservation confirmed.",
        "payment_details": { ... },
        "reservation_history": { ... },
        "new_wallet_balance": 1500000
    }

    Error Response (JSON - Status Code: 400 Bad Request):
    {
        "status": "error",
        "message": "Payment failed: Insufficient wallet balance.",
        "payment_details": { ... },
        "reservation_history": { ... }
    }

    Error Responses (JSON - other common errors):
    - 400 Bad Request: Invalid JSON, missing required fields, invalid payment_method, etc.
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
        reservation_id_input = data.get('reservation_id')
        payment_method = data.get('payment_method')
        user_provided_payment_status = data.get('payment_status')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    if not all([reservation_id_input, payment_method]):
        return JsonResponse({'status': 'error', 'message': 'Missing required fields: reservation_id, payment_method.'},
                            status=400)

    try:
        res_id = int(reservation_id_input)
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
    else:
        if user_provided_payment_status is None:
            return JsonResponse(
                {'status': 'error', 'message': f'Payment status is required for {payment_method_upper} payments.'},
                status=400)
        user_provided_payment_status_upper = user_provided_payment_status.upper()
        if user_provided_payment_status_upper not in ['SUCCESSFUL', 'UNSUCCESSFUL']:
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid payment_status. Must be SUCCESSFUL or UNSUCCESSFUL.'},
                status=400)

    try:
        redis_client_local = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        redis_client_local.ping()
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis within pay_ticket_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'Redis service unavailable. Cannot process payment.'},
                            status=503)
    except AttributeError:
        print("Redis settings (REDIS_HOST, REDIS_PORT) not found in Django settings within pay_ticket_view.")
        return JsonResponse({'status': 'error', 'message': 'Redis settings missing. Cannot process payment.'},
                            status=500)

    redis_key = f"temp_reservation:{res_id}"
    cached_data_json = redis_client_local.get(redis_key)

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

    if cached_reservation_data.get('username') != current_username:
        return JsonResponse(
            {'status': 'error', 'message': 'Forbidden: This temporary reservation does not belong to you.'}, status=403)

    actual_ticket_price_for_transaction = cached_reservation_data.get('ticket_price')
    ticket_departure_start_str_from_cache = cached_reservation_data.get(
        'ticket_departure_start')
    if actual_ticket_price_for_transaction is None or ticket_departure_start_str_from_cache is None:
        print(f"Error: Ticket price or departure time not found in Redis cache for reservation {res_id}.")
        return JsonResponse({'status': 'error',
                             'message': 'Ticket details missing from temporary reservation data in Redis. Cannot proceed.'},
                            status=500)

    try:
        departure_start_time_from_cache = datetime.fromisoformat(ticket_departure_start_str_from_cache)
        now_utc = datetime.now(timezone.utc)

        if departure_start_time_from_cache.tzinfo is None:
            departure_start_time_from_cache = departure_start_time_from_cache.replace(tzinfo=timezone.utc)

        if departure_start_time_from_cache <= now_utc:
            return JsonResponse({'status': 'error',
                                 'message': 'Cannot pay for a ticket for a trip that has already started or passed. This temporary reservation will expire soon.'},
                                status=409)
    except ValueError as ve:
        print(f"Error parsing departure time from cache for reservation {res_id}: {ve}")
        return JsonResponse({'status': 'error', 'message': 'Corrupted departure time in temporary reservation data.'},
                            status=500)

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
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
                    return JsonResponse({'status': 'error',
                                         'message': 'Reservation not found in DB or its status has changed unexpectedly. Please try again.'},
                                        status=404)

                current_wallet_balance, current_res_status_db, fetched_ticket_id_db = user_res_info

                if current_res_status_db != 'TEMPORARY':
                    return JsonResponse({'status': 'error',
                                         'message': f'Reservation status is {current_res_status_db}. Only TEMPORARY reservations can be paid. It might have expired or been processed.'},
                                        status=409)

                ticket_id_from_redis_cache = cached_reservation_data.get('ticket_id')

                if fetched_ticket_id_db != ticket_id_from_redis_cache:
                    print(
                        f"Warning: Ticket ID mismatch between Redis Cache ({ticket_id_from_redis_cache}) and DB ({fetched_ticket_id_db}) for reservation {res_id}. Proceeding with DB's ticket_id for integrity.")
                    ticket_id_for_db_ops = fetched_ticket_id_db
                else:
                    ticket_id_for_db_ops = fetched_ticket_id_db

                if payment_method_upper == 'WALLET':
                    if current_wallet_balance >= actual_ticket_price_for_transaction:
                        payment_successful_outcome = True
                        new_wallet_balance = current_wallet_balance - actual_ticket_price_for_transaction
                        cursor.execute("UPDATE users SET wallet_balance = %s WHERE username = %s;",
                                       [new_wallet_balance, current_username])

                        if redis_client:
                            try:
                                invalidate_user_profile_cache(current_username)
                                get_user_profile(current_username)
                                print(
                                    f"User profile cache forcefully updated for '{current_username}' after successful wallet payment.")
                            except redis.exceptions.RedisError as re_cache_err:
                                print(f"Redis error during cache update after payment: {re_cache_err}")

                    else:
                        payment_successful_outcome = False
                        new_wallet_balance = current_wallet_balance

                else:
                    payment_successful_outcome = (user_provided_payment_status_upper == 'SUCCESSFUL')

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

                if payment_successful_outcome:
                    redis_key_to_delete = f"temp_reservation:{res_id}"
                    try:
                        redis_client_local.delete(redis_key_to_delete)
                        print(f"Temporary reservation {res_id} deleted from Redis due to successful payment.")
                    except redis.exceptions.RedisError as re_del_err:
                        print(f"Redis error during deletion of temp_reservation {res_id}: {re_del_err}")

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
        print(f"DatabaseError in pay_ticket_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred during the payment process.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in pay_ticket_view: {e.__class__.__name__}: {e}")
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
    Crucially, it also UPDATES the `ticket_details` cache in Redis for the affected ticket
    to reflect changes like `remaining_capacity`, without changing its TTL.
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
                        SELECT req.request_id, \
                               req.request_subject, \
                               req.date_and_time AS requested_at, \
                               req.is_checked, \
                               res.reservation_id, \
                               res.ticket_id, \
                               res.username      AS user_username, \
                               t.departure_start, \
                               t.price, \
                               u.wallet_balance, \
                               t.remaining_capacity 
                        FROM requests req
                                 JOIN reservations res ON req.reservation_id = res.reservation_id
                                 JOIN tickets t ON res.ticket_id = t.ticket_id
                                 JOIN users u ON res.username = u.username
                        WHERE req.request_id = %s FOR UPDATE OF req, res, t, u; \
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
                if departure_start_time.tzinfo is None:
                    departure_start_time = departure_start_time.replace(tzinfo=timezone.utc)

                now_utc = datetime.now(timezone.utc)

                if departure_start_time <= now_utc:
                    cursor.execute(
                        "UPDATE requests SET is_checked = TRUE, is_accepted = FALSE, check_by = %s WHERE request_id = %s;",
                        [admin_username, request_id])
                    return JsonResponse(
                        {'status': 'error',
                         'message': 'Cannot approve request: The departure time for this ticket has already passed. The request has been automatically rejected.'},
                        status=409
                    )

                user_to_update = data_dict['user_username']
                message = ""

                current_remaining_capacity = data_dict['remaining_capacity']

                if data_dict['request_subject'] == 'CANCEL':
                    request_submit_time = data_dict['requested_at']
                    if request_submit_time.tzinfo is None:
                        request_submit_time = request_submit_time.replace(tzinfo=timezone.utc)

                    time_to_departure_from_request_submit = (
                                                                    departure_start_time - request_submit_time).total_seconds() / 3600

                    penalty_percentage = 10 if time_to_departure_from_request_submit > 1 else 50
                    penalty_amount = (data_dict['price'] * penalty_percentage) / 100
                    refund_amount = data_dict['price'] - penalty_amount

                    new_wallet_balance = data_dict['wallet_balance'] + refund_amount
                    cursor.execute("UPDATE users SET wallet_balance = %s WHERE username = %s;",
                                   [new_wallet_balance, user_to_update])
                    if redis_client:
                        try:
                            invalidate_user_profile_cache(user_to_update)
                            get_user_profile(user_to_update)
                            print(
                                f"User profile cache forcefully updated for '{user_to_update}' after cancellation refund.")
                        except redis.exceptions.RedisError as re_cache_err:
                            print(f"Redis error during user profile cache update after refund: {re_cache_err}")
                        except Exception as e:
                            print(f"Error processing user profile cache in admin_approve_request_view: {e}")

                    cursor.execute(
                        "UPDATE reservations SET reservation_status = 'NOT_RESERVED', username = NULL, date_and_time_of_reservation = NULL WHERE reservation_id = %s;",
                        [data_dict['reservation_id']])

                    new_remaining_capacity = current_remaining_capacity + 1
                    cursor.execute(
                        "UPDATE tickets SET remaining_capacity = %s WHERE ticket_id = %s;",
                        [new_remaining_capacity, data_dict['ticket_id']])

                    final_ticket_id = data_dict['ticket_id']
                    transaction.on_commit(
                        lambda: update_ticket_in_elastic(final_ticket_id,
                                                         {"remaining_capacity": new_remaining_capacity})
                    )

                    cursor.execute(
                        """
                        INSERT INTO reservations_history (username, reservation_id, date_and_time, operation_type,
                                                          buy_status, cancel_by)
                        VALUES (%s, %s, %s, 'CANCEL', NULL , %s);
                        """,
                        [data_dict['user_username'], data_dict['reservation_id'], datetime.now(timezone.utc),
                         admin_username]
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

                if req_status[0]:
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
    Retrieves the authenticated user's reservation history with extensive filtering options.

    This API uses the 'reservations_history' table as the source of truth, showing a log
    of all 'BUY' (successful) and 'CANCEL' operations. It allows filtering by:
    - Final status of the reservation ('RESERVED' or 'CANCELED')
    - Departure date range for the ticket
    - Origin and destination cities

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON - all fields are optional):
    {
        "status": "RESERVED",             // or "CANCELED"
        "start_departure_date": "YYYY-MM-DD",
        "end_departure_date": "YYYY-MM-DD",
        "origin_city": "Tehran",
        "destination_city": "Mashhad",
        "ticket_id": 123,
        "reservation_id": 101,
        "operation_type": "BUY"
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "count": 1,
        "data": [
            {
                "history_id": 1,
                "reservation_id": 101,
                "ticket_id": 123,
                "operation_type": "BUY",
                "operation_status": "SUCCESSFUL",
                "operation_time": "YYYY-MM-DDTHH:MM:SSZ",
                "ticket_details": {
                    "origin_city": "Tehran",
                    "destination_city": "Mashhad",
                    "departure_start": "YYYY-MM-DDTHH:MM:SS"
                }
            }
        ]
    }
    Error Responses (JSON):
    - 400 Bad Request: Returned under the following conditions:
        * If the request body contains invalid JSON.
          {"status": "error", "message": "Invalid JSON format."}
        * If 'ticket_id' or 'reservation_id' are provided but are not valid integers.
          {"status": "error", "message": "Invalid ticket_id. Must be an integer."}
        * If 'operation_type' is provided with a value other than 'BUY' or 'CANCEL'.
          {"status": "error", "message": "Invalid operation_type. Must be 'BUY' or 'CANCEL'."}
        * If 'reservation_status' is provided with a value other than 'RESERVED' or 'CANCELED'.
          {"status": "error", "message": "Invalid reservation_status. Use 'RESERVED' or 'CANCELED'."}
        * If 'start_departure_date' or 'end_departure_date' have an invalid format.
          {"status": "error", "message": "Invalid date format. Please use YYYY-MM-DD."}

    - 401 Unauthorized: Returned if the 'Authorization' header is missing or the JWT is invalid.
      (This is typically handled by the @token_required decorator).

    - 403 Forbidden: Returned if the authenticated user is not a regular user (i.e., has a role other than 'USER').
      {"status": "error", "message": "Forbidden: Only regular users can view their bookings."}

    - 500 Internal Server Error: Returned for any unexpected database errors or other server-side exceptions.
      {"status": "error", "message": "A database error occurred while fetching history."}
      {"status": "error", "message": "An unexpected server error occurred."}
    """
    current_username = request.user_payload.get('sub')
    user_role = request.user_payload.get('role')

    if user_role != 'USER':
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Only regular users can view their bookings.'},
                            status=403)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    filter_status = data.get('status')
    start_date_str = data.get('start_departure_date')
    end_date_str = data.get('end_departure_date')
    origin_city = data.get('origin_city')
    destination_city = data.get('destination_city')
    filter_ticket_id = data.get('ticket_id')
    filter_reservation_id = data.get('reservation_id')
    filter_operation_type = data.get('operation_type')

    start_date, end_date = None, None
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

    query = """
        SELECT
            rh.reservation_history_id AS history_id,
            rh.reservation_id,
            rh.operation_type,
            rh.buy_status AS operation_status,
            rh.date_and_time AS operation_time,
            res.ticket_id,
            t.departure_start,
            loc_origin.city AS origin_city,
            loc_dest.city AS destination_city
        FROM reservations_history rh
        JOIN reservations res ON rh.reservation_id = res.reservation_id
        JOIN tickets t ON res.ticket_id = t.ticket_id
        JOIN locations loc_origin ON t.origin_location_id = loc_origin.location_id
        JOIN locations loc_dest ON t.destination_location_id = loc_dest.location_id
        WHERE rh.username = %s
    """
    params = [current_username]

    if filter_status:
        status_upper = filter_status.upper()
        if status_upper == 'RESERVED':
            query += " AND rh.operation_type = 'BUY'"
        elif status_upper == 'CANCELED':
            query += " AND rh.operation_type = 'CANCEL'"
        else:
            return JsonResponse(
                {'status': 'error', 'message': "Invalid reservation_status. Use 'RESERVED' or 'CANCELED'."}, status=400)

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

    if filter_ticket_id is not None:
        try:
            query += " AND res.ticket_id = %s"
            params.append(int(filter_ticket_id))
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid ticket_id. Must be an integer.'}, status=400)

    if filter_reservation_id is not None:
        try:
            query += " AND rh.reservation_id = %s"
            params.append(int(filter_reservation_id))
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid reservation_id. Must be an integer.'},
                                status=400)

    if filter_operation_type:
        op_type = filter_operation_type.upper()
        if op_type not in ['BUY', 'CANCEL']:
            return JsonResponse({'status': 'error', 'message': "Invalid operation_type. Must be 'BUY' or 'CANCEL'."},
                                status=400)
        query += " AND rh.operation_type = %s"
        params.append(op_type)

    query += " ORDER BY rh.date_and_time DESC;"

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            user_history = []
            for row in rows:
                history_entry = dict(zip(columns, row))

                for key in ['operation_time', 'departure_start']:
                    if history_entry.get(key) and hasattr(history_entry[key], 'isoformat'):
                        history_entry[key] = history_entry[key].isoformat()

                history_entry['ticket_details'] = {
                    'origin_city': history_entry.pop('origin_city'),
                    'destination_city': history_entry.pop('destination_city'),
                    'departure_start': history_entry.pop('departure_start')
                }

                user_history.append(history_entry)

        return JsonResponse({
            'status': 'success',
            'count': len(user_history),
            'data': user_history
        }, status=200)

    except DatabaseError as e:
        print(f"DatabaseError in get_user_bookings_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while fetching history.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in get_user_bookings_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def report_ticket_issue_view(request):
    """
    Allows an authenticated user to report an issue related to their ticket reservation.

    This API is restricted to regular 'USER' roles. It enables users to submit reports
    for issues such as payment problems, incorrect ticket information, unexpected cancellations, etc.
    The report is associated with a specific reservation and includes a subject and a detailed text.

    Request Headers:
        Authorization: Bearer <JWT_access_token>

    Request Body (JSON):
    {
        "reservation_id": 123,           // Integer: The ID of the reservation the issue is about.
        "report_type": "PAYMENT",        // String: Type of the report (e.g., "PAYMENT", "TRAVEL_DELAY", "CANCEL", "OTHER").
        "report_text": "My payment failed but the ticket is still showing as temporary." // String: Detailed description of the issue.
    }

    Successful Response (JSON - Status Code: 201 Created):
    {
        "status": "success",
        "message": "Your issue report has been submitted successfully.",
        "report_details": {
            "report_id": 1,
            "reservation_id": 123,
            "username": "currentUser",
            "report_type": "PAYMENT",
            "report_text": "My payment failed but the ticket is still showing as temporary.",
            "report_status": "UNCHECKED"
        }
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON format, missing required fields, invalid report_type, invalid reservation_id.
    - 401 Unauthorized: Token missing or invalid.
    - 403 Forbidden: User is an admin (only regular users can submit reports) or user does not own the reservation.
    - 404 Not Found: Reservation with the given ID does not exist for the current user.
    - 409 Conflict: Reservation is not in a reportable status (e.g., already canceled or not found).
    - 500 Internal Server Error: Database or unexpected server errors.
    """
    current_username = request.user_payload.get('sub')
    user_role = request.user_payload.get('role')

    if not current_username:
        return JsonResponse({'status': 'error', 'message': 'Invalid token: Username missing.'}, status=401)

    if user_role != 'USER':
        return JsonResponse({
            'status': 'error',
            'message': 'Forbidden: Only regular users can submit issue reports.'
        }, status=403)

    try:
        data = json.loads(request.body)
        reservation_id = data.get('reservation_id')
        report_type = data.get('report_type')
        report_text = data.get('report_text')

        if not all([reservation_id, report_type, report_text]):
            return JsonResponse(
                {'status': 'error', 'message': 'Missing required fields: reservation_id, report_type, report_text.'},
                status=400)

        try:
            reservation_id = int(reservation_id)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Invalid reservation_id. Must be an integer.'},
                                status=400)

        valid_report_types = ['PAYMENT', 'TRAVEL_DELAY', 'CANCEL', 'OTHER']
        if report_type.upper() not in valid_report_types:
            return JsonResponse({'status': 'error',
                                 'message': f"Invalid report_type. Must be one of: {', '.join(valid_report_types)}."},
                                status=400)

        report_type_upper = report_type.upper()

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT reservation_id, username, reservation_status
                    FROM reservations
                    WHERE reservation_id = %s AND username = %s FOR UPDATE;
                    """,
                    [reservation_id, current_username]
                )
                reservation_info = cursor.fetchone()

                if not reservation_info:
                    return JsonResponse(
                        {'status': 'error', 'message': 'Reservation not found or does not belong to you.'}, status=404)

                res_id, res_username, res_status = reservation_info

                if res_status not in ['RESERVED', 'TEMPORARY', 'CANCELED']:
                    return JsonResponse(
                        {'status': 'error', 'message': f'Cannot report for reservation in status: {res_status}.'},
                        status=409)

                insert_query = """
                    INSERT INTO reports (username, reservation_id, report_type, report_text)
                    VALUES (%s, %s, %s, %s)
                    RETURNING report_id, report_status;
                """
                cursor.execute(insert_query, [current_username, reservation_id, report_type_upper, report_text])
                new_report_id, new_report_status = cursor.fetchone()

        return JsonResponse({
            'status': 'success',
            'message': 'Your issue report has been submitted successfully.',
            'report_details': {
                'report_id': new_report_id,
                'reservation_id': reservation_id,
                'username': current_username,
                'report_type': report_type_upper,
                'report_text': report_text,
                'report_status': new_report_status
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except IntegrityError as e:
        print(f"IntegrityError in report_ticket_issue_view: {e}")
        return JsonResponse({'status': 'error',
                             'message': 'A data integrity error occurred. This report might already exist or reservation is invalid.'},
                            status=409)
    except DatabaseError as e:
        print(f"DatabaseError in report_ticket_issue_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while submitting your report.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in report_ticket_issue_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'},
                            status=500)


@csrf_exempt
@require_http_methods(["PATCH"])
@token_required
def admin_manage_report_view(request, report_id):
    """
    Allows an admin to review and update the status and response for a user's report.
    If the report is already 'CHECKED', no updates will be performed.

    This endpoint is restricted to 'ADMIN' users only. It enables an admin to:
    - Add or update an administrative response to the report.
    - Implicitly marks the report as 'CHECKED' upon any call, if not already checked.
    - Provides a specific message if the report is already 'CHECKED', and prevents further updates.

    Path Parameter:
        report_id (int): The unique identifier for the report to be managed.

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body (JSON - optional):
    {
        "admin_response": "We have reviewed your report and will take action shortly." // Optional: Textual response from admin.
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "message": "Report updated successfully.",
        "updated_report": {
            "report_id": 123,
            "username": "reported_user",
            "reservation_id": 456,
            "report_type": "PAYMENT",
            "report_text": "Original issue text...",
            "report_status": "CHECKED",
            "admin_response": "We have reviewed your report and will take action shortly."
        }
    }
    OR (if report was already CHECKED):
    {
        "status": "info",
        "message": "Report is already checked. No further updates can be performed.",
        "current_report": { ... } // Returns current state
    }


    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON, invalid admin_response type.
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 404 Not Found: Report with the given ID does not exist.
    - 500 Internal Server Error: Database or unexpected server errors.
    """
    admin_username = request.user_payload.get('sub')
    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Admin access required.'}, status=403)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT report_id, username, reservation_id, report_type, report_text, report_status, admin_response
                    FROM reports
                    WHERE report_id = %s FOR UPDATE;
                    """,
                    [report_id]
                )
                existing_report_row = cursor.fetchone()
                if not existing_report_row:
                    return JsonResponse({'status': 'error', 'message': 'Report not found.'}, status=404)

                columns = [col[0] for col in cursor.description]
                existing_report_data = dict(zip(columns, existing_report_row))

                current_report_status = existing_report_data['report_status']
                current_admin_response = existing_report_data['admin_response']

                if current_report_status == 'CHECKED':
                    return JsonResponse({
                        'status': 'info',
                        'message': 'Report is already checked. No further updates can be performed.',
                        'current_report': existing_report_data
                    }, status=200)

                new_report_status_to_set = 'CHECKED'
                new_admin_response_to_set = current_admin_response

                requested_admin_response = data.get('admin_response')

                if requested_admin_response is not None:
                    if not isinstance(requested_admin_response, str):
                        return JsonResponse({'status': 'error', 'message': "admin_response must be a string."},
                                            status=400)
                    new_admin_response_to_set = requested_admin_response

                update_clauses = []
                params = []

                update_clauses.append("report_status = %s")
                params.append(new_report_status_to_set)

                if new_admin_response_to_set != current_admin_response:
                    update_clauses.append("admin_response = %s")
                    params.append(new_admin_response_to_set)

                if not update_clauses:
                    return JsonResponse({'status': 'error', 'message': 'Internal error: No update clauses generated.'},
                                        status=500)

                params.append(report_id)

                update_query = f"UPDATE reports SET {', '.join(update_clauses)} WHERE report_id = %s RETURNING *;"

                cursor.execute(update_query, params)
                updated_row = cursor.fetchone()

                if not updated_row:
                    raise DatabaseError("Failed to retrieve updated report data after update.")

                updated_columns = [col[0] for col in cursor.description]
                updated_report_info = dict(zip(updated_columns, updated_row))

        return JsonResponse({
            'status': 'success',
            'message': 'Report updated successfully.',
            'updated_report': updated_report_info
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)
    except DatabaseError as e:
        print(f"DatabaseError in admin_manage_report_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while updating the report.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in admin_manage_report_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'},
                            status=500)


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def admin_get_reports_view(request):
    """
    Allows an admin to retrieve a list of user reports with various filters sent in the POST body.

    This endpoint is restricted to 'ADMIN' users only. It enables an admin to filter reports by:
    - Username of the reporter
    - Ticket ID associated with the reservation
    - Report Type (e.g., PAYMENT, CANCEL)
    - Report Status (e.g., UNCHECKED, CHECKED)
    - Reservation ID

    Request Headers:
        Authorization: Bearer <JWT_access_token_of_an_admin>

    Request Body (JSON - all fields are optional):
    {
        "username": "user123",
        "ticket_id": 501,
        "report_type": "PAYMENT",
        "report_status": "UNCHECKED",
        "reservation_id": 101
    }

    Successful Response (JSON - Status Code: 200 OK):
    {
        "status": "success",
        "count": 1,
        "data": [
            {
                "report_id": 1,
                "report_username": "user123",
                "reservation_id": 101,
                "ticket_id": 501,
                "report_type": "PAYMENT",
                "report_text": "Payment failed but reservation is still temporary.",
                "report_status": "UNCHECKED",
                "admin_response": null,
                "ticket_details": {
                    "departure_start": "YYYY-MM-DDTHH:MM:SS",
                    "departure_end": "YYYY-MM-DDTHH:MM:SS",
                    "origin_city": "Tehran",
                    "destination_city": "Mashhad"
                }
            }
            // ... more reports
        ]
    }

    Error Responses (JSON):
    - 400 Bad Request: Invalid JSON or invalid filter value (e.g., non-integer ticket_id).
    - 401 Unauthorized: Token is missing or invalid.
    - 403 Forbidden: The authenticated user is not an admin.
    - 500 Internal Server Error: Database or unexpected server errors.
    """
    if request.user_payload.get('role') != 'ADMIN':
        return JsonResponse({'status': 'error', 'message': 'Forbidden: Admin access required.'}, status=403)

    try:
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in request body.'}, status=400)

        filter_username = data.get('username')
        filter_ticket_id_str = data.get('ticket_id')
        filter_report_type = data.get('report_type')
        filter_report_status = data.get('report_status')
        filter_reservation_id_str = data.get('reservation_id')

        query = """
            SELECT
                r.report_id,
                r.username AS report_username,
                r.reservation_id,
                r.report_type,
                r.report_text,
                r.report_status,
                r.admin_response,
                res.ticket_id,
                t.departure_start,
                t.departure_end,
                loc_origin.city AS origin_city,
                loc_dest.city AS destination_city
            FROM reports r
            JOIN reservations res ON r.reservation_id = res.reservation_id
            JOIN tickets t ON res.ticket_id = t.ticket_id
            JOIN locations loc_origin ON t.origin_location_id = loc_origin.location_id
            JOIN locations loc_dest ON t.destination_location_id = loc_dest.location_id
            WHERE 1=1
        """
        params = []

        if filter_username:
            query += " AND r.username ILIKE %s"
            params.append(f"%{filter_username}%")

        if filter_ticket_id_str is not None:
            try:
                filter_ticket_id = int(filter_ticket_id_str)
                query += " AND res.ticket_id = %s"
                params.append(filter_ticket_id)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid ticket_id. Must be an integer.'},
                                    status=400)

        if filter_report_type:
            valid_report_types = ['PAYMENT', 'TRAVEL_DELAY', 'CANCEL', 'OTHER']
            if filter_report_type.upper() not in valid_report_types:
                return JsonResponse({'status': 'error',
                                     'message': f"Invalid report_type. Must be one of: {', '.join(valid_report_types)}."},
                                    status=400)
            query += " AND r.report_type = %s"
            params.append(filter_report_type.upper())

        if filter_report_status:
            valid_report_statuses = ['UNCHECKED', 'CHECKED']
            if filter_report_status.upper() not in valid_report_statuses:
                return JsonResponse({'status': 'error',
                                     'message': f"Invalid report_status. Must be one of: {', '.join(valid_report_statuses)}."},
                                    status=400)
            query += " AND r.report_status = %s"
            params.append(filter_report_status.upper())

        if filter_reservation_id_str is not None:
            try:
                filter_reservation_id = int(filter_reservation_id_str)
                query += " AND r.reservation_id = %s"
                params.append(filter_reservation_id)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid reservation_id. Must be an integer.'},
                                    status=400)

        query += " ORDER BY r.report_id DESC;"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            reports_list = []
            for row in rows:
                report = dict(zip(columns, row))

                for key in ['departure_start', 'departure_end']:
                    if report.get(key) and hasattr(report[key], 'isoformat'):
                        report[key] = report[key].isoformat()

                report['ticket_details'] = {
                    'departure_start': report.pop('departure_start'),
                    'departure_end': report.pop('departure_end'),
                    'origin_city': report.pop('origin_city'),
                    'destination_city': report.pop('destination_city')
                }
                reports_list.append(report)

        return JsonResponse({
            'status': 'success',
            'count': len(reports_list),
            'data': reports_list
        }, status=200)

    except DatabaseError as e:
        print(f"DatabaseError in admin_get_reports_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'A database error occurred while fetching reports.'},
                            status=500)
    except Exception as e:
        print(f"Unexpected error in admin_get_reports_view: {e.__class__.__name__}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected server error occurred.'}, status=500)
