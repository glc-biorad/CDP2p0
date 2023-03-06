'''
'''

import multiprocessing 
from datetime import datetime

import time
from struct import pack, unpack
from ctypes import *

from api.util.utils import check_type, convert_hexidecimal_to_float32_ieee_754, convert_float32_to_hexidecimal_ieee_754, check_limit, delay

from api.util.controller import Controller

from api.reader.meerstetter.peltier_communication import PeltierCommunication
from api.reader.meerstetter.peltier_payload import PeltierPayload
from api.reader.meerstetter.peltier_parameters import PELTIER_PARAMETERS

from api.interfaces.fast_api_interface import FastAPIInterface

from api.util.logger import Logger
from api.util.timer import Timer

class Meerstetter():
    # Public variables.

    # Private variables.
    __controller = None
    __sequence_number = 1 # Starting at 2 since we get device address in __init__
    __sequence_numbers = [1,1,1,1,1,1,1,1,1]
    __device_status = None
    __device_address = 0
    __device_addresses = [1,2,3,4,5,6,7,8,9]

    # Private constants.
    __COM_PORT = 'COM8' # Unit A
    #__COM_PORT = 'COM5' # Unit D
    __BAUD_RATE = 57600
    __DATA_BITS = 8
    __PARITY = None
    __STOP_BITS = 1
    __HANDSHAKING = None
    
    # Private Constants (LIMITS).
    __LIMIT_MAX_TEMPERATURE = 120 #degC
    __LIMIT_MIN_TEMPERATURE = 2 #degC

    # Private constants (Thermocycler Address)
    __ADDRESSES = {
        1: 'Heater A',
        2: 'Heater B',
        3: 'Heater C',
        4: 'Heater D',
        5: 'Aux Heater A',
        6: 'Aux Heater B',
        7: 'Aux Heater C',
        8: 'Aux Heater D',
        9: 'PCR Thermocycler'
        }

    __reset_count = 0
    __temperatures = [None for i in range(1,10)]
    __target_temperatures = [None for i in range(1,11)]

    # Constructor.
    def __init__(self):
        # Setup the serial connection.
        # Setup the serial connection.
        self.__controller = Controller(self.__COM_PORT, self.__BAUD_RATE, dont_use_fast_api=True, timeout=1)
        self.__fast_api_interface = FastAPIInterface()
        # Get the device address.
        #self.__device_address = self.get_device_address()
        # Turn on Relays for Pre-Amp, A, B, C, D, Thermocyclers.
        #self.__fast_api_interface.chassis.relay.on(2)
        #self.__fast_api_interface.chassis.relay.on(3)
        #self.__fast_api_interface.chassis.relay.on(4)
        #self.__fast_api_interface.chassis.relay.on(5)
        #self.__fast_api_interface.chassis.relay.on(6)
        #time.sleep(2)
        # Enable temperature control.
        #self.enable_temperature_control(1)
        #self.enable_temperature_control(2)
        #self.enable_temperature_control(3)
        #self.enable_temperature_control(4)
        #self.enable_temperature_control(5)
        #self.enable_temperature_control(6)
        #self.enable_temperature_control(7)
        #self.enable_temperature_control(8)
        #self.enable_temperature_control(9)

    def __name_to_address(self, name):
        names = {
            'heater_a': 1,
            'heater_4': 1,
            'heater_b': 2,
            'heater_3': 2,
            'heater_c': 3,
            'heater_2': 3,
            'heater_d': 4,
            'heater_1': 4,
            'aux_heater_a': 5
            }

    def __calibrate_temperature(self, T):
        a = 1.3229
        b = -1.0585
        # calibrated_T = a * T + b
        calibrated_T = (T - b) / a
        return calibrated_T 

    # Get Device Address Method.
    def get_device_address(self):
        # Generate the payload (2051: Device Address) and communication.
        payload = PeltierPayload('get', 2051)
        pcom = PeltierCommunication('#', 0, self.__sequence_number, payload)
        logger = Logger(__file__, __name__)
        logger.log('SEND', pcom.to_string())
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number()
        # Get the response back.
        response = self.__controller.readline()
        logger.log('RECEIVED', response)
        # Compare the response.
        pcom.compare_with_response(response, assert_address=False, assert_checksum=False)
        # Get the address from the response.
        logger.log('MESSAGE', "Device address for this Peltier is {0}".format(int(response[7:-4])))
        return int(response[7:-4])

    # Get Device Status Method.
    def get_device_status(self, address, return_type=int):
        # Check return_type type.
        check_type(return_type, type)
        # Make sure the return_type is valid.
        return_types = [int, str]
        assert return_type in return_types
        # Generate the payload (104: Device Status) and communication.
        payload = PeltierPayload('get', 104)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response, assert_checksum=False)
        # Get the device status from the response.
        device_status_int = int(response[7:-4])
        if return_type == int:
            return device_status_int
        elif return_type == str:
            return PELTIER_PARAMETERS[104]["Description"][device_status_int]

    # Handle Device Status Method.
    def handle_device_status(self, address, reset_to_temperature=None):
        device_status_int = self.get_device_status(address)
        logger = Logger(__file__, self.handle_device_status.__name__)
        if device_status_int != 2:
            logger.log('LOG-START', "Handling the device status {0} for address {1}".format(device_status_int, address))
        if device_status_int == 3:
            # Restart the device.
            self.reset_device(address)
            logger.log("ERROR", "Restarting device with address {0}, this will take about 5 seconds due to {1}".format(address, self.get_device_status(address, str)))
            for i in range(5):
                print("\tTime Left (s): {0}".format(4 - i))
                time.sleep(1)
            if reset_to_temperature == None:
                self.__temperatures[address-1] = self.__temperatures[address-1]
            else:
                self.__temperatures[address-1] = reset_to_temperature
            self.change_temperature(address, self.__temperatures[address-1], block=False)
            logger.log('MESSAGE', "Device has been restarted setting temperature back to {0}".format(self.__temperatures[address-1]))
        if device_status_int != 2:
            logger.log('LOG-END', "Device status {0} handled.".format(device_status_int))

    # Get Temperature Method.
    def get_temperature(self, address, log=False):
        # Setup the logger.
        logger = Logger(__file__, self.get_temperature.__name__)
        if log:
            logger.log('LOG-START', "Getting the temperature of the peltier device.")
        # Generate the payload (1000: Object Temperature) and communication.
        payload = PeltierPayload('get', 1000)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response, assert_checksum=False)
        # Get the object temperature from the response.
        temperature_hexidecimal = response[7:-4]
        temperature = convert_hexidecimal_to_float32_ieee_754(temperature_hexidecimal)
        if log:
            logger.log('LOG-END', "Temperature of the peltier device is {0}.".format(temperature))
        self.__temperatures[address-1] = temperature
        return temperature

    # Change Temperature Method.
    def change_temperature(self, address, value, block=False):
        if type(value) == int:
            value = float(value)
        self.__target_temperatures[address] = value
        # Setup the logger.
        logger = Logger(__file__, self.change_temperature.__name__)
        # Make sure temperature choice is valid.
        if value > self.__LIMIT_MAX_TEMPERATURE:
            logger.log("WARNING", "Peltier cannot be set above {0}, changing {1} to {0}".format(self.__LIMIT_MAX_TEMPERATURE, value))
        elif value < self.__LIMIT_MIN_TEMPERATURE:
            logger.log("WARNING", "Peltier cannot be set below {0}, changing {1} to {0}".format(self.__LIMIT_MIN_TEMPERATURE, value))
        logger.log('LOG-START', "Changing the temperature of the peltier device with address {0} to {1} degC with blocking set to {2}.".format(address, value, block))
        # Generate the payload (3000: Target Object Temp) and communication.
        payload = PeltierPayload('set', 3000, value=value)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        t_start = time.time()
        response = self.__controller.readline()
        print(f'Timing of getting response from Meerstetter: {time.time() - t_start}')
        # Compare the response.
        pcom.compare_with_response(response)
        if block:
            delta = 2
            for i in range(0,10*60,10):
                temperature = self.get_temperature(address)
                if abs(temperature - value) < delta:
                    logger.log('LOG-END', "Changed the temperature of the peltier device.")
                    self.__temperatures[address-1] = value
                    return
                time.sleep(10)
        logger.log('LOG-END', "Changed the temperature of the peltier device.")
        self.__temperatures[address-1] = value

    # Increase Sequence Number Method.
    def __increase_sequence_number(self, address=None):
        if address == None:
            self.__sequence_number = self.__sequence_number + 1
        else:
            self.__sequence_numbers[address-1] = self.__sequence_numbers[address-1] + 1

    # Change Fan Temperature Method.
    def change_fan_temperature(self, address, value):
        if type(value) == int:
            value = float(value)
        # Use the calibrated temperature to set the true value from the desired temperature.
        # Generate the payload (6211: Target Temperature) and communication.
        payload = PeltierPayload('set', 6211, value=value)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response)

    # Enable Fan Method.
    def enable_fan(self, address):
        # Setup the logger.
        logger = Logger(__file__, self.enable_fan.__name___)
        logger.log('LOG-START', "Enabling the fan of the peltier device.")
        # Generate the payload (6200: Fan Control Enable) and communication.
        payload = PeltierPayload('set', 6200, value=1) # 1: Enabled
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response)
        logger.log('LOG-END', "Enabled the fan of the peltier device.")

    # Disable Fan Method.
    def disable_fan(self, address):
        # Generate the payload (6200: Fan Control Enable) and communication.
        payload = PeltierPayload('set', 6200, value=0) # 1: Enabled
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response)

    # Enable Temperature Control Method.
    def enable_temperature_control(self, address):
        # Generate the payload (2010: Status) and communication.
        payload = PeltierPayload('set', 2010, value=1) # 1: Static ON
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        logger = Logger(__file__, __name__)
        logger.log('SEND', pcom.to_string())
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        logger.log('RECEIVED', response)
        # Compare the response.
        #pcom.compare_with_response(response)

    # Disable Temperature Control Method.
    def disable_temperature_control(self, address):
        # Generate the payload (2010: Status) and communication.
        payload = PeltierPayload('reset')
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        print(pcom.to_string())
        #self.__controller.write(pcom.to_string())
        #self.__increase_sequence_number()
        # Get the response back.
        #response = self.__controller.readline()
        # Compare the response.
        #pcom.compare_with_response(response)

    # Reset Device Method.
    def reset_device(self, address):
        self.__reset_count = self.__reset_count + 1
        from api.util.crc import compute_crc16_xmodem
        # Setup the logger.
        logger = Logger(__file__, self.reset_device.__name__)
        logger.log('LOG-START', "Restarting Peltier device.")
        # Generate the payload (2010: Status) and communication.
        payload = PeltierPayload('reset', 2010, value=1) # 1: Static OFF
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        pcom_string = pcom.to_string()
        pcom_string = pcom_string.replace('0' + hex(2010)[2:].upper(), '')[:-4]
        pcom_string = '#0{0}000{1}RS000001'.format(address, self.__sequence_numbers[address-1])
        checksum = compute_crc16_xmodem(pcom_string)
        pcom_string = pcom_string + checksum + '\r'
        self.__controller.write(pcom_string)
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        #pcom.compare_with_response(response)
        logger.log('LOG-END', "Restarting Peltier device has been restarted.")

    # Monitor Device Method.
    def monitor_device(self, address, time_length_seconds, check_in_every_N_seconds=0):
        # Setup the logger.
        logger = Logger(__file__, self.monitor_device.__name__)
        logger.log("LOG-START", "Monitoring the peltier device for {0} seconds".format(time_length_seconds))
        if check_in_every_N_seconds == 0:
            check_in = False
            check_in_every_N_seconds = 1
        else:
            check_in = True
        time_start = time.time()
        while time.time() - time_start < time_length_seconds:
        #for i in range(0, time_length_seconds, check_in_every_N_seconds):
            self.handle_device_status(address, self.__target_temperatures[address])
            #time.sleep(check_in_every_N_seconds)
            if check_in:
                logger.log('MESSAGE', "Peltier device state is {0} with a temperature of {1}".format(self.get_device_status(address, str), self.get_temperature(address)))
        logger.log("LOG-END", "Done monitoring the peltier device.")

    def monitor_devices_2(self, address_1, address_2, time_length_seconds, check_in_every_N_seconds=0):
        # Setup the logger.
        logger = Logger(__file__, self.monitor_device.__name__)
        logger.log("LOG-START", "Monitoring the peltier device {0} and {1} for {2} seconds".format(address_1, address_2, time_length_seconds))
        if check_in_every_N_seconds == 0:
            check_in = False
            check_in_every_N_seconds = 1
        else:
            check_in = True
        time_start = time.time()
        time_check_in = time_start
        while time.time() - time_start < time_length_seconds:
            self.handle_device_status(address_1, self.__target_temperatures[address_1])
            self.handle_device_status(address_2, self.__target_temperatures[address_2])
            if check_in and time.time() - time_check_in >= check_in_every_N_seconds:
                time_check_in = time.time()
                logger.log('MESSAGE', "Peltier device {0} state is {1} with a temperature of {2}".format(address_1, self.get_device_status(address_1, str), self.get_temperature(address_1)))
                logger.log('MESSAGE', "Peltier device {0} state is {1} with a temperature of {2}".format(address_2, self.get_device_status(address_2, str), self.get_temperature(address_2)))
        logger.log("LOG-END", "Done monitoring the peltier devices {0} and {1}.".format(address_1, address_2))

    def monitor_devices_3(self, address_1, address_2, address_3, time_length_seconds, check_in_every_N_seconds=0):
        # Setup the logger.
        logger = Logger(__file__, self.monitor_device.__name__)
        logger.log("LOG-START", "Monitoring the peltier device {0}, {1} for {2} seconds".format(address_1, address_2, time_length_seconds))
        if check_in_every_N_seconds == 0:
            check_in = False
            check_in_every_N_seconds = 1
        else:
            check_in = True
        time_start = time.time()
        time_check_in = time_start
        while time.time() - time_start < time_length_seconds:
            self.handle_device_status(address_1, self.__target_temperatures[address_1])
            self.handle_device_status(address_2, self.__target_temperatures[address_2])
            if check_in and time.time() - time_check_in >= check_in_every_N_seconds:
                time_check_in = time.time()
                logger.log('MESSAGE', "Peltier device {0} state is {1} with a temperature of {2}".format(address_1, self.get_device_status(address_1, str), self.get_temperature(address_1)))
                logger.log('MESSAGE', "Peltier device {0} state is {1} with a temperature of {2}".format(address_2, self.get_device_status(address_2, str), self.get_temperature(address_2)))
        logger.log("LOG-END", "Done monitoring the peltier devices {0} and {1}.".format(address_1, address_2))

    def monitor_devices(self, addresses: list, time_length_seconds: int, check_in_every_N_seconds: int = 0) -> None:
        """ Monitors the TEC boards for a given time to handle errors to reset the board

        Parameters
        ----------
        addresses : list
            list of addresses to be monitored during the hold
        time_length_seconds : int
            how long to hold the monitor for
        check_in_every_N_seconds (optional) : int
            How often to print an update
        """
        # Setup the logger.
        logger = Logger(__file__, self.monitor_device.__name__)
        logger.log("LOG-START", f"Monitor Peltier Devices with addresses {addresses} for a hold time of {time_length_seconds} seconds")
        if check_in_every_N_seconds == 0:
            check_in = False
            check_in_every_N_seconds = 1
        else:
            check_in = True
        time_start = time.time()
        time_check_in = time_start
        while time.time() - time_start < time_length_seconds:
            for address in addresses:
                self.handle_device_status(address, self.__target_temperatures[address])
            if check_in and time.time() - time_check_in >= check_in_every_N_seconds:
                time_check_in = time.time()
                for address in addresses:
                    logger.log('MESSAGE', "Peltier device {0} state is {1} with a temperature of {2}".format(address, self.get_device_status(address, str), self.get_temperature(address)))
        logger.log("LOG-END", "Done monitoring the peltier devices addresses {0}.".format(addresses))

    # Calibration Method.
    def calibration(self, heater_label, temp_value, monitor_time):
        check_type(heater_label, str)
        labels = ['A', 'B', 'C', 'D']
        msg = "Run calibration on heater {0} [y/n]".format(heater_label.upper())
        if msg.lower() == 'y':
            msg = "Is the thermocuouple connected to heater {0} for calibration? [y/n]".format(heater_label.upper())
            if msg.lower() == 'y':
                # Set the temperature.
                self.change_temperature(temp_value)
                self.monitor_device(monitor_time, 1)

    # Enable Write to Flash Method.
    def write_to_flash_enable(self, address):
        enabled_value = 0
        # Setup the logger.
        logger = Logger(__file__, __name__)
        logger.log('LOG-START', "Enabling writing data to flash for the peltier device.")
        # Generate the payload (108: Save data to Flash) and communication.
        payload = PeltierPayload('set', 108, value=enabled_value)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        #pcom.compare_with_response(response)
        logger.log('LOG-END', "Writing to flash is now enabled on the peltier device.")

    # Disable Write to Flash Method.
    def write_to_flash_disable(self, address):
        disabled_value = 1
        # Setup the logger.
        logger = Logger(__file__, __name__)
        logger.log('LOG-START', "Disabling writing data to flash for the peltier device.")
        # Generate the payload (108: Save data to Flash) and communication.
        payload = PeltierPayload('set', 108, value=disabled_value)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        #pcom.compare_with_response(response)
        logger.log('LOG-END', "Writing to flash is now disabled on the peltier device.")

    # Set Address Method.
    def set_address(self, address, new_address):
        from api.util.crc import compute_crc16_xmodem
        # Setup the logger.
        logger = Logger(__file__, __name__)
        logger.log('LOG-START', "Setting the address for the Peltier device to {0}.".format(address))
        # Generate the payload (2010: Status) and communication.
        payload = PeltierPayload('set', 2051, value=new_address) 
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        pcom_string = pcom.to_string()
        pcom_string = pcom_string.replace('0' + hex(2010)[2:].upper(), '')[:-4]
        #pcom_string = '#0{0}000{1}SA00000{2}'.format(self.__device_address, self.__sequence_number, address)
        checksum = compute_crc16_xmodem(pcom_string)
        pcom_string = pcom_string + checksum + '\r'
        logger.log('SEND', pcom_string)
        self.__controller.write(pcom_string)
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        logger.log('RECEIVED', response)
        # Compare the response.
        #pcom.compare_with_response(response)
        logger.log('LOG-END', "The address to the Peltier device has been set to {0}.".format(address))

    def thermocycle_2(self, h1, h2, number_of_cycles, high_T, high_T_time, high_T_time_units, low_T, low_T_time, low_T_time_units, high_T_2, low_T_2):
        """
        Thermocycle for a certain number of cycles between a high and low temperature
        for certain times at each temperature.
        
        Inputs:
        - number_of_cycles (int): number of cycles for thermocycling between the two temperatures.
        - high_T (int): high temperature of the thermocycling protocol.
        - high_T_time (int): time to sit at high_T
        - high_T_time_unit (str): unit of time for high_T_time
        - low_T (int): low temperature of the thermocycling protocol.
        - low_T_time (int): time to sit at low_T
        - low_T_time_unit (str): unit of time for low_T_time

        Notes:
        - max temperature = 110 degC
        - min temperature = 3 degC
        - high_T must be larger than low_T
        - time units are either 'seconds', 'minutes', 'hours'
        """
        logger = Logger(__file__, __name__)
        T_max = 110
        T_min = 3
        check_type(number_of_cycles, int)
        check_type(high_T, int)
        check_type(high_T_time, int)
        check_type(high_T_time_units, str)
        check_type(low_T, int)
        check_type(low_T_time, int)
        check_type(low_T_time_units, str)
        check_limit(high_T, low_T, '>')
        check_limit(high_T, T_max, '<=')
        check_limit(low_T, T_max, '<=')
        check_limit(low_T, T_min, '>=')
        check_limit(high_T, T_min, '>=')
        check_limit(number_of_cycles, 0, '>')
        logger.log('LOG-START', "Starting a Thermocycling protocol with {0} cycles between {1} degC for {2} {3} and {4} degC for {5} {6} on {7}.".format(number_of_cycles, high_T, high_T_time, high_T_time_units, low_T, low_T_time, low_T_time_units, h1))
        cycles = [i for i in range(number_of_cycles)]
        for cycle in cycles:
            logger.log('MESSAGE', "Thermocycling Cycle Number: {0} of {1}".format(cycle, number_of_cycles))
            self.change_temperature(h1, high_T, block=False)
            self.change_temperature(h2, high_T_2, block=False)
            self.monitor_devices_2(h1, h2, high_T_time, 10)
            self.change_temperature(h1, low_T, block=False)
            self.change_temperature(h2, low_T_2, block=False)
            self.monitor_devices_2(h1, h2, low_T_time, 10)
        logger.log('WARNING', "During thermocycling on {0}, the meerstetter was reset {1} times.".format(h1, self.__reset_count))
        logger.log('LOG-END', "Thermocycling is now complete for {0}.".format(h1))

    def thermocycle(self, heater_name, number_of_cycles, high_T, high_T_time, high_T_time_units, low_T, low_T_time, low_T_time_units):
        """
        Thermocycle for a certain number of cycles between a high and low temperature
        for certain times at each temperature.
        
        Inputs:
        - number_of_cycles (int): number of cycles for thermocycling between the two temperatures.
        - high_T (int): high temperature of the thermocycling protocol.
        - high_T_time (int): time to sit at high_T
        - high_T_time_unit (str): unit of time for high_T_time
        - low_T (int): low temperature of the thermocycling protocol.
        - low_T_time (int): time to sit at low_T
        - low_T_time_unit (str): unit of time for low_T_time

        Notes:
        - max temperature = 110 degC
        - min temperature = 3 degC
        - high_T must be larger than low_T
        - time units are either 'seconds', 'minutes', 'hours'
        """
        logger = Logger(__file__, __name__)
        T_max = 110
        T_min = 3
        check_type(number_of_cycles, int)
        check_type(high_T, int)
        check_type(high_T_time, int)
        check_type(high_T_time_units, str)
        check_type(low_T, int)
        check_type(low_T_time, int)
        check_type(low_T_time_units, str)
        check_limit(high_T, low_T, '>')
        check_limit(high_T, T_max, '<=')
        check_limit(low_T, T_max, '<=')
        check_limit(low_T, T_min, '>=')
        check_limit(high_T, T_min, '>=')
        check_limit(number_of_cycles, 0, '>')
        logger.log('LOG-START', "Starting a Thermocycling protocol with {0} cycles between {1} degC for {2} {3} and {4} degC for {5} {6} on {7}.".format(number_of_cycles, high_T, high_T_time, high_T_time_units, low_T, low_T_time, low_T_time_units, heater_name))
        cycles = [i for i in range(number_of_cycles)]
        for cycle in cycles:
            logger.log('MESSAGE', "Thermocycling Cycle Number: {0}".format(number_of_cycles))
            self.change_temperature(heater_name, high_T, block=False)
            self.monitor_device(heater_name, high_T_time, 10)
            self.change_temperature(heater_name, low_T, block=False)
            self.monitor_device(heater_name, low_T_time, 10)
        logger.log('WARNING', "During thermocycling on {0}, the meerstetter was reset {1} times.".format(heater_name, self.__reset_count))
        logger.log('LOG-END', "Thermocycling is now complete for {0}.".format(heater_name))

    def get_checksum(self, value):
        from api.util.crc import compute_crc16_xmodem
        print(compute_crc16_xmodem(value))

    def test1(self, address):
        # Generate the payload (1000: Object Temperature) and communication.
        payload = PeltierPayload('get', 1000)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response, assert_checksum=False)
        # Get the object temperature from the response.
        temperature_hexidecimal = response[7:-4]
        temperature = convert_hexidecimal_to_float32_ieee_754(temperature_hexidecimal)
        self.__temperatures[address-1] = temperature
        print(f"Address ({address}) is at {temperature}")

    def test2(self, address):
        # Generate the payload (1000: Object Temperature) and communication.
        payload = PeltierPayload('get', 1000)
        pcom = PeltierCommunication('#', address, self.__sequence_numbers[address-1], payload)
        self.__controller.write(pcom.to_string())
        self.__increase_sequence_number(address)
        # Get the response back.
        response = self.__controller.readline()
        # Compare the response.
        pcom.compare_with_response(response, assert_checksum=False)
        # Get the object temperature from the response.
        temperature_hexidecimal = response[7:-4]
        temperature = convert_hexidecimal_to_float32_ieee_754(temperature_hexidecimal)
        self.__temperatures[address-1] = temperature
        print(f"Address ({address}) is at {temperature}")

    def test3(self):
        p1 = multiprocessing.Process(target=self.test1)
        p2 = multiprocessing.Process(target=self.test1)
        p1.start()
        p2.start()

    def multiprocessing_thermocycling(self, address: int, n_cycles: int, 
                                      denature_temperature: int, anneal_temperature: int, extension_temperature: int,
                                      denature_time: int, anneal_time: int, extension_time: int,
                                      final_temperature=30) -> None:
        cycles = [i for i in range(n_cycles)]
        checkin_time = 10
        # Denature for the denature time.
        self.change_temperature(address, denature_temperature)
        time.sleep(0.3)
        time_start = time.time()
        now = datetime.now()
        time_start = (now.hour * 60 * 60) + (now.minute * 60) + now.second
        i = 1
        while (datetime.now().hour * 60 * 60) + (datetime.now().minute * 60) + datetime.now().second - time_start >= denature_time:
            print(f"\nHeater {address} Denature Time Left: {denature_time - (time.time() - time_start)}\n")
            if time.time() - time_start() >= checkin_time * i:
                print(f"\nHeater {address} Denature Time Left: {denature_time - (time.time() - time_start)}\n")
                i = i + 1
        # Cycle for n cycles.
        for cycle in cycles:
            print(f"Time now: ")
            print(f"\nHeater {address} Cycle Progress: {cycle+1}/{n_cycles}\n")
            # High temperature for a time.
            self.change_temperature(address, extension_temperature)
            time.sleep(0.3)
            time_start = time.time()
            now = datetime.now()
            time_start = (now.hour * 60 * 60) + (now.minute * 60) + now.second
            i = 1
            while (datetime.now().hour * 60 * 60) + (datetime.now().minute * 60) + datetime.now().second - time_start >= extension_time:
                print(f"\nHeater {address} Extension Time Left: {extension_time - (time.time() - time_start)}\n")
                if time.time() - time_start() >= checkin_time * i:
                    print(f"\nHeater {address} Extension Time Left: {extension_time - (time.time() - time_start)}\n")
                    i = i + 1
            # Low temperature for a time.
            self.change_temperature(address, anneal_temperature)
            time.sleep(0.3)
            time_start = time.time()
            now = datetime.now()
            time_start = (now.hour * 60 * 60) + (now.minute * 60) + now.second
            i = 1
            while (datetime.now().hour * 60 * 60) + (datetime.now().minute * 60) + datetime.now().second - time_start >= anneal_time:
                print(f"\nHeater {address} Anneal Time Left: {anneal_time - (time.time() - time_start)}\n")
                if time.time() - time_start() >= checkin_time * i:
                    print(f"\nHeater {address} Anneal Time Left: {anneal_time - (time.time() - time_start)}\n")
                    i = i + 1
        # Cool to a low temperature.
        self.change_temperature(address, final_temperature)
        time.sleep(0.3)

    def thermocycle_3(self, addresses: list, cycles: list,
                      denature_temperatures: list, anneal_temperatures: list, extension_temperatures: list,
                      denature_times: list, anneal_times: list, extension_times: list,
                      final_temperatures: list = [30, 30, 30]) -> None:
        # Setup the processes for the three addresses.
        processes = [
            multiprocessing.Process(target = self.multiprocessing_thermocycling(addresses[i], cycles[i], 
                                                                                denature_temperatures[i], 
                                                                                anneal_temperatures[i], 
                                                                                extension_temperatures[i], 
                                                                                denature_times[i], 
                                                                                anneal_times[i], 
                                                                                extension_times[i])) for i in range(len(addresses))
            ]
        # Start the processes.
        for process in processes:
            print(f"\nStarting Process {process}\n")
            process.start()

    # Close Method.
    def close(self):
        self.__controller.close()

if __name__ == '__main__':
    peltier = Meerstetter()
    peltier.reset_device()
    #peltier.change_temperature(150.0)
    #peltier.enable_fan()
    #peltier.change_fan_temperature(30.0)
    #peltier.disable_fan()

    # 