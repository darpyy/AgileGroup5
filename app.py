from flask import Flask, render_template, session, redirect, request, flash, url_for
from forms import RegistrationForm, loginForm, PostForm
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime

app = Flask(__name__, template_folder='views')

app.config ['SECRET_KEY'] = '8e465ada7653afdc91a1be93b5403c23'

ADDRESS = "http://localhost"
PORT = 5000

startServer()


''' Json version
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():
        users = []

        # Read existing users
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r") as db:
                    users = json.load(db)
            except json.JSONDecodeError:
                pass

        # Check if email exists already
        if any(user.get("email") == form.email.data for user in users):
            flash("This email already exists")
            return redirect(url_for("login"))
        
        # Create new user
        newId = max([user.get('id', 0) for user in users], default=0) + 1
        new_user = {
            "id": newId,
            "name": form.username.data,
            "email": form.email.data,
            "password": form.password.data
        }
        users.append(new_user)

        # write to database
        try:
            with open("users.json", "w") as db:
                json.dump(users, db, indent=4)
            return redirect(url_for("login"))
        
        except Exception as e:
            flash("an error occurred")
    return render_template('signup.html', title='Register', form=form)
'''

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()   

    if form.validate_on_submit():
        try:
            # Check if email exists already
            with sqlite3.connect("users.db") as connection:
                cursor = connection.cursor()
                email = form.email.data
                query = "SELECT * FROM users WHERE email = ?"
                cursor.execute(query, (email,))


                if cursor.fetchone():
                    flash("This email already exists")
                    print("email exist")
                    return redirect(url_for("login"))
                
                else: # Create new user/write to database
                    
                    newemail, newpassword, newusername = form.email.data, hashlib.sha256(form.password.data.encode()).hexdigest(), form.username.data
                    cursor.execute("INSERT OR IGNORE INTO users (email, password, username) VALUES (?, ?, ?)", (newemail, newpassword, newusername))
                    connection.commit()
                    flash("Account created")
                    return redirect(url_for("login"))
            
        except sqlite3.Error as e:
            flash("An error occured with the database")
            print(f"database error: {e}")

        except Exception as e:
            flash("an error occured")
            print(f"Error: {e}")

    return render_template('signup.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = loginForm()
    
    if 'login' in request.form:
        if form.validate_on_submit():
            try:
                with sqlite3.connect("users.db") as connection:
                    cursor = connection.cursor()
                    email = form.email.data
                    password = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()

                    query = "SELECT * FROM users WHERE email = ?"
                    cursor.execute(query, (email,))

                    dbuser = cursor.fetchone()

                    if dbuser and dbuser[2] == password: #if a user with that email exists:
                        flash("login successful")
                        session['user_id'] = dbuser[0]
                        session['user_name'] = dbuser[3]
                        return redirect(url_for("dashboard"))
                            
                    else:
                        flash("Invalid email/password")

            except sqlite3.Error as e:
                flash("A database error occurred")
                print(f"Database error: {e}")

    elif 'logout' in request.form:
        session.clear()
        flash("You have been logged out")
        return redirect(url_for("index"))

    return render_template('login.html', title='Login', form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session.get("user_id"):
        flash("please log in to view the dashboard")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html') 

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin')
def admin():
    with sqlite3.connect("users.db") as connection:
        cursor = connection.cursor()
    requests = connection.execute('SELECT * FROM requests').fetchall()
    connection.close()
    return render_template('admin.html', requests=requests)

@app.route('/signup/tags')
def tags():
    return render_template('tags.html')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('signup.html', title='Register', form=form)    

@app.route("/posts/new", methods=['GET', 'POST'])
def new_post():
    # must be logged in
    if not session.get('user_id'):
        flash("You need to log in to create a post")
        return redirect('/login')
    
    form = PostForm()
    if form.validate_on_submit():
        posts = []
        if os.path.exists('posts.json'):
            try:
                with open('posts.json', 'r') as db:
                    posts = json.load(db)

            except Exception as e:
                flash("Could not read the post database")
                print(e)

        if posts:
            # collect all the ids into a list
            ids = []
            for p in posts:
                ids.append(p['id'])

            # find the biggest one
            biggest = max(ids)

            # the new id is one more than that
            new_id = biggest + 1
        else:
            # no posts yet, so this is the first one
            new_id = 1
        
        new = {
            'id': new_id,
            'user_id': session['user_id'],          # <-- the link
            'title': form.title.data,
            'body':  form.body.data,
            'created_at': datetime.utcnow().isoformat(),
        }
        posts.append(new)
        try:
            with open('posts.json', 'w') as db:
                json.dump(posts, db, indent=2)
            flash("Post created")
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash("an error occurred")
            print(e)

    return render_template('new_post.html', form=form)

# Error 404 handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    print(f"server should be running at http://localhost:{PORT}/")
    app.run(debug=True, port=PORT)
