
# Version: Test
'''
'''

import sys
import time
from math import ceil

from api.util.commands import commands
from api.util.coordinate import Coordinate, coordinates

from api.util.logger import Logger

from api.util.utils import check_type, check_if_dir_valid, replace_address, replace_word

class Motor(object):
    # Public variables.
    controller = None

    # Private variables.
    __request_ID = None
    __address = None        # uint
    __steps = None
    __limit = None
    __IO = None
    __velocity = None
    __commands = commands['motor']

    # Private constants (homing and non-homing velocity)
    __HVEL = {
        0x01 : 20000, # ustep / sec
        0x02 : 150000,
        0x03 : 80000,
        0x04 : 150000,
        0x06 : 100000,
        0x07 : 500000,
        0x08 : 100000,
        0x0B : 200000,
        0x10 : 100000,
        0x0F : 100000,
        0x0E : 100000,
        0x0D : 100000
        }
    __VEL = {
        0x01 : 300000, # ustep / sec
        0x02 : 3200000,
        0x03 : 800000,
        0x04 : 2500000,
        0x06 : 100000,
        0x07 : 500000,
        0x08 : 100000,
        0x0B : 200000,
        0x10 : 100000,
        0x0F : 100000,
        0x0E : 100000,
        0x0D : 100000
        }

    # Private constants (Move Time Scaling Factors).
    ''' 
        - Based on Aru's measurements on how long max speed movements take,
            the scale factor for each address allows us to make an estimate
            for how long each move should take when moving at a speed.
    '''
    __MOVE_TIME_SCALE_FACTOR = {
        0x01 : 2.13,
        0x02 : 67.20,
        0x03 : 2.03,
        0x04 : 6.25,
        0x06 : 1.0,
        0x07 : 1.0,
        0x08 : 1.0,
        0x0B : 1.0,
        0x10 : 1.0,
        0x0F : 1.0,
        0x0E : 1.0,
        0x0D : 1.0
        }

    def __init__(self, controller):
        self.controller = controller

    def get_axis_from_address(self, address):
        if address == 0x01:
            return 'X'
        elif address == 0x02:
            return 'Y'
        elif address == 0x03:
            return 'Z'
        elif address == 0x04:
            return 'DRIP PLATE or FILTER WHEEL'
        elif address == 0x06:
            return 'Tray AB'
        elif address == 0x07:
            return 'Tray CD'
        elif address == 0x08:
            return 'Heater B'
        elif address == 0x09:
            return 'Heater A'
        elif address == 0x0A:
            return 'Heater C'
        elif address == 0x0B:
            return 'Heater D'

    def poll_stall(self):
        # Check current on motor for stalling. # Needs threading.
        return None

    def home(self, address, block=True):
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "homing {0} with blocking set to {1}".format(axis, block))
        # Check the address type.
        check_type(address, int)
        # Get the home command.
        command = self.__commands['home']
        # Replace 'address' with the desired address. 
        command = replace_address(command, address)
        # Get the current location from home (0).
        steps = self.get_position_from_response(address)
        # Send the command.
        self.controller.write(command)
        time.sleep(1)
        # Check for a response.
        while True:
            try:
                response = self.controller.readline()
                if len(response) > 0:
                    break
            except:
                continue 
        if block:
            # Compute the timeout for the move.
            timeout = self.compute_move_timeout(address, steps, self.__HVEL[address])
            if timeout <= 1:
                timeout = self.compute_move_timeout(address, steps, self.__HVEL[address])
            if timeout <= 1:
                timeout = timeout + 5
            # Check the position was reached.
            self.check_position_response(address, 0, timeout)
        #logger.log('LOG-END', "homing {0} complete".format(axis))

    def mrel(self, address, steps, velocity):
        # Check the input types.
        check_type(address, int)
        check_type(steps, int)
        check_type(velocity, int)
        # Get the mrel command.
        command = self.__commands['mrel']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Replace 'steps' with the desired steps.
        command = replace_word(command, 'steps', steps)
        # Replace 'velocity' with the desired velocity.
        command = replace_word(command, 'velocity', velocity)
        # Send the command.
        self.controller.write(command)

    def mabs(self, address, steps, velocity, block=True):
        # Check the input types.
        check_type(address, int)
        check_type(steps, int)
        check_type(velocity, int)
        check_type(block, bool)
        # Setup the logger.
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "absolute move along {0} with blocking set to {1}".format(axis, block))
        # Get the mabs command.
        command = self.__commands['mabs']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Replace 'steps' with the desired steps.
        command = replace_word(command, 'steps', steps)
        # Replace 'velocity' with the desired velocity.
        command = replace_word(command, 'velocity', velocity)
        # Send the command.
        self.controller.write(command)
        time.sleep(0.2)
        # Check for a response.
        while True:
            try:
                response = self.controller.readline()
                if len(response) > 0:
                    break
            except:
                continue        
        if block:
            # Compute the timeout for the move.
            timeout =  self.compute_move_timeout(address, steps, velocity)
            # Check the position was reached.
            self.check_position_response(address, steps, timeout)
        #logger.log('LOG-END', "absolute move along {0} complete".format(axis))

    def mlim(self, address, limit, velocity):
        # Check the input types.
        check_type(address, int)
        check_type(limit, int)
        check_type(velocity, int)
        # Get the mlim command.
        command = self.__commands['mlim']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Replace 'steps' with the desired steps.
        command = replace_word(command, 'limit', limit)
        # Replace 'velocity' with the desired velocity.
        command = replace_word(command, 'velocity', velocity)
        # Send the command.
        self.controller.write(command)

    def mgp(self, address, IO, velocity):
        # Check the input types.
        check_type(address, int)
        check_type(IO, int)
        check_type(velocity, int)
        # Get the mgp command.
        command = self.__commands['mgp']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Replace 'steps' with the desired steps.
        command = replace_word(command, 'IO', IO)
        # Replace 'velocity' with the desired velocity.
        command = replace_word(command, 'velocity', velocity)
        # Send the command.
        self.controller.write(command)

    def qpos(self, address):
        # Check the input types.
        check_type(address, int)
        # Setup the logger.
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "Checking the position along {0}".format(axis))
        # Get the ?pos command.
        command = self.__commands['?pos']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Send the command.
        self.controller.write(command)
        #logger.log('LOG-END', "Query along {0} sent".format(axis))

    def qmv(self, address):
        # Check the input types.
        check_type(address, int)
        # Get the ?mv command.
        command = self.__commands['?mv']
        # Replace 'address' with the desired address.
        command = replace_address(command, address)
        # Send the command.
        self.controller.write(command)

    def hdir(self, address, direction):
        # Check the direction if valid.
        check_type(address, int)
        check_type(direction, int)
        check_if_dir_valid(direction)
        # Get the command.
        command = replace_address(self.__commands['hdir'], address)
        command = replace_word(command, 'direction', direction)
        # Send the command.
        self.controller.write(command)
    
    def hvel(self, address, velocity):
        # Check validity.
        check_type(address, int)
        check_type(velocity, int)
        # Get the command.
        command = replace_address(self.__commands['hvel'], address)
        command = replace_word(command, 'velocity', velocity)
        # Send the command.
        self.controller.write(command)

    def hpol(self, address, polarity):
        # Check validity.
        check_type(address, int)
        check_type(polarity, int)
        # Get the command.
        command = replace_word(self.__commands['hpol'], 'polarity', polarity)
        # Send the command.
        self.controller.write(command)

    def tout(Self, address, milliseconds):
        return None

    def gppol(self, address, polarity):
        return None

    def stop(self, address):
        # Check validity.
        check_type(address, int)
        # Get the command.
        command = replace_address(self.__commands['stop'], address)
        # Send the command.
        self.controller.write(command)

    def compute_move_timeout(self, address, steps, velocity):
        # Check the types.
        check_type(address, int)
        check_type(steps, int)
        check_type(velocity, int)
        # Setup the logger.
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "Computing the estimated move time along {0} for {1} steps with a velocity of {2} microsteps per second.".format(axis, steps, velocity))
        # Get the scale factor.
        time_scale_factor = self.__MOVE_TIME_SCALE_FACTOR[address]
        # Return the timeout
        move_timeout = ceil(time_scale_factor * abs(steps) / velocity)
        #logger.log('LOG-END', "Computed the estimated move time along {0} to be {1} seconds.".format(axis, move_timeout))
        return move_timeout

    def check_position_response(self, address, steps, timeout):
        # Check types
        check_type(address, int)
        check_type(steps, int)
        check_type(timeout, int)
        # Setup the logger.
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "Checking position response along {0}".format(axis))
        if timeout < 1:
            timeout = 60
        # Wait the specified time for the ?pos response
        time_start = time.time()
        position_0 = None
        delta_t = 4.0
        i = 0
        n = 4
        #print("MESSAGE (motor, check_position_response): starting check for reference during testing with timeout (total: {0}, computed: {1}) seconds".format(timeout * (1 + delta_t), timeout))
        while time.time() - time_start < timeout + (delta_t * timeout):
            self.qpos(address)
            # Get the ?pos response after waiting
            try:
                position_response = self.controller.readline()
            except:
                position_response = ''
            if position_response != '':
                position = self.get_position_from_response(address)
                #print("MESSAGE (motor, check_position_reached): position = {0}/{1}".format(position, position_0))
                if position == position_0 and i != n:
                    i = i + 1
                    if steps == 0:
                        self.home(address, block=False)
                        break
                    logger.log('WARNING', "Checking position response found no movement along {0}, forcing a move...".format(axis))
                    #print("MESSAGE (motor, check_position_response): didn't move, so forcing a mabs, attempt {0}/{1} - {2}/{3}".format(i,n,position,position_0))
                    self.mabs(address, steps, self.__VEL[address], block=True)
                position_0 = position
                if position == steps:
                    #logger.log('LOG-END', "Checking position response along {0} reached {1} in {2}".format(axis, steps, time.time() - time_start))
                    #print("MESSAGE (motor, check_position_reached): {0} reached in {1}".format(steps, time.time() - time_start))
                    return
            else:
                #print("MESSAGE (motor, check_position_reached): nothing... so forcing a mabs")
                logger.log('WARNING', "Checking position response along {0} received nothing as a response, so forcing a move".format(axis))
                self.mabs(address, steps, self.__VEL[address], block=True)
            time.sleep(0.2)
        # Send the ?pos command
        self.qpos(address)
        # Get the position
        position = self.get_position_from_response(address)
        # Check if the desired position was reached after the timeout period
        if position != steps:
            print("WARNING (motor, check_position_response): ({0}) != desired ({1}) in {2} seconds with computed timeout of {3} seconds!".format(position, steps, timeout + (delta_t * timeout), timeout))
            self.mabs(address, steps, 300000)
            #sys.exit("Exiting")

    def get_position_from_response(self, address):
        timeout = 10
        time_start = time.time()
        # Check types
        check_type(address, int)
        # Setup the logger.
        logger = Logger(__file__, self.home.__name__)
        axis = self.get_axis_from_address(address)
        #logger.log('LOG-START', "Reading position along {0} from a position query".format(axis))
        # Send out the ?pos 
        self.qpos(address)
        # Get the ?pos response
        position_response = ''
        try:
            position_response = self.controller.readline()
        except:
            # Return the position
            while position_response == '':
                self.qpos(address)
                try:
                    position_response = self.controller.readline()
                except:
                    position_response = ''
                if position_response != '':
                    pos = int(position_response.split(',')[-1])
                    #logger.log('LOG-END', "Reading position along {0} from a position query, positon = {1}".format(axis, pos))
                    return pos
                time.sleep(0.5)
                if time.time() - time_start > timeout:
                    #logger.log('LOG-END', "Reading position along {0} from a position query timeout".format(axis))
                    return 0
        pos = int(position_response.split(',')[-1])
        #logger.log('LOG-END', "Reading position along {0} from a position query, position = {1}".format(axis, pos))
        return pos

    def wait(self):
        return None