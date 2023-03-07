from api.upper_gantry.upper_gantry import UpperGantry
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.reader.meerstetter.meerstetter import Meerstetter

import time

if __name__ == '__main__':
    #ug = UpperGantry()
    #ug.get_pipettor().liquid_level_detect()

    m = Meerstetter()
    address = 2
    cutoff = 3
    
    target_temp = 30
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    temp = m.get_temperature(address) 
    
    target_temp = 60
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 300 seconds')
    time.sleep(300)

    target_temp = 40
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 400 seconds')
    time.sleep(400)

    target_temp = 50
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 300 seconds')
    time.sleep(300)

    target_temp = 84
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 500 seconds')
    time.sleep(500)
    
    
    target_temp = 4
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 400 seconds')
    time.sleep(400)

    target_temp = 84
    print(target_temp)
    m.change_temperature(address, target_temp, True)
    print(f'Wait 500 seconds')
    time.sleep(500)
    
    target_temp = 30
    print(target_temp)
    m.change_temperature(address, target_temp, True)