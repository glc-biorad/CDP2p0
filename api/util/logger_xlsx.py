"""
"""

import os

from datetime import date, datetime
import time

class LoggerXLSX():
    # Public variables.

    # Private variables.
    __time_start = 0
    __time_current = 0
    __time_end = 0

    # Private constants.
    __XLSX_FILE_PATH = './tat_files/'
    __XLSX_FILE_NAME = 'tat'
    __XLSX_FILE_EXTENSION = '.csv'

    # Constructor.
    def __init__(self):
        today = date.today()
        month = today.month
        day = today.day
        year = today.year
        self.__XLSX_FILE_NAME = self.__XLSX_FILE_PATH + self.__XLSX_FILE_NAME + '_{0}_{1}_{2}'.format(month, day, year) + self.__XLSX_FILE_EXTENSION

    # Log Method.
    def log(self, step_description, command, time_in_seconds, time_decimal_places=2):
        # Check if we need to create or append.
        mode = 'w'
        if os.path.exists(self.__XLSX_FILE_NAME):
            mode = 'a'
        with open(self.__XLSX_FILE_NAME, mode) as ofile:
            line = '{0},{1},{2},\n'.format(step_description, command, round(time_in_seconds,time_decimal_places))
            ofile.write(line)