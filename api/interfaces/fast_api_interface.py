
# Version: Test
'''
'''

# pythonnet
#import pythonnet
#from pythonnet import load

#load("coreclr")

import clr

clr.AddReference('System.Net')
clr.AddReference('System.IO')
clr.AddReference('System.Text.Encoding')

from System.Net import WebRequest
from System.IO import StreamReader
from System.Text import ASCIIEncoding

import ast
import os
import time
import asyncio

from api.util.logger import Logger

FAST_API_URL_BASE = 'http://127.0.0.1:8000/'

FAST_API_URL_PATHS = {
        'chassis': {
            'raw': {},
            'power': {},
            'relay': {
                '': {
                    'method': 'POST',
                    'url': 'chassis/relay/{chan}'
                    },
                },
            'gpio': {
                '': {
                    'method': 'POST',
                    'url': 'chassis/GPIO Port E/{chan}'
                    },
                },
            'utils' :{}
        },
        'pipettor_gantry': {
            'axis': {
                '': {
                    'method': 'GET',
                    'url': 'pipettor_gantry/axis/position/{id}'
                    },
                'move': {
                    'method': 'POST',
                    'url': 'pipettor_gantry/axis/move/{id}'
                    },
                'jog': {
                    'method': 'POST',
                    'url': 'pipettor_gantry/axis/jog/{id}'
                    },
                'home': {
                    'method': 'POST',
                    'url': 'pipettor_gantry/axis/home/{id}'
                    },
                },
            'pipettor': {},
            'air_valve_on': {
                '': {
                    'method': 'POST',
                    'url': 'pipettor_gantry/air_valve_on/{chan}'
                    },
                },
            'air_valve_off': {
                '': {
                    'method': 'POST',
                    'url': 'pipettor_gantry/air_valve_off/{chan}'
                    },
                },
        },
        'prep_deck': {
            'chiller-heater-shaker_raw_command' : {
                '': {
                    'method': 'GET',
                    'url': 'prep_deck/chiller-heater-shaker_raw_command/{id,command}'
                    }
            },
            'axis': {
                '': {
                    'method': 'GET',
                    'url': 'prep_deck/axis/position/'
                    },
                'move': {
                    'method': 'POST',
                    'url': 'prep_deck/axis/move/'
                    },
                'home': {
                    'method': 'POST',
                    'url': 'prep_deck/axis/home/'
                    },
                },
            'meerstetter': {},
            'heater': {},
        },
        'reader': {
            'axis': {
                '': {
                    'method': 'GET',
                    'url': 'reader/axis/position/{id}'
                    },
                'move': {
                    'method': 'POST',
                    'url': 'reader/axis/move/{id}'
                    },
                'jog': {
                    'method': 'POST',
                    'url': 'reader/axis/jog/{id}'
                    },
                'home': {
                    'method': 'POST',
                    'url': 'reader/axis/home/{id}'
                    },
                },
            'led': {
                '': {
                    'method': 'POST',
                    'url': 'reader/led/{id}'
                    },
                'off': {
                    'method': 'POST',
                    'url': 'reader/led/{id}/off'
                    }
                }
        },
    }

def add_fast_api_parameters(url, parameters_dict):
    first_parameter = True
    for parameter in parameters_dict:
        if first_parameter:
            url = url + '?'
            first_parameter = False
        'http://127.0.0.1:8000/pipettor_gantry/axis/move/1?position=-100000&velocity=50000'
        url = url + str(parameter) + '=' + str(parameters_dict[parameter]) + '&'
    return url[:-1]

def __retry(url, method, max_attempts=4, verbose=False):
        logger = Logger(__file__, __name__)
        for i in range(max_attempts):
            logger.log('MESSAGE', "The first attempt at sending {0} failed, will try again up to {1} times".format(url, max_attempts))
            logger.log('SEND', url)
            request = WebRequest.Create(url)
            request.Method = method
            response = request.GetResponse()
            status_code = response.StatusCode
            logger.log('RECEIVED', "Status Code: {0}".format(status_code))
            if str(status_code) == 'OK':
                return
        if str(status_code) != 'OK':
            logger('ERROR', "After {0} attempts {1} could not be sent successfully.".format(max_attempts, url))

