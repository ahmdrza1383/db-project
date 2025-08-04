import base64
import json
import redis
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone, date
from django.conf import settings
from django.http import JsonResponse
from django.db import connection
from functools import wraps

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

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 60)  # 30 دقیقه
JWT_REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, 'JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7)  # 7 روز


def generate_password_hash(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password_hash(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return "expired"
    except jwt.InvalidTokenError:
        return "invalid"


def token_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return JsonResponse({'status': 'error', 'message': 'Authorization token is missing.'}, status=401)

        payload = decode_token(token)

        if payload == "expired":
            return JsonResponse({'status': 'error', 'message': 'Token has expired.'}, status=401)
        if payload == "invalid" or payload.get("type") != "access":  # چک کردن نوع توکن
            return JsonResponse({'status': 'error', 'message': 'Invalid access token.'}, status=401)

        request.user_payload = payload

        return f(request, *args, **kwargs)

    return decorated_function


def get_user_profile(username):
    """
    Retrieves a user's profile, using a cache-aside strategy.
    First, it checks Redis cache. If not found, it queries the database
    and then caches the result in Redis for future requests.
    """
    if not redis_client:
        print("[CACHE WARNING] Redis client not available. Fetching from DB directly.")
        return _get_user_from_db(username)

    profile_cache_key = f"user_profile:{username}"
    try:
        cached_profile_str = redis_client.get(profile_cache_key)
        if cached_profile_str:
            print(f"Cache HIT for user: {username}")
            return json.loads(cached_profile_str)
        else:
            print(f"Cache MISS for user: {username}")
            user_profile = _get_user_from_db(username)
            if user_profile:
                profile_cache_ttl_seconds = getattr(settings, 'USER_PROFILE_CACHE_TTL_SECONDS', 3600)
                redis_client.setex(
                    profile_cache_key,
                    profile_cache_ttl_seconds,
                    json.dumps(user_profile)
                )
            return user_profile

    except redis.exceptions.RedisError as e:
        print(f"[CACHE WARNING] Redis error, fetching from DB directly: {e}")
        return _get_user_from_db(username)


def _get_user_from_db(username):
    """
    A private helper to fetch a complete user profile directly from PostgreSQL.
    Fetches all relevant fields except the password.
    """
    with connection.cursor() as cursor:
        query = """
            SELECT 
                username, user_role, name, email, phone_number, city, 
                date_of_sign_in, profile_picture, authentication_method, 
                profile_status, date_of_birth, wallet_balance 
            FROM users 
            WHERE username = %s
        """
        cursor.execute(query, [username])
        row = cursor.fetchone()
        if not row:
            return None

        columns = [col[0] for col in cursor.description]
        user_profile = dict(zip(columns, row))

        if user_profile.get('date_of_birth') and isinstance(user_profile['date_of_birth'], date):
            user_profile['date_of_birth'] = user_profile['date_of_birth'].isoformat()
        if user_profile.get('date_of_sign_in') and hasattr(user_profile['date_of_sign_in'], 'isoformat'):
            user_profile['date_of_sign_in'] = user_profile['date_of_sign_in'].isoformat()

        if user_profile.get('profile_picture') and isinstance(user_profile['profile_picture'], memoryview):
            user_profile['profile_picture'] = base64.b64encode(user_profile['profile_picture'].tobytes()).decode(
                'utf-8')

        if 'city' in user_profile:
            user_profile['city_id'] = user_profile.pop('city')

        return user_profile


def invalidate_user_profile_cache(username):
    """
    Deletes (invalidates) a user's profile from the Redis cache.
    This should be called after any update to the user's data in the database.
    """
    if not redis_client:
        return

    profile_cache_key = f"user_profile:{username}"
    try:
        redis_client.delete(profile_cache_key)
        print(f"Cache INVALIDATED for user: {username}")
    except redis.exceptions.RedisError as e:
        print(f"[CACHE WARNING] Failed to invalidate cache for user {username}: {e}")
