import os
import json
from django.core.management.base import BaseCommand
from django.db import connection
from elasticsearch import Elasticsearch, helpers


class Command(BaseCommand):
    help = 'Syncs tickets data from PostgreSQL to Elasticsearch for searching'

    def handle(self, *args, **options):
        self.stdout.write("Connecting to Elasticsearch...")
        es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
        try:
            es_client = Elasticsearch(
                hosts=[{"host": es_host, "port": 9200, "scheme": "http"}]
            )
            if not es_client.ping():
                raise ConnectionError("Could not connect to Elasticsearch cluster.")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Elasticsearch connection failed: {e}"))
            return

        index_name = "tickets"
        self.stdout.write(f"Preparing index '{index_name}'...")

        if es_client.indices.exists(index=index_name):
            self.stdout.write(f"Deleting existing index '{index_name}'...")
            es_client.indices.delete(index=index_name)

        es_client.indices.create(index=index_name)
        self.stdout.write(f"Index '{index_name}' created successfully.")

        query = """
        SELECT
            t.ticket_id, t.price, t.total_capacity, t.remaining_capacity, t.ticket_status,
            t.departure_start, t.departure_end, t.is_round_trip,
            origin.city AS origin_city,
            origin.province AS origin_province,
            dest.city AS destination_city,
            dest.province AS destination_province,
            v.vehicle_type,
            f.airline_name, f.flight_class, f.number_of_stop, f.flight_code,
            f.origin_airport, f.destination_airport, f.facility AS flight_facility,
            tr.train_stars, tr.choosing_a_closed_coupe, tr.facility AS train_facility,
            b.company_name, b.bus_type, b.number_of_chairs, b.facility AS bus_facility
        FROM tickets t
        LEFT JOIN locations origin ON t.origin_location_id = origin.location_id
        LEFT JOIN locations dest ON t.destination_location_id = dest.location_id
        LEFT JOIN vehicles v ON t.vehicle_id = v.vehicle_id
        LEFT JOIN flights f ON v.vehicle_id = f.vehicle_id
        LEFT JOIN trains tr ON v.vehicle_id = tr.vehicle_id
        LEFT JOIN buses b ON v.vehicle_id = b.vehicle_id;
        """

        self.stdout.write("Fetching data from PostgreSQL...")
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            fetched_rows = cursor.fetchall()
            self.stdout.write(f"Fetched {cursor.rowcount} rows from the database.")

            actions = []
            for row in fetched_rows:
                row_dict = dict(zip(columns, row))

                source_doc = {k: v for k, v in row_dict.items() if v is not None}

                for facility_key in ['flight_facility', 'train_facility', 'bus_facility']:
                    if facility_key in source_doc and isinstance(source_doc[facility_key], str):
                        try:
                            source_doc[facility_key] = json.loads(source_doc[facility_key])
                        except json.JSONDecodeError:
                            source_doc[facility_key] = {}  # Default to empty object on error

                if "ticket_id" not in source_doc:
                    self.stderr.write(self.style.WARNING(f"Skipping a row because it has no ticket_id: {row_dict}"))
                    continue

                actions.append({
                    "_index": index_name,
                    "_id": source_doc["ticket_id"],
                    "_source": source_doc
                })

        if not actions:
            self.stdout.write("No documents to index.")
            return

        self.stdout.write(f"Attempting to index {len(actions)} documents into Elasticsearch...")
        try:
            success_count, errors = helpers.bulk(es_client, actions, raise_on_error=False)

            self.stdout.write(self.style.SUCCESS(f'Successfully indexed {success_count} documents.'))

            if errors:
                self.stderr.write(self.style.ERROR(f'Encountered {len(errors)} errors during indexing:'))
                for i, error in enumerate(errors):
                    if i >= 5:
                        self.stderr.write(self.style.ERROR("... and more errors."))
                        break
                    self.stderr.write(f" - Error: {error}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'A critical error occurred during the bulk indexing operation: {e}'))
