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

    #m.change_temperature(2,37)
    #m.change_temperature(3,37)
    #m.change_temperature(4,37)
    #delay(2700)

    #m.change_temperature(2,90)
    m.change_temperature(3,90)
    m.change_temperature(4,90)
    delay(600)
    print(m.get_temperature(2))

    cycles = 45
    for cycle in range(cycles):
        print(f"cycle: {cycle+1}")
        #m.change_temperature(2,90)
        m.change_temperature(3,90)
        m.change_temperature(4,90)
        print(m.get_temperature(2))
        delay(40)
        #m.change_temperature(2,58)
        m.change_temperature(3,58)
        m.change_temperature(4,58)
        print(m.get_temperature(2))
        delay(80)

    #m.change_temperature(2,72)
    #m.change_temperature(3,72)
    #m.change_temperature(4,72)
    #print(m.get_temperature(2))
    #delay(900)

    #m.change_temperature(2,90)
    #m.change_temperature(3,90)
    #m.change_temperature(4,90)
    #print(m.get_temperature(2))
    #delay(600)

    #m.change_temperature(2,4)
    #m.change_temperature(3,4)
    #m.change_temperature(4,4)
    #print(m.get_temperature(2))
    #delay(1800)

    #m.change_temperature(2,20)
    m.change_temperature(3,20)
    m.change_temperature(4,20)
    print(m.get_temperature(2))

if __name__ == '__main__':
    tc()

