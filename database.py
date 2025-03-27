import psycopg2

conn = psycopg2.connect(
    dbname="mydatabase",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

cur.execute("SELECT * FROM authentication_methods")

rows = cur.fetchall()

for r in rows:
    print(r)