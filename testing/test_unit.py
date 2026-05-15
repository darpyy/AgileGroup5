from venv import create
from flask import Flask, render_template, session, redirect, request, flash, url_for
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime
import pytest
from app import app



@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    with app.test_client() as testing_client:
        yield testing_client

# Test to see if posts exist
# def test_posts(test_client):
#     response = test_client.get('/posts/new')

#     with open("posts.json", 'r') as f:
#         posts = json.load(f)
    
#     assert response.status_code == 302


# Test to see if post creation works
# def test_create_post(test_client):
#     response = test_client.post('/posts/new', data={'title': 'Test Post', 'content': 'This is a test post.'}, follow_redirects=True)

#     with open("posts.json", 'r') as f:
#         posts = json.load(f)

#     assert response.status_code == 200
#     print(posts[-1])
#     assert len(posts) == 2
#     assert posts[-1]['title'] == 'Test Post'
#     assert posts[-1]['content'] == 'This is a test post.'

# def test_create_post(test_client):
  
#     with test_client.session_transaction() as sess:
#         sess['user_id'] = 1  

#     response = test_client.post('/posts/new', data={
#         'title': 'Test Post', 
#         'body': 'This is a test post.'
#     }, follow_redirects=True)

#     assert response.status_code == 200
    
#     with open("posts.json", 'r') as f:
#         posts = json.load(f)
    
#     assert posts[-1]['title'] == 'Test Post'

# #test to see if post deletion works
# def test_delete_post(test_client):
#     response = test_client.delete('/posts/delete', follow_redirects=True)

#     with open('posts.json', 'r') as f:
#         posts = json.load(f)
    
#     assert response.status_code == 200
#     assert len(posts) == 0

# #post to see if post update works
# def test_update_post(test_client):
#     response = test_client.put('/posts/update', data={'title': 'Updated Post', 'content': 'This post has been updated.'}, follow_redirects=True)

#     with open('posts.json', 'r') as f:
#         posts = json.load(f)
#     assert response.status_code == 200
#     assert len(posts) == 1
#     assert posts[0]['title'] == 'Updated Post'
#     assert posts[0]['content'] == 'This post has been updated.'


#Routing tests
def test_route_posts(test_client):
    response = test_client.get('/posts')
    assert response.status_code == 404

def test_route_home(test_client):
    response = test_client.get('/')
    assert response.status_code == 200

def test_route_signup(test_client):
    response = test_client.get('/signup')
    assert response.status_code == 200

def test_route_login(test_client): 
    response = test_client.get('/login')
    assert response.status_code == 200

def test_route_logout(test_client):
    response = test_client.post('/login', data={'logout': 'true'}, follow_redirects=False)
    assert response.status_code == 302

def test_route_dashboard(test_client):
    response = test_client.get('/dashboard')
    assert response.status_code == 302


def test_request_form(test_client):

    test_client.application.config['WTF_CSRF_ENABLED'] = False

    with test_client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_city'] = 1  

    test_title = "Baking Forum"
    test_desc = "A place to discuss sourdough and pastries."

    response = test_client.post('/contact', data={
        'reqtitle': test_title,
        'reqdescription': test_desc
    }, follow_redirects=True)

    assert response.status_code == 200

    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = "SELECT * FROM requests WHERE reqtitle = ?"
        row = cursor.execute(query, (test_title,)).fetchone()

    assert row is not None, "Request was not found in the database."
    assert row['reqtitle'] == test_title
    assert row['reqdescription'] == test_desc
    assert row['reqauth'] == 1
