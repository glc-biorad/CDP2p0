import time
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
from api.util.log import Log

import time

if __name__ == '__main__':
    m = Meerstetter()
    l = Log('this is where the name goes')
    
    t_start = time.time()
    address = 4
    temp = 95
    t = 180
    l.log(f"Step 1 -- Temp: {temp} C -- Time: {t} s -- Info: Activation/denaturation", time.time() - t_start)
    m.change_temperature(address, temp)
    delay(t)
    for i in range(10):
        print(i + 1)
        temp = 95
        t = 30        
        l.log(f"Step 2 -- Cycle: {i+1} -- Temp: {temp} C -- Time: {t} s -- Info: Denaturation", time.time() - t_start)
        m.change_temperature(address, temp)
        delay(t)
        temp = 60
        t = 60 
        l.log(f"Step 3 -- Cycle: {i+1} -- Temp: {temp} C -- Time: {t} s -- Info: Annealing/Extension", time.time() - t_start)
        m.change_temperature(address, temp)
        delay(t)
    temp = 30
    l.log(f"Step 4 -- Temp: {temp} C -- Time: {t} s -- Info: Final Hold", time.time() - t_start)
    m.change_temperature(address, temp)