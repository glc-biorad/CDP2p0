
# Version: Test
import time
import pythonnet
from pythonnet import load

try:
    load("coreclr")
except:
    print("Cannot load coreclr")


from api.util.controller import Controller
from api.reader.reader import Reader
from api.upper_gantry.upper_gantry import UpperGantry
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.reader.meerstetter.meerstetter import Meerstetter
from api.util.utils import delay
from api.util.log import Log

import time

def tc():
    c = Controller('COM8', 57600, dont_use_fast_api=True, timeout=1)
    m = Meerstetter()
    m.connect_to_opened_port(c)

    m.change_temperature(2,37)
    m.change_temperature(3,37)
    m.change_temperature(4,37)
    delay(45*60)

    m.change_temperature(2,93)
    m.change_temperature(3,94)
    m.change_temperature(4,95)
    delay(600)
    print(m.get_temperature(4))

    cycles = 45
    for cycle in range(cycles):
        print(f"cycle: {cycle+1}")
        m.change_temperature(2,58)
        m.change_temperature(3,58)
        m.change_temperature(4,60)
        print(m.get_temperature(4))
        delay(100)
        
        m.change_temperature(2,98)
        m.change_temperature(3,97)
        m.change_temperature(4,99)
        print(m.get_temperature(4))
        delay(50)


    m.change_temperature(2,57)
    m.change_temperature(3,57)
    m.change_temperature(4,61)
    print(m.get_temperature(4))
    delay(100)

    m.change_temperature(2,72)
    m.change_temperature(3,72)
    m.change_temperature(4,72)
    print(m.get_temperature(4))
    delay(15*60)

    m.change_temperature(2,93)
    m.change_temperature(3,94)
    m.change_temperature(4,95)
    delay(600)
    print(m.get_temperature(4))

    m.change_temperature(2,8)
    m.change_temperature(3,8)
    m.change_temperature(4,8)
    delay(1800)
    print(m.get_temperature(4))

    m.change_temperature(2,18)
    m.change_temperature(3,18)
    m.change_temperature(4,18)
    print(m.get_temperature(4))

if __name__ == '__main__':
    tc()

