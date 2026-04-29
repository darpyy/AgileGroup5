from flask import Flask, render_template


app = Flask(__name__, template_folder='views')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/signup/tags')
def tags():
    return render_template('tags.html')

if __name__ == '__main__':
    app.run(debug=True)
