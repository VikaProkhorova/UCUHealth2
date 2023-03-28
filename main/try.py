from datetime import datetime


obj_2 = datetime.date(datetime.utcnow())
obj_3 = datetime(*tuple(map(int, datetime.utcnow().strftime('%Y-%m-%d').split('-'))))
print(obj_3)

x = 124
print(round(x, -1))

x = ('Шарлотка з яблуком, порція - 1', 'Капустяні деруни, порція - 2', 'Баклажани запечені з сиром, порція - 0.5', 'Баклажани тушковані з грибами, порція - 0.5')
print(str(x)[1:-1])