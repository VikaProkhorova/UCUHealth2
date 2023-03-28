from datetime import datetime


obj_2 = datetime.date(datetime.utcnow())
obj_3 = datetime(*tuple(map(int, datetime.utcnow().strftime('%Y-%m-%d').split('-'))))
print(obj_3)

x = 124
print(round(x, -1))

x = ('Шарлотка з яблуком, порція - 1', 'Капустяні деруни, порція - 2', 'Баклажани запечені з сиром, порція - 0.5', 'Баклажани тушковані з грибами, порція - 0.5')
print(str(x)[1:-1])

def stringer(input_str: str) -> str:
    "Converts str into normal look"
    input_str = input_str.split(", ")
    new_str = ''
    for value in input_str:
        new_str += value[1:-1] + ', '
    return new_str.rstrip()

print(stringer("'Англійський сніданок: порція - 2',"))