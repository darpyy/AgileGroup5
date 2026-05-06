from flask import Flask, render_template, session, redirect, request, flash, url_for, app
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_new_posts(client):
    response = client.get('/posts/new')
    with open("posts.json", 'r') as f:
        posts = json.load(f)
    assert response.status_code == 200
    assert len(posts) == 1;

