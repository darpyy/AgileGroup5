from flask import Flask, render_template, session, redirect, request, flash, url_for
from app import app 
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

#Fixtures

@pytest.fixture
def test_client(tmp_path):
    """
    Each test gets a fresh in-memory SQLite DB and its own temp directory.
    We patch sqlite3.connect so the app never touches the real users.db.
    """
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
 
    # Create a fresh test database in tmp_path
    db_path = str(tmp_path / "users.db")
 
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                email    TEXT UNIQUE,
                password TEXT,
                username TEXT
            )
        """)
        conn.commit()
 
    original_dir = os.getcwd()
    os.chdir(tmp_path)
 
    # Redirect all sqlite3.connect("users.db") calls to our test db
    with patch("app.sqlite3.connect", return_value=sqlite3.connect(db_path)):
        with app.test_client() as client:
            yield client, db_path
 
    os.chdir(original_dir)
 
 
@pytest.fixture
def test_client_with_user(tmp_path):
    """Same as test_client but pre-populates one user for login tests."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
 
    db_path = str(tmp_path / "users.db")
    hashed = hashlib.sha256("testpassword".encode()).hexdigest()
 
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                email    TEXT UNIQUE,
                password TEXT,
                username TEXT
            )
        """)
        conn.execute(
            "INSERT INTO users (email, password, username) VALUES (?, ?, ?)",
            ("existing@example.com", hashed, "ExistingUser")
        )
        conn.commit()
 
    original_dir = os.getcwd()
    os.chdir(tmp_path)
 
    with patch("app.sqlite3.connect", return_value=sqlite3.connect(db_path)):
        with app.test_client() as client:
            yield client, db_path
 
    os.chdir(original_dir)
 


# Signup
 
class TestSignup:
    def test_new_user_redirects_to_login(self, test_client):
        client, db_path = test_client
        with patch("app.sqlite3.connect", return_value=sqlite3.connect(db_path)):
            response = client.post('/signup', data={
                'username': 'testme',
                'email': 'testme@example.com',
                'password': 'testpassword',
                'confirm_password': 'testpassword',
            })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'
 