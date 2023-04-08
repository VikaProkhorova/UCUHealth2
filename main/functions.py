'Function module'

import json
import secrets
import os
from typing import List
from flask import url_for
from PIL import Image
from flask_login import current_user
from flask_mail import Message
from main.forms import MultiCheckboxFormMeals, MultiCheckboxFormSettings
from main import mail, app

def calcalories(state: str, hight: int, age: int,
        wase: int, activity: float, wants: int) -> tuple:
    """ Cal calculator
    For A
    1,2 - сидячий ОЖ;
    1,4 - наявність фізичних навантажень двічі на тиждень;
    1,46 - активний ОЖ із наявністю 4-5 тренувань на тиждень;
    1,55 - 5-6 фізичних тренувань на тиждень; 1,63 - щоденні тренування;
    1,72 - щоденні фізичні навантаження не менше 2 разів на день;
    1,9 - важка робота чи інтенсивні фізичні тренування двічі на день.
    """
    if state.lower()== 'male':
        kilokalories = (10*wase + 6.25* hight - 5* age + 5)*activity
    else:
        kilokalories = (10*wase + 6.25* hight - 5* age - 161)* activity
    if wants==1:
        kilokalories*=0.8
    elif wants==2:
        kilokalories*=1.2
    bilku = int(round((kilokalories* 0.3)/4, -1))
    fats = int(round((kilokalories*0.2)/9, -1))
    vuglevodu = int(round((kilokalories* 0.5)/4, -1))
    return (int(round(kilokalories, -1)), bilku, vuglevodu, fats)

def meal_getter() -> List[object]:
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

def send_email(email: str, pers_info: tuple[str]) -> None:
    'Sends email'
    token = secrets.token_hex(20)
    msg = Message('Email Confirmation',
                  sender='noreply@demo.com',
                  recipients=[email])
    msg.html = f'<a class="button" \
href="{url_for("personal_info", _=token, _external=True, pers_info = pers_info)}\
">Confirm Email</a>'
    mail.send(msg)

def save_picture(form_picture: str) -> str:
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

def save_json(info_unrepeatable: List[float], info_portions: dict) -> None:
    'Saves json'
    dct = {"unrepeatable meals": info_unrepeatable, "portions": {}}
    portions = info_portions['choices']
    for i in portions:
        key, value = i.split('-')
        if key not in dct['portions']:
            dct['portions'].update({key: []})
        if len(value) == 1:
            value = int(value)
        else:
            value = float(value)
        dct['portions'][key].append(value)
    with open(f'main/settings/{current_user.settings}', 'w', encoding='utf-8') as file:
        json.dump(dct, file, indent=2)

def form_creator(keys: List[str]) -> List[object]:
    "Gets settings info to create form"
    with open('main/settings/default.json', 'r', encoding='utf-8') as file:
        info = json.load(file)['max_portions']
    lst = []
    for i in keys:
        new_lst = []
        for inf in info:
            new_lst.append(f'{i}-{inf}')
        field = MultiCheckboxFormSettings()
        field.choices.label = i.title()
        field.choices.choices = list(zip(new_lst, info))
        lst.append(field)
    return lst

def send_reset_email(user: object) -> None:
    'Sends reset mail'
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.html = f'<a class="button" \
href="{url_for("reset_token", token=token, _external=True)}\
">Reset Password</a>'
    mail.send(msg)

def opener(path_lst: List[str]) -> None:
    'Creates json with specific category' 
    dct = {}
    total = {}
    for path in path_lst:
        with open(f"main/data/{path}.csv", "r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip().split(",")
                dct.update({line[0]: tuple(float(x) for x in line[2:])})
        total.update({path: dct.copy()})
        dct.clear()
    with open("main/data/meals.json", "w", encoding="utf-8") as file:
        json.dump(total, file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    meal_lst = ["breakfasts", "second meals", "salads", "garnirs", "soups"]
    opener(meal_lst)
