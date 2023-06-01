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
    def __init__(self, log_name: str = 'log', log_path: str = './logs/', log_extension: str = '.csv') -> None:
        self.__XLSX_FILE_NAME = log_name
        self.__XLSX_FILE_PATH = log_path
        self.__XLSX_FILE_EXTENSION = log_extension
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

    # Seyonic Log Header
    def seyonic_log_header(self) -> None:
        # Check if we need to create or append
        mode = 'w'
        if os.path.exists(self.__XLSX_FILE_NAME):
            mode = 'a'
        try:
            with open(self.__XLSX_FILE_NAME, mode) as ofile:
                line = "Action,Type,Pressure (mbar),Ch 1 - Status,Ch 2 - Status,Ch 3 - Status,Ch 4 - Status,Ch 5 - Status,Ch 6 - Status,Ch 7 - Status,Ch 8 - Status,Elapsed Time (s),Time (HH:MM:SS),Date (MM/DD/YYYY)\n"
                ofile.write(line)
        except Exception as e:
            print(e)

    # Write Method
    def seyonic_log(self, action: str, type: str, pressure: int, channel_status_list: list, elapsed_time: float) -> None:
        """
        """
        # Check if we need to create or append
        mode = 'w'
        if os.path.exists(self.__XLSX_FILE_NAME):
            mode = 'a'
        try:
            with open(self.__XLSX_FILE_NAME, mode) as ofile:
                # Get the channel status info
                ch1_status = channel_status_list[0]
                ch2_status = channel_status_list[1]
                ch3_status = channel_status_list[2]
                ch4_status = channel_status_list[3]
                ch5_status = channel_status_list[4]
                ch6_status = channel_status_list[5]
                ch7_status = channel_status_list[6]
                ch8_status = channel_status_list[7]
                # Get the current date
                hour = datetime.now().hour
                minute = datetime.now().minute
                second = datetime.now().second
                today = date.today()
                month = today.month
                day = today.day
                year = today.year
                # Write to the seyonic log
                line = f"{action}, {type}, {pressure}, {ch1_status}, {ch2_status}, {ch3_status}, {ch4_status}, {ch5_status}, {ch6_status}, {ch7_status}, {ch8_status}, {elapsed_time}, {hour}:{minute}:{second}, {month}/{day}/{year}\n"
                ofile.write(line)
        except Exception as e:
            print(e)