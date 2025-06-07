from celery import Celery
from datetime import datetime, timedelta
import psycopg2
import os
import time

app = Celery('tasks', broker='redis://redis:6379/0')

def get_db_connection(retries=5, delay=3):
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host="db",
                port=5432
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"DB connection failed: {e}, retrying {i+1}/{retries}...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after retries.")

@app.task
def expire_reservation(reservation_id):
    print("Running expire_reservation task for id:", reservation_id)
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
                SELECT date_and_time_of_reservation, reservation_status
                FROM reservations
                WHERE reservation_id = %s
                """, (reservation_id,))

    row = cur.fetchone()
    print("Fetched row:", row)

    if row and row[1] == 'TEMPORARY':
        reserve_time = row[0]
        if (datetime.utcnow() - reserve_time).total_seconds() > 590:
            cur.execute("""
                        UPDATE reservations
                        SET reservation_status           = 'NOT_RESERVED',
                            username                     = NULL,
                            date_and_time_of_reservation = NULL
                        WHERE reservation_id = %s
                        """, (reservation_id,))

            cur.execute("""
                        UPDATE tickets
                        SET remaining_capacity = remaining_capacity + 1
                        WHERE ticket_id = (SELECT ticket_id FROM reservations WHERE reservation_id = %s)
                        """, (reservation_id,))

            conn.commit()
            print(f"Reservation {reservation_id} expired and ticket updated.")
        else:
            print(f"Reservation {reservation_id} is not expired yet.")
    else:
        print(f"No reservation found or status is not TEMPORARY for id {reservation_id}.")

    cur.close()
    conn.close()
