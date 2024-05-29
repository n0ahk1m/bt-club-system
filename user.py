import sqlite3
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

#user object
class User(UserMixin):
#initialize club object with its parameters
    #future parameters: google classroom code(?)
    def __init__(self, id, first_name, last_name, email, isAdmin, major, interests):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email 
        self.isAdmin = isAdmin
        self.major = major
        self.interests = interests
        
def set_password(password):
        password_hash = generate_password_hash(password)
        return password_hash
def check_password(user_password_hash, password):
        return check_password_hash(user_password_hash, password)

def register_user(User):
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db_cursor.execute(
                """INSERT INTO users
                (first_name, last_name, email) VALUES (?,?,?)""",
                (User.first_name, User.last_name, User.email)
            )
    db.commit()
    db.close()

### USER SEARCHING FUNCTIONS
def get_all_users():
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db_cursor.execute(
            #have to add the other parameters later
                "SELECT * FROM users"
            )
    data = db_cursor.fetchall()
    db.close()
    return data
def search_user(email):
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db_cursor.execute(
            #have to add the other parameters later
                """SELECT * FROM users
                WHERE email=?""",
                (email,)
            )
    data = db_cursor.fetchall()
    db.close()
    return data
#get user by id
def get_user_by_id(user_id):
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db_cursor.execute(
            #have to add the other parameters later
                """SELECT * FROM users
                WHERE id=?""",
                (user_id,)
            )
    data = db_cursor.fetchall()
    db.close()
    return data
#getting the users for the club (need for attendance)
def get_users_in_club(club_id):
    pass

def change_pfp(user_id,picture):
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db.cursor.execute("""UPDATE users
                      SET picture = ?
                      WHERE id = ? """,
                      (picture,user_id))
    db.commit()
    db.close()


def add_to_user(user_id,grad_year,major):
    db = sqlite3.connect('db/database.db')
    db_cursor = db.cursor()
    db_cursor.execute("""UPDATE users 
                      SET grad_year = ?, major = ? 
                      WHERE id = ? """, 
                      (grad_year,major,user_id))  
    db.commit()
    db.close()

# Generate a Verification Token:
def generate_verification_token():
    return secrets.token_urlsafe(50)  # Adjust the token length as needed