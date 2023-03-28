'Meals calculator'

from typing import List
from copy import deepcopy
from itertools import combinations
import json

def rebuilder(meals: dict[dict]) -> List[tuple]:
    """Rebuilds dict in conveniet form
    >>> rebuilder({'second meals': {'Котлета куряча': [222.0, 21.0, 13.8, 12.0]}, \
    'salads': {'Салат з домашнього сиру з редискою': [166.0, 8.97, 3.69, 12.61]}})
    [('second meals', 'Котлета куряча', [222.0, 21.0, 13.8, 12.0]), ('salads', \
'Салат з домашнього сиру з редискою', [166.0, 8.97, 3.69, 12.61])]
    """
    result = []
    for meal in meals:
        for meal_type in meals[meal]:
            result.append((meal, meal_type, meals[meal][meal_type]))
    return result

def portioner(meals: List[tuple]) -> List[tuple]:
    """Adds portion variations
    >>> portioner([('second meals', 'Котлета куряча', [222.0, 21.0, 13.8, 12.0]), ('salads', \
'Салат з домашнього сиру з редискою', [166.0, 8.97, 3.69, 12.61])])
    [('second meals', 'Котлета куряча', [222.0, 21.0, 13.8, 12.0]), \
('salads', 'Салат з домашнього сиру з редискою', [166.0, 8.97, 3.69, \
12.61]), ('second meals', 'Котлета куряча, порція - 2', (444.0, 42.0, 27.6, 24.0))]
    """
    new_meals = []
    portions = [0.5, 1, 1.5, 2]
    for meal in meals:
        if meal[0] in ('soups', 'salads'):
            continue
        for portion in portions:
            if meal[0] in ('second meals', "breakfasts") and str(portion) in ("0.5", "1.5"):
                continue
            new_meal = multiplier(meal, portion)
            new_meals.append(new_meal)
    return new_meals

def multiplier(meal: tuple, portion: float) -> tuple:
    """Multiplies by amount of portion
    >>> multiplier(('second meals', 'Котлета куряча', [222.0, 21.0, 13.8, 12.0]), 2)
    ('second meals', 'Котлета куряча, порція - 2', (444.0, 42.0, 27.6, 24.0))
    """
    new_values = []
    for value in meal[2]:
        new_values.append(value*portion)
    return meal[0], meal[1]+f', порція - {portion}', tuple(new_values)

def variator(meals: List[tuple], nutrition: tuple[float]) -> List[tuple]:
    """Generates variants"""
    j = 2
    result = []
    while j < 5:
        variants = combinations(meals, j)
        variants_amount = len(list(combinations(meals, j)))
        i = 0
        while i < variants_amount:
            variant = next(variants)
            if checker(variant) is False:
                i += 1
                continue
            counted_var = satisfactor(variant, nutrition)
            result.append(counted_var)
            i += 1
        j += 1
    return sorted(result, key = lambda x: x[1])[:5]

def checker(variant: List[tuple]) -> bool:
    """Prevents from two soups appearing in one selection
    or reaping meals with different portion
    >>> checker((('garnirs', 'Овочевий рататуй, порція - 2', \
(222.0, 5.5, 36.4, 5.74)), ('garnirs', 'Банош, порція - 0.5', \
(137.0, 4.0, 12.0, 7.0)), ('garnirs', 'Банош, порція - 1.5', \
(411.0, 12.0, 36.0, 21.0)), ('garnirs', 'Банош, порція - 2', \
(548.0, 16.0, 48.0, 28.0))))
    False
    >>> checker((('second meals', 'Котлета куряча', [222.0, 21.0, 13.8, 12.0]),\
('second meals', 'Котлета рибна', [172.0, 13.0, 13.3, 7.6]), ('second meals', 'Курка відварна', \
[276.0, 60.0, 0.0, 4.0]), ('salads', 'Салат з домашнього сиру з редискою', \
    [166.0, 8.97, 3.69, 12.61])))
    True
    """
    count = 0
    meal_names = []
    for meal in variant:
        name = meal[1]
        if meal[0] == 'soups':
            count += 1
        if ", " in name:
            name = name[:name.index(", ")]
        meal_names.append(name)
    for name in meal_names:
        if meal_names.count(name) > 1:
            return False
    if count > 1:
        return False
    return True

