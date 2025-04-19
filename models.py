from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        try:
            from app import supabase
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            if response.data:
                user_data = response.data[0]
                return User(user_data['id'], user_data['username'])
            return None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    @staticmethod
    def authenticate(username, password):
        try:
            from app import supabase
            response = supabase.table('users').select('*').eq('username', username).execute()
            if response.data:
                user_data = response.data[0]
                if user_data['password'] == password:
                    return User(user_data['id'], user_data['username'])
            return None
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(200))
    province = db.Column(db.String(100))
    score = db.Column(db.Float)
    subject = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now()) 