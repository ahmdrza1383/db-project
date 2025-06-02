from celery import shared_task
from django.db import connection, transaction
from datetime import datetime, timezone


@shared_task(bind=True, max_retries=3)
def check_and_revert_reservation_task(self, reservation_id):
    """
    Celery task to check a specific temporary reservation after its TTL
    and revert it if it hasn't been confirmed (paid).
    """
    self.stdout.write(f"[{datetime.now(timezone.utc).isoformat()}] Task started for reservation_id: {reservation_id}")
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.ticket_id, r.reservation_seat, t.remaining_capacity
                    FROM reservations r
                    INNER JOIN tickets t ON r.ticket_id = t.ticket_id
                    WHERE r.reservation_id = %s AND r.reservation_status = 'TEMPORARY'
                    FOR UPDATE OF r, t; 
                    """,
                    [reservation_id]
                )
                reservation_info = cursor.fetchone()

                if not reservation_info:
                    self.stdout.write(
                        f"Reservation ID {reservation_id} not found or no longer temporary. No action needed.")
                    return f"Reservation {reservation_id} not found or status changed."

                ticket_id_for_revert, seats_in_this_reservation, current_ticket_capacity = reservation_info

                cursor.execute(
                    """
                    UPDATE reservations 
                    SET reservation_status = 'NOT_RESERVED', username = NULL, date_and_time_of_reservation = NULL
                    WHERE reservation_id = %s;
                    """,
                    [reservation_id]
                )

                new_capacity = current_ticket_capacity + seats_in_this_reservation
                cursor.execute(
                    "UPDATE tickets SET remaining_capacity = %s WHERE ticket_id = %s;",
                    [new_capacity, ticket_id_for_revert]
                )

                self.stdout.write(self.style.SUCCESS(
                    f"Reverted temporary reservation ID {reservation_id} for ticket {ticket_id_for_revert}. Capacity adjusted."))
                return f"Reservation {reservation_id} reverted successfully."

    except Exception as e:
        self.stderr.write(self.style.ERROR(f"Error processing reservation_id {reservation_id}: {e}"))
        try:
            raise self.retry(exc=e, countdown=60)
        except self.MaxRetriesExceededError:
            self.stderr.write(
                self.style.ERROR(f"Max retries exceeded for reservation_id {reservation_id} with error: {e}"))
            return f"Failed to revert reservation {reservation_id} after multiple retries: {e}"
        except Exception as retry_exc:
            self.stderr.write(self.style.ERROR(
                f"Could not retry task for reservation_id {reservation_id}. Original error: {e}. Retry_exc: {retry_exc}"))
            return f"Failed to revert reservation {reservation_id}, retry mechanism failed: {e}"