import pythonnet
from pythonnet import load

try:
    load("coreclr")
except:
    print("Cannot load coreclr")



from api.reader.reader import Reader
from api.upper_gantry.upper_gantry import UpperGantry
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.reader.meerstetter.meerstetter import Meerstetter
from api.util.utils import delay

import time

if __name__ == '__main__':
    m = Meerstetter()
    
    address = 1
    temp = 38
    t = 45 * 60
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    address = 2
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)

    address = 1
    temp = 92
    t = 10 * 60
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    address = 2
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)

    for i in range(44):
        print(f"Cycle: {i+1}")
        address = 1
        temp = 59
        t = 105
        print(f"Working on temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        address = 2
        print(f"Working on temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        time.sleep(t)
        # 
        address = 1
        temp = 91
        t = 50
        print(f"Working on temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        address = 2
        print(f"Working on temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        time.sleep(t)

    address = 1
    temp = 59
    t = 105
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    address = 2
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)

    address = 1
    temp = 74
    t = 15 * 60
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    address = 2
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)

    address = 1
    temp = 93
    t = 10 * 60
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    address = 2
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)
   
    address = 1
    target_temp = 20
    m.change_temperature(address, target_temp, True)
    address = 2
    m.change_temperature(address, target_temp, True)
    print('dONe')
