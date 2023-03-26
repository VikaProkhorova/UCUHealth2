"Models module"

from flask_login import UserMixin
from main import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    "Loads user"
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    "User class"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
