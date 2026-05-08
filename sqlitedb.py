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
    locid INTEGER, 
    FOREIGN KEY (locid) REFERENCES locations(locid)
);
CREATE TABLE IF NOT EXISTS requests (
    reqid INTEGER PRIMARY KEY,
    reqauth INTEGER NOT NULL,
    reqtitle VARCHAR(255) NOT NULL,
    reqdescription VARCHAR(255) NOT NULL,
    locid INTEGER NOT NULL,
    FOREIGN KEY (locid) REFERENCES locations(locid),
    FOREIGN KEY (reqauth) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS activities (
    actid INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    locid INTEGER NOT NULL,
    tagid INTEGER NOT NULL,
    FOREIGN KEY (locid) REFERENCES locations(locid),
    FOREIGN KEY (tagid) REFERENCES tags(tagid)
);
CREATE TABLE IF NOT EXISTS locations (
    locid INTEGER PRIMARY KEY,
    city VARCHAR(255) UNIQUE NOT NULL
);
CREATE TABLE IF NOT EXISTS tags (
    tagid INTEGER PRIMARY KEY,
    tagname VARCHAR(50) UNIQUE NOT NULL
);       
CREATE TABLE IF NOT EXISTS usertags (
    tagid INTEGER NOT NULL,
    userid INTEGER NOT NULL,
    PRIMARY KEY (tagid, userid) 
    FOREIGN KEY (tagid) REFERENCES tags(tagid) ON DELETE CASCADE,
    FOREIGN KEY (userid) REFERENCES users(id) ON DELETE CASCADE
);
""")

    #not for testing, do not remove
    id1, email1, password1, username1 = 0, "admin@me.ca", hashlib.sha256("123".encode()).hexdigest(), "admin"
    cursor.execute("INSERT OR IGNORE INTO users (id, email, password, username) VALUES (?, ?, ?, ?)", (id1, email1, password1, username1))

    #for testing, remove later
    reqid, reqauth, reqtitle, reqdescription, locid = 0, 0, "my 1st request", "hi", 2
    cursor.execute("INSERT OR IGNORE INTO requests (reqid, reqauth, reqtitle, reqdescription, locid) VALUES (?, ?, ?, ?, ?)", (reqid, reqauth, reqtitle, reqdescription, locid))

    actid, title, description, locid, tagid = 0, "my 1st activity", "hi", 1, 1
    cursor.execute("INSERT OR IGNORE INTO activities (actid, title, description, locid, tagid) VALUES (?, ?, ?, ?, ?)", (actid, title, description, locid, tagid))

    newtags = [('music',), ('art',), ('sports',), ('gaming',), ('food',), ('travel',)]
    cursor.executemany("INSERT OR IGNORE INTO tags (tagname) VALUES (?)", newtags)
    
    newcities = [('Vancouver',), ('Surrey',), ('Burnaby',)]
    cursor.executemany("INSERT OR IGNORE INTO locations (city) VALUES (?)", newcities)

    connection.commit()
    connection.close()