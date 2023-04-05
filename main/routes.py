"Routes module"

import secrets
import os
import json
from datetime import datetime
from typing import List
from PIL import Image
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from main import app, db, bcrypt
from main.forms import CalculatorForm, PossibleMeals, RegistrationForm, \
    LoginForm, PersonalInfoForm, AddMeal, UpdateAccountForm, CustomPlan, MealForm, \
    MultiCheckboxFormMeals, PersonalPlan, SettingsForm, MultiCheckboxFormSettings
from main.calculator import calculator_func
from main.models import User, Meal, Dish
from main.calccalories import calcalories

@app.route("/", methods=['GET', 'POST'])
@app.route("/main", methods=['GET', 'POST'])
def main():
    "Main page"
    if not current_user.is_authenticated:
        return render_template('home.html', title = 'Home')
    if request.method == 'POST':
        if request.form['submit_button'] == "Daily Distribution":
            with open('main/data/daily_distribution.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            for i, j in data[str(current_user.servings)]:
                meal = Meal(name = j, calories = round(current_user.calories*i, -1),
                    proteins = current_user.proteins*i, carbs = current_user.carbs*i,
                    fats = current_user.fats*i, author = current_user)
                db.session.add(meal)
                db.session.commit()
        if request.form['submit_button'] == "Add Meal":
            return redirect(url_for('add_meal', user_id = current_user))
    meals = Meal.query.filter_by(date_added = datetime.date(datetime.utcnow()),
            user_id = current_user.id).all()
    return render_template('main.html', title = 'Main', meals = meals)

@login_required
@app.route('/add_meal', methods=['GET', 'POST'])
def add_meal():
    "Adds meal"
    form = AddMeal()
    if form.validate_on_submit():
        proteins = int(form.proteins.data)
        carbs = int(form.carbs.data)
        fats = int(form.fats.data)
        meal = Meal(name = form.meal_name.data,
            calories = round(((proteins+carbs)*4 + fats*9), -1),
            proteins = proteins, carbs = carbs,
            fats = fats, author = current_user)
        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('add_meal.html', form = form, title = 'Add Meal')

@login_required
@app.route('/choose_dishes/<int:meal_id>', methods=['GET', 'POST'])
def choose_dishes(meal_id):
    "Chooses dish"
    form = MealForm()
    form.meals = meal_getter()
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user or meal.choicen != 0:
        abort(403)
    if form.validate_on_submit():
        if form.meals[0].data['choices'] == []:
            flash('Choose at least one option', 'danger')
        else:
            dishes = calculator_func(form.meals[0].data['choices'],
                nutrition=(meal.calories, meal.proteins, meal.carbs, meal.fats))
            for dish in dishes:
                processed = str(dish[0])[1:-1]
                if processed[-1] == ",":
                    processed = processed[:-1]
                new_dish = Dish(dishes = stringer(processed), satis = dish[1],
                calories = dish[2][0], proteins = dish[2][1], carbs = dish[2][2],
                fats = dish[2][3], meal = meal)
                db.session.add(new_dish)
                db.session.commit()
                if meal.choicen == 0:
                    meal.choicen = new_dish.id
                    db.session.commit()
            return redirect(url_for('main'))
    return render_template('meals.html', form = form, title = 'Meals')

@app.route("/view_dishes/<int:meal_id>", methods=['GET', 'POST'])
def view_dishes(meal_id):
    "Views and chooses the dishes"
    form = PossibleMeals()
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user:
        abort(403)
    dishes = Dish.query.filter_by(meal = meal).all()
    if not dishes:
        abort(404)
    choices = []
    dct = {}
    for dish in dishes:
        choices.append((dish.id, dish))
        dct[dish.id] = dish.dishes.split(', ')
    form.dish_var.choices = choices
    if request.method == 'GET':
        form.dish_var.data = meal.choicen
    test_form = list(zip(form.dish_var.choices, form.dish_var))
    if form.validate_on_submit():
        meal.choicen = form.dish_var.data
        db.session.commit()
        dish = Dish.query.get_or_404(meal.choicen)
        meal.calories = dish.calories
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('view_dishes.html', dishes = dict(choices),
            test = test_form, form = form, title = 'View Dishes', dct = dct)

def meal_getter():
    "Gets meal from json and creates form"
    with open('main/data/meals.json', 'r', encoding='utf-8') as file:
        info = json.load(file)
    lst = []
    for i, j in info.items():
        field = MultiCheckboxFormMeals()
        field.choices.label = i.title()
        field.choices.choices = sorted(list(j.keys()))
        lst.append(field)
    return lst

def stringer(input_str: str) -> str:
    "Converts str into normal look"
    input_str = input_str.split(", ")
    new_str = ''
    for value in input_str:
        new_str += value[1:-1] + ', '
    return new_str[:-2]

@login_required
@app.route('/show_dish/<int:meal_id>', methods=['GET', 'POST'])
def show_dish(meal_id):
    "Shows choicen meal"
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user:
        abort(403)
    dish = Dish.query.get_or_404(meal.choicen)
    if request.method == 'POST':
        if request.form['submit_button'] == "Back":
            return redirect(url_for('main'))
    lst = dish.dishes.split(', ')
    return render_template('show_dish.html', dish = dish, title = 'Show dish', dish_lst = lst)

@app.route("/results/<dishes_id>", methods=['GET', 'POST'])
def results(dishes_id):
    "Result page"
    ids = list(map(int, dishes_id[1:-1].split(', ')))
    dishes = []
    for someid in ids:
        dish = Dish.query.filter_by(id = someid).first()
        dishes.append(dish)
    if not dishes:
        abort(404)
    choices = []
    for dish in dishes:
        choices.append(dish.dishes)
        db.session.delete(dish)
        db.session.commit()
    return render_template('results.html', results=choices, title = 'Results')

@app.route('/available_meals/<nutrients>', methods=['GET', 'POST'])
def available_meals(nutrients):
    'Test page'
    form = MealForm()
    form.meals = meal_getter()
    meal = list(map(int, nutrients[1:-1].split(", ")))
    if form.validate_on_submit():
        if form.meals[0].data['choices'] == []:
            flash('Choose at least one option', 'danger')
        else:
            dishes = calculator_func(form.meals[0].data['choices'],
                nutrition=(meal[0], meal[1], meal[2], meal[3]))
            id_lst = []
            for dish in dishes:
                processed = str(dish[0])[1:-1]
                if processed[-1] == ",":
                    processed = processed[:-1]
                new_dish = Dish(dishes = stringer(processed), satis = dish[1],
                calories = dish[2][0], proteins = dish[2][1], carbs = dish[2][2],
                fats = dish[2][3])
                db.session.add(new_dish)
                db.session.commit()
                id_lst.append(new_dish.id)
            return redirect(url_for('results', dishes_id = tuple(id_lst)))
    return render_template('meals.html', form = form, title = 'Available Meals')

@app.route('/calculator', methods=['GET','POST'])
def calculator():
    "Calculator page"
    form = CalculatorForm()
    if form.validate_on_submit():
        proteins = int(form.proteins.data)
        carbs = int(form.carbs.data)
        fats = int(form.fats.data)
        return redirect(url_for('available_meals',
            nutrients = ((int(round(((proteins+carbs)*4 + fats*9), -1))), proteins, carbs, fats)))
    return render_template('calculator.html', form=form, title = 'Calculator')

@app.route("/register", methods=['GET', 'POST'])
def register():
    "Register route"
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
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
        nutrients = calcalories(form.sex.data, form.height.data, form.age.data,
            form.weight.data, form.activity.data, form.goal.data)
        user = User(username = pers_infos[0], email = pers_infos[1], password = hashed_password,\
        sex = form.sex.data, age = form.age.data, height = form.height.data,\
            weight = form.weight.data, goal = form.goal.data, activity = form.activity.data,
            calories = nutrients[0], proteins = nutrients[1], carbs = nutrients[2],
            fats = nutrients[3])
        db.session.add(user)
        db.session.commit()
        flash('Your account had been created', 'success')
        return redirect(url_for('login'))
    return render_template('personal_info.html', title='Personal Info', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    "Log in route"
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main'))
        flash('Login Unsuccessful. Please check username and password', "danger")
    return render_template('login.html', title='Login', form=form)

def save_picture(form_picture):
    "Trim and saves picture"
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=["GET", 'POST'])
@login_required
def account():
    "Account page"
    if request.method == 'POST':
        if request.form['submit_button'] == "Personal Info":
            return redirect(url_for('account_update'))
        elif request.form['submit_button'] == "Personal Plan":
            return redirect(url_for('account_plan'))
        elif request.form['submit_button'] == "Settings":
            return redirect(url_for('settings'))
        elif request.form['submit_button'] == "Calendar":
            return redirect(url_for('calendar'))
        else:
            return redirect(url_for('logout'))
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file = image_file)

