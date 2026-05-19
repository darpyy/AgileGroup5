from flask import Flask, render_template, session, redirect, request, flash, url_for, jsonify
from forms import RegistrationForm, loginForm, PostForm, ActivityForm, RequestForm
import json
import os
import sqlite3, hashlib #for talking to relational database
from sqlitedb import startServer
from datetime import datetime,timezone
import uuid
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from flask import send_from_directory

app = Flask(__name__, template_folder='views')

app.config ['SECRET_KEY'] = '8e465ada7653afdc91a1be93b5403c23'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0   # disable static-file caching during dev

ADDRESS = "http://localhost"
PORT = 5000

# hi


# for MongoDB ---
uri = "mongodb+srv://sblair2001_db_user:6BUf6rQxUNhRFqk1@cluster0.fy6qtp5.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
mdb = client.agile
posts_col = mdb.posts

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#--- 

#for Sqlite ---
startServer()

#---


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
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'favicon.ico')

@app.route('/signup', methods=['GET', 'POST']) #--------------------------------------------------------------------------------------------------------------------
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
    
                    newemail = form.email.data
                    newpassword = hashlib.sha256(form.password.data.encode()).hexdigest()
                    newusername = form.username.data
    
                    cursor.execute(
                        "INSERT INTO users (email, password, username) VALUES (?, ?, ?)",
                        (newemail, newpassword, newusername)
                    )
                    connection.commit()

                    # log the new user in
                    session['user_id'] = cursor.lastrowid
                    session['user_name'] = newusername

                    flash("Account created")
                    return redirect(url_for("tags"))
            
        except sqlite3.Error as e:
            flash("An error occured with the database")
            print(f"database error: {e}")

        except Exception as e:
            flash("an error occured")
            print(f"Error: {e}")
    print(f"Form Errors: {form.errors}")
    print(f"Form Data Received: {form.data}")
    print("signup failed")
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
                        print(f"Logged in user: {session['user_id']}")
                        session['user_city'] = dbuser[4]
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


