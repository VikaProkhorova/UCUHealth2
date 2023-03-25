from main import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    sex = db.Column(db.String(), nullable = False)
    age = db.Column(db.String(5), nullable = False)
    height = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.String(10), nullable=False)
    goal = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
