from flask import Flask, render_template
import json

with open('meals.json', 'r', encoding='utf-8') as r_file:
    content = json.load(r_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/main", methods=['GET', 'POST'])
def main():
    return render_template('main.html')


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    return render_template('calories.html')


@app.route("/meals", methods=['GET', 'POST'])
def meals():
    # return render_template('available_meals.html')
    return render_template('available_meals.html', content=content)

result=[(('Курка відварна', 'Крем-суп з гарбуза', 'Капуста тушкована з грибами, порція - 1.5', 'Картопля фрі, порція - 0.5'), '98.91%', (999.0, 75.075, 96.445, 33.2)), (('Курка відварна', 'Баклажани тушковані з грибами, порція - 2', 'Капуста тушкована з грибами, порція - 1.5', 'Картопля фрі, порція - 0.5'), '98.84%', (1009.0, 77.375, 99.875, 33.15)), (('Курка відварна', 'Овочевий рататуй', 'Капуста тушкована з грибами, порція - 2', 'Картопля фрі, порція - 0.5'), '95.27%', (1004.5, 77.625, 103.45, 29.195)), (('Суп-пюре морквяний', 'Котлета куряча, порція - 2', 'Котлета рибна, порція - 2', 'Баклажани тушковані з грибами, порція - 0.5'), '91.98%', (999.0, 74.65, 95.55, 41.925)), (('Курка відварна', 'Капуста тушкована з грибами, порція - 1.5', 'Картопля фрі, порція - 0.5', 'Овочевий рататуй, порція - 1.5'), '95.68%', (991.5, 76.5, 102.175, 28.955))]
@app.route("/results", methods=['GET', 'POST'])
def results():
    return render_template('results.html', results=result)


if __name__ == '__main__':
    app.run(debug=True)
