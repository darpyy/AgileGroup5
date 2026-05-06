import sqlite3, hashlib

def startServer():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email VARCHAR (255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        username VARCHAR (255) UNIQUE NOT NULL
    )
    """)

    id1, email1, password1, username1 = 0, "admin@me.ca", hashlib.sha256("123".encode()).hexdigest(), "admin"
    cursor.execute("INSERT OR IGNORE INTO users (id, email, password, username) VALUES (?, ?, ?, ?)", (id1, email1, password1, username1))

    connection.commit()
    connection.close()

