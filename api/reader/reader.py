
# Version: Test
'''
'''

import os

from api.util.logger import Logger

from api.util.commands import commands
from api.util.controller import Controller
from api.util.coordinate import coordinates

from api.interfaces.fast_api_interface import FastAPIInterface

from api.util.utils import check_type, delay

from api.reader.reader_coordinate import ReaderCoordinate, target_to_reader_coordinate
from api.reader.reader_velocity import ReaderVelocity

import api.util.motor
from api.util.led import LED, LEDS, led_channel_str_to_int, led_channel_int_to_str

import time

import tifffile

import api.reader.camera.camera as camera

class Reader(api.util.motor.Motor):
    # Public variables.
    controller = None
    led = None

    # Private variables.
    __commands = commands['Reader']
    __coordinate = ReaderCoordinate()
    __velocity = ReaderVelocity()

    # Private constants (Com Port)
    __COM_PORT = 'COM8'

    # Private constants (Addresses).
    __ADDRESS_X_AXIS = 0x01
    __ADDRESS_Y_AXIS = 0x02
    __ADDRESS_Z_AXIS = 0x03
    __ADDRESS_FILTER_WHEEL = 0x04
    __ADDRESS_LED = 0x05
    __ADDRESS_FRONT_TRAY = 0x07
    __ADDRESS_REAR_TRAY = 0x06
    __ADDRESS_HEATER_FRONT_1 = 0x0B
    __ADDRESS_HEATER_FRONT_2 = 0x0A
    __ADDRESS_HEATER_REAR_1 = 0x09
    __ADDRESS_HEATER_REAR_2 = 0x08
    __ID = {
        'X': __ADDRESS_X_AXIS,
        'Y': __ADDRESS_Y_AXIS,
        'Z': __ADDRESS_Z_AXIS,
        'Filter Wheel': __ADDRESS_FILTER_WHEEL,
        'LED': __ADDRESS_LED,
        'Tray AB': __ADDRESS_REAR_TRAY,
        'Tray CD': __ADDRESS_FRONT_TRAY,
        'Heater A': __ADDRESS_HEATER_REAR_2,
        'Heater B': __ADDRESS_HEATER_REAR_1,
        'Heater C': __ADDRESS_HEATER_FRONT_2,
        'Heater D': __ADDRESS_HEATER_FRONT_1
        }

    # Private constants (Limits).
    __LIMIT_MAX_STEPS_FROM_HOME_X, __LIMIT_MAX_STEPS_FROM_HOME_Y, __LIMIT_MAX_STEPS_FROM_HOME_Z, __LIMIT_MAX_STEPS_FROM_HOME_FILTER_WHEEL = __coordinate.get_limit_max() # usteps
    __LIMIT_TRAY_OPEN = __coordinate.get_limit_tray_open()
    __LIMIT_TRAY_CLOSED = __coordinate.get_limit_tray_closer()
    __LIMIT_HEATER_OPEN = __coordinate.get_limit_heater_open()
    __LIMIT_HEATER_CLOSED = __coordinate.get_limit_heater_closed()
    __LIMIT_MAX_VELOCITY_X, __LIMIT_MAX_VELOCITY_Y, __LIMIT_MAX_VELOCITY_Z, __LIMIT_MAX_VELOCITY_FILTER_WHEEL, __LIMIT_MAX_VELOCITY_TRAY, __LIMIT_MAX_VELOCITY_HEATER = __velocity.get_limit_max() # usteps/sec

    # Private constants (Homing velocity -- hvel).
    __HVEL_X = 80000  # usteps/sec
    __HVEL_Y = 500000
    __HVEL_Z = 80000
    __HVEL_FILTER_WHEEL = 1
    __HVEL_TRAY = 200000

    # Private constants (FastAPI).
    __FAST_API_INTERFACE = None
    __MODULE_NAME = 'reader'

    # Constructor.
    def __init__(self, unit=None):
        super(api.util.motor.Motor, self).__init__()
        self.controller = Controller(com_port=self.__COM_PORT)
        self.__FAST_API_INTERFACE = FastAPIInterface(unit)
        self.led = LED(self.controller, self.__ADDRESS_LED)
        try:
            self.camcontroller = camera.CamController()
        except Exception as e:
            print(e)
            self.camcontroller = None

    def get_fast_api_interface(self):
        return self.__FAST_API_INTERFACE

    def get_position(self):
        x = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['X'])
        y = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['Y'])
        z = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['Z'])
        fw = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['Filter Wheel'])
        return x,y,z,fw

    def get_position_from_axis(self, axis: str) -> int:
        """ Get the position of the reader from the axis """
        val = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID[axis])
        return val

    def move_imager_relative(self, direction: str, value: int, velocity: str) -> None:
        """ Move the Reader Imager relative to the current position given a direction, value to move (usteps), and a speed (usteps/sec) """
        direction = direction.lower()[0]
        directions = ['left', 'right',' backwards', 'forwards', 'up', 'down', 'l', 'r', 'b', 'f', 'u', 'd']
        assert direction in directions
        velocity = velocity.lower()[0]
        velocities = ['fast', 'slow', 'f', 's']
        assert velocity in velocities
        # Set the sign of the value
        if direction in ['r', 'd', 'f']:
            value = -abs(value)
        else:
            value = abs(value)
        # Get where we are based on the direction
        if direction in ['l', 'r']:
            # Set the ID and speed
            ID = 'X'
            if velocity == 'f':
                speed = self.__LIMIT_MAX_VELOCITY_X
            else:
                speed = int(self.__LIMIT_MAX_VELOCITY_X * 0.5)
        elif direction in ['b', 'f']:
            # Set the ID and speed
            ID = 'Y'
            if velocity == 'f':
                speed = self.__LIMIT_MAX_VELOCITY_Y
            else:
                speed = int(self.__LIMIT_MAX_VELOCITY_Y * 0.4)
        elif direction in ['u', 'd']:
            # Set the ID and speed
            ID = 'Z'
            if velocity == 'f':
                speed = self.__LIMIT_MAX_VELOCITY_Z
            else:
                speed = int(self.__LIMIT_MAX_VELOCITY_Z * 0.8)
        # Get the position of the imager for this axis
        current_pos = self.get_position_from_axis(ID)
        # Move to a position relative to the current position
        pos = current_pos + value
        # Move to the new position
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID[ID], pos, speed, False, True)

    def turn_on_led(self, channel: int, intensity: int) -> None:
        """ Turn on the LED """
        self.__FAST_API_INTERFACE.reader.led.on(self.__ID['LED'], channel, intensity)

    def turn_off_led(self, channel: int) -> None:
        """ Turn off the LED """
        self.__FAST_API_INTERFACE.reader.led.off(self.__ID['LED'], channel)

    def set_filter_wheel_location(self, value: int, block: bool = False) -> None:
        """ Set the filter wheel location """
        value = -abs(value)
        speed = self.__LIMIT_MAX_VELOCITY_FILTER_WHEEL
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Filter Wheel'], value, speed, block, True)

    # Home Reader Method.
    def home_reader(self, use_z=True):
        # Setup the logger.
        logger = Logger(__file__, self.home_reader.__name__)
        logger.log('LOG-START', "Homing the reader module (filter wheel, Z, Y, X axes, trays, and heaters)")
        # Home Filter Wheel.
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Filter Wheel'])
        # Home along Z, Y, and X.
        if use_z:
            self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Z'])
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Y'], block=False)
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['X'])
        # Home heater 1, 2, 3, 4.
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Heater A'], block=False)
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Heater B'])
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Heater C'], block=False)
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Heater D'])
        # Home reader tray 1 and 2.
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Tray AB'], block=False)
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Tray CD'])
        logger.log('LOG-END', "Homing of the reader module is now complete.")

    def home_imager(self):
        logger = Logger(__file__, self.home_imager.__name__)
        logger.log('LOG-START', "Homing the imager submodule (filter wheel, Z, Y, X axes)")
        # Home Filter Wheel.
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Filter Wheel'])
        # Home along Z, Y, and X.
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Z'])
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Y'], block=False)
        self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['X'])
        logger.log('LOG-END', "Homing of the imager submodule is now complete.")

    def home_reader_deprecated(self):
        # Setup the logger.
        logger = Logger(__file__, self.home_reader.__name__)
        logger.log('LOG-START', "Homing the reader module (filter wheel, Z, Y, X axes, trays, and heaters)")
        # Home Filter Wheel.
        if self.get_position_from_response(self.__ADDRESS_FILTER_WHEEL) != 0 or True:
            self.home(self.__ADDRESS_FILTER_WHEEL, block=False)
            time.sleep(2)
        # Home along Z, Y, and X.
        #if self.get_position_from_response(self.__ADDRESS_Z_AXIS) != 0 or True:
            #self.home(self.__ADDRESS_Z_AXIS, block=True)
            #time.sleep(2)
        if self.get_position_from_response(self.__ADDRESS_X_AXIS) != 0 or True:
            self.home(self.__ADDRESS_X_AXIS, block=True)
            #self.mabs(self.__ADDRESS_X_AXIS, 0, self.__LIMIT_MAX_VELOCITY_X, block=True)
            time.sleep(2)
        if self.get_position_from_response(self.__ADDRESS_Y_AXIS) != 0 or True:
            self.home(self.__ADDRESS_Y_AXIS, block=True)
            #self.mabs(self.__ADDRESS_Y_AXIS, 0, self.__LIMIT_MAX_VELOCITY_Y, block=True)
            time.sleep(2)
        # Home heater 1, 2, 3, 4.
        if self.get_position_from_response(self.__ADDRESS_HEATER_FRONT_1) != 0 or True:
            self.home(self.__ADDRESS_HEATER_FRONT_1, block=True)
            #self.raise_heater(1)
            time.sleep(2)
        if self.get_position_from_response(self.__ADDRESS_HEATER_FRONT_2) != 0 or True:
            self.home(self.__ADDRESS_HEATER_FRONT_1, block=True)
            #self.raise_heater(2)
            time.sleep(2)
        # Home reader tray 1 and 2.
        if self.get_position_from_response(self.__ADDRESS_FRONT_TRAY) != 0 or True:
            self.home(self.__ADDRESS_FRONT_TRAY, block=True)
            #self.open_tray('front')
            time.sleep(3)
        #self.home(self.__ADDRESS_REAR_TRAY, block=True)
        logger.log('LOG-END', "Homing reader module complete.")

    # Move Reader Method.
    def move_imager(self, target):
        target_rc = target_to_reader_coordinate(target)
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_rc.y, self.__LIMIT_MAX_VELOCITY_Y)
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['X'], target_rc.x, self.__LIMIT_MAX_VELOCITY_X, block=False)
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_rc.z, self.__LIMIT_MAX_VELOCITY_Z)

    # Move Reader Method.
    def move_reader(self, target, use_z=True):
        # Convert the target to a ReaderCoordinate object.
        if type(target) == str:
            if target.lower() == 'heater_a':
                target = 'heater_4'
            elif target.lower() == 'heater_b':
                target = 'heater_3'
            elif target.lower() == 'heater_c':
                target = 'heater_2'
            elif target.lower() == 'heater_d':
                target = 'heater_1'
        target_rc = target_to_reader_coordinate(target)
        if use_z:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Z'], target_rc.z, self.__LIMIT_MAX_VELOCITY_Z)
        # Move along Y and X to the target location.
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Y'], target_rc.y, self.__LIMIT_MAX_VELOCITY_Y, block=False)
        time.sleep(0.2)
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['X'], target_rc.x, self.__LIMIT_MAX_VELOCITY_X)

    def move_reader_deprecated(self, target):
        # Convert the target to a ReaderCoordinate object.
        target_rc = target_to_reader_coordinate(target)
        # Move along Y and X to the target location.
        self.mabs(self.__ADDRESS_Y_AXIS, target_rc.y, self.__LIMIT_MAX_VELOCITY_Y, block=True)
        time.sleep(0.2)
        self.mabs(self.__ADDRESS_X_AXIS, target_rc.x, self.__LIMIT_MAX_VELOCITY_X, block=True)

    # Illumination On Method.
    def illumination_on(self, color, intensity_percent=50, use_fast_api=True, rotate_filter_wheel=True):
        # Convert color to int if it is a str.
        assert type(color) == str
        color = led_channel_str_to_int(color)
        # Rotate the filter wheel to the desired color.
        if rotate_filter_wheel:
            self.rotate_filter_wheel(color)
        #self.rotate_filter_wheel(color)
        # Use Cy5 light if wanting Cy5.5 for now.
        if color == 3:
                color = 5
        # Check for Bright Field to switch to hex led while keeping the fam filter.
        if color == 0:
                color = 'hex'
        # Set the given LED color to its on intensity level.
        if use_fast_api:
            self.__FAST_API_INTERFACE.reader.led.on(self.__ID['LED'], color)
            fw = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['Filter Wheel'])
        else:
            self.led.set(self.__ADDRESS_LED, color, self.led.get_limit_max_level() * intensity_percent / 100)

    def illumination_on_deprecated(self, color, intensity_percent=50):
        # Convert color to int if it is a str.
        if type(color) == str:
            color = led_channel_str_to_int(color)
        # Rotate the filter wheel to the desired color.
        self.rotate_filter_wheel(color)
        # Use Cy5 light if wanting Cy5.5 for now.
        if color == 3:
                color = 5
        # Set the given LED color to its on intensity level.
        self.led.set(self.__ADDRESS_LED, color, self.led.get_limit_max_level() * intensity_percent / 100)

    def illumination_off(self, color, use_fast_api=True, go_home=False):
        if type(color) == str:
            color = led_channel_str_to_int(color)
        # Rotate the filter wheel to home.
        if go_home:
            self.rotate_filter_wheel('home')
        # Set the given LED color to its on intensity level.
        if use_fast_api:
            self.__FAST_API_INTERFACE.reader.led.off(self.__ID['LED'], color)
            fw = self.__FAST_API_INTERFACE.reader.axis.get_position(self.__MODULE_NAME, self.__ID['Filter Wheel'])
        else:
            self.led.off(self.__ADDRESS_LED, color)

    # Illumination Off Method.
    def illumination_offmult(self):
        # Turn all LEDs off.
        self.led.offmult(self.__ADDRESS_LED, [i for i in range(self.led.get_number_of_channels())])

    # Open Tray Method.
    def open_tray(self, mode):
        check_type(mode, str)
        modes = ['front', 'rear', 'CD', 'AB']
        # Open the tray
        if mode == modes[0] or mode.upper() == 'CD':
            # Lift the heaters.
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater C'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=False)
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater D'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER)
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Tray CD'], self.__LIMIT_TRAY_OPEN, self.__LIMIT_MAX_VELOCITY_TRAY)
        elif mode == mode[1] or mode.upper() == 'AB':
            # Lift the heaters.
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater A'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=False)
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater B'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER)
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Tray AB'], self.__LIMIT_TRAY_OPEN, self.__LIMIT_MAX_VELOCITY_TRAY)

    def open_tray_deprecated(self, mode):
        check_type(mode, str)
        modes = ['front', 'rear', 'CD', 'AB']
        # Open the tray
        if mode == modes[0] or mode.upper() == 'CD':
            # Lift the heaters.
            #self.raise_heater(1, block=False)
            #self.raise_heater(2)
            self.mabs(self.__ADDRESS_FRONT_TRAY, self.__LIMIT_TRAY_OPEN, self.__LIMIT_MAX_VELOCITY_TRAY, block=True)
        elif mode == mode[1] or mode.upper() == 'AB':
            # Lift the heaters.
            #self.raise_heater(3, block=False)
            #self.raise_heater(4)
            self.mabs(self.__ADDRESS_REAR_TRAY, self.__LIMIT_TRAY_OPEN, self.__LIMIT_MAX_VELOCITY_TRAY, block=True)

    def close_thermocycler_tray(self, tray: str, amount: int, speed: int = None) -> None:
        assert tray in ['AB', 'CD']
        if speed == None:
            speed = self.__LIMIT_MAX_VELOCITY_TRAY
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID[f'Tray {tray}'], amount, speed)

    # Close Tray Method.
    def close_tray(self, mode, percent=100):
        modes = ['front', 'rear', 'CD', 'AB']
        check_type(mode, str)
        # Open the tray
        if mode == modes[0] or mode.upper() == 'CD':
            # Home the heaters.
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater C'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=False)
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater D'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER)
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Tray CD'], self.__LIMIT_TRAY_CLOSED, self.__LIMIT_MAX_VELOCITY_TRAY)
        elif mode == mode[1] or mode.upper() == 'AB':
            # Home the heaters.
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater A'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=False)
            #self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater B'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER)
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Tray AB'], self.__LIMIT_TRAY_CLOSED, self.__LIMIT_MAX_VELOCITY_TRAY)

    def close_tray_deprecated(self, mode, percent=100):
        modes = ['front', 'rear', 'CD', 'AB']
        check_type(mode, str)
        # Open the tray
        if mode == modes[0] or mode.upper() == 'CD':
            # Home the heaters.
            #self.home(self.__ADDRESS_HEATER_FRONT_1, block=False)
            #self.home(self.__ADDRESS_HEATER_FRONT_2)
            self.mabs(self.__ADDRESS_FRONT_TRAY, self.__LIMIT_TRAY_CLOSED, self.__LIMIT_MAX_VELOCITY_TRAY, block=True)
        elif mode == mode[1] or mode.upper() == 'AB':
             # Home the heaters.
            #self.home(self.__ADDRESS_HEATER_REAR_1, block=False)
            #self.home(self.__ADDRESS_HEATER_REAR_2)
            self.mabs(self.__ADDRESS_REAR_TRAY, self.__LIMIT_TRAY_CLOSED, self.__LIMIT_MAX_VELOCITY_TRAY, block=True)

    # Lower Heater Method.
    def lower_heater(self, number, block=True):
        if type(number) == str:
            letters = ['A', 'B', 'C', 'D']
            if number.upper() == 'A':
                number = 4
            elif number.upper() == 'B':
                number = 3
            elif number.upper() == 'C':
                number = 2
            elif number.upper() == 'D':
                number = 1
        numbers = [1, 2, 3, 4] # front1, front2, rear1, rear2
        if number == numbers[0]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater D'], self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[1]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater C'], self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[2]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater B'], self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[3]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater A'], self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)

    def lower_heater_deprecated(self, number, block=True):
        if type(number) == str:
            letters = ['A', 'B', 'C', 'D']
            if number.upper() == 'A':
                number = 4
            elif number.upper() == 'B':
                number = 3
            elif number.upper() == 'C':
                number = 2
            elif number.upper() == 'D':
                number = 1
        numbers = [1, 2, 3, 4] # front1, front2, rear1, rear2
        if number == numbers[0]:
            self.mabs(self.__ADDRESS_HEATER_FRONT_1, self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[1]:
            self.mabs(self.__ADDRESS_HEATER_FRONT_2, self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[2]:
            self.mabs(self.__ADDRESS_HEATER_REAR_1, self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[3]:
            self.mabs(self.__ADDRESS_HEATER_REAR_2, self.__LIMIT_HEATER_CLOSED, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)

    # Raise Heater Method.
    def raise_heater(self, number, block=True):
        if type(number) == str:
            letters = ['A', 'B', 'C', 'D']
            if number.upper() == 'A':
                number = 4
            elif number.upper() == 'B':
                number = 3
            elif number.upper() == 'C':
                number = 2
            elif number.upper() == 'D':
                number = 1
        numbers = [1, 2, 3, 4] # front1, front2, rear1, rear2
        if number == numbers[0]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater D'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[1]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater C'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[2]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater B'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[3]:
            self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Heater A'], self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)

    def raise_heater_deprecated(self, number, block=True):
        if type(number) == str:
            letters = ['A', 'B', 'C', 'D']
            if number.upper() == 'A':
                number = 4
            elif number.upper() == 'B':
                number = 3
            elif number.upper() == 'C':
                number = 2
            elif number.upper() == 'D':
                number = 1
        numbers = [1, 2, 3, 4] # front1, front2, rear1, rear2
        if number == numbers[0]:
            self.mabs(self.__ADDRESS_HEATER_FRONT_1, self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[1]:
            self.mabs(self.__ADDRESS_HEATER_FRONT_2, self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[2]:
            self.mabs(self.__ADDRESS_HEATER_REAR_1, self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)
        elif number == numbers[3]:
            self.mabs(self.__ADDRESS_HEATER_REAR_2, self.__LIMIT_HEATER_OPEN, self.__LIMIT_MAX_VELOCITY_HEATER, block=block)

    # Focus Reader Method.
    def focus_reader(self):
        return None

    # Capture Image Method.
    def capture_image(self, 
                      led_id: int,  
                      experiment_name: str,
                      filter_wheel_location: int=None,
                      fov_id: int=None,
                      unit_id_to_str: dict={
                          1: {'name': 'atto', 'filter_wheel': -21000, 'exposure': 1000},
                          2: {'name': 'fam', 'filter_wheel': -37000, 'exposure': 1000},
                          3: {'name': 'cy55', 'filter_wheel': -4000, 'exposure': 1000},
                          4: {'name': 'alexa405', 'filter_wheel': -47000, 'exposure': 1000},
                          5: {'name': 'cy5', 'filter_wheel': -13000, 'exposure': 1000},
                          6: {'name': 'hex', 'filter_wheel': -30000, 'exposure': 1000},
                          },
                      exposure_time_microseconds: int=1000, 
                      extension: str = '.tif') -> None:
        # Rotate the filter wheel
        if filter_wheel_location == None:
            filter_wheel_location = unit_id_to_str[led_id]['filter_wheel']
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Filter Wheel'], filter_wheel_location, 80000, block=True)
        # Turn on the LED
        self.turn_on_led(channel=led_id, intensity=200)
        # Capture the image
        self.camcontroller.close()
        cc = camera.CamController()
        self.camcontroller = cc
        # Set the exposure time
        self.set_exposure(exposure_time_microseconds)
        img = cc.snap_single()
        print(img.shape)
        # Turn off the LED
        self.turn_off_led(channel=led_id)
        # Convert led_id if possible
        if unit_id_to_str != None:
            led_id = unit_id_to_str[led_id]['name']
        # Set the file name
        if fov_id == None:
            fname = f"{experiment_name}___{led_id}_{exposure_time_microseconds}{extension}"
        else:
            fname = f"fov{fov_id}_{experiment_name}___{led_id}_{exposure_time_microseconds}{extension}"
        # Set the file path
        fdir = os.getcwd()
        fpath = os.path.join(fdir, fname)
        # Save the image
        print(f"Saving {fname} in {os.path.join(fdir, experiment_name)}")
        if not os.path.isdir(os.path.join(fdir, experiment_name)):
            os.makedirs(os.path.join(fdir, experiment_name))
        tifffile.imwrite(os.path.join(fdir, experiment_name, fname), img)
        return None

    # Set Cartridge Temp Method.
    def set_cartridge_temp(self, number):
        return None

    # Start Camera Streaming Method.
    def start_camera_streaming(self):
        return None

    # Stop Camera Streaming Method.
    def stop_camera_streaming(self):
        return None

    # Rotate Filter Wheel Method.
    def rotate_filter_wheel(self, color, block=True):
        if type(color) == str:
            if color.lower() == 'home':
                self.__FAST_API_INTERFACE.reader.axis.home(self.__MODULE_NAME, self.__ID['Filter Wheel'])
                return
            color = led_channel_str_to_int(color)
        # Rotate the filter wheel based on the color.
        self.__FAST_API_INTERFACE.reader.axis.move(self.__MODULE_NAME, self.__ID['Filter Wheel'], LEDS[color]['steps'], 10000, block=block)


    def rotate_filter_wheel_deprecated(self, color):
        if type(color) == str:
            if color.lower() == 'home':
                self.home(self.__ADDRESS_FILTER_WHEEL, block=True)
                return
            color = led_channel_str_to_int(color)
        # Rotate the filter wheel based on the color.
        if color == 1:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[1]['steps'], 10000, block=False)
        elif color == 2:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[2]['steps'], 10000, block=False)
        elif color == 3:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[3]['steps'], 10000, block=False)
        elif color == 4:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[4]['steps'], 10000, block=False)
        elif color == 5:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[5]['steps'], 10000, block=False)
        elif color == 6:
            self.mabs(self.__ADDRESS_FILTER_WHEEL, LEDS[6]['steps'], 10000, block=False)


    # Light Show (for demos) Method.
    def light_show(self):
        self.controller.write(b'>05,0,setmul,3F,100,<CR>')
        time.sleep(5)
        for i in range(6):
            print("Starting for channel {0}".format(i+1))
            #self.led.set(self.__ADDRESS_LED, i+1, 1000)
            self.controller.write('>05,0,set,{0},500,<CR>\n'.format(i+1).encode('utf-8'))
            #>0A,0,setmul,3F,100,<CR>
            print(self.controller.readline())
            time.sleep(3)
            #self.led.off(self.__ADDRESS_LED, i+1)
            self.controller.write('>05,0,off,{0},<CR>\n'.format(i+1).encode('utf-8'))

     # Capture Image Method.
    def capture_image_old(self, color, **kwargs):
        #self.rotate_filter_wheel(color)
        if 'exposure_time_microseconds' in kwargs.keys():
            self.set_exposure(**kwargs)
        self.illumination_on(color)
        img = self.camcontroller.snap_single()
        self.illumination_off(color)
        return img

    # Set Exposer Method.
    def set_exposure(self, exp_time_microseconds):
        _ = self.camcontroller.setExposureTimeMicroseconds(exp_time_microseconds)

    def filter_wheel_test(self, color, exposure=500, filename='test'):
        self.set_exposure(exposure)
        img = self.capture_image(color)
        _ = color
        if color.upper() == 'ALEXA405':
            _ = 'alexa'
        color = color.lower()
        fw = -int(coordinates['reader']['filter_wheel_{0}'.format(color)][3])
        logger = Logger(__file__, __name__)
        logger.log('MESSAGE', "Writing image to ...")
        tifffile.imwrite('{0}___{1}_exp{2}ms_fw{3}.tif'.format(filename, _.lower(), int(exposure/1000), fw), img)
        self.illumination_off(color)

    def take_all_6_colors(self, exposure=999999, filename='test'):
        # Take Alexa405.
        self.filter_wheel_test(color='alexa405', exposure=exposure, filename=filename)
        # Take Cy55.
        self.filter_wheel_test('cy55', exposure, filename)
        # Take Cy5.
        self.filter_wheel_test('cy5', exposure, filename)
        # Take Atto.
        self.filter_wheel_test('atto', exposure, filename)
        # Take Hex.
        self.filter_wheel_test('hex', exposure, filename)
        # Take Fam.
        self.filter_wheel_test('fam', exposure, filename)

    def fine_tune_filter_wheel_helper(self):
        # Cy5.5
        self.illumination_on('CY55')
        delay(5, 'seconds')
        self.illumination_off('CY55')
        # Cy5
        self.illumination_on('CY5')
        delay(5, 'seconds')
        self.illumination_off('CY5')
        # Atto
        self.illumination_on('ATTO')
        delay(5, 'seconds')
        self.illumination_off('ATTO')
        # Hex
        self.illumination_on('HEX')
        delay(5, 'seconds')
        self.illumination_off('HEX')
        # Fam
        self.illumination_on('FAM')
        delay(5, 'seconds')
        self.illumination_off('FAM')
        # Alexa405
        self.illumination_on('ALEXA405')
        delay(5, 'seconds')
        self.illumination_off('ALEXA405')
        return None

    def turn_on_bf(self):
        self.rotate_filter_wheel('fam')
        self.illumination_on('hex', rotate_filter_wheel=False)
    def turn_off_bf(self):
        self.illumination_off('hex')

    def demo(self):
        # Home the reader system.
        #self.home_reader()
        # Close the front tray.
        self.close_tray('front')
        # Lower Heater D.
        self.lower_heater(1)
        # Move the reader under Heater D.
        self.move_reader('heater_1')
        # Light show.
        print('\a')
        time.sleep(5)
        self.light_show()
        print('\a')
        time.sleep(5)
        # Home everything.
        self.home_reader()
        return None


    def close(self):
        if self.controller != None:
            self.controller.close()
