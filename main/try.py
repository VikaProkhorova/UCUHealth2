dct = {3: [(0.3, 'Breakfast'), (0.4, 'Lunch'), (0.3, 'Dinner')],
       4: [(0.25, 'Breakfast'), (0.05, 'Morning Snack'), (0.4, 'Lunch'), (0.3, 'Dinner')],
       5: [(0.25, 'Breakfast'), (0.05, 'Morning Snack'), (0.4, 'Lunch'), (0.05, 'Afternoon Snack'), (0.25, 'Dinner')]}

import json

with open('main/data/daily_distribution.json', 'w', encoding='utf-8') as file:
    json.dump(dct, file, indent=2)