class LED():
    # Public variables.
    # Private variables.
    __parameters_dict = {
        'channel': None,
        'intensity': None,
        }
    # Private constants.
    # Constructor.
    def __init__(self):
        a = 1

    # On Method.
    def on(self, id:int , channel: int, intensity: int):
        logger = Logger(__file__, __name__)
        # Update the parameters dict.
        self.__parameters_dict = {}
        self.__parameters_dict['channel'] = channel
        self.__parameters_dict['intensity'] = intensity
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['reader']['led']['']['url']
        url = url.replace('{id}', str(id))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['reader']['led']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)  

    # Off Method.
    def off(self, id, channel):
        logger = Logger(__file__, __name__)
        # Update parameters dict.
        self.__parameters_dict = {}
        self.__parameters_dict['channel'] = channel
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['reader']['led']['off']['url']
        url = url.replace('{id}', str(id))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['reader']['led']['off']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method) 

class Axis():
    # Public variables.
    # Private variables.
    __parameters_dict = {
        'position': None,
        'velocity': None
        }
    # Private constants.
    # Private constants
    __LIMITS = {
        'pipettor_gantry': {
            1: 300000, #microsteps per second
            2: 3200000,
            3: 800000,
            4: 2500000
            },
        'reader': {
            1: 100000,
            2: 1000000,
            3: 100000,
            4: 100000,
            6: 200000,
            7: 200000,
            8: 100000,
            9: 100000,
            10: 100000,
            11: 100000,
            },
        'prep_deck': {
            6: 50000 # Mag Separator
            }
        }

    # Constructor.
    def __init__(self):
        a = 1

    def __block(self, wait_time=7):
        print("Waiting {0} seconds...".format(wait_time))
        for i in range(wait_time):
            print("Seconds left: {0}".format(wait_time-i))
            time.sleep(1)

    def __retry(self, url, method, max_attempts=4, verbose=False):
        for i in range(max_attempts):
            if verbose:
                print("Warning (fast_api_interface, __retry): no response, attempt ({0}/{1}) with url {2}".format(i, max_attempts, url))
            request = WebRequest.Create(url)
            request.Method = method
            response = request.GetResponse()
            status_code = response.StatusCode
            if str(status_code) == 'OK':
                return
        if str(status_code) != 'OK':
            print("ERROR (fast_api_interface, __retry): no response, out of attempts with url {0}".format(url))

    # Get Status and Position Method.
    def get_position(self, module_name, id, verbose=True):
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS[module_name]['axis']['']['url']
        if module_name.lower() != 'prep_deck':
            url = url.replace('{id}', str(id))
        # Generate the request.
        request = WebRequest.Create(url)
        if verbose:
            logger = Logger(__file__, __name__)
            logger.log('SEND', url)
        method = FAST_API_URL_PATHS[module_name]['axis']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        if str(status_code) != 'OK':
            self.__retry()  
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        try:
            value = int(response_str.split(':')[-1].split(',')[-1].replace('\\r"}',''))
            if verbose:
                logger.log('RECEIVED', response_str)
        except ValueError:
            value = None
        return value

    def block_till_value_reached(self, module_name, id, value, cutoff=0.01, max_timeout=55, checkin_time=0.25, verbose=True):
        logger = Logger(__file__, self.block_till_value_reached.__name__)
        time_start = time.time()
        value_changed = True
        value_was = 0.19
        id_strs = {
            'pipettor_gantry': {
                1: 'X',
                2: 'Y',
                3: 'Z',
                4: 'Drip Plate'
                },
            'reader': {
                1: 'X',
                2: 'Y',
                3: 'Z',
                4: 'Filter Wheel',
                6: 'Tray AB',
                7: 'Tray CD',
                8: 'Heater A',
                9: 'Heater B',
                10: 'Heater C',
                11: 'Heater D'
                }
            }

        #for i in range(max_timeout):
        while time.time() - time_start <= max_timeout:
            response_value = self.get_position(module_name, id)
            id_str = id_strs[module_name][id]
            if abs(response_value - value) <= cutoff:
                logger.log("MESSAGE", "{0} reached in {1} seconds for {2} module along {3}".format(value, time.time() - time_start, module_name, id_str))
                return
            else:
                print(time.time() - time_start)
            time.sleep(checkin_time)
            if value_was - response_value == 0:
                value_changed = False
            if value_changed == False:
                if int(value) == 0:
                    self.home(module_name, id)
                else:
                    self.move(module_name, id, value, self.__LIMITS[module_name][id], block=True)
            value_was = response_value
        logger.log("ERROR", "{0} not reached within a cutoff of {1} in a max timeout of {2} for the {3} module along the {4} axis".format(value, cutoff, max_timeout, module_name, id_str))

    def test_block_till_value_reached(self, module_name, id, value, cutoff=0.01, max_timeout=55, checkin_time=0.25, verbose=True):
        logger = Logger(__file__, self.block_till_value_reached.__name__)
        time_start = time.time()
        value_changed = True
        value_was = 0.19
        id_strs = {
            'pipettor_gantry': {
                1: 'X',
                2: 'Y',
                3: 'Z',
                4: 'Drip Plate'
                },
            'reader': {
                1: 'X',
                2: 'Y',
                3: 'Z',
                4: 'Filter Wheel',
                6: 'Tray AB',
                7: 'Tray CD',
                8: 'Heater A',
                9: 'Heater B',
                10: 'Heater C',
                11: 'Heater D'
                }
            }
        # Create the task for reaching the value for the position
        #asyncio.run(self.__are_we_there_yet(module_name, id, value))
        self.__are_we_there_yet(module_name, id, value)

    # Are We There Yet
    #async def __are_we_there_yet(self, module_name: str, id: int, value: int) -> None:
    def __are_we_there_yet(self, module_name: str, id: int, value: int) -> None:
        velocity = {'pipettor_gantry': {1: 300000, 2: 3200000, 3: 800000, 4: 2500000},}
        time_start = time.time()
        # Get the current position
        current_position = self.get_position(module_name, id)
        # Compare with where we want to be
        diff = abs(current_position - value)
        # Estimate a time left
        time_left = diff / float(velocity[module_name][id])
        while diff != 0:
            # Get the current position
            current_position = self.get_position(module_name, id)
            # Compare with where we want to be
            diff = abs(current_position - value)
            # Estimate a time left
            time_left = diff / float(velocity[module_name][id])
            if time_left <= 0.3:
                return True
        return True

    # Move Method.
    def move(self, module_name, id, position, velocity, block=True, use_fast_api=True):
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.move.__name__))
        if position > 0:
            position = -position
        if module_name == 'pipettor_gantry':
            if id == 4:
                if position < -1198000:
                    position = 0
        # Update the parameters.
        self.__parameters_dict['position'] = position
        self.__parameters_dict['velocity'] = velocity
        # Get the current positon to see if a move needs to occur.
        #value = self.get_position(module_name, id)
        #if value == position:
        #    logger.log('MESSAGE', "Already at the {0} along the axis {1}".format(value, id))
            #return
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS[module_name]['axis']['move']['url']
        if module_name.lower() != 'prep_deck':
         url = url.replace('{id}', str(id))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS[module_name]['axis']['move']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            self.__retry()  
        if block == False:
            return
        elif block and use_fast_api == False:
            self.__block()
        elif block and use_fast_api:
            #asyncio.run(self.test_block_till_value_reached(module_name, id, position))
            self.test_block_till_value_reached(module_name, id, position)
            #self.block_till_value_reached(module_name, id, position)

    # Jog Method.

    # Home Method.
    def home(self, module_name, id, block=True, use_fast_api=True):
        # Get the current positon to see if a move needs to occur.
        value = self.get_position(module_name, id)
        #if value == 0:
        #    return
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS[module_name]['axis']['home']['url']
        if module_name.lower() != 'prep_deck':
            url = url.replace('{id}', str(id))
        # Generate the request.
        logger = Logger(os.path.split(__file__)[1], '{0}.{1}'.format(__name__, self.home.__name__))
        logger.log('SEND', url)
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS[module_name]['axis']['home']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            self.__retry() 
        if block and use_fast_api == False:
            self.__block()
        elif block and use_fast_api:
            self.block_till_value_reached(module_name, id, 0)

