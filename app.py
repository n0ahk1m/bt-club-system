from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from authlib.integrations.flask_client import OAuth
import json
import sqlite3
from werkzeug.utils import secure_filename
import csv
from datetime import datetime
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required
import random
import base64
from cryptography.fernet import Fernet
#external py modules
from init.db_init import create_tables
from user import *
from user import User
from clubs import *
from messages import *
from admin import *
import os

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY"  # Change this to a secure ENCRYPTED key

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='954980088912-ukn276fifnqm5g5fncnptb9pnl3esmhs.apps.googleusercontent.com',
    client_secret='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',
    authorize_params=None,
    access_token_params=None,
    access_token_params_callback=None,
    access_token_method='POST',
    redirect_uri='http://localhost:5000/login/callback',  # Local URI for callback
    client_kwargs={'scope': 'openid email profile',
                   'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs'
                   },
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is Google's OpenID Connect user info endpoint
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)

@app.route('/')
def home():
    return render_template("home.html")

### LOGIN FUNCTIONALITIES
@app.route('/login')
def login():
    return google.authorize_redirect(redirect_uri=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('id')
    session.pop('email')
    session.pop('google_data')
    logout_user()
    flash("Successfully logged out.", "success")
    return redirect(url_for('home'))


@app.route('/login/callback')
def authorized():
    nonce = session.get('nonce')
    # try:
    if nonce is None:
        token = google.authorize_access_token()
        message = ""
        #get the user data from google
        user = google.parse_id_token(token, nonce=None)
        session['token'] = token

        #check if the user exists
        google_user_data = search_user(user.email)

    #register new user
    if google_user_data==[]:
        new_user = User(None, user.given_name, user.family_name, user.email, None, None, None, None, user['picture'])
        register_user(new_user)
        message =  "Registered successfully!"
        google_user_data = search_user(user.email)
    else: 
        change_pfp(google_user_data[0][0],user['picture'])
        message =  "Logged in successfully!"
    #add user to user object (id!) with session id token
    google_user_object = load_user(google_user_data[0][0])

    #save the id of the user in a session variable
    session['id'] = google_user_data[0][0]
    session['email'] = google_user_data[0][3]
    session['google_data'] = user

    login_user(google_user_object)
    flash(message, "success")
    
    return redirect(url_for('home'))
    # except Exception as e:
    #     flash('An error occurred: ' + str(e))
    #     return redirect(url_for('home'))

#set mail 
mail = Mail(app)
#main page

#login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login' #specify the login route
login_manager.login_message = "Unauthorized access please log in!"
login_manager.login_message_category = 'danger'

@login_manager.user_loader
def load_user(user_id):
    #just run the load user connection here
    conn = sqlite3.connect('db/database.db')
    curs = conn.cursor()
    curs.execute("SELECT * from users where id = (?)",[user_id])
    lu = curs.fetchone()
    if lu is None:
        return None
    else:
        return User(int(lu[0]), lu[1], lu[2], lu[3], None, None, None, None, None)


@app.route('/profile', methods=['GET','POST'])
@login_required  
def profile():
    if request.method == 'GET':
        user_id = session.get('id')
        user_email = session.get('email')
        user = search_user(user_email)
    elif request.method == 'POST':
        grad_year = request.form.get('grad_year').strip()
        major = request.form['major']
        user_id = session.get('id')
        add_to_user(user_id,major,grad_year)
        user_email = session.get('email')
        user = search_user(user_email)

    google_data = session.get('google_data')
    user_picture = google_data['picture']
    flash("Updated Profile!", "success")
    return render_template('profile.html', user=user, picture=user_picture, name=google_data['name'])

### CLUB FUNCTIONALITIES
@app.route('/clubs', methods=['GET', 'POST'])
def clubs():
    if request.method=='GET':
        all_clubs = get_all_clubs()
        return render_template("clubs.html", clubs=all_clubs)
    elif request.method=='POST':
        club_name = request.form.get('search').strip()
        club = search_clubs(club_name)
        return render_template("clubs.html", clubs=club)

@app.route('/join_club/<club_name>', methods=['GET', 'POST'])
@login_required  
def join_club(club_name):
    #search for the club by club name
    club = search_clubs(club_name)
    #get the club id by the club
    club_id = club[0][0]
    #get the user id in the form of a session variable
    user_id = session.get('id')
    #need to add this
    if user_club_exists(user_id, club_id):
        flash("Already added this club!", "warning")
        return redirect(url_for('clubs'))
    add_club_to_user(user_id, club_id)
    flash("Added club!", "success")
    return redirect(url_for('clubs'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def myclubs():
    if request.method == 'GET':
        #get user_id 
        user_id = session.get('id')
        ### HIGHLY INEFFICIENT
        #need to get all the user's clubs
        user_clubs = get_user_clubs(user_id)
        user_clubs_name = []
        recent_messages = []
        for clubs in user_clubs:
            pass
        #get the names of the clubs specified by the club id
        for i in range(len(user_clubs)):
            club = search_club_by_id(user_clubs[i][2])[0][2]
            recent_message_from_club = get_most_recent_message(user_clubs[i][2])
            user_clubs_name.append(club)
            recent_messages.append(recent_message_from_club)
            #get the most recent messages
        return render_template("dashboard.html", user_clubs = user_clubs_name, recent_club_messages = recent_messages)

### STREAM OF THE CLASSROOM
@app.route('/stream/<club_name>', methods=['GET','POST'])
@login_required
def stream(club_name):
    #get the id of the club
    club_id = search_clubs(club_name)[0][0]
    #check if the user is an owner of the club
    user_id = session.get('id')
    user_clubs = get_user_clubs(user_id)
    user_clubs_name = []
    #get the names of the clubs specified by the club id
    for i in range(len(user_clubs)):
        club = search_club_by_id(user_clubs[i][2])[0][2]
        user_clubs_name.append(club)
    #ownership of club CHANGE THIS LATER!!!!
    ownership = False
    messages = (get_messages(club_id))[::-1]
    message_dates = []
    message_names = []
    for message in messages:
        datetime_str = message[2]
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        month_day = datetime_obj.strftime('%B %d')
        time = datetime_obj.strftime('%H:%M')
        message_dates.append([month_day,time])

        message_poster = get_user_by_id(message[3])
        message_name = message_poster[0][1] + ' ' + message_poster[0][2]
        message_names.append(message_name)
    #if statement to reverse messages so newest is frist
    if request.method == 'GET':
        #determine ownership of club
        if is_club_owner(user_id, club_id):
            ownership = True
        #get the messages of the club to get ready to output
        #need club name just in case of routing?
        return render_template('stream.html', ownership=ownership, messages=messages, club_name=club_name, edit_access=True, user_clubs=user_clubs_name, message_dates=message_dates, message_names=message_names)
    #for now can only make announcements
    #if the user is an owner, allow for the post announcements functionality
    elif request.method == 'POST':
        #get the text from the textarea form?
        #parse it and add it to the relational text database 
        message = request.form.get("message")
        #get the current time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #post the message into the database
        post_message(user_id, club_id, message, current_time)

        #redirect to the stream and flash that post has been successful (? hopefully the posts are there? )
        return redirect(url_for('stream', club_name=club_name, user_clubs = user_clubs_name))

@app.route('/stream/attendance/<club_name>')
@login_required
def attendance(club_name):
    club_id = search_clubs(club_name)[0][0]
    users = search_users_of_a_club(club_id)
    if request.method == 'GET':
        return render_template('attendance.html', users=users)
    elif request.method == 'POST':
        pass

@app.route('/stream/create_events/<club_name>')
def create_events(club_name):
    pass

@app.route('/calendar')
def calendar():
    return render_template("calendar.html")


###ADMIN STUFF

@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    if request.method == 'GET':
        return render_template("admin_base.html")
@app.route('/admin/manage_users', methods=["GET", "POST"])
@login_required
def manage_users():
    if request.method == 'GET':
        users = get_all_users()
        return render_template("admin_users.html", users = users)
    
@app.route('/admin/manage_clubs', methods=["GET", "POST"])
@login_required
def manage_clubs():
    if request.method == 'GET':
        clubs = get_all_clubs()
        return render_template("admin_clubs.html", clubs=clubs)

@app.route('/admin/manage_attendance')
def manage_attendance():
    pass

@app.route('/admin/manage_events', methods=['GET', 'POST'])
def manage_events():
    pass

if __name__ == "__main__":
    #create the tables
    create_tables()
    #create the clubs list
    initialize_clubs()
    #make jake admiN!
    make_jake_owner()
    app.run(host="localhost", port=5000, debug=True)