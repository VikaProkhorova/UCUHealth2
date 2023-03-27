"Routes module"

import json
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from main import app, db, bcrypt
from main.forms import CalculatorForm, ExampleForm, \
    RegistrationForm, LoginForm, PersonalInfoForm
from main.calculator import calculator_func
from main.models import User

with open('Main/data/meals.json', 'r', encoding='utf-8') as r_file:
    content = json.load(r_file)

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    "Home page"
    return render_template('home.html', title = 'Home')


@app.route("/main", methods=['GET', 'POST'])
def main():
    "Main page"
    return render_template('main.html', title = 'Main')


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    "Calories settings page"
    return render_template('calories.html', title = 'Calories')

@app.route("/results/<_>", methods=['GET', 'POST'])
def results(_):
    "Result page"
    with open('main/data/results.txt', 'r', encoding='utf-8') as file:
        resul = file.read()
        resul = resul.split('\n\n')
        resul.pop(-1)
        for inx, value in enumerate(resul):
            resul[inx] = value.split('\n')
    print(resul)
    return render_template('results.html', results=resul, title = 'Results')

@app.route('/available_meals/<nutrients>', methods=['GET', 'POST'])
def available_meals(nutrients):
    'Test page'
    form = ExampleForm()
    if form.validate_on_submit():
        nutrients = list(map(float, nutrients[1:-2].split(', ')))
        calor = (nutrients[0]+nutrients[1])*3 + nutrients[2]*9
        result = calculator_func(form.choices.data,
            nutrition=(calor, nutrients[0], nutrients[1], nutrients[2]))
        with open('main/data/results.txt', 'w', encoding='utf-8') as file:
            for res in result:
                for meal in res[0]:
                    file.write(meal + '\n')
                file.write('\n')
        return redirect(url_for('results', _ = result))
    return render_template('meals.html', form = form, title = 'Available Meals')

@app.route("/register", methods=['GET', 'POST'])
def register():
    "Register route"
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        print(form.password.data)
        return redirect(url_for("personal_info", pers_info = (form.username.data, \
        form.email.data, form.password.data)))
    return render_template('register.html', title='Register', form=form)

@app.route('/personal_info/<pers_info>', methods=['GET', 'POST'])
def personal_info(pers_info):
    "Personal info route"
    form = PersonalInfoForm()
    pers_infos = [x[1:-1] for x in list(pers_info[1:-1].split(', '))]
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(pers_infos[2]).decode('utf-8')
        user = User(username = pers_infos[0], email = pers_infos[1], password = hashed_password,\
        sex = form.sex.data, age = form.age.data, height = form.height.data,\
            weight = form.weight.data, goal = form.goal.data, activity = form.activity.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account had been created', 'success')
        flash('Now you can log in!')
        return redirect(url_for('login'))
    return render_template('personal_info.html', title='Personal Info', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    "Log in route"
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Login Unsuccessful. Please check username and password', "danger")
    return render_template('login.html', title='Login', form=form)

@app.route('/calculator', methods=['GET','POST'])
def calculator():
    "Calculator page"
    form = CalculatorForm()
    if form.validate_on_submit():
        proteins = float(form.proteins.data)
        carbs = float(form.carbs.data)
        fats = float(form.fats.data)
        return redirect(url_for('available_meals', nutrients = (proteins, carbs, fats)))
    return render_template('calculator.html', form=form, title = 'Calculator')

@app.route('/account', methods=["GET", 'POST'])
@login_required
def account():
    "Account page"
    return render_template('account.html', title = "Account")

@app.route('/logout')
def logout():
    "Logout route"
    logout_user()
    return redirect(url_for('home'))
