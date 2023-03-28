"Models module"

from datetime import datetime
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
    goal = db.Column(db.Integer, nullable=False)
    activity = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    proteins = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)
    meals = db.relationship('Meal', backref="author", lazy = True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Meal(db.Model):
    "Meal Group"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False)
    calories = db.Column(db.Float, nullable = False)
    proteins = db.Column(db.Float, nullable = False)
    carbs = db.Column(db.Float, nullable = False)
    fats = db.Column(db.Float, nullable = False)
    choicen = db.Column(db.Integer, nullable = False, default = 0)
    date_added = db.Column(db.DateTime, nullable = False,
        default = datetime.date(datetime.utcnow()))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    dishes = db.relationship('Dish', backref = 'meal', lazy=True)

    def __repr__(self):
        return f"Meal('{self.name}', '{self.calories}')"

class Dish(db.Model):
    "Meal class"
    id = db.Column(db.Integer, primary_key = True)
    dishes = db.Column(db.String(200), nullable = False)
    satis = db.Column(db.String(10), nullable = False)
    calories = db.Column(db.Float, nullable = False)
    proteins = db.Column(db.Float, nullable = False)
    carbs = db.Column(db.Float, nullable = False)
    fats = db.Column(db.Float, nullable = False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), nullable = False)

    def __repr__(self):
        return f"Dish('{self.dishes}', '{self.satis}', '{self.calories}')"


