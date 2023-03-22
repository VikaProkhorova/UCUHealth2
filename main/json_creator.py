"Creates nessasary json"

import json
from typing import List

def opener(path_lst: List[str]) -> json:
    'Creates json with specific category' 
    dct = {}
    total = {}
    for path in path_lst:
        with open(f"Compicraft/data/{path}.csv", "r", encoding="utf-8") as file:
            for line in file:
                line = line.rstrip().split(",")
                dct.update({line[0]: tuple(float(x) for x in line[2:])})
        total.update({path: dct.copy()})
        dct.clear()
    with open("Compicraft/data/meals.json", "w", encoding="utf-8") as file:
        json.dump(total, file, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    lst = ["breakfasts", "second", "salats", "garnirs", "soups"]
    opener(lst)
