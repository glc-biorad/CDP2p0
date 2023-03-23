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
    #interface.pipettor_gantry.axis.home('pipettor_gantry', 1)

    #coordinate = [-259500,-630000,-947000,0]
    coordinate = [-259500,-630000,-647000,0]
    dz = -400000
    x = coordinate[0]
    y = coordinate[1]
    z = coordinate[2]
    dp = coordinate[3]
    ug.move(x,y,z,dp,tip=1000)
    #ug.move_relative('down', dz, 'fast')
    interface.pipettor_gantry.axis.move('pipettor_gantry', 3, -947000, 50000, False)
    if ug.get_pipettor().liquid_level_detect():
        ug.aspirate(935, 'high', 1000)
        interface.pipettor_gantry.axis.move('pipettor_gantry',3, -647000,190000, False)
        ug.dispense(1000,'high')
    #t_start = time.time()
    #lld = False
    #print(ug.get_pipettor()._poll_until_complete(check_for_sum=16))
    #print(ug.get_pipettor().liquid_level_detect())
    #if ug.get_pipettor().liquid_level_detect() == True:
        #ug.aspirate(935, 'high', 1000)
        #interface.pipettor_gantry.axis.move('pipettor_gantry',3, -647000,190000, False)
        #ug.dispense(1000,'high')

    #while ug.get_pipettor().liquid_level_detect() != True:
    #    if time.time() - t_start > 5:
    #        lld = True
    #        break
        #interface.pipettor_gantry.axis.move('pipettor_gantry',3, -647000,190000, False)
    #if lld:
    #    ug.aspirate(935, 'high', 1000)
    #interface.pipettor_gantry.axis.move('pipettor_gantry',3, -647000,190000, False)
    #ug.dispense(1000,'high')