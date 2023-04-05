dct = {'unrepeatable meals': ['soups'],
       'portions': {
              'soups': [0.5, 1, 1.5, 2],
              'garnirs': [0.5, 1, 1.5, 2],
              'salads': [1],
              'breakfasts': [1, 2],
              'second meals': [1, 2]
       },
       'max': [0.5, 1, 1.5, 2, 2.5, 3]
       }

import json

with open('main/settings/default.json', 'w', encoding='utf-8') as file:
    json.dump(dct, file, indent=2)
