"Models module"

from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from main import db, login_manager, app

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
    image_file = db.Column(db.String(20), nullable = False, default='default.jpg')
    settings = db.Column(db.String(100), nullable = False, default='default.json')
    custom_plan = db.Column(db.Boolean, default = False)
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
    servings = db.Column(db.Integer, nullable = False, default = 3)
    options = db.Column(db.Integer, nullable = False, default = 5)
    meals = db.relationship('Meal', backref="author", lazy = True)

    def get_reset_token(self, expires_sec=1800):
        'Gets reset token'
        obj = Serializer(app.config['SECRET_KEY'], expires_sec)
        return obj.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        'Verifies reset token'
        obj = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = obj.loads(token)['user_id']
        except Exception as _:
            return None
        return User.query.get(user_id)

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
    choicen = db.Column(db.Integer, default = 0)
    date_added = db.Column(db.Date, nullable = False,
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
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id'), default = 0)

    def __repr__(self):
        return f"Dish('{self.dishes}', '{self.satis}', '{self.calories}')"
