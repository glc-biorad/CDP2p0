"""
"""

import os

from datetime import date, datetime
import time

class Log():
    # Public variables.

    # Private variables.
    __time_start = 0
    __time_current = 0
    __time_end = 0

    # Private constants.
    __XLSX_FILE_PATH = './logs/'
    __XLSX_FILE_NAME = 'log'
    __XLSX_FILE_EXTENSION = '.csv'

    # Constructor.
    def __init__(self, log_name='log'):
        self.__XLSX_FILE_NAME = log_name
        hour = datetime.now().hour
        minute = datetime.now().minute
        second = datetime.now().second
        today = date.today()
        month = today.month
        day = today.day
        year = today.year
        self.__XLSX_FILE_NAME = self.__XLSX_FILE_PATH + self.__XLSX_FILE_NAME + '_{0}_{1}_{2}__{3}_{4}_{5}'.format(month, day, year, hour, minute, second) + self.__XLSX_FILE_EXTENSION

    # Log Method.
    def log(self, action_message, time_in_seconds=None, time_decimal_places=2):
        # Check if we need to create or append.
        mode = 'w'
        if os.path.exists(self.__XLSX_FILE_NAME):
            mode = 'a'
        with open(self.__XLSX_FILE_NAME, mode) as ofile:
            if time_in_seconds == None:
                line = '{0},{1},\n'.format(action_message, datetime.now().ctime())
            else:
                line = '{0},{1},\n'.format(action_message, round(time_in_seconds,time_decimal_places))
            ofile.write(line)