@app.route('/logout', methods=['GET','POST'])
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/activity/<int:actid>')
def showActivity(actid):

    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
            SELECT activities.*, locations.city, tags.tagname
            FROM activities
            JOIN locations ON activities.locid = locations.locid
            JOIN tags ON activities.tagid = tags.tagid
            WHERE activities.actid = ?
        """
        activity = cursor.execute(query, (actid,)).fetchone()
        if not activity:
            return render_template('404.html'), 404

        # Fetch the created posts for the activity
        posts = list(posts_col.find({"actid": actid}).sort("created_at", -1))

        post_form = PostForm() 

    return render_template('activitiestemplate.html', activity=activity, posts=posts, post_form=post_form)

# Create Post route
@app.route('/activity/<int:actid>/post', methods=['POST'])
def create_post(actid):
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    form = PostForm()
    if form.validate_on_submit():
        new_post = {
            'actid': actid,
            'user_id': session['user_id'],
            'username': session['user_name'],
            'title': form.title.data,
            'body': form.body.data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'comments': []
        }
        try:
            posts_col.insert_one(new_post)
            flash("Post created.")
        except Exception as e:
            flash("An error occured while creating post")
            print(e)
            
    return redirect(url_for('showActivity', actid=actid))


# Edit a post
@app.route('/post/<post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    # Find post with mongoDB objectId
    post = posts_col.find_one({"_id": ObjectId(post_id)})

    # Check to see if the user editing is the creator of the post
    if not post or post['user_id'] != session['user_id']:
        flash("Cannot edit")
        return redirect(url_for('dashboard'))
    
    form = PostForm()
    if request.method == 'GET':
        form.title.data = post['title']
        form.body.data = post['body']

    if form.validate_on_submit():
        posts_col.update_one(

            {"_id": ObjectId(post_id)},
            {"$set": {
                "title": form.title.data,
                "body": form.body.data
            }}
        )
        flash("Post edited")
        return redirect(url_for('showActivity', actid=post['actid']))
    
    return render_template('edit_post.html', form=form, post=post)


# Delete Post
@app.route('/post/<post_id>/delete', methods=['POST'])
def delete_post(post_id):

    if not session.get('user_id'):
        return redirect(url_for('login'))
    

    post = posts_col.find_one({"_id": ObjectId(post_id)})

    # Check if the user is the creator of the post or the admin
    if post and (post['user_id'] == session['user_id'] or session.get('user_id') == 0):
        posts_col.delete_one({"_id": ObjectId(post_id)})
        flash("Post deleted")
        return redirect(url_for('showActivity', actid=post['actid']))
    
    flash("Unable to delete or Post was not found")
    return redirect(url_for('dashboard'))

# Add comment to a post
@app.route('/post/<post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    comment_body = request.form.get('body')

    if comment_body:
        # generate an id for each comment
        comment = {
            'comment_id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'username': session['user_name'],
            'body': comment_body,
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        # Append the comment to the comment array
        post = posts_col.find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        )

        if post:
            # if user came from the dashboard, send them back there
            if request.referrer and 'dashboard' in request.referrer:
                return redirect(url_for('dashboard'))
            return redirect(url_for('showActivity', actid=post['actid']))

        flash("Unable to comment")
        return redirect(url_for('dashboard'))

# Delete a comment
@app.route('/post/<post_id>/comment/<comment_id>/delete', methods=['POST'])
def delete_comment(post_id, comment_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    post = posts_col.find_one({"_id": ObjectId(post_id)})

    # check if the user is the one who posted the comment
    if post:
        comment = next((c for c in post.get('comments', []) if c['comment_id'] == comment_id), None)

        if comment and (comment['user_id'] == session['user_id'] or post['user_id'] == session['user_id'] or session.get('user_id') == 0):

            # remove the comment from the array based on its id
            posts_col.update_one(
                {"_id": ObjectId(post_id)},
                {"$pull": {"comments": {"comment_id": comment_id}}}
            )

        else:
            flash("Unable to delete comment")
    
        return redirect(url_for('showActivity', actid=post['actid']))
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    #check user is logged in
    if session.get('user_id') is None:
        flash("please log in to view the dashboard")
        return redirect(url_for('login'))
    
    # requested and existing activities
    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
        SELECT DISTINCT activities.actid, activities.title, activities.description, locations.city
        FROM activities
        JOIN usertags ON activities.tagid = usertags.tagid
        JOIN locations ON activities.locid = locations.locid
        WHERE usertags.userid = ?
        """

        forums = cursor.execute(query, (session.get('user_id'),)).fetchall()

    # return render_template('dashboard.html', forums=forums)

    profile_pic = None
    try:
        with sqlite3.connect("users.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT profile_pic FROM users WHERE id = ?",
                (session['user_id'],)
            )
            row = cursor.fetchone()
            if row and row[0]:
                profile_pic = row[0]
    except sqlite3.Error as e:
        print(f"DB error: {e}")
    
    # --- Feed: pull recent posts from forums the user is in ---
    user_actids = [forum['actid'] for forum in forums]
    feed_posts = []
    if user_actids:
        feed_posts = list(
            posts_col.find({"actid": {"$in": user_actids}})
                 .sort("created_at", -1)
                 .limit(20)
            )   

    # Build a lookup so we can show forum titles in the feed
    forum_titles = {forum['actid']: forum['title'] for forum in forums}
    for post in feed_posts:
        post['forum_title'] = forum_titles.get(post['actid'], 'Unknown forum')
        post['_id'] = str(post['_id'])
        # Format date nicely
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(post['created_at'])
            post['created_at'] = dt.strftime('%b %d')   # "May 14"
        except (ValueError, TypeError):
            pass

    return render_template(
    'dashboard.html',
    forums=forums,
    profile_pic=profile_pic,
    posts=feed_posts
)

@app.route('/search')
def search():
    # only logged-in users can search
    if not session.get('user_id'):
        return redirect(url_for('login'))

    # get whatever the user typed in the search bar
    query = request.args.get('q', '').strip()
    results = []

    # only search if they actually typed something
    if query:
        try:
            with sqlite3.connect("users.db") as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()

                # find users whose username CONTAINS what they typed
                # (e.g. "ale" matches "alex", "alexandra", "kale")
                cursor.execute("""
                    SELECT id, username, profile_pic
                    FROM users
                    WHERE username LIKE ? AND id != ?
                    LIMIT 50
                """, (f"%{query}%", session['user_id']))

                results = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"DB error: {e}")

    return render_template('search.html', query=query, results=results)


