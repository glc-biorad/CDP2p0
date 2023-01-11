
'''
'''

import time

class Timer():
    # Public variables.
    time_start = None
    time_end = None
    time_total = None

    # Private variables.
    __logger = None

    # Constructor.
    def __init__(self, logger):
        self.time_start = 0
        self.time_end = 0
        self.time_total = 0
        self.__logger = logger

    # Start Method.
    def start(self, module_name, function_name):
        self.time_start = time.time()
        self.__logger.log('TIMING', "Starting the timer for module [{0}] and function [{1}]".format(module_name, function_name))

    def get_current_elapsed_time(self, time_units='seconds') -> float:
        units = ['seconds', 'minutes', 'hours', 's', 'm', 'h']
        assert type(time_units) == str
        assert time_units.lower()[0] in units
        time_current = time.time() - self.time_start
        if time_units.lower()[0] == 's':
            return time_current
        elif time_units.lower()[0] == 'm':
            return (time_current / 60.)
        elif time_units.lower()[0] == 'h':
            return (time_current / 60. / 60.)
        
    # Log Current Elapsed Time Method.
    def log_current_elapsed_time(self, module_name, function_name, message=None, time_units='seconds'):
        units = ['seconds', 'minutes', 'hours', 's', 'm', 'h']
        assert type(time_units) == str
        assert time_units.lower()[0] in units
        time_current = time.time() - self.time_start
        if message != None:
            self.__logger.log('MESSAGE', message)
        if time_units.lower()[0] == 's':
            self.__logger.log('TIMING', "Current Elapsed Time for module [{0}] and function [{1}]: {2} seconds.".format(module_name, function_name, time_current))
        elif time_units.lower()[0] == 'm':
            self.__logger.log('TIMING', "Current Elapsed Time for module [{0}] and function [{1}]: {2} minutes.".format(module_name, function_name, time_current / 60.))
        elif time_units.lower()[0] == 'h':
            self.__logger.log('TIMING', "Current Elapsed Time for module [{0}] and function [{1}]: {2} hours.".format(module_name, function_name, time_current / 60. / 60.))
    
    # Stop Method.
    def stop(self, module_name, function_name, time_units='seconds'):
        units = ['seconds', 'minutes', 'hours', 's', 'm', 'h']
        assert type(time_units) == str
        assert time_units.lower()[0] in units
        self.time_end = time.time() - self.time_start
        if time_units.lower()[0] == 's':
            self.__logger.log('TIMING', "Total Elapsed Time for module [{0}] and function [{1}]: {2} seconds.".format(module_name, function_name, self.time_end))
        elif time_units.lower()[0] == 'm':
            self.__logger.log('TIMING', "Total Elapsed Time for module [{0}] and function [{1}]: {2} minutes.".format(module_name, function_name, self.time_end / 60.))
        elif time_units.lower()[0] == 'h':
            self.__logger.log('TIMING', "Total Elapsed Time for module [{0}] and function [{1}]: {2} hours.".format(module_name, function_name, self.time_end / 60. / 60.))

    # Pause Method.
    def pause(self, module_name, function_name):
        time_pause = time.time()