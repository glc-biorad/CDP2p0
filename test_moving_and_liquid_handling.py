
# Version: Test
import pythonnet
from pythonnet import load

try:
    load("coreclr")
except:
    print("Cannot load coreclr")

from api.upper_gantry.upper_gantry import UpperGantry
from api.interfaces.fast_api_interface import FastAPIInterface as fapi_interface
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.util.utils import delay

import time
import threading

def lld_thread_func():
    max_poll = 5
    start = time.time()
    action_status = [-26] * 8 # -26 is init value
    while time.time() - start < max_poll:
        for chan in range(1, 9):
            action_status[chan-1] = ug.get_pipettor().client.Get("Action Status",
                                    ug.get_pipettor().pip_addr, chan)
        completed_chan = [1 for asval in action_status if asval == 0]
        if sum(completed_chan) == 16:
            #ug.aspirate(935, 'high', 1000)
            break

if __name__ == '__main__':
    ug = UpperGantry()
    interface = fapi_interface()

    # Move down till LLD
    #ug.dispense(200, 'low')
    #ug.detect_liquid_level()
    #ug.move_relative('down', 250000)
    #ug.move_relative('down', 5000)
    #ug.move_relative('up', 250000)
    #ug.home_pipettor()

    #ug.get_pipettor().safe_aspirate(-200, [1,2,3,4,5,6,7,8])
    #ug.aspirate(300, 'high', 1000)
    #delay(2)
    #ug.dispense(400, 'high')
    #print(ug.get_pipettor().get_pressure())
    #print(ug.get_pipettor().get_actual_aspirate_volume())

    #ug.drip()
    #ug.close_valve()

    #coordinate = [-259500,-630000,-647000,0]
    #dz = -400000
    #x = coordinate[0]
    #y = coordinate[1]
    #z = coordinate[2]
    #dp = coordinate[3]
    #ug.move(x,y,z,dp,tip=1000)
    #interface.pipettor_gantry.axis.move('pipettor_gantry', 3, -947000, 50000, False)
    #if ug.get_pipettor().liquid_level_detect():
    #    ug.aspirate(935, 'high', 1000)
    #    interface.pipettor_gantry.axis.move('pipettor_gantry',3, -647000,190000, False)
    #    ug.dispense(1000,'high')