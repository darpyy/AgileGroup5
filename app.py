from flask import Flask, render_template,session,redirect, request
from forms import RegistrationForm, loginForm, PostForm
import json
from datetime import datetime

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
    if 'login' in request.form:
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

    elif 'logout' in request.form:
        session['user_id'] = ""
        session['user_name'] = ""
        return redirect("/")
    return render_template('login.html', title='Login', form=form)


@app.route("/posts/new", methods=['GET', 'POST'])
def new_post():
    # must be logged in
    if not session.get('user_id'):
        return redirect('/login')
    
    form = PostForm()
    if form.validate_on_submit():
        with open('posts.json', 'r') as db:
            posts = json.load(db)

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

        with open('posts.json', 'w') as db:
            json.dump(posts, db, indent=2)

        return redirect('/dashboard')

    return render_template('new_post.html', form=form)


if __name__ == '__main__':
    print(f"server should be running at http://localhost:{PORT}/")
    app.run(debug=True, port=PORT)
