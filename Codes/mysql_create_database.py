import mysql.connector
from faker import Faker
import datetime

num_entries = 1_000_00

fake = Faker()

try:
    conn = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='test',
        database='test'
    )
    print("Success: Connected to MySQL server!")
    
    cursor = conn.cursor()
    # Erstellt eine Tabelle, wenn nicht existiert
    cursor.execute('''CREATE TABLE IF NOT EXISTS books
                    (id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255),
                    author VARCHAR(255),
                    year INT,
                    publisher VARCHAR(255),
                    timestamp DATETIME)''')

    # fügt die Daten der Tabelle hinzu, anhand der anzahl der angegebenen Einträgen in new_entries
    for i in range(num_entries):
        # generiert die Daten mit Faker
        title =  fake.sentence()
        author = fake.name()
        year = fake.random_int(min=1900, max=2023)
        publisher = fake.company()
       
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

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

except mysql.connector.Error as error:
    print("Error connecting to MySQL:", error)

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
