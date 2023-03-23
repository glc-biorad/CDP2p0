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
    
    address = 4
    cutoff = 3

    target_temp = 89
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'180 seconds')
    time.sleep(180)

    for i in range(40):
        target_temp = 93
        print(target_temp)
        m.change_temperature(address, target_temp, True)
        print(f'Wait 40 seconds')
        time.sleep(40)
        target_temp = 55
        print(target_temp)
        m.change_temperature(address, target_temp, True)
        print(f'Wait 80 seconds')
        time.sleep(80)

    target_temp = 30
    print(target_temp)
    m.change_temperature(address, target_temp, True)