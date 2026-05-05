from flask import Flask, render_template, session, redirect, request, flash, url_for
from forms import RegistrationForm, loginForm
import json
import os
app = Flask(__name__, template_folder='views')

app.config ['SECRET_KEY'] = '8e465ada7653afdc91a1be93b5403c23'

PORT = 5000

@app.route('/')
def index():
    return render_template('index.html')

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
            return redirect(url_for("signup"))
        
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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html') 

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup/tags')
def tags():
    return render_template('tags.html')

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('signup.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():    
    form = loginForm()
    if form.validate_on_submit():
        users = []
        try:
        # try to open and read the json file
            with open('users.json', 'r') as db:
                users = json.load(db)

        except FileNotFoundError:
            flash("Error: Database not found")
            return render_template("login.html", title="Login", form=form)
        
        # Checking a users credentials
        for user in users:
            if user['email'] == form.email.data and user['password'] == form.password.data:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                print("success!")
                return redirect(url_for("dashboard"))
            
        flash("Invalid email/password")

    elif 'logout' in request.form:
        session['user_id'] = ""
        session['user_name'] = ""
        return redirect(url_for("index"))
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    print(f"server should be running at http://localhost:{PORT}/")
    app.run(debug=True, port=PORT)
