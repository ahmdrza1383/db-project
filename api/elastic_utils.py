import os
from elasticsearch import NotFoundError, Elasticsearch


def update_ticket_in_elastic(ticket_id: int, updates: dict):
    """
    Updates a specific ticket document in Elasticsearch.

    Args:
        ticket_id: The ID of the ticket to update.
        updates: A dictionary containing the fields to update.
                 Example: {"remaining_capacity": 19}
    """
    try:
        es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
        es_client = Elasticsearch(
            hosts=[{"host": es_host, "port": 9200, "scheme": "http"}]
        )
        if es_client.ping():
            es_client.update(index="tickets", id=ticket_id, doc=updates)
            print(f"Successfully updated ticket {ticket_id} in Elasticsearch with: {updates}")
    except NotFoundError:
        print(f"Warning: Ticket with ID {ticket_id} not found in Elasticsearch. Could not update.")
    except Exception as e:
        print(f"ERROR: Failed to update ticket {ticket_id} in Elasticsearch: {e}")