@app.route('/calendar', methods=["GET", 'POST'])
@login_required
def calendar():
    'Calendar route'
    return render_template('calendar.html', title = 'Calendar')
    
@app.route('/account_update', methods=["GET", 'POST'])
@login_required
def account_update():
    "Account page"
    form = UpdateAccountForm()
    with open('main/data/daily_distribution.json', 'r', encoding='utf-8') as file:
        choices = list(json.load(file).keys())
    form.servings.choices = choices
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.sex = form.sex.data
        current_user.age = form.age.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        current_user.goal = form.goal.data
        current_user.activity = form.activity.data
        if current_user.custom_plan is False:
            nutrients = calcalories(form.sex.data, int(form.height.data), int(form.age.data),
                int(form.weight.data), float(form.activity.data), int(form.goal.data))
            current_user.calories = nutrients[0]
            current_user.proteins = nutrients[1]
            current_user.carbs = nutrients[2]
            current_user.fats = nutrients[3]
            current_user.servings = form.servings.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account_update'))
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.sex.data = current_user.sex
    form.age.data = current_user.age
    form.height.data = current_user.height
    form.weight.data = current_user.weight
    form.goal.data = current_user.goal
    form.activity.data = current_user.activity
    form.servings.data = current_user.servings
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account_update.html', title = "Account Update",
        image_file=image_file, form=form)

