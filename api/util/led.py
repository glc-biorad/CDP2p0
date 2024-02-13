
# Version: Test
'''
DESCRIPTION:
This module contains the LED class which controlls the LED.

AUTHOR:
G.LC

AFFILIATION:
Bio-Rad, CDG, Advanced-Tech Team

CREATED ON:
9/2/2022
'''

import time
import os.path as osp

from api.util.commands import commands

from api.util.coordinate import coordinates

from api.util.utils import check_type, check_limit, replace_address, replace_word

from gui.util.utils import import_config_file

#LEDS = {
#    0: {
#        'name': 'BF',
#        'steps': coordinates['reader']['filter_wheel_fam'][-1],
#        'default intensity percent': 50
#        },
#    1: {
#        'name': 'ATTO',
#        'steps': coordinates['reader']['filter_wheel_atto'][-1],
#        'default intensity percent': 50
#        },
#    2: {
#        'name': 'FAM',
#        'steps': coordinates['reader']['filter_wheel_fam'][-1],
#        'default intensity percent': 50
#        },
#    3: {
#        'name': 'CY55',
#        'steps': coordinates['reader']['filter_wheel_cy55'][-1],
#        'default intensity percent': 50
#        },
#    4: {
#        'name': 'ALEXA405',
#        'steps': coordinates['reader']['filter_wheel_alexa405'][-1],
#        'default intensity percent': 50
#        },
#    5: {
#        'name': 'CY5',
#        'steps': coordinates['reader']['filter_wheel_cy5'][-1],
#        'default intensity percent': 50
#        },
#    6: {
#        'name': 'HEX',
#        'steps': coordinates['reader']['filter_wheel_hex'][-1],
#        'default intensity percent': 50
#        },
#    }
config_data = import_config_file(osp.join('config', 'unit_config.json'))
LEDS = config_data['LEDS']

def led_channel_str_to_int(channel_str):
    check_type(channel_str, str)
    channel_str = channel_str.upper()
    for channel in LEDS:
        channel_name = LEDS[channel]['name']
        if channel_str == channel_name:
            return channel
    raise ValueError("{0} is not a valid LED channel".format(channel_str))

def led_channel_int_to_str(channel_int):
    check_type(channel_int)
    for channel in LEDS:
        if channel_int == channel:
            return LEDS[channel]['name']
    raise ValueError("{0} is not a valid LED channel".format(channel_int))

class LED():
    # Public varibales.
    controller = None

    # Private variables.
    __address = None
    __levels = None # Intensity level
    __states = None # [0;OFF,1-ON] Following IEC 60417-5008 and IEC 60417-5007, respectively
    __commands = commands['led']

    # Private constants.
    __N_CHANNELS = 8
    __LIMIT_MIN_LEVEL = 0
    __LIMIT_MAX_LEVEL = 4095

    # Constructor.
    def __init__(self, controller, address):
        self.controller = controller
        self.__address = address

        # Set the defaults
        self.__levels = [0] * self.__N_CHANNELS
        self.__states = [0] * self.__N_CHANNELS

    # Getter Methods.
    def get_address(self):
        return self.__address
    def get_levels(self):
        return self.__levels
    def get_states(self):
        return self.__states
    def get_level(self, chan):
        return self.__levels[chan]
    def get_state(self, chan):
        return self.__states[chan]
    def get_number_of_channels(self):
        return self.__N_CHANNELS
    def get_limit_min_level(self):
        return self.__LIMIT_MIN_LEVEL
    def get_limit_max_level(self):
        return self.__LIMIT_MAX_LEVEL

    # Set Method
    def set(self, address, chan, level):
        # Check types.
        check_type(address, int)
        check_type(chan, int)
        check_type(level, int)
        # Check limits.
        check_limit(chan, 0, '>=')
        check_limit(chan, self.__N_CHANNELS, '<')
        check_limit(level, self.__LIMIT_MIN_LEVEL, '>=')
        check_limit(level, self.__LIMIT_MAX_LEVEL, '<=')
        # Get the command
        command = self.__commands['set']
        # Replace the address.
        command = replace_address(command, address)
        # Replace the channel.
        command = replace_word(command, 'chan', chan)
        # Replace the level.
        command = replace_word(command, 'level', level)
        print(command)
        # Send the command.
        self.controller.write(command)
        # Check the intensity level for confirmation.
        # Set the level and state for this channel.
        self.__levels[chan] = level
        self.__states[chan] = 1
        time.sleep(1)

    # Off Method
    def off(self, address, chan):
        # Check the types.
        check_type(address, int)
        check_type(chan, int)
        # Check limits.
        check_limit(chan, 0, '>=')
        check_limit(chan, self.__N_CHANNELS, '<')
        # Get the command.
        command = self.__commands['off']
        # Replace address.
        command = replace_address(command, address)
        # Replace chan.
        command = replace_word(command, 'chan', chan)
        # Send the command.
        self.controller.write(command)
        # Check the intensity level is 0.
        # Set the level and state for this channel.
        self.__levels[chan] = 0
        self.__states[chan] = 0
        time.sleep(1)

    # Setmul Method
    def setmul(self, address, chans, level):
        return None

    # Offmul Method
    def offmult(self, address, chans):
        return None

    # ?led Method
    def qled(self, address, chan):
        return None

    # Max Method
    def max(self, address, chan, level):
        return None