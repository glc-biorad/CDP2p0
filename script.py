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

    temp = 90
    t = 180
    print(f"Working on temperature set to {temp} C for {t} seconds.")
    m.change_temperature(address, temp, True)
    time.sleep(t)

    for i in range(40):
        temp = 93
        t = 40
        print(f"Working on step {i} with temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        time.sleep(t)
        temp = 55
        t = 80
        print(f"Working on step {i} with temperature set to {temp} C for {t} seconds.")
        m.change_temperature(address, temp, True)
        time.sleep(t)

    target_temp = 30
    m.change_temperature(address, target_temp, True)
    print('dONe')