class AirValve():
    # Public variables.
    # Private variables.
    # Private constants.
    __CHANNELS = {
        0: {
            'valve': 1,
            'description': 'High Pressure Compressor (Tip Eject)'
            },
        1: {
            'valve': 2,
            'description': 'Pipettor Vacuum (Aspirate/Dispense)'
            },
        2: {
            'valve': 3,
            'description': 'Vacuum Pickup (Suction Cups)'
            }
        }
    # Constructor.
    def __init__(self):
        a = 1 

    # On Method.
    def on(self, chan):
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['pipettor_gantry']['air_valve_on']['']['url']
        url = url.replace('{chan}', str(chan-1))
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['pipettor_gantry']['air_valve_on']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)

    # Off Method.
    def off(self, chan):
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['pipettor_gantry']['air_valve_off']['']['url']
        url = url.replace('{chan}', str(chan-1))
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['pipettor_gantry']['air_valve_off']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)

class GPIO():
    # Public variables.
    # Private variables.
    __parameters_dict = {
        'state': None,
        }
    # Private constants.
    # Constructor.
    def __init__(self):
        a = 1 

    # On Method.
    def on(self, chan):
        # Update the parameters dict.
        self.__parameters_dict['state'] = True
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['chassis']['gpio']['']['url']
        url = url.replace('{chan}', str(chan))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['chassis']['gpio']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        logger.log('RECEIVED', response_str)

    # Off Method.
    def off(self, chan):
        # Update the parameters dict.
        self.__parameters_dict['state'] = False
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['chassis']['gpio']['']['url']
        url = url.replace('{chan}', str(chan))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['chassis']['gpio']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        logger.log('RECEIVED', response_str)

