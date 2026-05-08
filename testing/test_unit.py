from venv import create
from flask import Flask, render_template, session, redirect, request, flash, url_for
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime
import pytest
from app import app

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    
    with app.test_client() as testing_client:
        yield testing_client

# Test to see if posts exist
def test_posts(test_client):
    response = test_client.get('/posts/new')

    with open("posts.json", 'r') as f:
        posts = json.load(f)
    
    assert response.status_code == 302
    assert len(posts) == 1


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

def test_create_post(test_client):
    # 1. Fake the login session
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1  # Set this to any valid ID

    # 2. Match your form data to your route
    # Note: Your route uses 'form.body.data', but your test was sending 'content'
    response = test_client.post('/posts/new', data={
        'title': 'Test Post', 
        'body': 'This is a test post.'  # Changed 'content' to 'body'
    }, follow_redirects=True)

    # 3. Check the results
    assert response.status_code == 200
    
    with open("posts.json", 'r') as f:
        posts = json.load(f)
    
    assert posts[-1]['title'] == 'Test Post'

#test to see if post deletion works
def test_delete_post(test_client):
    response = test_client.delete('/posts/delete', follow_redirects=True)

    with open('posts.json', 'r') as f:
        posts = json.load(f)
    
    assert response.status_code == 200
    assert len(posts) == 0

#post to see if post update works
def test_update_post(test_client):
    response = test_client.put('/posts/update', data={'title': 'Updated Post', 'content': 'This post has been updated.'}, follow_redirects=True)

    with open('posts.json', 'r') as f:
        posts = json.load(f)
    assert response.status_code == 200
    assert len(posts) == 1
    assert posts[0]['title'] == 'Updated Post'
    assert posts[0]['content'] == 'This post has been updated.'


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
    response = test_client.get('/logout')
    assert response.status_code == 302

def test_route_dashboard(test_client):
    response = test_client.get('/dashboard')
    assert response.status_code == 302