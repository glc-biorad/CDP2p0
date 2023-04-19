'''
'''
from ast import Try
from cmath import e
from re import T
import time
import threading

import api.util.motor 
from api.util.commands import commands
from api.util.coordinate import Coordinate, coordinates

from api.util.chassis import Chassis

from api.upper_gantry.upper_gantry_coordinate import UpperGantryCoordinate, target_to_upper_gantry_coordinate
from api.upper_gantry.upper_gantry_velocity import UpperGantryVelocity

from api.upper_gantry.seyonic.seyonic import Seyonic

from api.upper_gantry.qinstruments.qinstruments import BioShake3000T

from api.util.pipette_tip import PipetteTip

from api.util.log import Log
from api.util.logger import Logger
from api.util.timer import Timer
from api.util.logger_xlsx import LoggerXLSX

from api.util.controller import Controller
from api.interfaces.fast_api_interface import FastAPIInterface

from api.util.utils import wait, check_limit, check_type, microliters_to_seyonic, delay

import os

class UpperGantry(api.util.motor.Motor):
    """ UpperGantry API for the CDP 2.0 Units
    
    Description
    -----------
    API for controlling all aspects of the Upper Gantry including the Seyonic Pipettor, Gantry Motion, Air Valves, 
    Suction Cups, Heater/Shaker, Chiller, and Deck Magnet Motion.
    """
    # Public variables.
    controller = None

    # Private variables.
    __commands = commands['UpperGantry']
    __coordinate = UpperGantryCoordinate()
    __velocity = UpperGantryVelocity()
    __moved = None # bool
    __pipettor = None
    __heater_shaker = None
    __chiller = None
    __mag_separator = None
    __chassis = None
    __location_str = None
    __pipette_tip = PipetteTip()
    __current_volume = 0 # 0.1 microliters
    
    # Private constants (Com Port)
    __COM_PORT = 'COM10'

    # Private constants (Addresses).
    __ADDRESS_PIPETTOR_X = 0x1
    __ADDRESS_PIPETTOR_Y = 0x2
    __ADDRESS_PIPETTOR_Z = 0x3
    __ADDRESS_DRIP_PLATE = 0x4
    __ADDRESS_AIR_MODULE = 0x5
    __ADDRESS_MAG_SEPARATOR = 0x06
    __ADDRESS_TRAY_AB = 0x06
    __ADDRESS_TRAY_CD = 0x07
    __ADDRESS_HEATER_A = 0x08
    __ADDRESS_HEATER_B = 0x09
    __ADDRESS_HEATER_C = 0x09
    __ADDRESS_HEATER_D = 0x08

    # Private constants (IDs for FastAPI).
    __ID = {
        'X': __ADDRESS_PIPETTOR_X,
        'Y': __ADDRESS_PIPETTOR_Y,
        'Z': __ADDRESS_PIPETTOR_Z,
        'Drip Plate': __ADDRESS_DRIP_PLATE,
        'Air Module': __ADDRESS_AIR_MODULE,
        'Mag Separator': __ADDRESS_MAG_SEPARATOR,
        }

    # Private constants (Limits).
    __LIMIT = {
        'X': {
            'max': {
                'current': 1.4,
                'position': __coordinate.get_limit_max()[0],
                'velocity': __velocity.get_limit_max()[0]
                },
            'min': {
                'current': None,
                'position': 0,
                'velocity': __velocity.get_limit_min()[0]
                },
            },
        'Y': {
            'max': {
                'current': 2.8,
                'position': __coordinate.get_limit_max()[1],
                'velocity': __velocity.get_limit_max()[1]
                },
            'min': {
                'current': None,
                'position': 0,
                'velocity': __velocity.get_limit_min()[1]
                },
            },
        'Z': {
            'max': {
                'current': 0.54,
                'position': __coordinate.get_limit_max()[2],
                'velocity': __velocity.get_limit_max()[2]
                },
            'min': {
                'current': None,
                'position': 0,
                'velocity': __velocity.get_limit_min()[2]
                },
            },
        'Drip Plate': {
            'max': {
                'current': 0.24,
                'position': __coordinate.get_limit_max()[3],
                'velocity': __velocity.get_limit_max()[3]
                },
            'min': {
                'current': None,
                'position': 0,
                'velocity': __velocity.get_limit_min()[3]
                },
            },
        'Air Module': {}
        }

    __LIMIT_MAX_CURRENT_X = 1.4 # Amphere
    __LIMIT_MAX_CURRENT_Y = 2.8
    __LIMIT_MAX_CURRENT_Z = 0.54
    __LIMIT_MAX_CURRENT_DRIP_PLATE = 0.24
    __LIMIT_MAX_STEPS_FROM_HOME_X, __LIMIT_MAX_STEPS_FROM_HOME_Y, __LIMIT_MAX_STEPS_FROM_HOME_Z, __LIMIT_MAX_STEPS_FROM_HOME_DRIP_PLATE = __coordinate.get_limit_max() # usteps
    __LIMIT_MAX_VELOCITY_X, __LIMIT_MAX_VELOCITY_Y, __LIMIT_MAX_VELOCITY_Z, __LIMIT_MAX_VELOCITY_DRIP_PLATE = __velocity.get_limit_max() # usteps/sec

    # Private constants (Homing velocity -- hvel).
    __HVEL_X = 20000  # usteps
    __HVEL_Y = 150000
    __HVEL_Z = 80000
    __HVEL_DRIP_PLATE = 150000
    
    # Private constants (Run and Hold currents).
    __HOLD_CURRENT_X = 7
    __HOLD_CURRENT_Y = 14
    __HOLD_CURRENT_Z = 2
    __HOLD_CURRENT_DRIP_PLATE = 1
    __RUN_CURRENT_X = 14
    __RUN_CURRENT_Y = 28
    __RUN_CURRENT_Z = 5
    __RUN_CURRENT_DRIP_PLATE = 1

    # Private constants (dg8).
    __DZ_DG8 = 329000

    # Private constants (FastAPI).
    __FAST_API_INTERFACE = None
    __MODULE_NAME = 'pipettor_gantry'

    def __init__(self, unit=None) -> None:
        super(api.util.motor.Motor, self).__init__()
        logger = Logger(os.path.split(__file__)[1], self.__init__.__name__)
        logger.log('LOG-START', "Initializing the Upper Gantry.")
        timer = Timer(logger)
        timer.start(__file__, __name__)
        self.controller = Controller(com_port=self.__COM_PORT)
        self.__FAST_API_INTERFACE = FastAPIInterface(unit)
        try:
            global __pipettor
            __pipettor = Seyonic()
        except Exception as e:
            print(e)
            try:
                __pipettor.close()
            except Exception as e:
                print(e)
                __pipettor = None
        self.__pipettor = __pipettor
        self.__chassis = Chassis()
        self.__heater_shaker = None #BioShake3000T()
        # Turn on the Relay for the Heater/Shaker nad Chiller.
        #relay_8_info = self.__FAST_API_INTERFACE.chassis.relay.get_relay_info(8)
        #logger.log('MESSAGE', "Turning on Relay 8 - {0}.".format(relay_8_info['description']))
        #self.__FAST_API_INTERFACE.chassis.relay.on(relay_8_info['channel'])
        # Turn on the Motor Relay.
        logger.log('MESSAGE', "Turning on the Motor Relay, this will take 10 seconds.")
        #self.__FAST_API_INTERFACE.chassis.relay.on(7)
        #time.sleep(10)
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.__init__.__name__))
        logger.log('LOG-END', "Initialization of the Upper Gantry is complete.")

        
    def get_fast_api_interface(self):
        return self.__FAST_API_INTERFACE
    def move_pipettor_fast_api_test(self):
        self.__FAST_API_INTERFACE.move_pipettor(1, -100000, 50000)
    def home_pipettor_fast_api_test(self):
        self.__FAST_API_INTERFACE.home_pipettor()
    def get_position_fast_api_test(self, id):
        self.__FAST_API_INTERFACE.get_position(id)

    # Getter Functions: Address
    def get_address_pipettor_x(self):
        return self.__ADDRESS_PIPETTOR_X
    def get_address_pipettor_y(self):
        return self.__ADDRESS_PIPETTOR_Y
    def get_address_pipettor_z(self):
        return self.__ADDRESS_PIPETTOR_Z
    def get_address_drip_plate(self):
        return self.__ADDRESS_DRIP_PLATE
    def get_address_air_module(self):
        return self.__ADDRESS_AIR_MODULE

    # Getter Functions: Limits
    def get_limit_max_current(self):
        return self.__LIMIT_MAX_CURRENT_X, self.__LIMIT_MAX_CURRENT_Y, self.__LIMIT_MAX_CURRENT_Z, self.__LIMIT_MAX_CURRENT_DRIP_PLATE
    def get_limit_max_current_x(self):
        return self.__LIMIT_MAX_CURRENT_X
    def get_limit_max_current_y(self):
        return self.__LIMIT_MAX_CURRENT_Y
    def get_limit_max_current_z(self):
        return self.__LIMIT_MAX_CURRENT_Z
    def get_limit_max_current_drip_plate(self):
        return self.__LIMIT_MAX_CURRENT_DRIP_PLATE
    def get_limit_max_steps_from_home(self):
        return self.___LIMIT_MAX_STEPS_FROM_HOME_X, self.___LIMIT_MAX_STEPS_FROM_HOME_Y, self.___LIMIT_MAX_STEPS_FROM_HOME_Z, self.___LIMIT_MAX_STEPS_FROM_HOME_DRIP_PLATE
    def get_limit_max_steps_from_home_x(self):
        return self.___LIMIT_MAX_STEPS_FROM_HOME_X
    def get_limit_max_steps_from_home_y(self):
        return self.___LIMIT_MAX_STEPS_FROM_HOME_Y
    def get_limit_max_steps_from_home_z(self):
        return self.___LIMIT_MAX_STEPS_FROM_HOME_Z
    def get_limit_max_steps_from_home_drip_plate(self):
        return self.___LIMIT_MAX_STEPS_FROM_HOME_DRIP_PLATE
    def get_limit_max_velocity(self):
        return self.__LIMIT_MAX_VELOCITY_X, self.__LIMIT_MAX_VELOCITY_Y, self.__LIMIT_MAX_VELOCITY_Z, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE
    def get_limit_max_velocity_x(self):
        return self.__LIMIT_MAX_VELOCITY_X
    def get_limit_max_velocity_y(self):
        return self.__LIMIT_MAX_VELOCITY_Y
    def get_limit_max_velocity_z(self):
        return self.__LIMIT_MAX_VELOCITY_Z
    def get_limit_max_velocity_drip_plate(self):
        return self.__LIMIT_MAX_VELOCITY_DRIP_PLATE

    # Getter Functions: hvel
    def get_hvel(self):
        return self.__HVEL_X, self.__HVEL_Y, self.__HVEL_Z, self.__HVEL_DRIP_PLATE
    def get_hvel_x(self):
        return self.__HVEL_X
    def get_hvel_y(self):
        return self.__HVEL_Y
    def get_hvel_z(self):
        return self.__HVEL_Z
    def get_hvel_drip_pltat(self):
        return self.__HVEL_DRIP_PLATE

    # Home Pipettor Method
    def home_pipettor(self):
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.home_pipettor.__name__))
        logger.log('LOG-START', "Homing the Pipettor.")
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.home_pipettor.__name__))
        # Home the Z axis.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.home(self.__MODULE_NAME, self.__ID['Z'])
        # Home the drip plate.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.home(self.__MODULE_NAME, self.__ID['Drip Plate'])
        # Home the Y and X axis.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.home(self.__MODULE_NAME, self.__ID['Y'], block=False)
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.home(self.__MODULE_NAME, self.__ID['X'])
        # Check if y is home
        while self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position(self.__MODULE_NAME, self.__ID['Y']) != 0:
            time.sleep(0.2)
        self.__location_str = 'home'
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Home the Seyonic Pipettor", '{0}.{1}()'.format(__name__, self.home_pipettor.__name__), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.home_pipettor.__name__))
        logger.log('LOG-END', "Pipettor has been homed.")

    # Tip Pickup Method
    def tip_pickup_new(self, x: int, y: int, z: int, tip: int = None) -> None:
        """ Picks up tips based on a coordinate (Needed for using the coordinates model datatable)
        
        Parameters
        ----------
        x (optional): int
            x coordinate for where to eject the tips
        y (optional): int
            y coordinate for where to eject the tips
        z (optional): int
            z coordinate for where to eject the tips
        tip (optional): int
            tip size being picked up (1000, 50, or 200 uL tips)
        """
        self.move(x=x, y=y, z=z, drip_plate=0, tip=tip, ignore_tips=True)
        self.move_relative('up', z, velocity='fast')

    # Tip Eject Method
    def tip_eject_new(self, x: int = None, y: int = None, z: int = None, eject_at_dz: int = 290000) -> None:
        """ Ejects tips based on a coordinate 
        
        Parameters
        ----------
        x (optional): int
            x coordinate for where to eject the tips
        y (optional): int
            y coordinate for where to eject the tips
        z (optional): int
            z coordinate for where to eject the tips
        eject_at_dz (optional): int
            z offset to eject from the original tip pickup coordinate
        """
        if x == None and y == None and z == None:
            self.__eject_tips_now()
            return None
        self.move(x=x, y=y, z=z, drip_plate=0, relative_moves=[0,0,eject_at_dz,0], tip=1000)
        self.__eject_tips_now()
        
    # Tip Pickup Method
    def tip_pickup(self, tray, row, pipette_tip_type=None, slow_z=False):
        # Setup the logger.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_pickup.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_pickup.__name__))
        # Check types.
        if type(tray) == str:
            # Convert the string to an int.
            letters = ['A', 'B', 'C', 'D', 'TIP_TRANSFER_TRAY']
            tray_letter = tray
            assert tray.upper() in letters
            if tray.upper()[0] == 'A':
                tray = 4
            elif tray.upper()[0] == 'B':
                tray = 3
            elif tray.upper()[0] == 'C':
                tray = 2
            elif tray.upper()[0] == 'D':
                tray = 1
            elif tray.upper()[0] == 'T':
                target = 'tip_transfer_tray_row{0}'.format(row)
                self.move_pipettor(target, use_drip_plate=False, pipette_tip_type=pipette_tip_type)
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT['Z']['max']['velocity'])
                self.__location_str = target
                logger.log('LOG-START', "Picking up tips from the Tip Transfer Tray, row {0}".format(row))
                logger_xlsx = LoggerXLSX()
                logger_xlsx.log("Pickup tips from the Tip Transfer Tray Row {0}".format(row), "{0}.{1}(tray='{2}', row={3}, pipette_tip_type={4}, slow_z={5})".format(__name__, self.tip_pickup.__name__, tray, row, pipette_tip_type, slow_z), timer.get_current_elapsed_time())
                timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_pickup.__name__))
                logger.log('LOG-END', "Tips picked up from Tip Transfer Tray, row {0}".format(row))
                return
        check_type(tray, int)
        check_type(row, int)
        # Set the pipette tip type based on the row.
        if row >= 1 and row <= 4:
            if pipette_tip_type == None:
                self.__pipette_tip.change_tip(1000)
        elif row > 4 and row <= 12:
            if pipette_tip_type == None:
                self.__pipette_tip.change_tip(50)
        if pipette_tip_type != None:
            check_type(pipette_tip_type, int)
            self.__pipette_tip.change_tip(pipette_tip_type)
        logger.log('LOG-START', "Picking up tips from tray {0}, row {1}".format(tray_letter, row))
        # Check tray and row exist.
        trays = [1, 2, 3, 4] # Will change to ['A', 'B', 'C', 'D']
        rows = [i for i in range(1, 13, 1)]
        # Create location name.
        target = 'tip_trays_tray{0}_row{1}'.format(tray, row)
        # Use the location name to get the target upper gantry coordinate.
        target_ugc = target_to_upper_gantry_coordinate(target)
        # Move to safe Z1 and Z2 (head and drip tray).
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT['Z']['max']['velocity'])
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT['Drip Plate']['max']['velocity'])
        # Move to Y and X.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_ugc.y, self.__LIMIT['Y']['max']['velocity'], block=False)
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], target_ugc.x, self.__LIMIT['X']['max']['velocity'])
        # Move to Z.
        if slow_z:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z, int(4 * self.__LIMIT['Z']['min']['velocity']))
        else:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z, self.__LIMIT['Z']['max']['velocity'])
        # Move to safe Z.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT['Z']['max']['velocity'])
        self.__location_str = target
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Pickup tips from the Tip Transfer Tray Row {0}".format(row), "{0}.{1}(tray='{2}', row={3}, pipette_tip_type={4}, slow_z={5})".format(__name__, self.tip_pickup.__name__, tray, row, pipette_tip_type, slow_z), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_pickup.__name__))
        logger.log('LOG-END', "{0} uL tips picked up from tray {1}, row {2}".format(self.__pipette_tip.get_type(), tray_letter, row))

    # Convert tray letter (A,B,C,D) to int Method.
    def __get_int_from_ABCD(self, letter):
        # Check type.
        check_type(letter, str)
        # Make sure the given letter is valid.
        letters = ['A', 'B', 'C', 'D', 'AB', 'CD']
        assert letter.upper() in letters
        # Convert.
        if letter == 'D':
            return 1
        elif letter == 'C':
            return 2
        elif letter == 'B':
            return 3
        elif letter == 'A':
            return 4
        elif letter == 'AB':
            return 1
        elif letter == 'CD':
            return 2

    def __get_ABCD_from_int(self, int_value:int) -> str:
        check_type(int_value, int)
        int_values = [1,2,3,4]
        assert int_value in int_values
        if int_value == 1:
            return 'D'
        elif int_value == 2:
            return 'C',
        elif int_value == 3:
            return 'B'
        elif int_value == 4:
            return 'A'

    # Turn On Air Valve Method.
    def turn_on_air_valve(self, number: int) -> None:
        """ Turns on the specified air valve for the chassis
        
        Parameters
        ----------
        number : int
            Valve number to be turned on (1:tip eject,2: aspirate/dispense,3: suction cups)
        """
        numbers = [1,2,3]
        messages = {
            1: "High Pressure Compressor (Tip Eject)",
            2: "Pipettor Vacuum (Aspirate or Dispense)",
            3: "Vacuum Pickup (Suction Cups)",
            }
        assert number in numbers
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_on_air_valve.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_on_air_valve.__name__))
        logger.log('LOG-START', "Turning on Air Valve {0} - {1}".format(number, messages[number]))
        self.__FAST_API_INTERFACE.pipettor_gantry.air_valve.on(number)
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_on_air_valve.__name__))
        logger.log('LOG-END', "Turned on Air Valve {0} - {1}".format(number, messages[number]))


    # Turn Off Air Valve Method.
    def turn_off_air_valve(self, number: int) -> None:
        """ Turns off the specified air valve for the chassis
        
        Parameters
        ----------
        number : int
            Valve number to be turned off (1:tip eject,2: aspirate/dispense,3: suction cups)
        """
        numbers = [1,2,3]
        messages = {
            1: "High Pressure Compressor (Tip Eject)",
            2: "Pipettor Vacuum (Aspirate or Dispense)",
            3: "Vacuum Pickup (Suction Cups)",
            }
        assert number in numbers
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_off_air_valve.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_off_air_valve.__name__))
        logger.log('LOG-START', "Turning off Air Valve {0} - {1}".format(number, messages[number]))
        self.__FAST_API_INTERFACE.pipettor_gantry.air_valve.off(number)
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.turn_off_air_valve.__name__))
        logger.log('LOG-END', "Turned off Air Valve {0} - {1}".format(number, messages[number]))

    # Check For Tips Method.
    def has_tips(self):
        self.__pipettor.test()

    def get_chassis(self):
        return self.__chassis

    def __eject_tips_now(self) -> None:
        """ Eject tips exactly where the pipettor head is currently """
        valve_1_tip_eject = 1
        self.turn_on_air_valve(valve_1_tip_eject)
        self.__chassis.turn_on_control_relay()
        self.__chassis.turn_on_pump()
        time.sleep(1.2)
        self.__chassis.turn_off_pump()
        self.__chassis.turn_off_control_relay()
        self.turn_off_air_valve(valve_1_tip_eject)

    # Tip Eject Method
    def tip_eject(self, tray=None, row=None):
        # Setup the logger.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_eject.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_eject.__name__))
        if tray == None or row == None:
            self.__eject_tips_now()
            return
        # Check types.
        check_type(tray, str)
        check_type(row, int)
        #dz = 190000
        dz = 240000
        if tray.upper()[0] == 'tip_transfer_tray'.upper()[0]:
                target = 'tip_transfer_tray_row{0}'.format(row)
                self.move_pipettor(target, use_drip_plate=False, relative_moves=[0,0,dz,0])
                #self.move_relative('up', 190000, 'fast')
                self.__eject_tips_now()
                logger.log('LOG-END', "Tips ejected in the Tip Transfer Tray, Row {0}".format(row))
                self.__location_str = target + '_up_{0}'.format(dz)
                logger_xlsx = LoggerXLSX()
                logger_xlsx.log("Eject tips in the Tip Transfer Tray Row {0}".format(row), "{0}.{1}(tray='{2}', row={3})".format(__name__, self.tip_eject.__name__, tray, row), timer.get_current_elapsed_time())
                timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_eject.__name__))
                return
        # Make sure the tray and row are valid.
        logger.log('LOG-START', "Tip eject in tray {0}, row {1}".format(tray, row))
        trays = ['A', 'B', 'C', 'D']
        rows = [i+1 for i in range(12)]
        assert tray.upper() in trays
        assert row in rows
        # Make sure that spot is empty from this run.
        # Generate the target string.
        tray_int = self.__get_int_from_ABCD(tray)
        target_str = 'tip_trays_tray{0}_row{1}'.format(tray_int, row)
        # Move to the target location.
        self.move_pipettor(target_str, use_drip_plate=False, relative_moves=[0,0,dz,0])
        #self.move_relative('up', dz, 'fast')
        self.__eject_tips_now()
        self.__location_str = target_str + '_up_{0}'.format(dz)
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Eject tips in the Tip Transfer Tray Row {0}".format(row), "{0}.{1}(tray='{2}', row={3})".format(__name__, self.tip_eject.__name__, tray, row), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.tip_eject.__name__))
        logger.log('LOG-END', "Tips ejected in tray {0}, row {1}".format(tray, row))

    # test
    def move_pipettor_test(self, target, use_drip_plate=True, pipette_tip_type=None):
        # Check types.
        if pipette_tip_type != None:
            check_type(pipette_tip_type, int)
        else:
            pipette_tip_type = self.__pipette_tip.get_type()
        self.__pipette_tip.change_tip(pipette_tip_type)
        # Convert the target to an UpperGantryCoordinate.
        target_ugc = target_to_upper_gantry_coordinate(target)
        # Check if a change in z1 and z2 are needed for the pipette tips.
        if self.__check_for_z_axes_change_needed(target):
            target_ugc.z = self.__pipette_tip.get_z1(target_ugc)
            target_ugc.drip_plate = self.__pipette_tip.get_z2(target_ugc)
        # Move the upper gantry along Z to clear the prep deck.
        #if self.get_position_from_response(self.__ADDRESS_PIPETTOR_Z) != 0:
        #self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT_MAX_VELOCITY_Z)
        # Move the upper gantry along X and Y to the target location.
        print("Y")
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_ugc.y, self.__LIMIT_MAX_VELOCITY_Y, block=True)
        print("X")
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], target_ugc.x, self.__LIMIT_MAX_VELOCITY_X, block=True)
        # Move the upper gantry along Z to mount the tips on the pipettor mandrels.
        print("Z")
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z, self.__LIMIT_MAX_VELOCITY_Z, block=True)

    def __get_location_name_from_coordinate_name(self, coordinate_name: str) -> str:
        location_name = ''
        # Replace all _ with spaces and capitolize the first letter of each word.
        name = coordinate_name.replace('_', ' ').title()
        # Change the number to a letter after the tray.
        words = name.split(' ')
        for word in words:
            if 'Tray' in word:
                try:
                    tray_int = int(word[-1])
                    tray_str = self.__get_ABCD_from_int(tray_int)
                    new_word = "Tray {0}".format(tray_str)
                    location_name = location_name + new_word + ' '
                except:
                    location_name = location_name + word + ' '
                    continue
            elif 'Row' in word:
                location_name = location_name + "Row {0}".format(word[-1]) + ' '
            else:
                location_name = location_name + word + ' '
        return location_name[:-1]

    def jet(
        self,
        z: int,
        v_z: int,
        volume: int
    ) -> None:
        """
        """
        thread = threading.Thread(target=self.__pipettor.liquid_level_detect)
        # Move down until LLD 
        # Move up by a fixed amount based on volume 

    def stop_motion(self) -> None:
        """
        Stop motion of pipettor where it currently is
        """
        x,y,z,dp = self.get_position()
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move('pipettor_gantry', id=3, position=z, block=False, velocity=self.__LIMIT['Z']['max']['velocity'])
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move('pipettor_gantry', id=4, position=dp, block=False, velocity=self.__LIMIT['Drip Plate']['max']['velocity'])
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move('pipettor_gantry', id=2, position=y, block=False, velocity=self.__LIMIT['Y']['max']['velocity'])
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move('pipettor_gantry', id=1, position=x, block=False, velocity=self.__LIMIT['X']['max']['velocity'])

    def detect_liquid_level(self, max_z_range: int = 350000, z_velocity: int = 30000):
        """
        Move down in z (bound by a max downward relative z motion)
        """
        # Setup the seyonic logger for lld
        seyonic_log = Log('status', './logs/seyonic/')
        seyonic_log.seyonic_log_header()
        # Get current z position
        initial_z = self.get_position_from_axis('Z')
        # Set the pressure to 20 mbar
        self.__pipettor.set_pressure(pressure=20, direction=1)
        time.sleep(2) # delay to equalize pressure
        # Set the action mode to LLD
        self.__pipettor.set_LLD_action_mode()
        # Trigger LLD
        self.__pipettor.trigger_LLD()
        lld_clock_start = time.time()
        self.status_log.seyonic_log('LLD', "Trigger", 20, [4, 4, 4, 4, 4, 4, 4, 4], time.time() - lld_clock_start)
        # Start timing
        t = time.time()
        while time.time() - t <= 1:
            print(self.__pipettor.get_status())
        # Start the move
        self.move_relative('down', value=max_z_range, velocity=z_velocity, block=False)
        # Look for LLD success status
        t = time.time()
        while self.get_position_from_axis('Z') >= initial_z - max_z_range:
            action_status = self.__pipettor.get_status()
            #print(action_status)
            self.status_log.seyonic_log('LLD', "In Progress", 
                                 20, 
                                 [action_status[0],
                                 action_status[1],
                                 action_status[2],
                                 action_status[3],
                                 action_status[4],
                                 action_status[5],
                                 action_status[6],
                                 action_status[7]],
                                 time.time() - lld_clock_start
            )
            if 2 in action_status:
                self.stop_motion()
                self.status_log.seyonic_log('LLD', "Completed", 
                                 20, 
                                 [action_status[0],
                                 action_status[1],
                                 action_status[2],
                                 action_status[3],
                                 action_status[4],
                                 action_status[5],
                                 action_status[6],
                                 action_status[7]],
                                 time.time() - lld_clock_start
                )
                break
        self.__pipettor.set_pressure(pressure=0, direction=1)
        time.sleep(2)

    def move(
        self,
        x: int,
        y: int,
        z: int,
        drip_plate: int,
        use_z: bool = True,
        slow_z: bool = False,
        use_drip_plate: bool = False,
        tip: int = None,
        relative_moves: list = [0,0,0,0],
        max_drip_plate: int = -1198000,
        ignore_tips: bool = False
       ) -> None:
        """ Moves the pipettor head based on the coordinates

        Parameters
        ----------
        x: int
            Where to move the pipettor head along the x-axis
        y: int
            Where to move the pipettor head along the y-axis
        z: int
            Where to move the pipettor head along the z-axis
        drip_plate: int
            Where to move the pipettor head along the z2-axis
        use_z: bool
            Specifies whether or not to use z motion (i.e. whether or not
            to stay homed in z (False) or move down to the specified z
            coordinate (True))
        slow_z: bool
            Specifies if the move is to use a slow velocity while moving
            down along the z-axis
        use_drip_plate: bool
            Specifies whether or not to use the drip plate from the beginning of the move
            to the end of the move (i.e. lower the drip plate fully, then move the drip
            plate to the drip plate coordinate of the specified value)
        tip: int
            Type of tip on the pipettor head at the end of the move (1000, 50, or 200), this
            allows us to determine if a z offset is needed for getting to the correct height 
            of the coordinate
        """
        # Modify the coordinate based on the relative moves
        print(f"z: {z} -> {z + relative_moves[2]}")
        x = x + relative_moves[0]
        y = y + relative_moves[1]
        z = z + relative_moves[2]
        drip_plate = drip_plate + relative_moves[3]
        if drip_plate < max_drip_plate:
            drip_plate = max_drip_plate
        # Offset z and the drip plate for the tip
        if ignore_tips == True:
            z = z
        else:
            if tip == 50 or tip == 200:
                z = z - 305000
            elif tip == None:
                z = 0
        # Home Z and the drip plate
        self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 3, 0, 800000, True, True)
        # Check if the user wants to use the drip plate
        if use_drip_plate:
            # Move the drip plate
            self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, max_drip_plate, 2500000, True, True)
        else:
            self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, 0, 2500000, True, True)
        # Check if we need to block y
        _x = self.get_position_from_axis('X')
        if _x == x:
            block_y = True
        else:
            block_y = False
        # Move to the Y and X coordiantes
        self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 2, y, 3200000, block_y, True)
        self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 1, x, 300000, True, True)
        # Check if the user wants to use the drip plate
        if use_drip_plate:
            # Move the drip plate
            self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, drip_plate, 2500000, True, True)
        # Wait till x and y are achieved
        _x = self.get_position_from_axis('X')
        _y = self.get_position_from_axis('Y')
        while _x != x and _y != y:
            _x = self.get_position_from_axis('X')
            _y = self.get_position_from_axis('Y')
        # Move to the Z height
        self.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 3, z, 800000, True, True)



    def move_pipettor_new(self, 
                          consumable:str, tray=None, row=None, 
                          use_z=True, use_drip_plate=True,
                          slow_x=False, slow_y=False, slow_z=False, slow_drip_plate=False,
                          pipette_tip_type=None,
                          relative_moves=[0,0,0,0]):
        # Make sure the parameters are valid.
        if tray != None:
            check_type(tray, str)
        if row != None:
            check_type(row, int)
        location_names = [
            'home',
            'dna quant strip',
            'tip tray', 'tip trays',
            'reagent cartridge',
            'sample loading', 'sample rack', 'sample loading rack',
            'aux heater', 'rna heater', 'auxilary heater',
            'heater shaker', 'heater/shaker',
            'mag separator',
            'chiller',
            'pre-amp thermocycler', 'pcr thermocycler',
            'lid tray',
            'tip transfer tray',
            'assay strip',
            'tray cd nipt',
            'tray cd ff',
            'tray cd quant',
            'dg8 1000',
            'dg8 0100',
            'dg8 0010',
            'dg8 0001',
            ]
        location_name = consumable
        location_name.replace('_', ' ')
        assert location_name.lower() in location_names
        # Setup the loggers and Timers.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor_new.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor_new.__name__))
        if pipette_tip_type != None:
            check_type(pipette_tip_type, int)
        else:
            pipette_tip_type = self.__pipette_tip.get_type()
        # Set the tip type.
        self.__pipette_tip.change_tip(pipette_tip_type)
        # Get the relative moves.
        relative_x = relative_moves[0]
        relative_y = relative_moves[1]
        relative_z = relative_moves[2]
        relative_dp = relative_moves[3]
        for i in range(len(relative_moves)):
            if int(relative_moves[i]) != 0:
                logger.log('MESSAGE', "During the move to {0} a relative move of {1} usteps along the {2}-axis is being used.".format(self.__get_full_location_name(location_name, tray, row), relative_moves[i], self.__int_to_axis_str(i+1)))
        # Convert the target to an UpperGantryCoordinate.
        target = self.__convert_location_name(location_name, tray, row)
        target_ugc = target_to_upper_gantry_coordinate(target)
        # Check if a change in z1 and z2 are needed for the pipette tips.
        if self.__check_for_z_axes_change_needed(target):
            target_ugc.z = self.__pipette_tip.get_z1(target_ugc)
            target_ugc.drip_plate = self.__pipette_tip.get_z2(target_ugc)
        if self.__pipette_tip.get_type() != None:
            logger.log('LOG-START', "Moving pipettor to {0} with {1} uL tips.".format(self.__get_full_location_name(location_name, tray, row), self.__pipette_tip.get_type()))
        else:
            logger.log('LOG-START', "Moving pipettor to {0} with no tips.".format(self.__get_full_location_name(location_name, tray, row)))
        # Move the upper gantry along Z to clear the prep deck.
        #if self.get_position_from_response(self.__ADDRESS_PIPETTOR_Z) != 0:
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT_MAX_VELOCITY_Z)
        # Lower the drip plate to prevent contamination.
        if use_drip_plate:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], self.__LIMIT_MAX_STEPS_FROM_HOME_DRIP_PLATE, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
        else:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
        # Move the upper gantry along X and Y to the target location.
        if slow_y:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_ugc.y + relative_y, int(4 * self.__HVEL_Y), block=False)
        else:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_ugc.y + relative_y, self.__LIMIT_MAX_VELOCITY_Y, block=False)
        if slow_x:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], target_ugc.x + relative_x, int(4 * self.__HVEL_X))
        else:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], target_ugc.x + relative_x, self.__LIMIT_MAX_VELOCITY_X)
        # Move the upper gantry along Z to mount the tips on the pipettor mandrels.
        if use_drip_plate:
            logger.log('MESSAGE', "The drip plate is in use.")
            if type(target) == str:
                if target[0:3].lower() == 'mag':
                    self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
                else:
                    self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], target_ugc.drip_plate, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)            
            else:
                logger.log('MESSAGE', "The drip plate is not in use.")
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], target_ugc.drip_plate, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)            
            #time.sleep(0.2)
        if use_z:
            if slow_z:
                logger.log('MESSAGE', "Moving the pipettor slowly in Z (4 * homing velocity - this is best used for calibration/testing).")
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z + relative_z, int(4 * self.__HVEL_Z), block=True)
            else:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z + relative_z, self.__LIMIT_MAX_VELOCITY_Z, block=True)
        else:
            logger.log('MESSAGE', "The use_z parameter has been set to False, so the Z axis has been homed.")
            target = target + '_z_homed'
        self.__location_str = target
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Move the Seyonic Pipettor to {0}".format(location_name), self.move_pipettor_new.__name__, timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor_new.__name__))
        logger.log('LOG-END', "Moved pipettor to {0}.".format(self.__get_full_location_name(location_name, tray, row)))

    def __convert_location_name(self, location_name:str, tray=None, row=None) -> str:
        location_names = [
            'Home',
            'DNA Quant Strip',
            'Tip Tray','Tip Trays'
            'Reagent Cartridge',
            'Sample Loading', 'Sample Rack', 'Sample Loading Rack',
            'Aux Heater', 'RNA Heater', 'Auxilary Heater',
            'Heater Shaker', 'Heater/Shaker',
            'Mag Separator',
            'Chiller',
            'Pre-Amp Thermocycler', 'PCR Thermocycler',
            'Lid Tray',
            'Tip Transfer Tray',
            'Assay Strip',
            'Tray CD NIPT', 
            'Tray CD FF', 
            'Tray CD Quant', 
            'DG8 1000',
            'DG8 0100',
            'DG8 0010',
            'DG8 0001',
            ]
        old_location_names = [
            'home',
            'dna_quant_stip',
            'tip_trays',
            'reagent_cartridge',
            'sample_loading',
            'aux_heater',
            'heater_shaker',
            'mag_separator',
            'chiller',
            'pcr_thermocycler',
            'lid_tray',
            'tip_transfer_tray',
            'assay_strip',
            'tray_out_location_nipt',
            'tray_out_location_quant',
            'tray_out_location_ff',
            'dg8_1000',
            'dg8_0100',
            'dg8_0010',
            'dg8_0001',
            ]
        trays = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
        if tray != None:
            assert tray.upper() in trays
        # Convert any of the location names to the old location name format submodule_tray(int)_row(int).
        old_location_name = location_name.lower().replace(' ', '_').replace('/', '_').replace('-', '_')
        if old_location_name not in old_location_names:
            # Look for special cases.
            if old_location_name == 'sample_rack' or old_location_name == 'sample_loading_rack':
                old_location_name = 'sample_loading'
            elif old_location_name == 'rna_heater' or old_location_name == 'auxiliary_heater':
                old_location_name = 'aux_heater'
            elif old_location_name == 'pre_amp_thermocycler':
                old_location_name = 'pcr_thermocycler'
            elif old_location_name == 'tip_tray':
                old_location_name = 'tip_trays'
            elif old_location_name == 'tray_cd_nipt' or old_location_name == 'tray_cd_ff' or old_location_name == 'tray_cd_quant':
                assay = old_location_name.split('_')[-1]
                old_location_name = 'tray_out_location'
        # Construct the old location name fully.
        if tray != None:
            if old_location_name == 'tray_out_location':
                old_location_name = old_location_name + f'_{assay}_{tray}'
            else:
                old_location_name = old_location_name + '_tray{0}'.format(trays[tray.upper()])
        if row != None:
            if old_location_name == 'dg8_1000' or old_location_name == 'dg8_0100' or old_location_name == 'dg8_0010' or old_location_name == 'dg8_0001':
                if row == 1:
                    old_location_name = old_location_name + f'_100'
                elif row == 2:
                    old_location_name = old_location_name + f'_010'
                elif row == 3:
                    old_location_name = old_location_name + f'_001'
            else:
                old_location_name = old_location_name + '_row{0}'.format(row)
        return old_location_name

    def __int_to_axis_str(self, int_value: int) -> str:
        conv = {1: 'X', 2: 'Y', 3: 'Z', 4: 'Drip Plate'}
        assert int_value in conv
        return conv[int_value]

    def __get_full_location_name(self, location_name: str, tray=None, row=None) -> str:
        # Title the location name.
        location_str = location_name.title() + ' '
        # Setup the tray portion
        if tray == None:
            tray_str = ''
        else:
            tray_str = "Tray {0} ".format(tray.upper())
        # Setup the row portion.
        if row == None:
            row_str = ''
        else:
            row_str = "Row {0} ".format(row)
        # Setup the full string.
        return '{0}{1}{2}'.format(location_str, tray_str, row_str)[:-1]

    # Move Pipettor Method
    def move_pipettor(self, target, use_drip_plate=True, pipette_tip_type=None, use_z=True, slow_z=False, relative_moves=[0,0,0,0]):
        # Setup the logger.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor.__name__))
        if type(target) == str:
            location_name = self.__get_location_name_from_coordinate_name(target)
        if target == 'home' or target == [0,0,0,0] or target == UpperGantryCoordinate(0,0,0,0):
            if use_drip_plate == False:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
        relative_x = relative_moves[0]
        relative_y = relative_moves[1]
        relative_z = relative_moves[2]
        relative_dp = relative_moves[3]
        logger.log('MESSAGE', "During this move the following relative moves are being used dx = {0}, dy = {1}, dz1 = {2}, dz2 = {3}".format(relative_x, relative_y, relative_z, relative_dp))
        # Check types.
        if pipette_tip_type != None:
            check_type(pipette_tip_type, int)
        else:
            pipette_tip_type = self.__pipette_tip.get_type()
        self.__pipette_tip.change_tip(pipette_tip_type)
        # Convert the target to an UpperGantryCoordinate.
        target_ugc = target_to_upper_gantry_coordinate(target)
        # Check if a change in z1 and z2 are needed for the pipette tips.
        if self.__check_for_z_axes_change_needed(target):
            target_ugc.z = self.__pipette_tip.get_z1(target_ugc)
            target_ugc.drip_plate = self.__pipette_tip.get_z2(target_ugc)
        logger.log('LOG-START', "Moving the pipettor to {0} with {1} uL tips.".format(target, self.__pipette_tip.get_type()))
        # Move the upper gantry along Z to clear the prep deck.
        #if self.get_position_from_response(self.__ADDRESS_PIPETTOR_Z) != 0:
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], 0, self.__LIMIT_MAX_VELOCITY_Z)
        # Lower the drip plate to prevent contamination.
        if use_drip_plate:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], self.__LIMIT_MAX_STEPS_FROM_HOME_DRIP_PLATE, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
        else:
            self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
        # Move the upper gantry along X and Y to the target location.
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_ugc.y + relative_y, self.__LIMIT_MAX_VELOCITY_Y, block=False)
        self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], target_ugc.x + relative_x, self.__LIMIT_MAX_VELOCITY_X)
        # Move the upper gantry along Z to mount the tips on the pipettor mandrels.
        if use_drip_plate:
            logger.log('MESSAGE', "The drip plate is in use.")
            if type(target) == str:
                if target[0:3].lower() == 'mag':
                    self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], 0, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)
                else:
                    self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], target_ugc.drip_plate, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)            
            else:
                logger.log('MESSAGE', "The drip plate is not in use.")
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], target_ugc.drip_plate, self.__LIMIT_MAX_VELOCITY_DRIP_PLATE)            
            time.sleep(0.2)
        if use_z:
            if slow_z:
                logger.log('MESSAGE', "Moving the pipettor slowly in Z (4 * homing velocity - this is best used for calibration/testing).")
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z + relative_z, int(4 * self.__HVEL_Z), block=True)
            else:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_ugc.z + relative_z, self.__LIMIT_MAX_VELOCITY_Z, block=True)
        else:
            logger.log('MESSAGE', "The use_z parameter has been set to False, so the Z axis has been homed.")
            target = target + '_z_homed'
        self.__location_str = target
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Move the Seyonic Pipettor to {0}".format(location_name), "{0}.{1}(target='{2}', use_drip_plate={3}, pipette_tip_type={4}, use_z={5}, slow_z={6}, relative_moves={7})".format(__name__, self.move_pipettor.__name__, target, use_drip_plate, pipette_tip_type, use_z, slow_z, relative_moves), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_pipettor.__name__))
        logger.log('LOG-END', "Moved pipettor to {0}.".format(target))

    # Move Aspirate Dispense Method
    def move_aspirate_dispense(self, source, target, aspirate_vol, dispense_vol, use_drip_plate_source=True, use_drip_plate_target=True):
        # Convert from microliters to seyonic units
        aspirate_vol = microliters_to_seyonic(aspirate_vol)
        dispense_vol = microliters_to_seyonic(dispense_vol)
        # Move the upper gantry to the source.
        if self.__location_str != source:
            self.move_pipettor(source, use_drip_plate=use_drip_plate_source)
        # Turn on the valve 2.
        self.__chassis.relayon(channel=2-1)
        # Set the pipettor aspirate volume
        self.__pipettor.set_aspirate_volumes(aspirate_vol)
        # Set the pipettor aspiration residual volume
        # Set the pipettor dispense volume
        self.__pipettor.set_dispense_volumes(dispense_vol)
        # Set the pipettor dispense residual volume
        # Set the pipettor mode to ASPIRATE <---- Taken care off in aspirate method
        # Trigger pipettor action
        self.__pipettor.aspirate()
        # Delay to allow the pipettor to complete this action <---- Taken care off in aspirate method
        # Poll pipettor to check action completion status <---- Taken care off in aspirate method
        # Move the upper gantry along Z to clear the prep deck.
        time.sleep(2)
        # Move to the target.
        self.move_pipettor(target, use_drip_plate=use_drip_plate_target)
        self.__location_str = target
        # Set the pipettor mode to DISPENSE
        self.__pipettor.dispense()
        time.sleep(2)
        self.__chassis.relayoff(channel=2-1)
        # Trigger the pipettor action <---- Taken care off in dispense method
        # Delay to allow pipettor to complete action <---- Taken care off in dispense method
        # Poll the pipettor to check the action completion status <---- Taken care off in dispense method

    # Check for tipless contact Method.
    def check_for_tipless_contact(self):
        target_ugc = UpperGantryCoordinate(-258000, -205000, -1524300, 0) # About 20k off in z for contact?
        if self.__pipette_tip.get_type() == None:
            self.move_pipettor_deprecated(target_ugc, use_drip_plate=False)
            # Move slowly to a relative position downward.
            delta = 12000
            self.move_relative('down', delta)
            # Check if we reached that position in z.
            z_expected = -1524300-delta
            self.qpos(0x03)
            time.sleep(1)
            x,y,z_actual,dp = self.get_position()
            if abs(z_expected - z_actual) != 0:
                print("HERE")
            # Set a negative pressure when in contact with the surface.
            #self.__pipettor.set_aspirate_volumes(1000)
            #self.__pipettor.aspirate(pressure=-120)
            # Poll the action status.
        else:
            logger = Logger(__file__, self.check_for_tipless_contact.__name__)
            logger.log('WARNING', "Unit believes it has {0} microliter tips on currently.".format(self.__pipette_tip.get_type()))

    def drip(self):
        self.turn_on_air_valve(2)
        self.__pipettor.open_valve()

    def close_valve(self):
        self.turn_off_air_valve(2)
        self.__pipettor.close_valve()

    # Aspirate Method.
    def aspirate(self, aspirate_vol, pressure=None, pipette_tip_type=None):
        # Pressures:
        pressures = [None, 'default', 'low', 'high', 'half', 'lowest', 'highest']
        # Check type.
        check_type(aspirate_vol, int)
        if pressure != None:
            pressure = pressure.lower()
            check_type(pressure, str)
            assert pressure in pressures
            # Get the pressure value.
            if pressure == 'default':
                pressure = None
            elif pressure == 'low':
                pressure = -100
            elif pressure == 'lowest':
                pressure = -15
            elif pressure == 'highest':
                pressure = -300
            elif pressure == 'high':
                pressure = -300
            elif pressure == 'half':
                print(self.__pipettor.max_pressure)
                pressure = 0.5 * (self.__pipettor.max_pressure - self.__pipettor.min_pressure)
        # Make sure the pressure is valid.
        # Setup logger.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.aspirate.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.aspirate.__name__))
        logger.log('LOG-START', "Aspirating {0} microliters using a {1} microliter tip at {2} with {3} pressure.".format(aspirate_vol, self.__pipette_tip.get_type(), self.__location_str, pressure))
        # Convert from microliters to seyonic units
        vol = aspirate_vol
        aspirate_vol = microliters_to_seyonic(aspirate_vol)
        # Check limit.
        if pipette_tip_type != None:
            self.__pipette_tip.change_tip(pipette_tip_type)
        limit = self.__pipette_tip.get_type() * 10 + 10
        if limit != None:
            if check_limit(aspirate_vol, limit, '<='):
                #time.sleep(1)
                # Set the current volume in the Seyonic Pipettor.
                self.__current_volume = self.__current_volume + aspirate_vol
                # Check the aspiration limit.
                check_limit(self.__current_volume, limit, '<=')
                # Turn on the valve 2.
                self.turn_on_air_valve(2)
                # Set the pipettor aspirate volume
                self.__pipettor.set_aspirate_volumes(aspirate_vol)
                # Trigger pipettor action
                self.__pipettor.aspirate(pressure)
                time.sleep(1)
                self.turn_off_air_valve(2)
                #time.sleep(1)
                logger.log('LOG-END', "Aspiration complete.")
            else:
                logger.log('WARNING', "Would aspirate too much, skipping...")
                logger.log('LOG-END', "Aspiration skipped...")
                #time.sleep(1)
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Aspirate {0} uL".format(vol), "{0}.{1}(aspirate_vol={2}, pressure={3}, pipette_tip_type={4})".format(__name__, self.aspirate.__name__, aspirate_vol, pressure, pipette_tip_type), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.aspirate.__name__))

    # Dispense Method.
    def dispense(self, dispense_vol, pressure=None, turn_off_air_valve=True):
        # Pressures:
        pressures = [None, 'default', 'low', 'high', 'lowest', 'highest', 'very low']
        if type(pressure) == str:
            if pressure.lower() == 'low':
                pressure = 100
            elif pressure.lower() == 'high':
                pressure = 300
            elif pressure.lower() == 'lowest':
                pressure = 15
            elif pressure.lower() == 'highest':
                pressure = 500
        # Check the type.
        check_type(dispense_vol, int)
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.dispense.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.dispense.__name__))
        # Convert from microliters to seyonic units
        vol = dispense_vol
        dispense_vol = microliters_to_seyonic(dispense_vol)
        # Set the current volume of the Seyonic Pipettor.
        self.__current_volume = self.__current_volume - dispense_vol
        if self.__current_volume < 0:
            self.__current_volume = 0
        # Turn on the valve 2.
        self.turn_on_air_valve(2)
        # Set the pipettor dispense volume
        self.__pipettor.set_dispense_volumes(dispense_vol)
        # Set the pipettor mode to DISPENSE
        self.__pipettor.dispense(pressure)
        logger.log('WARNING', "Nima says that turning off the valve while still in the liquid is causing residual solution in the tips.")
        time.sleep(1)
        if turn_off_air_valve:
            self.turn_off_air_valve(2)
            logger.log('WARNING', "Valve 2 (Aspirate/Dispense) was turned off after the dispense.")
        else:
            logger.log('WARNING', "Valve 2 (Aspirate/Dispense) was not turned off after the dispense.")
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Dispense {0} uL".format(vol), "{0}.{1}(dispense_vol={2}, pressure={3}, turn_off_air_valve={4})".format(__name__, self.dispense.__name__, dispense_vol, pressure, turn_off_air_valve), timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.dispense.__name__))
        
    def generate_droplets(self, droplet_type='standard'):
        # Change the timeout for the seyonic controller
        self.__pipettor.change_timeout(200)
        droplet_types = ['standard', 'pico', 'small', 'standard_universal_oil', 'demo', 'st' , 'sm', 'un', 'de', 'pi']
        assert type(droplet_type) == str 
        assert droplet_type.lower()[0:2] in droplet_types
        # Turn on the pump and let it equalize.
        self.__pipettor.set_pressure(pressure=-241, direction=2)
        delay(0.5, 'seconds')
        # Open Valve 2.
        self.turn_on_air_valve(2)
        # Delay.
        delay(0.25, 'seconds')
        # Open Pipettor Valve
        self.__pipettor.open_valve()
        # Get the flow rate.
        flow_rate = min(self.__pipettor.get_flow_rate())
        # Delay.
        time_start = time.time()
        if droplet_type.lower()[0:2] == 'st':
            max_time = 64
            max_push_out_time = 13.5
            max_flow_rate = 99999
        elif droplet_type.lower()[0:2] == 'sm' or droplet_type.lower()[0:2] == 'pi':
            max_time = 166 
            max_push_out_time = 23
            max_flow_rate = 99999
        elif droplet_type.lower()[0:2] == 'de':
            max_time = 4
            max_push_out_time = 4
            max_flow_rate = 99999
        while (time.time() - time_start <= max_time) or (flow_rate > max_flow_rate):
            # Get flow rate.
            flow_rate = min(self.__pipettor.get_flow_rate())
            delay(1, 'second')
        # Close Pipettor Valve.
        self.__pipettor.close_valve()
        # Close air valve.
        self.turn_off_air_valve(2)
        # Set pressure.
        self.__pipettor.set_pressure(pressure=0, direction=2)
        # Turn the pump back on.
        self.__pipettor.set_pressure(pressure=241, direction=1)
        # Open the valve.
        #self.__pipettor.open_valve()
        # Pushout air.
        #delay(max_push_out_time, 'seconds')
        # Close the valve.
        #self.__pipettor.close_valve()
        # Set pressure.
        self.__pipettor.set_pressure(pressure=0, direction=1)
        # Change the timeout for the seyonic controller to the default of 65 seconds
        time.sleep(3)
        self.__pipettor.change_timeout()

    def mix(self, asp_vol: int, disp_vol: int, tip: int, pressure: str, count: int = 1):
        """ Mixes the solution where it is at with an aspirate then dispense """
        aspirate_vol = microliters_to_seyonic(asp_vol)
        dispense_vol = microliters_to_seyonic(disp_vol)
        for cycle in range(count):
            # Trigger pipettor action
            self.aspirate(aspirate_vol, pipette_tip_type=tip, pressure=pressure)
            # Trigger pipettor action
            self.dispense(dispense_vol, pressure=pressure)

    # Mix Method
    def old_mix(self, aspirate_vol, dispense_vol, cycles=1):
        # Convert from microliters to seyonic units
        aspirate_vol = microliters_to_seyonic(aspirate_vol)
        dispense_vol = microliters_to_seyonic(dispense_vol)
        for cycle in range(cycles):
            # Trigger pipettor action
            self.aspirate(aspirate_vol)
            # Trigger pipettor action
            self.dispense(dispense_vol)

    def get_position(self):
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position.__name__))
        x = self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position('pipettor_gantry', self.__ID['X'])
        y = self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position('pipettor_gantry', self.__ID['Y'])
        z = self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position('pipettor_gantry', self.__ID['Z'])
        dp = self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position('pipettor_gantry', self.__ID['Drip Plate'])
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position.__name__))
        return x,y,z,dp

    def get_position_from_axis(self, axis: str) -> int:
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position_from_axis.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position_from_axis.__name__))
        assert type(axis) == str
        position = self.__FAST_API_INTERFACE.pipettor_gantry.axis.get_position('pipettor_gantry', self.__ID[axis.title()])
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.get_position_from_axis.__name__))
        return position

    def get_position_deprecated(self):
        x = self.get_position_from_response(self.__ADDRESS_PIPETTOR_X)
        y = self.get_position_from_response(self.__ADDRESS_PIPETTOR_Y)
        z = self.get_position_from_response(self.__ADDRESS_PIPETTOR_Z)
        dp = self.get_position_from_response(self.__ADDRESS_DRIP_PLATE)
        return x,y,z,dp

    def print_position(self):
        x,y,z,dp = self.get_position()
        print('[x, y, z, drip plate]')
        print('[{0},{1},{2},{3}]'.format(x,y,z,dp))

    # move_relative method
    def move_relative(self, direction, value, velocity='slow', use_fast_api=True, block=True):
        modules = ['x','y','z','drip plate']
        __directions = ['left', 'right', 'backwards', 'forwards', 'up', 'down']
        directions = ['l', 'r', 'b', 'f', 'u', 'd']
        check_type(direction, str)
        value = abs(value)
        direction.lower()
        module = ''
        assert direction[0] in directions
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_relative.__name__))
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_relative.__name__))
        #x,y,z,dp = self.get_position()
        if direction[0] == 'l':
            module = 'x'   
            x = self.get_position_from_axis(module)
            # Value needs to be negative.
            if use_fast_api:
                value = x - value
            else:
                if value > 0:
                    value = -value
        elif direction[0] == 'r':
            module = 'x' 
            x = self.get_position_from_axis(module)
            # Value needs to be positive.
            if use_fast_api:
                value = x + value
            else:
                if value < 0:
                    value = -value
        elif direction[0] == 'b':
            module = 'y' 
            y = self.get_position_from_axis(module)
            # Value needs to be positive.
            if use_fast_api:
                value = y + value
            else:
                if value < 0:
                    value = -value
        elif direction[0] == 'f':
            module = 'y' 
            y = self.get_position_from_axis(module)
            # Value needs to be negative.
            if use_fast_api:
                value = y - value
            else:
                if value > 0:
                    value = -value
        elif direction[0] == 'u':
            module = 'z' 
            z = self.get_position_from_axis(module)
            # Value needs to be positive.
            if use_fast_api:
                value = z + value
            else:
                if value < 0:
                    value = -value
        elif direction[0] == 'd':
            module = 'z' 
            z = self.get_position_from_axis(module)
            # Value needs to be negative.
            if use_fast_api:
                value = z - value
            else:   
                if value > 0:
                    value = -value
        if module == 'x':
            if velocity == 'fast':
                velocity = self.__LIMIT_MAX_VELOCITY_X
            elif velocity == 'slow':
                velocity = self.__HVEL_X
            elif type(velocity) == int:
                pass
            if use_fast_api:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['X'], value, velocity, block)
            else:
                self.mrel(self.__ADDRESS_PIPETTOR_X, value, velocity)
        elif module == 'y':
            if velocity == 'fast':
                velocity = self.__LIMIT_MAX_VELOCITY_Y
            elif velocity == 'slow':
                velocity = self.__HVEL_Y
            elif type(velocity) == int:
                pass
            if use_fast_api:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Y'], value, velocity, block)
            else:
                self.mrel(self.__ADDRESS_PIPETTOR_Y, value, velocity)
        elif module == 'z':
            if velocity == 'fast':
                velocity = self.__LIMIT_MAX_VELOCITY_Z
            elif velocity == 'slow':
                velocity = self.__HVEL_Z
            elif type(velocity) == int:
                pass
            if use_fast_api:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Z'], value, velocity, block)
            else:
                self.mrel(self.__ADDRESS_PIPETTOR_Z, value, velocity)
        elif module == 'drip plate':
            if velocity == 'fast':
                velocity = self.__LIMIT_MAX_VELOCITY_DRIP_PLATE
            elif velocity == 'slow':
                velocity = self.__HVEL_DRIP_PLATE
            elif type(velocity) == int:
                pass
            if use_fast_api:
                self.__FAST_API_INTERFACE.pipettor_gantry.axis.move(self.__MODULE_NAME, self.__ID['Drip Plate'], value, velocity, block)
            else:
                self.mrel(self.__ADDRESS_DRIP_PLATE, value, velocity)
        if self.__location_str != None and type(self.__location_str) == str:
            self.__location_str = self.__location_str + '_relative_move_along_{0}_by_{1}'.format(module, value)
        else:
            print(self.__location_str)
        logger_xlsx = LoggerXLSX()
        logger_xlsx.log("Move relative", "{0}.{1}(direction={2}, value={3}, velocity='{4}')".format(__name__, self.move_relative.__name__, direction, value, velocity),timer.get_current_elapsed_time())
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_relative.__name__))

    # Move Relative From Known Method
    def mrel_from_known(self, known_location, relative_distance):
        # Convert known_location and relative_distance to UpperGantryCoordinates.
        known_location_ugc = target_to_upper_gantry_coordinate(known_location)
        relative_distance_ugc = target_to_upper_gantry_coordinate(relative_distance)
        # Compute the unknown location.
        unknown_location_ugc = known_location_ugc + relative_distance_ugc
        print("{0}, {1}, {2}, {3}".format(unknown_location_ugc.x, unknown_location_ugc.y, unknown_location_ugc.z, unknown_location_ugc.drip_plate))
        # Move along Z to clear the prep deck.
        #self.mabs(self.__ADDRESS_PIPETTOR_Z, 0, self.__LIMIT_MAX_VELOCITY_Z, block=True)
        # Move along Y and X to the unknown location.
        self.mabs(self.__ADDRESS_PIPETTOR_Y, unknown_location_ugc.y, self.__LIMIT_MAX_VELOCITY_Y, block=False)
        self.mabs(self.__ADDRESS_PIPETTOR_X, unknown_location_ugc.x, self.__LIMIT_MAX_VELOCITY_X, block=True)
        # Move along Z to the unknown location.
        self.mabs(self.__ADDRESS_PIPETTOR_Z, unknown_location_ugc.z, self.__LIMIT_MAX_VELOCITY_Z, block=True)

    def get_pipettor(self):
        return self.__pipettor
    def get_chassis(self):
        return self.__chassis

    def turn_on_suction_cups(self):
        # Turn on Valve 3 (Channel 2) which is Vacuum Pickup - Suction Cup
        self.turn_on_air_valve(3)
        # Set a negative pressure of -300 mbar.
        self.__pipettor.set_pressure(-300, 2)
        # Let the pressure get stable.
        time.sleep(self.__pipettor.pressure_delay)
        action_values = self.__pipettor._poll_until_complete()
        return action_values

    def turn_off_suction_cups(self):
        # Set the pressure to 0 mbar.
        self.__pipettor.set_pressure(0, 2)
        # Turn off Valve 3 (Channel 2) which is the Vacuum Pickup - Suction Cups.
        self.turn_off_air_valve(3)
        action_values = self.__pipettor._poll_until_complete()

    def test_suction_cups(self):
        #valve_3 = 2
        #self.__FAST_API_INTERFACE.pipettor_gantry.air_valve.on(valve_3)
        #self.__pipettor.set_pressure(pressure=-300, direction=2)
        #time.sleep(self.__pipettor.pressure_delay)
        #action_value = self.__pipettor._poll_until_complete()
        #time.sleep(5)
        #self.__pipettor.set_pressure(pressure=0, direction=2)
        #self.__FAST_API_INTERFACE.pipettor_gantry.air_valve.off(valve_3)
        self.turn_on_suction_cups()
        time.sleep(5)
        self.turn_off_suction_cups()


    def __check_for_z_axes_change_needed(self, target):
        names_that_need_change = [
        'reagent_cartridge',
        'mag_separator',
        'tray_out_location',
        'heater_shaker',
        'assay_strip',
        'pcr_thermocycler',
        ]
        # Check if the first few letters match a name in the deck plate names that need Z axes changes.
        if type(target) == str:
            for name in names_that_need_change:
                if target[:4] == name[:4]:
                    return True
        return False

    def move_chip(self, chip_id, chip_type, tray_out_location_letter):
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_chip.__name__))
        logger.log('LOG-START', "Moving a {0} chip, moving chip {1}/4 to {2} .".format(chip_type, chip_id, tray_out_location_letter))
        chip_ids = [1,2,3,4]
        chip_types = ['droplets', 'microwells', 'd', 'm']
        location_letters = ['A', 'B', 'C', 'D']
        assert type(chip_id) == int
        assert type(chip_type) == str
        assert type(tray_out_location_letter) == str
        assert chip_id in chip_ids
        assert chip_type[0].lower() in chip_types
        assert tray_out_location_letter.upper() in location_letters
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_chip.__name__))
        # Get the chip type.
        if chip_type[0].lower() == 'd':
            chip_type = 'droplets'
        elif chip_type[0].lower() == 'm':
            chip_type = 'microwells'
        # Move the pipettor head to the chip location.
        self.move_pipettor('{0}_chip_{1}'.format(chip_type, chip_id), use_drip_plate=False, use_z=False)
        # Turn on suction cups.
        #self.turn_on_suction_cups()
        self.move_pipettor('{0}_chip_{1}'.format(chip_type, chip_id))
        self.turn_on_suction_cups()
        # Move the chip to the Tray Out Location.
        if tray_out_location_letter.upper() == 'D':
            tray_out_location_int = 1
        elif tray_out_location_letter.upper() == 'C':
            tray_out_location_int = 2
        elif tray_out_location_letter.upper() == 'B':
            tray_out_location_int = 3
        elif tray_out_location_letter.upper() == 'A':
            tray_out_location_int = 4
        #self.move_relative('up', 200000, velocity='fast')
        self.move_pipettor('tray_out_location_chip{0}'.format(tray_out_location_int), pipette_tip_type=1000)
        # Turn of the suction cups.
        self.turn_off_suction_cups()
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_chip.__name__))
        logger.log('LOG-END', "Chip {0}/4 has been moved to {1}".format(chip_id, tray_out_location_letter))

    def move_lid_new(self, lid: list, tray: list) -> None:
        """ Moves a lid from the lid tray to a tray """
        # Move the pipettor to lid_xyz with the drip tray
        self.move(x=lid[0], y=lid[1], z=lid[2], drip_plate=lid[3], use_drip_plate=True, tip=1000)
        # Turn on suction cup
        self.turn_on_suction_cups()
        delay(2, 'seconds')
        # Move to tray_xyz with drip plate
        self.move(x=tray[0], y=tray[1], z=tray[2], drip_plate=tray[3], use_drip_plate=True, tip=1000)
        # Turn off suction cup
        self.turn_off_suction_cups()

    def move_chip_new(self, chip: list, tray: list) -> None:
        """ Moves a lid from the lid tray to a tray """
        # Move the pipettor to lid_xyz with the drip tray
        self.move(x=chip[0], y=chip[1], z=chip[2], drip_plate=chip[3], use_drip_plate=True, tip=1000)
        # Turn on suction cup
        self.turn_on_suction_cups()
        delay(3, 'seconds')
        # Move to tray_xyz with drip plate
        self.move(x=tray[0], y=tray[1], z=tray[2], drip_plate=tray[3], use_drip_plate=True, tip=1000)
        # Turn off suction cup
        self.turn_off_suction_cups()

    def move_chip_and_lid_temporary(self, chip: list, tray: list) -> None:
        """ Moves a lid from the lid tray to a tray 
        
        Moves the chip on a tray to a different tray for testing transfer of engaged
        chips and lids
        """
        # Move the pipettor to lid_xyz with the drip tray
        self.move(x=chip[0], y=chip[1], z=chip[2], drip_plate=chip[3], use_drip_plate=True, tip=1000)
        # Turn on suction cup
        self.turn_on_suction_cups()
        delay(2, 'seconds')
        # Move to tray_xyz with drip plate
        self.move(x=tray[0], y=tray[1], z=tray[2], drip_plate=tray[3], use_drip_plate=True, tip=1000)
        # Turn off suction cup
        self.turn_off_suction_cups()

    def move_lid(self, lid_id, tray_out_location_letter):
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_lid.__name__))
        logger.log('LOG-START', "Moving lid {0}/4 to {1}".format(lid_id, tray_out_location_letter))
        lid_ids = [1,2,3,4]
        location_letters = ['A', 'B', 'C', 'D']
        assert type(lid_id) == int
        assert type(tray_out_location_letter) == str
        assert lid_id in lid_ids
        assert tray_out_location_letter.upper() in location_letters
        timer = Timer(logger)
        timer.start(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_lid.__name__))
        # Move the pipettor head to the lid location.
        self.move_pipettor('lid{0}'.format(lid_id), use_drip_plate=False, use_z=False)
        # Turn on suction cups.
        #self.turn_on_suction_cups()
        self.move_pipettor('lid{0}'.format(lid_id))
        self.turn_on_suction_cups()
        # Move the chip to the Tray Out Location.
        if tray_out_location_letter.upper() == 'D':
            tray_out_location_int = 1
        elif tray_out_location_letter.upper() == 'C':
            tray_out_location_int = 2
        elif tray_out_location_letter.upper() == 'B':
            tray_out_location_int = 3
        elif tray_out_location_letter.upper() == 'A':
            tray_out_location_int = 4
        self.move_pipettor('tray_out_location_chip{0}'.format(tray_out_location_int), pipette_tip_type=1000)
        # Turn of the suction cups.
        self.turn_off_suction_cups()
        timer.stop(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move_lid.__name__))
        logger.log('LOG-END', "Moved lid {0}/4 to {1}".format(lid_id, tray_out_location_letter))

    def test_heater_shaker(self):
        print("Shake for 3 seconds:\n")
        bs3000T = self.__heater_shaker
        bs3000T.shakeOn(mixing_speed_rpm=50)
        time.sleep(3)
        print("Shaking will now stop (takes 6 seconds)...\n")
        bs3000T.shakeOff()
        print("Shake for 2 seconds:\n")
        bs3000T.shakeOnWithRuntime(runtime=2, mixing_speed_rpm=50)
        print("Shake Go Home:\n")
        bs3000T.shakeGoHome()

    def get_heater_shaker_temp_state(self):
        """ Obtains the state of the temperature function for the Heater/Shaker
            REturns 0 if disabled and 1 if the the temp control is enabled
        """
        temp_state = self.get_fast_api_interface().prep_deck.heater.get_temp_state()
        print(temp_state)

    def change_heater_shaker_temperature(self, temp: float) -> None:
        """ Change the heater/shaker temperature """
        # Set the Target Temp
        self.get_fast_api_interface().prep_deck.heater.stt(temp)
        # Turn on temp control
        self.get_fast_api_interface().prep_deck.heater.ton()

    def turn_on_shake(self, rpm: int, shake_time: int = None, time_units: str = None) -> None:
        """ Turns on the heater shaker shaking """
        if shake_time == None:
            self.get_fast_api_interface().prep_deck.heater.set_shake_target_speed(rpm)
            self.get_fast_api_interface().prep_deck.heater.shake_on()
        else:
            self.get_fast_api_interface().prep_deck.heater.set_shake_target_speed(rpm)
            self.get_fast_api_interface().prep_deck.heater.shake_on()
            delay(shake_time, time_units)
            self.get_fast_api_interface().prep_deck.heater.shake_off()
            self.get_fast_api_interface().prep_deck.heater.shake_go_home()

    def turn_off_shake(self) -> None:
        """ Turns off the heater shaker shaking """
        self.get_fast_api_interface().prep_deck.heater.shake_off()

    def _turn_on_shake(self, rpm, shake_time=None, time_units=None):
        logger = Logger(__file__, __name__)
        if shake_time == None and time_units == None:
            a = 1
            logger.log('LOG-START', "Heater/Shaker shaking at {0} rpm continuously.".format(rpm))
            self.__heater_shaker.shakeOn(mixing_speed_rpm=rpm)
        else:
            logger.log('LOG-START', "Heater/Shaker shaking at {0} rpm for {1} {2}".format(rpm, shake_time, time_units))
            self.__heater_shaker.shakeOn(mixing_speed_rpm=rpm)
            delay(shake_time, time_units)
            self.__heater_shaker.shakeOff()
            self.__heater_shaker.shakeGoHome()
        logger.log('LOG-END', "Heater/Shaker done shaking.")

    def _turn_off_shake(self):
        logger = Logger(__file__, __name__)
        logger.log('LOG-START', "Stopping the Heater/Shaker from shaking and homing it.")
        self.__heater_shaker.shakeOff()
        self.__heater_shaker.shakeGoHome()
        logger.log('LOG-END', "Heater/Shaker done shaking.")

    def engage_magnet(self):
        logger = Logger(__file__, __name__)
        logger.log('WARNING', "This function is empty.")
        #self.__FAST_API_INTERFACE.prep_deck
        #self.__FAST_API_INTERFACE.prep_deck.axis.move('prep_deck', self.__ID['Mag Separator'], 0, 50000, block=False)
        self.__FAST_API_INTERFACE.prep_deck.axis.home('prep_deck', self.__ID['Mag Separator'], block=False)

    def disengage_magnet(self):
        logger = Logger(__file__, __name__)
        logger.log('WARNING', "This function is empty.")
        self.__FAST_API_INTERFACE.prep_deck.axis.move('prep_deck', self.__ID['Mag Separator'], -140000, 50000, block=False)

    def set_pre_amp_thermocycler_temperature(self, temperature: int, address: int = 9) -> None:
        #from meerstetter import Meerstetter
        #meerstetter = Meerstetter()
        #meerstetter.change_temperature(address, temperature, False)
        a = 1

    def close(self):
        # Turn off the Relay for the Heater/Shaker nad Chiller.
        try:
            self.__pipettor.close()
        except:
            pass
        #relay_8_info = self.__FAST_API_INTERFACE.chassis.relay.get_relay_info(8)
        #self.__FAST_API_INTERFACE.chassis.relay.off(relay_8_info['channel'])
        if self.controller != None:
            self.controller.close()
