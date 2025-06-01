import psycopg2
from django.contrib.auth.backends import BaseBackend
import hashlib


class CustomUser:
    def __init__(self, username, password, name, email, phone_number, city, date_of_sign_in=None, profile_picture=None,
                 user_role='USER', authentication_method='EMAIL'):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.city = city
        self.date_of_sign_in = date_of_sign_in
        self.profile_picture = profile_picture
        self.user_role = user_role
        self.authentication_method = authentication_method
        self.is_authenticated = False
        self.is_active = True
        self.is_staff = False
        self.is_superuser = False

    def change_authentication_status(self, status):
        self.is_authenticated = status

    def change_staff_status(self, status):
        self.is_staff = status

    def change_superuser_status(self, status):
        self.is_superuser = status

    def change_active_status(self, status):
        self.is_active = status

    @classmethod
    def create(cls, validated_data):
        try:
            with psycopg2.connect(
                    dbname="mydatabase",
                    user="postgres",
                    password="postgres",
                    host="db",
                    port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (username, password, name, email, phone_number, city, user_role, authentication_method)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING  username
                    """, (
                        validated_data['username'],
                        validated_data['password'],
                        validated_data['name'],
                        validated_data['email'],
                        validated_data['phone_number'],
                        validated_data['city'],
                        validated_data['user_role'],
                        validated_data['authentication_method']
                    ))

                    user_id = cur.fetchone()[0]
                    return cls(**validated_data)
        except Exception as e:
            print("Database Error:", e)
            return None

    @classmethod
    def get_user(self, username):
        try:
            with psycopg2.connect(
                    dbname="mydatabase",
                    user="postgres",
                    password="postgres",
                    host="db",
                    port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                    user_data = cur.fetchone()

            if user_data:
                return create_user(user_data)

        except Exception as e:
            print("Database Error:", e)


def create_user(user_data):
    username = user_data[0]
    password = user_data[1]
    user_role = user_data[2]
    name = user_data[3]
    email = user_data[4]
    phone_number = user_data[5]
    city = user_data[6]
    date_of_sign_in = user_data[7]
    profile_picture = user_data[8]
    authentication_method = user_data[9]
    return CustomUser(
        username, password, name, email, phone_number, city, date_of_sign_in, profile_picture, user_role,
        authentication_method
    )


class CustomPostgresBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with psycopg2.connect(
                    dbname="mydatabase",
                    user="postgres",
                    password="postgres",
                    host="db",
                    port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                                (username, hashed_password))
                    user_data = cur.fetchone()

            if user_data:
                return create_user(user_data).change_authentication_status(True)

        except Exception as e:
            print("Database Error:", e)

        return None

    def get_user(self, username):
        try:
            with psycopg2.connect(
                    dbname="mydatabase",
                    user="postgres",
                    password="postgres",
                    host="db",
                    port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                    user_data = cur.fetchone()

            if user_data:
                return create_user(user_data)

        except Exception as e:
            print("Database Error:", e)

        return None
