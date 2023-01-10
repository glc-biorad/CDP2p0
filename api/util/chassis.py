'''
DESCRIPTION:
This module contains the Chassis object for controlling relay valves.

AUTHOR:
G.LC

AFFILIATION:
Bio-Rad, CDG, Advanced-Tech Team

# CREATED ON:
9/1/2022
'''

from api.util.logger import Logger

from api.util.commands import commands

from api.interfaces.fast_api_interface import FastAPIInterface

from api.util.utils import replace_address, replace_word

class Chassis():
    # Public variables.
    controller = None

    # Private variables.
    __id = None
    __relay_state = None # [0;OFF,1-ON] Following IEC 60417-5008 and IEC 60417-5007, respectively 
    __commands = commands['chassis']
    __address = None
    __FAST_API_INTERFACE = None

    # Private Constants.
    __CHANNELS = {
        'gpio': {
            0: 'pump',
            },
        'relay': {
            1: {
                'description': 'PC Power',
                'voltage': 24
                },
            2: {
                'description': 'Pre-Amp Thermocycler',
                'voltage': 36
                },
            3: {
                'description': 'Thermocycler A',
                'voltage': 36
                },
            4: {
                'description': 'Thermocycler B',
                'voltage': 36
                },
            5: {
                'description': 'Thermocycler C',
                'voltage': 36
                },
            6: {
                'description': 'Thermocycler D',
                'voltage': 36
                },
            7: {
                'description': 'Motion Power',
                'voltage': 36
                },
            8: {
                'description': 'Heater/Shaker and Chiller',
                'voltage': 24
                },
            9: {
                'description': 'Control Relay',
                'voltage': None
                },
            10: {
                'description': 'Interlock Relay',
                'voltage': None
                },
            }
        }

    # Constructor.
    def __init__(self):
        self.__FAST_API_INTERFACE = FastAPIInterface()

        # Set the default settings.
        self.__relay_state = 0 # OFF (IEC 60417-5008)

    # Getter Methods
    def get_id(self):
        return self.__id
    def get_relay_state(self):
        return self.__relay_state

    # Relayon Method
    def relayon(self, channel):
        # Send the command.
        self.__FAST_API_INTERFACE.chassis.relay.on(channel)

    # Relayoff Method
    def relayoff(self, channel):
        # Turn of the channel.
        self.__FAST_API_INTERFACE.chassis.relay.off(channel)

    # GPIO On Method.
    def gpio_on(self, channel):
        self.__FAST_API_INTERFACE.chassis.gpio.on(channel)

    # GPIO Off Method.
    def gpio_off(self, channel):
        self.__FAST_API_INTERFACE.chassis.gpio.off(channel)

    # Pump On Method.
    def turn_on_pump(self):
        pump_channel = 0
        self.gpio_on(pump_channel)

    # Pump Off Method.
    def turn_off_pump(self):
        pump_channel = 0
        self.gpio_off(pump_channel)

    # Control Relay On Method.
    def turn_on_control_relay(self):
        control_relay_channel = 10
        self.relayon(control_relay_channel)

    # Control Relay Off Method.
    def turn_off_control_relay(self):
        control_relay_channel = 10
        self.relayoff(control_relay_channel)

    def relayon_deprecated(self, channel):
        channels = [1-1, 2-1, 3-1]
        # Get the relayon command.
        command = self.__commands['relayon']
        # Repalce the address.
        command = replace_address(command, self.__address)
        # Replace the channel.
        command = replace_word(command, 'channel', channel)
        # Send the command.
        self.controller.write(command)
        self.__relay_state = 1 # ON (IEC 60417-5007)

    def relayoff_deprecated(self, channel):
        channels = [1-1, 2-1, 3-1]
        # Get the relayoff command.
        command = self.__commands['relayoff']
        # Replace the address.
        command = replace_address(command, self.__address)
        # Replace the channel.
        command = replace_word(command, 'channel', channel)
        # Send the command.
        self.__relay_state = 0 # OFF (IEC 60417-5008)