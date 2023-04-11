'Meals calculator'

from typing import List
from copy import deepcopy
from itertools import combinations
import json

def rebuilder(meals: dict[dict]) -> List[tuple]:
    "Rebuilds dict in conveniet form"
    result = []
    for meal in meals:
        for meal_type in meals[meal]:
            result.append((meal, meal_type, meals[meal][meal_type]))
    return result

def portioner(meals: List[tuple], portion_info: dict) -> List[tuple]:
    "Adds portion variations"
    new_meals = []
    for meal in meals:
        for portion in portion_info[meal[0]]:
            new_meal = multiplier(meal, portion)
            new_meals.append(new_meal)
    return new_meals

def multiplier(meal: tuple, portion: float) -> tuple:
    "Multiplies by amount of portion"
    new_values = []
    for value in meal[2]:
        new_values.append(value*portion)
    return meal[0], meal[1]+f': порція - {portion}', tuple(new_values)

def variator(meals: List[tuple], nutrition: tuple[float],
        unrepeatable_info: List[str], maxim: int, amount: int) -> List[tuple]:
    "Generates variants"
    j = 1
    result = []
    while j < amount + 1:
        variants = combinations(meals, j)
        variants_amount = len(list(combinations(meals, j)))
        i = 0
        while i < variants_amount:
            variant = next(variants)
            if checker(variant, unrepeatable_info) is False:
                i += 1
                continue
            counted_var = satisfactor(variant, nutrition)
            result.append(counted_var)
            i += 1
        j += 1
    return result[:maxim]

def checker(variant: List[tuple], unrepeatable_info: List[str]) -> bool:
    "Checks for valid meals"
    meal_names = []
    check_dct = {}
    for meal in unrepeatable_info:
        check_dct[meal] = 0
    for meal in variant:
        name = meal[1]
        name = name[:name.index(": ")]
        meal_names.append(name)
        category = meal[0]
        if category in check_dct:
            check_dct[category] += 1
    for name in meal_names:
        if meal_names.count(name) > 1:
            return False
    for value in check_dct.items():
        if value[1] > 1:
            return False
    return True

def satisfactor(meal_var: tuple[tuple], goal: tuple[float]) -> tuple[tuple]:
    "Counts how meal variation satisfies need"
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
    "Converts result into normal form"
    new_lst = []
    for variant in variants:
        nutrients = []
        for inx, value in enumerate(variant[2]):
            acc_val = goal[inx]-value
            nutrients.append(acc_val)
        new_lst.append((variant[0], variant[1], tuple(nutrients)))
    return new_lst

def calculator_func(choicen_meals: List[str], nutrition: tuple[float],
        settings: dict, maxim: int, amount: int) -> List[tuple]:
    "Main function"
    needed_meals = meal_getter(choicen_meals)
    worked_meals = rebuilder(needed_meals)
    all_meals = portioner(worked_meals, settings["portions"])
    variants = variator(all_meals, nutrition, settings["unrepeatable meals"], maxim, amount)
    final_vars = conclusioner(variants, nutrition)
    return sorted(final_vars, key = lambda x: x[1])