@app.route('/usernames')
def get_usernames():
    if not session.get('user_id'):
        return jsonify([])

    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, username, profile_pic
            FROM users
            WHERE id != ?
        """, (session['user_id'],))
        rows = cursor.fetchall()

    results = []
    for row in rows:
        pic_url = None
        if row['profile_pic']:
            pic_url = url_for('static', filename='uploads/avatars/' + row['profile_pic'])
        results.append({
            'username': row['username'],
            'profile_pic': pic_url
        })

    return jsonify(results)

@app.route('/user/<username>')
def user_profile(username):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    try:
        with sqlite3.connect("users.db") as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            # get the user's basic info + their city (if they have one)
            cursor.execute("""
                SELECT u.id, u.username, u.profile_pic, l.city
                FROM users u
                LEFT JOIN locations l ON u.locid = l.locid
                WHERE u.username = ?
            """, (username,))
            user = cursor.fetchone()

            if not user:
                flash("User not found")
                return redirect(url_for('dashboard'))

            # get the tags they picked during signup
            cursor.execute("""
                SELECT t.tagname FROM tags t
                JOIN usertags ut ON t.tagid = ut.tagid
                WHERE ut.userid = ?
            """, (user['id'],))
            tags = [row['tagname'] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        flash("Database error")
        print(f"DB error: {e}")
        return redirect(url_for('dashboard'))
    
    # --- Pull this user's posts across all forums ---
    user_posts = list(
        posts_col.find({"user_id": user['id']})
                 .sort("created_at", -1)
                 .limit(50)
    )

    # Look up forum titles for each post (post only stores actid)
    if user_posts:
        actids = list({p.get('actid') for p in user_posts if p.get('actid')})
        with sqlite3.connect("users.db") as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            placeholders = ','.join('?' * len(actids))
            cursor.execute(
                f"SELECT actid, title FROM activities WHERE actid IN ({placeholders})",
                actids
            )
            forum_titles = {row['actid']: row['title'] for row in cursor.fetchall()}

        for post in user_posts:
            post['forum_title'] = forum_titles.get(post['actid'], 'Unknown forum')
            post['_id'] = str(post['_id'])
            try:
                dt = datetime.fromisoformat(post['created_at'])
                post['created_at'] = dt.strftime('%b %d')
            except (ValueError, TypeError):
                pass

    return render_template('user_profile.html', user=user, tags=tags, posts=user_posts)

@app.route('/about')
def about(): 
    user = session.get('user')
    return render_template('about.html') 

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    #add a new request
    form = RequestForm()

    print(session.get('user_id'))
    if session.get('user_id') is None:
        return redirect(url_for('login'))

    if form.validate_on_submit():

        try:
            with sqlite3.connect("users.db") as connection:
                cursor = connection.cursor()

                newreqauth, newtitle, newdescription, newlocation = session.get('user_id'), form.reqtitle.data, form.reqdescription.data, session.get('user_city')
                cursor.execute("INSERT OR IGNORE INTO requests (reqauth, reqtitle, reqdescription, locid) VALUES (?, ?, ?, ?)", (newreqauth, newtitle, newdescription, newlocation))
                connection.commit()
                print("Request created")
                return redirect(url_for("contact"))
            
        except sqlite3.Error as e:
            flash("An error occured with the database")
            print(f"database error: {e}")

        except Exception as e:
            flash("an error occured")
            print(f"Error: {e}")
    print(f"Form Errors: {form.errors}")
    print(f"Form Data Received: {form.data}")
    print("request failed")

    return render_template('contact.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    #check user is admin
    print(session.get('user_id'))
    if not session.get('user_id') == 0:
        return redirect(url_for('login'))
    
    form = ActivityForm(request.form)

    # connect
    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
    # requested and existing activities
        requests = connection.execute('SELECT * FROM requests').fetchall()
        activities = connection.execute('SELECT * FROM activities').fetchall()
    # data for the form dropdowns
        locrow = cursor.execute('SELECT locid, city FROM locations').fetchall()
        tagrow = cursor.execute('SELECT tagid, tagname FROM tags').fetchall()
        form.location.choices = [(str(l['locid']), l['city']) for l in locrow]
        form.tag.choices = [(str(t['tagid']), t['tagname']) for t in tagrow]

    #add a new activity

    if form.validate_on_submit():
        try:
            # Check if activity exists already
            with sqlite3.connect("users.db") as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                title = form.title.data
                query = "SELECT * FROM activities WHERE title = ?"
                cursor.execute(query, (title,))

                if cursor.fetchone():
                    flash("This activity already exists")
                    print("title exist")
                    return redirect(url_for("admin"))
                
                else: # Create new user/write to database

                    #lquery = "SELECT locid FROM locations WHERE city = ?"
                    #newlocation = cursor.execute(lquery, (form.location.data)).fetchone()
                    #print(newlocation)
                    newlocation = form.location.data

                    #tquery = "SELECT tagid FROM tags WHERE tagname = ?"
                    #newtag = cursor.execute(tquery, (form.tag.data)).fetchone()
                    #print(newtag)
                    newtag = form.tag.data

                    newtitle, newdescription = form.title.data, form.description.data
                    cursor.execute("INSERT OR IGNORE INTO activities (title, description, locid, tagid) VALUES (?, ?, ?, ?)", (newtitle, newdescription, newlocation, newtag))#dumbest thing alive
                    connection.commit()
                    print("Activity created")
                    return redirect(url_for("admin"))
            
        except sqlite3.Error as e:
            flash("An error occured with the database")
            print(f"database error: {e}")

        except Exception as e:
            flash("an error occured")
            print(f"Error: {e}")
    print(f"Form Errors: {form.errors}")
    print(f"Form Data Received: {form.data}")
    print("bruhhh")
    connection.close()
    return render_template('admin.html', requests=requests, activities=activities, form =form,locations=locrow, tags=tagrow)


@app.route('/signup/tags', methods=['GET', 'POST'])
def tags():
    # must be logged in
    if not session.get('user_id'):
        flash("Please log in to continue")
        return redirect(url_for('login'))

    if request.method == 'POST':
        locid = request.form.get('city')
        selected_tags = request.form.getlist('tags')[:3]   # cap at 3

        try:
            with sqlite3.connect("users.db") as connection:
                cursor = connection.cursor()

                # save city on the user row
                cursor.execute(
                    "UPDATE users SET locid = ? WHERE id = ?",
                    (locid, session['user_id'])
                )

                # clear old tags for this user (in case they resubmit later)
                cursor.execute(
                    "DELETE FROM usertags WHERE userid = ?",
                    (session['user_id'],)
                )

                # insert each selected tag
                for tagid in selected_tags:
                    cursor.execute(
                        "INSERT INTO usertags (userid, tagid) VALUES (?, ?)",
                        (session['user_id'], tagid)
                    )

                connection.commit()
                flash("Preferences saved")
                return redirect(url_for('dashboard'))

        except sqlite3.Error as e:
            flash("A database error occurred")
            print(f"Database error: {e}")

    #get locations and tags to list on form
    with sqlite3.connect("users.db") as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        locations = cursor.execute("SELECT * FROM locations").fetchall()
        tags = cursor.execute("SELECT * FROM tags").fetchall()

    return render_template('tags.html', locations=locations, tags=tags)

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('signup.html', title='Register', form=form)    

''' json version
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
'''
# Old route
# @app.route("/posts/new", methods=['GET', 'POST'])
# def new_post():
#     # must be logged in
#     if not session.get('user_id'):
#         flash("You need to log in to create a post")
#         return redirect('/login')
    
#     form = PostForm()
#     if form.validate_on_submit():
#         posts = []

#         #removed checking, app should break earlier if connection problem

#         #removed id & id math, mongo adds _id as primary key by default

#         new = {
#             'user_id': session['user_id'],
#             'title': form.title.data,
#             'body':  form.body.data,
#             'created_at': datetime.now(timezone.utc).isoformat(), #changed because vscode got mad at me
#         }

#         try:
#             posts_col.insert_one(new)
#             flash("Post created")
#             return redirect(url_for('dashboard'))

#         except Exception as e:
#             flash("an error occurred")
#             print(e)
#             print(type(e).__name__)

#     return render_template('new_post.html', form=form)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads/avatars'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   # 2 MB cap

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if not session.get('user_id'):
        flash("Please log in")
        return redirect(url_for('login'))

    print(f"DEBUG — user_id: {session.get('user_id')}, user_name: {session.get('user_name')}")

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash("No file selected")
        return redirect(url_for('dashboard'))

    if not allowed_file(file.filename):
        flash("Only PNG, JPG, GIF, or WEBP allowed")
        return redirect(url_for('dashboard'))
    
    # Builds the user's personal folder using their usernames
    username = session.get('user_name', 'unknown')
    safe_username = secure_filename(username)
    userfolder = os.path.join(UPLOAD_FOLDER, safe_username)
    os.makedirs(userfolder, exist_ok=True)

    # Build 
    # build a unique safe filename so users can't overwrite each other
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(userfolder, safe_name)
    

    # what will get stored in the DB — folder + filename, so we can find it later
    relative_path = f"{safe_username}/{safe_name}"
    # save the filename in the database
    try:
        with sqlite3.connect("users.db") as connection:
            cursor = connection.cursor()

            # Look up the OLD picture before we replace it
            cursor.execute(
                "SELECT profile_pic FROM users WHERE id = ?",
                (session['user_id'],)
            )
            row = cursor.fetchone()
            old_pic = row[0] if row else None

            # Save the new file to disk
            file.save(save_path)

            # Update the DB to point to the new picture
            cursor.execute(
                "UPDATE users SET profile_pic = ? WHERE id = ?",
                (relative_path, session['user_id'])
            )
            connection.commit()

            # Delete the OLD file (now that the DB is updated successfully)
            if old_pic:
                old_full_path = os.path.join(UPLOAD_FOLDER, old_pic)
                if os.path.exists(old_full_path):
                    os.remove(old_full_path)

        flash("Profile picture updated")
    except sqlite3.Error as e:
        flash("Database error")
        print(f"DB error: {e}")

    return redirect(url_for('dashboard'))

# Error 404 handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    print(f"server should be running at http://localhost:{PORT}/")
    app.run(debug=True, port=PORT)