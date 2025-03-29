import psycopg2

conn = psycopg2.connect(
    dbname="mydatabase",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
# for connect database on docker host should be db


cur = conn.cursor()

cur.execute("SELECT * FROM users")
rows = cur.fetchall()
conn.close()

for r in rows:
    print(r)