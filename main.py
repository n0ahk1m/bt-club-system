from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os, io
from werkzeug.utils import secure_filename
import csv
from sqlalchemy import desc, asc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required
import random
import base64
from cryptography.fernet import Fernet
# #external py files
# import user
# import clubs

app = Flask(__name__)
#main page
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    return render_template("register.html")

@app.route('/clubs', methods=['GET', 'POST'])
def clubs():
    if request.method == 'GET':
        return render_template("clubs.html")

@app.route('/events')
def events():
    pass

@app.route('/my_clubs')
def my_clubs():
    pass

if __name__ == "__main__":
    app.secret_key = ""  # Change this to a secure ENCRYPTED key
    app.run(debug=True)