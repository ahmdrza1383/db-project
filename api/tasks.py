from celery import Celery
from datetime import datetime, timedelta
import psycopg2
import os
import time
import json
import redis
from django.conf import settings

redis_client = None
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    print("Successfully connected to Redis in tasks!")
except redis.exceptions.ConnectionError as e:
    print(f"Could not connect to Redis in tasks: {e}. Cache operations will be impaired.")
except AttributeError:
    print("Redis settings (REDIS_HOST, REDIS_PORT) not found in environment for tasks.")

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
            print(f"DB connection failed: {e}, retrying {i + 1}/{retries}...")
            time.sleep(delay)
    raise Exception("Could not connect to the database after retries.")


@app.task
def expire_reservation(reservation_id):
    print("Running expire_reservation task for id:", reservation_id)
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
                    SELECT date_and_time_of_reservation, reservation_status, t.ticket_id, t.remaining_capacity
                    FROM reservations r
                             INNER JOIN tickets t ON r.ticket_id = t.ticket_id
                    WHERE r.reservation_id = %s FOR UPDATE OF r, t;
                    """, (reservation_id,))

        row = cur.fetchone()
        print("Fetched row:", row)

        if row and row[1] == 'TEMPORARY':
            reserve_time = row[0]
            ticket_id_for_revert = row[2]
            current_ticket_capacity = row[3]

            if (datetime.utcnow() - reserve_time).total_seconds() > 590:
                cur.execute("""
                            UPDATE reservations
                            SET reservation_status           = 'NOT_RESERVED',
                                username                     = NULL,
                                date_and_time_of_reservation = NULL
                            WHERE reservation_id = %s
                            """, (reservation_id,))

                new_remaining_capacity = current_ticket_capacity + 1
                cur.execute("""
                            UPDATE tickets
                            SET remaining_capacity = %s
                            WHERE ticket_id = %s
                            """, (new_remaining_capacity, ticket_id_for_revert))

                conn.commit()
                print(
                    f"Reservation {reservation_id} expired and ticket {ticket_id_for_revert} updated to new capacity {new_remaining_capacity}. Transaction committed.")

                if redis_client:
                    ticket_details_cache_key = f"ticket_details:{ticket_id_for_revert}"
                    try:
                        cached_ticket_details_json = redis_client.get(ticket_details_cache_key)
                        if cached_ticket_details_json:
                            cached_ticket_data = json.loads(cached_ticket_details_json)

                            cached_ticket_data['remaining_capacity'] = new_remaining_capacity

                            current_ttl = redis_client.ttl(ticket_details_cache_key)
                            if current_ttl > 0:
                                redis_client.setex(
                                    ticket_details_cache_key,
                                    current_ttl,
                                    json.dumps(cached_ticket_data)
                                )
                                print(
                                    f"Updated ticket details cache for {ticket_details_cache_key} (remaining_capacity: {new_remaining_capacity}), preserving original TTL.")
                            else:
                                redis_client.set(ticket_details_cache_key, json.dumps(cached_ticket_data))
                                print(
                                    f"Updated ticket details cache for {ticket_details_cache_key} (remaining_capacity: {new_remaining_capacity}), no TTL changed.")

                        else:
                            print(
                                f"Ticket details for {ticket_id_for_revert} not found in cache during expiry. Not updating cache.")

                    except redis.exceptions.RedisError as re_cache_err:
                        print(f"Redis error during updating ticket details cache in expire_reservation: {re_cache_err}")
                    except Exception as e:
                        print(f"Error processing ticket details cache in expire_reservation: {e}")

            else:
                print(f"Reservation {reservation_id} is not expired yet (time difference is less than 10 minutes).")
        else:
            print(f"No reservation found or status is not TEMPORARY for id {reservation_id}.")

    except Exception as e:
        print(f"An error occurred in expire_reservation for {reservation_id}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()