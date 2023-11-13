''' The goal for this file is to be able to wrap functions to control the
instrument to make execution on CDP2.0 independent of implementation
'''

# pipettor stuff, may want to move this to upper_gantry
#import pythonnet
#from pythonnet import load
#try:
#    load("coreclr")
#except RuntimeError:
#    print('Could not load .net libraries, they were either loaded before, or config is not properly enabled')
# from logger import Logger
import os.path as osp

from api.upper_gantry.upper_gantry import UpperGantry
from api.reader.reader import Reader
#from peltier import Peltier
from gui.util import utils


class Connection_Interface(object):
    def __init__(self,):
        # init reader (xyz motion, imager, filterwheel, )
        self.reader = Reader()
        # init upper gantry (pipettor, xyz1z2 motion)
        # self.upper_gantry = UpperGantry()
        self.upper_gantry = None
        self.config_data = utils.import_config_file(osp.join('config', 'unit_config.json'))
        self.led_colors = [self.config_data['LEDS'][k]['name'] for k in self.config_data['LEDS'].keys()]
        # init prep deck components
        # init thermocyclers


    # upper gantry
    def moveAspirateDispense(self, start, end, asp_vol, disp_vol, **kwargs):
        self.upper_gantry.move_aspirate_dispense(self, start, end,
            asp_vol, disp_vol, use_drip_plate_source=True,
            use_drip_plate_target=True, **kwargs)

    def moveUpperGantry(self, loc, **kwargs):
        ''' would be great if loc could be a string, a number in microsteps, or
        a number in mm'''
        self.upper_gantry.move_pipettor(self, loc, use_drip_plate=True,
            pipette_tip_type=None, use_z=True, **kwargs)

    def homeUpperGantry(self,):
        self.upper_gantry.home_pipettor()

    def turnOnSuction(self,):
        pass

    def turnOffSuction(self,):
        pass

    def aspirate(self, asp_vol, **kwargs):
        self.upper_gantry.aspirate(self, asp_vol, pressure=None,
            pipette_tip_type=None, **kwargs)

    def dispense(self, disp_vol, **kwargs):
        self.upper_gantry.dispense(self, disp_vol, pressure=None,
            pipette_tip_type=None, **kwargs)


    # prep deck stuff
    def setPreampTemp(self, temp):
        pass
    def getPreampTemp(self,):
        pass
    def setHSTemp(self, temp):
        pass
    def getGSTemp(self,):
        pass
    def setHSSpeed(self, rpm):
        pass
    def startHSShake(self,):
        pass
    def stopHSShake(self,):
        pass
    def engageMagSep(self,):
        pass
    def disengageMagSep(self,):
        pass
    def setAuxHTemp(self, num, temp):
        pass
    def getAuxHTemp(self, num):
        pass
    def setChillerTemp(self, temp):
        pass
    def getChillerTemp(self,):
        pass

    # reader stuff
    def homeImager(self,):
        self.reader.home_reader()

    def homeImagerComponent(self, component: str) -> None:
        # is this blocking?? i dont think so
        self.reader.home_component(component=component)

    def moveImager(self, loc):
        ''' would be great if loc could be a string, numbers in microsteps, or
        numbers in mm'''
        print(loc, 'loc instrument interface')
        self.reader.move_reader(loc)

    def moveImagerXY(self, XYloc: list):
        '''move the imager in absolute motor steps, only in XY'''
        x_now, y_now, z_now, fw_now = self.reader.get_position() # x, y, z, fw
        target = [XYloc[0], XYloc[1], z_now, fw_now]
        target = list(map(int, target))
        self.reader.move_reader(target)

    def moveImager_relative(self, loc):
        '''currently loc is in steps, loc is a [x, y, z] list'''
        x_now, y_now, z_now, fw_now = self.reader.get_position() # x, y, z, fw
        # common error: CHECK THAT CHASSIS BOARD RESPONDS
        print(x_now, y_now, z_now, 'printed list')
        msg_parts = ['------------------ERROR----------------',
        'No response from chassis board.',
        'Please confirm with FastAPI web GUI that board is responding.',
        '------------------ERROR----------------']
        msg = '\n'.join(msg_parts)
        for val in [x_now, y_now, z_now, fw_now]:
            assert val != None, msg
        # convert to mm!
        xconv = self.config_data['motor2mm']['x']
        yconv = self.config_data['motor2mm']['y']
        zconv = self.config_data['motor2mm']['z']
        target = [loc[0]*xconv + x_now, loc[1]*yconv + y_now, loc[2]*zconv + z_now, fw_now]
        target = list(map(int, target))
        self.reader.move_reader(target)

    def moveFilterWheel(self, color):
        self.reader.rotate_filter_wheel(color)

    def turnOnLED(self, color, intensity=1000):
        # "accept" both floating point numbers and integers
        if intensity < 1:
            intensity_percent = intensity * 100
        elif intensity == 1:
            intensity_percent = 100
        else:
            intensity_percent = intensity
        self.reader.illumination_only_on(color, intensity_percent)

    def turnOffLED(self, color):
        self.reader.illumination_off(color, use_fast_api=True,)

    def turnOffLEDs(self,):
        self.reader.illumination_offmult()

    def setExposureTimeMicroseconds(self, exp_time_microseconds):
        self.reader.set_exposure(exp_time_microseconds)

    def getExposureTime(self):
        return self.reader.get_exposure()

    def setdPCRTemp(self, num, temp):
        pass

    def getdPCRTemp(self, num, temp):
        pass

    def captureImage(self):
        return self.reader.camcontroller.snap_single()

    def close(self):
        self.reader.close()
        self.upper_gantry.close()
        # close peltier

# the rest of this is for debugging purposes, so that the GUI will run when
# it cannot connect to the instrument hardware
class Dummy_Camera(object):
    def __init__(self):
        self.camera = None

class Dummy_Reader(object):
    def __init__(self):
        self.camcontroller = Dummy_Camera()

    def get_position(self,):
        return -1, -1, -1, -1

class Dummy_Interface(object):
    def __init__(self,):
        self.reader = Dummy_Reader()

    def illumination_offmult(self):
        pass

    def turnOffLED(self, led):
        pass