@app.route('/account_plan', methods=["GET", 'POST'])
@login_required
def account_plan():
    "Account plan page"
    choice_form = CustomPlan()
    nutrients_form = PersonalPlan()
    with open('main/data/daily_distribution.json', 'r', encoding='utf-8') as file:
        choices = list(json.load(file).keys())
    nutrients_form.servings.choices = choices
    if choice_form.validate_on_submit():
        user_choice = choice_form.plan_choice.data
        if user_choice == 1:
            current_user.custom_plan = user_choice
            proteins = int(nutrients_form.proteins.data)
            carbs = int(nutrients_form.carbs.data)
            fats = int(nutrients_form.fats.data)
            current_user.calories = int(round((proteins+carbs)*4 + fats*9, -1))
            current_user.proteins = proteins
            current_user.carbs = carbs
            current_user.fats = fats
            current_user.servings = nutrients_form.servings.data
        else:
            current_user.custom_plan = user_choice
            nutrients = calcalories(current_user.sex, current_user.height, current_user.age,
            current_user.weight, current_user.activity, current_user.goal)
            current_user.calories = nutrients[0]
            current_user.proteins = nutrients[1]
            current_user.carbs = nutrients[2]
            current_user.fats = nutrients[3]
        db.session.commit()
        return redirect(url_for('account'))
    choice_form.plan_choice.data = current_user.custom_plan
    nutrients_form.proteins.data = int(round(current_user.proteins, -1))
    nutrients_form.carbs.data = int(round(current_user.carbs, -1))
    nutrients_form.fats.data = int(round(current_user.fats, -1))
    nutrients_form.servings.data = current_user.servings
    return render_template('account_plan.html', form = nutrients_form,
        choice_form = choice_form, title = "Personal Plan")

@app.route('/settings', methods=["GET", 'POST'])
@login_required
def settings():
    'Settings route'
    form = SettingsForm()
    with open('main/data/meals.json', 'r', encoding='utf-8') as file, \
        open(f'main/settings/{current_user.settings}', 'r', encoding='utf-8') as file_sec:
        info = list(json.load(file).keys())
        default = json.load(file_sec)['unrepeatable meals']
    form_lst = form_creator(info)
    form.unrepeatable.choices = [(cat, cat) for cat in info]
    form.portions = form_lst
    if form.validate_on_submit():
        print(form.portions[0].data)
    form.unrepeatable.data = default
    with open(f'main/settings/{current_user.settings}', 'r', encoding='utf-8') as file:
        user_data = json.load(file)['portions']
        for portion_form in form.portions:
            portion_form.choices.data = user_data[portion_form.choices.label.lower()]
    return render_template('settings.html', title = 'Settings', form = form)

def form_creator(keys: List):
    "Gets settings info to create form"
    with open('main/settings/portions.json', 'r', encoding='utf-8') as file:
        info = json.load(file)['max_portions']
    lst = []
    for i in keys:
        field = MultiCheckboxFormSettings()
        field.choices.label = i.title()
        field.choices.choices = info
        lst.append(field)
    return lst

@app.route('/logout')
def logout():
    "Logout route"
    logout_user()
    return redirect(url_for('main'))

@app.route('/delete_meal/<int:meal_id>', methods=['POST', 'GET'])
@login_required
def delete_meal(meal_id):
    "Deletes meal"
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user:
        abort(403)
    dishes = Dish.query.filter_by(meal = meal).all()
    for dish in dishes:
        db.session.delete(dish)
        db.session.commit()
    db.session.delete(meal)
    db.session.commit()
    return redirect(url_for('main'))
