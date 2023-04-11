"Routes module"

import secrets
import json
from datetime import datetime
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, current_user, logout_user, login_required
from main import app, db, bcrypt
from main.forms import CalculatorForm, PossibleMeals, RegistrationForm, \
    LoginForm, PersonalInfoForm, AddMeal, UpdateAccountForm, CustomPlan, MealForm, \
    PersonalPlan, RequestResetForm, ResetPasswordForm, SettingsForm
from main.calculator import calculator_func
from main.models import User, Meal, Dish
from main.functions import calcalories, meal_getter, stringer, send_email, \
    save_picture, save_json, form_creator, send_reset_email

@app.route("/", methods=['GET', 'POST'])
@app.route("/main", methods=['GET', 'POST'])
def main():
    "Main page"
    if not current_user.is_authenticated:
        return render_template('home.html', title = 'Home')
    meals = Meal.query.filter_by(date_added = datetime.date(datetime.utcnow()),
        user_id = current_user.id).all()
    if request.method == 'POST':
        if request.form['submit_button'] == "Daily Distribution":
            if meals:
                return redirect(url_for('main'))
            with open('main/data/daily_distribution.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            for i, j in data[str(current_user.servings)]:
                meal = Meal(name = j, calories = round(current_user.calories*i, -1),
                    proteins = current_user.proteins*i, carbs = current_user.carbs*i,
                    fats = current_user.fats*i, author = current_user)
                db.session.add(meal)
                db.session.commit()
            return redirect(url_for('main'))
        if request.form['submit_button'] == "Add Meal":
            return redirect(url_for('add_meal', user_id = current_user))
    return render_template('main.html', title = 'Main', meals = meals)

@app.route('/menu', methods=['GET'])
def menu():
    'Menu route'
    with open('main/data/meals.json', 'r', encoding='utf-8') as file:
        info = json.load(file)
    return render_template('menu.html', meals = info, title = 'Menu')

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
            with open(f'main/settings/{current_user.settings}', 'r', encoding='utf-8') as file:
                setting = json.load(file)
            dishes = calculator_func(form.meals[0].data['choices'],
                nutrition=(meal.calories, meal.proteins, meal.carbs, meal.fats),
                settings=setting, maxim = current_user.options, amount=current_user.meals_amount)
            for dish in dishes:
                processed = str(dish[0])[1:-1]
                if processed[-1] == ",":
                    processed = processed[:-1]
                new_dish = Dish(dishes = stringer(processed), satis = dish[1],
                calories = round(dish[2][0], -1), proteins = round(dish[2][1], -1),
                carbs = round(dish[2][2], -1),
                fats = round(dish[2][3], -1), meal = meal)
                db.session.add(new_dish)
                db.session.commit()
                if meal.choicen == 0:
                    meal.choicen = new_dish.id
                    meal.calories = new_dish.calories
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

@login_required
@app.route('/show_dish/<int:meal_id>', methods=['GET', 'POST'])
def show_dish(meal_id):
    "Shows choicen meal"
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user:
        abort(403)
    dish = Dish.query.get_or_404(meal.choicen)
    lst = dish.dishes.split(', ')
    return render_template('show_dish.html', dish = dish, title = 'Show dish', dish_lst = lst)

@app.route("/results/<dishes_id>", methods=['GET', 'POST'])
def results(dishes_id):
    "Result page"
    ids = list(map(int, dishes_id[1:-1].split(', ')))
    dishes = []
    for someid in ids:
        dish = Dish.query.filter_by(id = someid).first()
        if dish is None:
            return redirect(url_for('main'))
        dishes.append(dish)
    choices = []
    for dish in dishes:
        choices.append((dish.dishes.split(', '), dish))
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
            file_path = 'default.json' if not \
                current_user.is_authenticated else current_user.settings
            maxim = 5 if not current_user.is_authenticated else current_user.options
            amount = 4 if not current_user.is_authenticated else current_user.meals_amount
            with open(f'main/settings/{file_path}', 'r', encoding='utf-8') as file:
                setting = json.load(file)
            dishes = calculator_func(form.meals[0].data['choices'],
                nutrition=(meal[0], meal[1], meal[2], meal[3]),
                settings = setting, maxim=maxim, amount = amount)
            id_lst = []
            for dish in dishes:
                processed = str(dish[0])[1:-1]
                if processed[-1] == ",":
                    processed = processed[:-1]
                new_dish = Dish(dishes = stringer(processed), satis = dish[1],
                calories = round(dish[2][0]), proteins = round(dish[2][1]),
                carbs = round(dish[2][2]), fats = round(dish[2][3]))
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

@app.route('/flash_message')
def flash_message():
    'Empty page'
    message = "The confirmation was sent to your email. Check it and follow the link"
    flash(message, 'info')
    flash('If you did not receive an email, check your spam folder.', 'info')
    return render_template('layout.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    "Register route"
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hased_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        send_email(form.email.data, (form.username.data, \
        form.email.data, hased_password))
        return redirect(url_for('flash_message'))
    return render_template('register.html', title='Register', form=form)

@app.route('/personal_info/<path:pers_info>/<_>', methods=['GET', 'POST'])
def personal_info(pers_info, _):
    "Personal info route"
    form = PersonalInfoForm()
    pers_infos = [x[1:-1] for x in list(pers_info[1:-1].split(', '))]
    user = User.query.filter_by(email=pers_infos[1]).first()
    if user:
        flash('Email is already confirmed', 'info')
        return redirect(url_for('login'))
    if form.validate_on_submit():
        nutrients = calcalories(form.sex.data, form.height.data, form.age.data,
            form.weight.data, form.activity.data, form.goal.data)
        json_name = secrets.token_hex(8) + '.json'
        with open('main/settings/default.json', 'r', encoding='utf-8') as file, \
        open(f'main/settings/{json_name}', 'w', encoding='utf-8') as user_file:
            default_info = json.load(file)
            json.dump(default_info, user_file, indent=2)
        user = User(username = pers_infos[0], email = pers_infos[1], password = pers_infos[2],\
        sex = form.sex.data, age = form.age.data, height = form.height.data,\
            weight = form.weight.data, goal = form.goal.data, activity = form.activity.data,
            calories = nutrients[0], proteins = nutrients[1], carbs = nutrients[2],
            fats = nutrients[3], settings = json_name)
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
            redirect(url_for('main'))
        flash('Login Unsuccessful. Please check username and password', "danger")
    return render_template('login.html', title='Login', form=form)

@app.route('/account', methods=["GET", 'POST'])
@login_required
def account():
    "Account page"
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file = image_file, title = 'Account')

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
        current_user.sex = form.sex.data
        current_user.age = form.age.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        current_user.goal = form.goal.data
        current_user.activity = form.activity.data
        current_user.servings = form.servings.data
        if current_user.custom_plan is False:
            nutrients = calcalories(form.sex.data, int(form.height.data), int(form.age.data),
                int(form.weight.data), float(form.activity.data), int(form.goal.data))
            current_user.calories = nutrients[0]
            current_user.proteins = nutrients[1]
            current_user.carbs = nutrients[2]
            current_user.fats = nutrients[3]
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account_update'))
    form.username.data = current_user.username
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
    return render_template('account_plan.html', form = nutrients_form,
        choice_form = choice_form, title = "Personal Plan")

@app.route('/settings', methods=["GET", 'POST'])
@login_required
def settings():
    'Settings route'
    form = SettingsForm()
    with open('main/data/meals.json', 'r', encoding='utf-8') as file:
        info = list(json.load(file).keys())
    form_lst = form_creator(info)
    form.unrepeatable.choices = [(cat, cat) for cat in info]
    form.portions = form_lst
    if form.validate_on_submit():
        check_set = set()
        for res in form.portions[0].data['choices']:
            check_set.add(res[:res.index('-')])
        if check_set == set(info):
            current_user.options = form.option.data
            current_user.meals_amount = form.amount.data
            save_json(form.unrepeatable.data, form.portions[0].data)
            db.session.commit()
            return redirect(url_for('account'))
        flash('Choose at least one portion in every category', 'danger')
        return redirect(url_for('settings'))
    with open(f'main/settings/{current_user.settings}', 'r', encoding='utf-8') as file:
        data = json.load(file)
        user_data = data['portions']
        default = data['unrepeatable meals']
        for portion_form in form.portions:
            default_lst = []
            for i in user_data[portion_form.choices.label.lower()]:
                default_lst.append(f'{portion_form.choices.label.lower()}-{i}')
            portion_form.choices.data = default_lst
        form.unrepeatable.data = default
        form.option.data = current_user.options
        form.amount.data = current_user.meals_amount
    return render_template('settings.html', title = 'Settings', form = form)

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

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    'Resets request'
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        flash('If you did not receive an email, check your spam folder.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    'Resets token'
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
