"Routes module"

import json
from flask import render_template, redirect, url_for, flash
from main import app
from main.forms import CalculatorForm, ExampleForm, \
    RegistrationForm, LoginForm, PersonalInfoForm
from main.calculator import calculator_func


with open('Main/data/meals.json', 'r', encoding='utf-8') as r_file:
    content = json.load(r_file)



@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    "Home page"
    return render_template('home.html')


@app.route("/main", methods=['GET', 'POST'])
def main():
    "Main page"
    return render_template('main.html')


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    "Calories settings page"
    return render_template('calories.html')

@app.route("/results/<dishes>", methods=['GET', 'POST'])
def results(dishes):
    "Result page"
    with open('main/data/results.txt', 'r', encoding='utf-8') as file:
        resul = file.read()
        resul = resul.split('\n\n')
        resul.pop(-1)
        for inx, value in enumerate(resul):
            resul[inx] = value.split('\n')

    print(resul)
    return render_template('results.html', results=resul)

@app.route('/test/<nutrients>', methods=['GET', 'POST'])
def test(nutrients):
    'Test page'
    form = ExampleForm()
    if form.validate_on_submit():
        nutrients = list(map(float, nutrients[1:-2].split(', ')))
        calor = (nutrients[0]+nutrients[1])*3 + nutrients[2]*9
        result = calculator_func(form.choices.data, nutrition=(calor, nutrients[0], nutrients[1], nutrients[2]))
        print(result)
        with open('main/data/results.txt', 'w', encoding='utf-8') as file:
            for res in result:
                for meal in res[0]:
                    file.write(meal + '\n')
                file.write('\n')
        return redirect(url_for('results', dishes = result))
    return render_template('test.html', form = form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    form = PersonalInfoForm()
    return render_template('personal_info.html', form=form)

@app.route('/calculator', methods=['GET','POST'])
def calculator():
    "Calculator page"
    form = CalculatorForm()
    if form.validate_on_submit():
        proteins = float(form.proteins.data)
        carbs = float(form.carbs.data)
        fats = float(form.fats.data)
        return redirect(url_for('test', nutrients = (proteins, carbs, fats)))
    return render_template('calculator.html', form=form)