def satisfactor(meal_var: tuple[tuple], goal: tuple[float]) -> tuple[tuple]:
    """Counts how meal variation satisfies need
    >>> satisfactor((('salads', 'Салат з домашнього сиру з редискою', [170, 9, 4, 13]),\
    ('garnirs', 'Банош', [270, 8, 24, 14]), ('soups', 'Суп квасолевий', [280, 16, 42, 5])),\
    (1000, 75.0, 100.0, 33.0))
    (('Салат з домашнього сиру з редискою', 'Банош', 'Суп квасолевий'), \
353.0, (280, 42.0, 30.0, 1.0))
"""
    satis = list(goal)
    meal_lst = []
    satis_point = 0
    for meal in meal_var:
        for inx, value in enumerate(meal[2]):
            satis[inx] -= value
        meal_lst.append(meal[1])
    for point in satis:
        satis_point += abs(point)
    return (tuple(meal_lst), satis_point, tuple(satis))

def meal_getter(choicen_meals: List[str]) -> dict:
    "Reads json file"
    result = {}
    selection = deepcopy(choicen_meals)
    with open("main/data/meals.json", "r", encoding='utf-8') as file:
        meals = json.load(file)
    for section in meals:
        for meal in meals[section]:
            if meal in selection:
                if not section in result:
                    result.update({section: {}})
                result[section].update({meal: meals[section][meal]})
                selection.remove(meal)
                if len(selection) == 0:
                    break
    return result

def conclusioner(variants: List[tuple], goal: tuple[float]) -> List[tuple]:
    """Converts result into normal form
    >>> conclusioner([(('Курка відварна', 'Крем-суп з гарбуза', \
'Капуста тушкована з грибами, порція - 1.5', 'Картопля фрі, порція - 0.5'), \
4.830000000000007, (1.0, -0.07499999999999929, 3.555000000000007, -0.20000000000000107))],\
    (1000, 75.0, 100.0, 33.0))
    [(('Курка відварна', 'Крем-суп з гарбуза', 'Капуста тушкована з грибами, порція - 1.5', \
'Картопля фрі, порція - 0.5'), '98.91%', (999.0, 75.075, 96.445, 33.2))]"""
    new_lst = []
    for variant in variants:
        nutrients = []
        numb = 0
        for inx, value in enumerate(variant[2]):
            acc_val = goal[inx]-value
            numb += (goal[inx]-abs(value))/goal[inx]
            nutrients.append(acc_val)
        new_lst.append((variant[0], f"{round(100*numb/4, 2)}%", tuple(nutrients)))
    return new_lst

def calculator_func(choicen_meals: List[str], nutrition: tuple[float]) -> List[tuple]:
    "Main function"
    needed_meals = meal_getter(choicen_meals)
    worked_meals = rebuilder(needed_meals)
    all_meals = portioner(worked_meals)
    variants = variator(all_meals, nutrition)
    final_vars = conclusioner(variants, nutrition)
    return sorted(final_vars, key = lambda x: x[1], reverse=True)

if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
    test_lst = ['Суп квасолевий', 'Крем-суп з гарбуза', 'Суп-пюре морквяний',
       'Макарони з томатним соусом', 'Овочевий рататуй', 'Банош',
       'Салат з домашнього сиру з редискою', 'Салат з черемші і огірків',
       'Салат зі шпинату з ягодами', 'Котлета куряча', 'Котлета рибна','Курка відварна',
       "Баклажани тушковані з грибами", "Капуста тушкована з грибами",
       "Картопля фрі"]
    GOAL = 1000
    PROTEINS = (GOAL*0.3)//4
    CARBS = (GOAL*0.4)//4
    FATS = (GOAL*0.3)//9
    GOAL_SAMPLE = (GOAL, PROTEINS, CARBS, FATS)
    results = calculator_func(test_lst, GOAL_SAMPLE)
    print(f"""Goal was:
Calories: {GOAL}
Proteins: {PROTEINS}
Carbs: {CARBS}
Fats: {FATS}
""")
    for k in results:
        print("Meals")
        for dish in k[0]:
            print(dish)
        print(f"""\nSatisfaction - {k[1]}
Calories: {k[2][0]}
Proteins: {k[2][1]}
Carbs: {k[2][2]}
Fats: {k[2][3]}
              """)
