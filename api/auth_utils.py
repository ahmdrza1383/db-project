import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.http import JsonResponse
from functools import wraps

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