class Relay():
    # Public variables.
    # Private variables.
    __parameters_dict = {
        'state': None,
        }
    # Private constants.
    __CHANNELS = {
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

    # Constructor.
    def __init__(self):
        a = 1 

    # Get Relay Info.
    def get_relay_info(self, relay_id):
        relay_dict = {
            'channel': relay_id - 1,
            'description': self.__CHANNELS[relay_id]['description'],
            'voltage': self.__CHANNELS[relay_id]['voltage']
            }
        return relay_dict

    # On Method.
    def on(self, relay_number):
        chan = relay_number - 1
        # Update the parameters dict.
        self.__parameters_dict['state'] = True
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['chassis']['relay']['']['url']
        url = url.replace('{chan}', str(chan))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['chassis']['relay']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        logger.log('RECEIVED', response_str)

    # Off Method.
    def off(self, relay_number):
        chan = relay_number - 1
        # Update the parameters dict.
        self.__parameters_dict['state'] = False
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['chassis']['relay']['']['url']
        url = url.replace('{chan}', str(chan))
        url = add_fast_api_parameters(url, self.__parameters_dict)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['chassis']['relay']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        logger.log('RECEIVED', response_str)

class HeaterShaker:
    def __init__(self, ID: int = 2) -> None:
        """ Initialize the Heater/Shaker """
        self.ID = 2

    def ton(self):
        """ Turn on temp control """
        command = 'ton'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        print(response_str)
        logger.log('RECEIVED', response_str)

    def toff(self):
        """ Turn off temp control """
        command = 'toff'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        print(response_str)
        logger.log('RECEIVED', response_str)

    def gtt(self):
        """ Get Target Temp """
        command = 'gtt'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        print(url)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        response_dict = ast.literal_eval(response_str)
        temp = response_dict['response'].rstrip('\r').rstrip('\n')
        logger.log('RECEIVED', response_str)
        return float(temp)

    def gat(self) -> float:
        """ Get Actual Temp """
        command = 'gat'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        print(url)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        response_dict = ast.literal_eval(response_str)
        temp = response_dict['response'].rstrip('\r').rstrip('\n')
        logger.log('RECEIVED', response_str)
        return float(temp)

    def stt(self, temp: float) -> None:
        """ Set Target Temp """
        temp = str(round(temp,1))
        if len(temp) == 2:
            temp = temp + '0'
        elif len(temp) == 1:
            temp = '0' + temp + '0'
        command = f'stt{temp}'.replace('.','')
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        print(url)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        print(response_str)
        logger.log('RECEIVED', response_str)
     
    def shake_on(self):
        """ Start shaking with the current mixing speed """
        command = 'son'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        print(response_str)
        logger.log('RECEIVED', response_str)

    def shake_off(self):
        """ Stop shaking """
        command = 'soff'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        print(response_str)
        logger.log('RECEIVED', response_str)

    def set_shake_target_speed(self, rpm: float) -> None:
        """ Set the shaking speed (rpm) """
        command = f'ssts{rpm}'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        logger.log('RECEIVED', response_str)

    def get_shake_target_speed(self) -> float:
        """ Deals with getting the Heater/Shaker speed in rpm """
        command = 'gsts'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        print(url)
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        response_dict = ast.literal_eval(response_str)
        rpm = response_dict['response'].rstrip('\r').rstrip('\n')
        logger.log('RECEIVED', response_str)
        return float(rpm)

    def get_temp_state(self) -> int:
        """ Deals with getting the Heater/Shaker temp control (enabled: 1, disabled: 0) """
        command = 'gts'
        # Generate the URL.
        url = FAST_API_URL_BASE + FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['url'] + f'?id={self.ID}&command={command}'
        logger = Logger(__file__, __name__)
        logger.log('SEND', url)
        # Generate the request.
        request = WebRequest.Create(url)
        method = FAST_API_URL_PATHS['prep_deck']['chiller-heater-shaker_raw_command']['']['method']
        request.Method = method
        response = request.GetResponse()
        status_code = response.StatusCode
        logger.log('RECEIVED', "Status Code: {0}".format(status_code))
        if str(status_code) != 'OK':
            __retry(url, method)
        # Read the response.
        encoding = ASCIIEncoding.ASCII
        reader = StreamReader(response.GetResponseStream(), encoding)
        response_str = reader.ReadToEnd()
        response_dict = ast.literal_eval(response_str)
        val = response_dict['response'].rstrip('\r').rstrip('\n')
        logger.log('RECEIVED', response_str)
        return int(val)

class PrepDeck():
    # Public variables.
    axis = Axis()
    meerstetter = None
    heater = None
    # Constructor.
    def __init__(self):
        self.axis = Axis()
        self.heater = HeaterShaker()

class PipettorGantry():
    # Public variables.
    axis = Axis()
    pipettor = None
    air_valve = None
    mag_separator = None
    # Private variables.
    # Private constants.
    # Constructor.
    def __init__(self):
        self.axis = Axis()
        self.pipettor = None
        self.air_valve = AirValve()

class Reader():
    # Public variables.
    axis = Axis()
    led = LED()
    # Private variables.
    # Private constants.
    # Constructor.
    def __init__(self):
        self.axis = Axis()
        self.led = LED()

class Chassis():
    # Public variables.
    raw = None
    power = None
    relay = Relay()
    gpio = GPIO()
    utils = None
    # Private variables.
    # Private constants.
    # Constructor.
    def __init__(self):
        self.relay = Relay()
        self.gpio = GPIO()

class FastAPIInterface():
    # Public variables.
    unit = None
    pipettor_gantry = None
    prep_deck = None
    reader = None
    chassis = None
    calibrator = None

    # Private variables.

    # Private constants.
    __MODULES = {
        'Chassis': 'chassis',
        "Upper Gantry": 'pipettor_gantry',
        'Reader': 'reader',
        }
    
    # Constructor.
    def __init__(self, unit=None):
        self.unit = unit
        self.pipettor_gantry = PipettorGantry()
        self.reader = Reader()
        self.chassis = Chassis()
        self.prep_deck = PrepDeck()
        #self.calibrator = Calibrator(unit)


if __name__ == '__main__':
    print("Hello, World!")
