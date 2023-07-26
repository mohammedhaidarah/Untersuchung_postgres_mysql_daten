import psycopg2
import time


conn = psycopg2.connect(
    dbname="test",
    user="test",
    password="test",
    host="localhost",
    port="5433"
)


cur = conn.cursor()

cur.execute("BEGIN TRANSACTION;")
delete_query = "DELETE FROM books;"
cur.execute(delete_query)


start_time = time.time()
cur.execute("ROLLBACK;")
end_time = time.time()
rollback_time = end_time - start_time
print(f"Rollback time: {rollback_time} seconds")

cur.close()
conn.close()

