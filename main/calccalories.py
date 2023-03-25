""" For A
1,2 – сидячий ОЖ; 
1,4 – наявність фізичних навантажень двічі на тиждень;
1,46 – активний ОЖ із наявністю 4-5 тренувань на тиждень; 
1,55 – 5-6 фізичних тренувань на тиждень; 1,63 – щоденні тренування; 
1,72 – щоденні фізичні навантаження не менше 2 разів на день; 
1,9 – важка робота чи інтенсивні фізичні тренування двічі на день.
"""
state = str(input()) #male, female
hight = int(input())
age = int(input())
wase = float(input())
A = float(input()) 
wants=int(input()) #1- lose weight 2- gain weight 3- keep in shape
if state== 'male':
    kilokalories = (10*wase + 6.25* hight - 5* age + 5)*A
else:
    kilokalories = (10*wase + 6.25* hight - 5* age - 161)* A
if wants==1:
    kilokalories*=0.8
elif wants==2:
    kilokalories*=1.2
bilku = round((kilokalories* 0.3)/4, 1)
fats = round((kilokalories*0.2)/9, 1)
vuglevodu = round((kilokalories* 0.5)/4, 1)
print(kilokalories, bilku, vuglevodu, fats)
