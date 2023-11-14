
# Version: Test
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
    
    #ug = UpperGantry()
    #ug.dispense(1000, 'low')
    #s = Seyonic()
    address = 3
    print(f"MSRE Digestion")
    m.change_temperature(address, 37, True)
    delay(45, 'minutes')
    print("Enzyme activation")
    m.change_temperature(address, 95, True)
    delay(10, 'minutes')
    for i in range(45):
        print(f"Denaturation: cycle number {i+1}/{45}")
        m.change_temperature(address, 94, True)
        delay(30, 'seconds')
        print(f"Annealing/Extension: cycle number {i+1}/{45}")
        m.change_temperature(address, 60, True)
        delay(1, 'minute')
    print("Signal augmentation")
    m.change_temperature(address, 73, True)
    delay(15, 'minutes')
    print("Enzyme activation")
    m.change_temperature(address, 98, True)
    delay(10, 'minutes')
    print("Hold")
    m.change_temperature(address, 20, True)
    delay(30, 'minutes')
