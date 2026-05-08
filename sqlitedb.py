import sqlite3, hashlib

def startServer():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.executescript(""" 
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email VARCHAR (255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR (255) UNIQUE NOT NULL,
    city VARCHAR(255)
);
CREATE TABLE IF NOT EXISTS activities (
    actid INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS members (
    actid INTEGER NOT NULL,
    id INTEGER NOT NULL,
    PRIMARY KEY (actid, id),
    FOREIGN KEY (id) REFERENCES users(id),
    FOREIGN KEY (actid) REFERENCES activities(actid)
);
CREATE TABLE IF NOT EXISTS requests (
    reqid INTEGER PRIMARY KEY,
    id INTEGER NOT NULL,
    reqtitle VARCHAR(255) NOT NULL,
    reqdescription VARCHAR(255) NOT NULL,
    FOREIGN KEY (id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS user_tags (
    id INTEGER NOT NULL,
    tag VARCHAR(50) NOT NULL,
    PRIMARY KEY (id, tag),
    FOREIGN KEY (id) REFERENCES users(id)
);
""")

    #not for testing, do not remove
    id1, email1, password1, username1 = 0, "admin@me.ca", hashlib.sha256("123".encode()).hexdigest(), "admin"
    cursor.execute("INSERT OR IGNORE INTO users (id, email, password, username) VALUES (?, ?, ?, ?)", (id1, email1, password1, username1))

    #for testing, remove later
    reqid, id, reqtitle, reqdescription = 0, 0, "my 1st request", "hi"
    cursor.execute("INSERT OR IGNORE INTO requests (reqid, id, reqtitle, reqdescription) VALUES (?, ?, ?, ?)", (reqid, id, reqtitle, reqdescription))

    actid, title, description = 0, "my 1st activity", "hi"
    cursor.execute("INSERT OR IGNORE INTO activities (actid, title, description) VALUES (?, ?, ?)", (actid, title, description))


    connection.commit()
    connection.close()