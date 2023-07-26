import psycopg2
from faker import Faker
import datetime

num_entries = 1_000_00

fake = Faker()

try:
    conn = psycopg2.connect(user='test',
                            password='test',
                            host='localhost',
                            port='5433',
                            database='test')
    print("Success: Connected to PostgreSQL server!")
    
    cursor = conn.cursor()
    # Erstellt eine Tabelle, wenn nicht existiert
    cursor.execute('''CREATE TABLE IF NOT EXISTS books
                    (id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    author VARCHAR(255),
                    year INT,
                    publisher VARCHAR(255),
                    timestamp TIMESTAMP)''')
    # fügt die Daten der Tabelle hinzu, anhand der anzahl der angegebenen Einträgen in new_entries    
    for i in range(num_entries):
        # generiert die Daten mit Faker
        title = fake.sentence()
        author = fake.name()
        year = fake.random_int(min=1900, max=2023)
        publisher = fake.company()
        timestamp = datetime.datetime.now()

        insert_query = '''INSERT INTO books (title, author, year, publisher, timestamp)
                        VALUES (%s, %s, %s, %s, %s)'''
        insert_values = (title, author, year, publisher, timestamp)
        cursor.execute(insert_query, insert_values)
        conn.commit()

        print(f"Entry {i+1}:")
        print("Title:", title)
        print("Author:", author)
        print("Year of Publication:", year)
        print("Publisher:", publisher)
        print("Timestamp:", timestamp)
        print()

except psycopg2.Error as error:
    print("Error connecting to PostgreSQL:", error)

finally:
    if 'conn' in locals() and conn.closed == 0:
        cursor.close()
        conn.close()
