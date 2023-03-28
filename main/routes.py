"Routes module"

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from main import app, db, bcrypt
from main.forms import CalculatorForm, ExampleForm, PossibleMeals,\
    RegistrationForm, LoginForm, PersonalInfoForm, AddMeal
from main.calculator import calculator_func
from main.models import User, Meal, Dish
from main.calccalories import calcalories

@app.route("/")
@app.route("/main", methods=['GET', 'POST'])
def main():
    "Main page"
    if not current_user.is_authenticated:
        return render_template('home.html', title = 'Home')
    if request.method == 'POST':
        if request.form['submit_button'] == "Daily Distribution":
            for i, j in [(0.3, 'Breakfast'), (0.4, 'Lunch'), (0.3, 'Dinner')]:
                meal = Meal(name = j, calories = round(current_user.calories*i, -1),
                    proteins = current_user.proteins*i, carbs = current_user.carbs*i,
                    fats = current_user.fats*i, author = current_user)
                db.session.add(meal)
                db.session.commit()
        if request.form['submit_button'] == "Add Meal":
            return redirect(url_for('add_meal', user_id = current_user))
    meals = Meal.query.filter_by(date_added = datetime(*tuple(map(int,
            datetime.utcnow().strftime('%Y-%m-%d').split('-')))), author = current_user).all()
    return render_template('main.html', title = 'Main', meals = meals)

@login_required
@app.route('/add_meal', methods=['GET', 'POST'])
def add_meal():
    "Adds meal"
    form = AddMeal()
    if form.validate_on_submit():
        proteins = float(form.proteins.data)
        carbs = float(form.carbs.data)
        fats = float(form.fats.data)
        meal = Meal(name = form.meal_name.data,
            calories = round(((proteins+carbs)*4 + fats*9), -1),
            proteins = proteins, carbs = carbs,
            fats = fats, author = current_user)
        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('add_meal.html', form = form)

@login_required
@app.route('/choose_dishes/<int:meal_id>', methods=['GET', 'POST'])
def choose_dishes(meal_id):
    "Chooses dish"
    form = ExampleForm()
    meal = Meal.query.get_or_404(meal_id)
    if meal.author != current_user:
        abort(403)
    if form.validate_on_submit():
        dishes = calculator_func(form.choices.data,
            nutrition=(meal.calories, meal.proteins, meal.carbs, meal.fats))
        for dish in dishes:
            new_dish = Dish(dishes = stringer(str(dish[0])[1:-1]), satis = dish[1],
            calories = dish[2][0], proteins = dish[2][1], carbs = dish[2][2],
            fats = dish[2][3], meal = meal)
            db.session.add(new_dish)
            db.session.commit()
        return redirect(url_for('view_dishes', meal_id = meal.id))
    return render_template('meals.html', form = form)

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
    for dish in dishes:
        choices.append((dish.id, dish.dishes))
    form.dish_var.choices = choices
    if form.validate_on_submit():
        meal.choicen = form.dish_var.data
        db.session.commit()
        return redirect(url_for('main'))
    return render_template('view_dishes.html', form = form)

def stringer(input_str: str) -> str:
    "Converts str into normal look"
    input_str = input_str[1:-1].split("', '")
    new_str = ''
    for value in input_str:
        new_str += value + ', '
    return new_str.rstrip()

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
    return render_template('show_dish.html', dish = dish)

@app.route("/results/<int:meal_id>", methods=['GET', 'POST'])
def results(meal_id):
    "Result page"
    meal = Meal.query.get_or_404(meal_id)
    dishes = Dish.query.filter_by(meal = meal).all()
    if not dishes:
        abort(404)
    choices = []
    for dish in dishes:
        choices.append(dish.dishes)
        db.session.delete(dish)
        db.session.commit()
    if request.method == 'POST':
        if request.form['submit_button'] == "Exit":
            db.session.delete(meal)
            db.session.commit()
            return redirect(url_for('main'))
    return render_template('results.html', results=choices, title = 'Results')

@app.route('/available_meals/<int:meal_id>', methods=['GET', 'POST'])
def available_meals(meal_id):
    'Test page'
    form = ExampleForm()
    meal = Meal.query.get_or_404(meal_id)
    if form.validate_on_submit():
        dishes = calculator_func(form.choices.data,
            nutrition=(meal.calories, meal.proteins, meal.carbs, meal.fats))
        for dish in dishes:
            new_dish = Dish(dishes = stringer(str(dish[0])[1:-1]), satis = dish[1],
            calories = dish[2][0], proteins = dish[2][1], carbs = dish[2][2],
            fats = dish[2][3], meal = meal)
            db.session.add(new_dish)
            db.session.commit()
        return redirect(url_for('results', meal_id = meal.id))
    return render_template('meals.html', form = form, title = 'Available Meals')

@app.route('/calculator', methods=['GET','POST'])
def calculator():
    "Calculator page"
    form = CalculatorForm()
    if form.validate_on_submit():
        proteins = float(form.proteins.data)
        carbs = float(form.carbs.data)
        fats = float(form.fats.data)
        meal = Meal(name = 'Guest_Meal',
            calories = ((proteins+carbs)*4 + fats*9),
            proteins = proteins, carbs = carbs,
            fats = fats)
        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('available_meals', meal_id = meal.id))
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

@app.route('/account', methods=["GET", 'POST'])
@login_required
def account():
    "Account page"
    return render_template('account.html', title = "Account")

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
