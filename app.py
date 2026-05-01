from flask import Flask, render_template,session,redirect
from forms import RegistrationForm, loginForm
import json
app = Flask(__name__, template_folder='views')

app.config ['SECRET_KEY'] = '8e465ada7653afdc91a1be93b5403c23'

PORT = 5000

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

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
    #if conditions for the form are met
    if form.validate_on_submit():
        with open('users.json', 'r') as db:
            users = json.load(db)

        for user in users:
            if user['email'] == form.email.data and user['password'] == form.password.data:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                print("success!")
                return redirect('../dashboard')
        
        print("failure")

    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    print(f"server should be running at http://localhost:{PORT}/")
    app.run(debug=True, port=PORT)
