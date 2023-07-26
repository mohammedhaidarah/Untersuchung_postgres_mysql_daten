import mysql.connector
import time

conn = mysql.connector.connect(user='root',
                                    password='test',
                                    host='localhost',
                                    port='3306',
                                    database='test')
cur = conn.cursor()


cur.execute("START TRANSACTION;")
delete_query = "DELETE FROM books;"
cur.execute(delete_query)
    


start_time = time.time()
cur.execute("ROLLBACK;")
end_time = time.time()
rollback_time = end_time - start_time
print(f"Rollback time: {rollback_time} seconds")

cur.close()
conn.close()
