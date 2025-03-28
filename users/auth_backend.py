import psycopg2
from django.contrib.auth.backends import BaseBackend
import hashlib

class CustomUser:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
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



class CustomPostgresBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with psycopg2.connect(
                dbname="mydatabase",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, username FROM users WHERE username = %s AND password = %s", (username, hashed_password))
                    user_data = cur.fetchone()

            if user_data:
                return CustomUser(user_data[0], user_data[1]).change_authentication_status(True)

        except Exception as e:
            print("Database Error:", e)

        return None

    def get_user(self, user_id):
        try:
            with psycopg2.connect(
                dbname="mydatabase",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
                    user_data = cur.fetchone()

            if user_data:
                return CustomUser(user_data[0], user_data[1])

        except Exception as e:
            print("Database Error:", e)

        return None