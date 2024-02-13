
# Version: Test
import os.path as osp
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
from api.reader import instrument_interface
from api.util.server import Server
from gui.controllers.chipscanner_controller import StartScan
from gui.util.utils import import_config_file, get_unit_name
import tifffile


import time
default_exposure = {'bf':1000, 'alexa405':200000, 'fam':400000, 'hex':999999,
    'atto':999999,'cy5':999999, 'cy55':999999, }

def acquire_image(channel, ins_intf, cycle):
    fdir = osp.join('E:/', 'AdvTechImagingData', 'continuous_imaging')
    fpath = osp.join(fdir, '{0}_cycle{1}.tif'.format(channel, cycle))
    ins_intf.moveFilterWheel(channel)
    ins_intf.setExposureTimeMicroseconds(default_exposure[channel])
    ins_intf.turnOnLED(channel)
    img = ins_intf.captureImage()
    ins_intf.turnOffLED(channel)
    tifffile.imwrite(fpath, img)

def tc():
    c = Controller('COM7', 57600, dont_use_fast_api=True, timeout=1)
    m = Meerstetter()
    m.connect_to_opened_port(c)
    heaterA = 1
    heaterB = 2
    heaterC = 3
    heaterD = 4

    ins_intf = instrument_interface.Connection_Interface()
    channels_to_image = ('fam', 'hex', 'cy5')

    for channel in channels_to_image:
            acquire_image(channel, ins_intf, '0000')

   # m.change_temperature(2,37)
    #m.change_temperature(3,37)
    #m.change_temperature(4,37)
    #delay(45*60)

    #m.change_temperature(2,95)
    m.change_temperature(3,94)
    m.change_temperature(4,95)
    delay(200)
    print(m.get_temperature(4))

    cycles = 45
    for cycle in range(cycles):
        print(f"cycle: {cycle+1}")
        for channel in channels_to_image:
            acquire_image(channel, ins_intf, cycle)
        #m.change_temperature(2,62)
        m.change_temperature(3,58)
        m.change_temperature(4,60)
        print(m.get_temperature(4))
        delay(100)
        
        #m.change_temperature(2,98)
        m.change_temperature(3,97)
        m.change_temperature(4,99)
        print(m.get_temperature(4))
        delay(50)


    #m.change_temperature(2,62)
    m.change_temperature(3,57)
    m.change_temperature(4,60)
    print(m.get_temperature(4))
    delay(100)

    #m.change_temperature(2,72)
    #m.change_temperature(3,72)
    #m.change_temperature(4,72)
    #print(m.get_temperature(2))
    #delay(15*60)

    #m.change_temperature(2,95)
    #m.change_temperature(3,94)
    #m.change_temperature(4,95)
    #delay(600)
    #print(m.get_temperature(2))

    #m.change_temperature(2,8)
    #m.change_temperature(3,8)
    #m.change_temperature(4,8)
    #delay(1800)
    #print(m.get_temperature(2))

    #m.change_temperature(2,18)
    m.change_temperature(3,18)
    m.change_temperature(4,18)
    print(m.get_temperature(4))

if __name__ == '__main__':
    tc()

