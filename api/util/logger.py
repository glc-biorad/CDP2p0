'''
'''

#from multiprocessing import Value
import os

import ast

from datetime import date, datetime
import time

class Logger():
    # Public variables.
    time_start_A = 0
    time_start_B = 0
    # Private variables.
    __current_python_file_name = None
    __current_function_name_called = None
    __output_file_name = None
    # Private constants.
    __MESSAGE_TYPES = [
        'ERROR',
        'WARNING',
        'DEBUG',
        'LOG',
        'LOG-START',
        'LOG-END',
        'TIMING',
        'TIMING-START-A',
        'TIMING-START-B',
        'TIMING-END-A',
        'TIMING-END-B',
        'MESSAGE',
        'SENT',
        'RECEIVED',
        'HEADER',
        ]
    # Constructor.
    def __init__(self, current_python_file_path, current_function_name_called, output_file_name=None):
        self.__current_python_file_name = os.path.split(current_python_file_path)[1]
        self.__current_function_name_called = current_function_name_called
        if output_file_name == None:
            today = date.today()
            month = today.month
            day = today.day
            year = today.year
            self.__output_file_name = 'log_files/output_file_{0}_{1}_{2}.txt'.format(month, day, year)

    # Log Method.
    def log(self, message_type, message):
        try:
            assert type(message_type) == str
            dt = datetime.now()
            time_str = str(dt.strftime('%H')) + ':' + str(dt.strftime('%M')) + ':' + str(dt.strftime('%S'))
            # Check if we need to create or append.
            mode = 'w'
            if os.path.exists(self.__output_file_name):
                mode = 'a'
            with open(self.__output_file_name, mode) as ofile:
                if message_type.upper() == 'MESSAGE':
                    ofile.write("\t- Message: {0}\n".format(message))
                    ofile.write("\t- Current Time: {0}\n".format(time_str))
                    print("\t- Message: {0}".format(message))
                    print("\t- Current Time: {0}".format(time_str))
                elif message_type.upper() == 'HEADER':
                    ofile.write('\n{0}\n'.format(message))
                    print('\n{0}'.format(message))
                elif message_type.upper() == 'SEND':
                    ofile.write("\t\t- Message ({0}): {1}\n".format(message_type, message))
                    print("\t\t- Message ({0}): {1}".format(message_type, message))
                elif message_type.upper() == 'RECEIVED':
                    try:
                        message_dict = ast.literal_eval(message)
                        duration_microseconds = int(message_dict['_duration_us']) / 1.0e6
                        command_full = message_dict['message']
                        address, _1, command, _2 = command_full.split(',')
                        address = int(address[1:])
                        response = message_dict['response']
                        ofile.write("\t\t- Message ({0})\n".format(message_type))
                        ofile.write("\t\t\t- Duration (s): {0}\n".format(round(duration_microseconds, 2)))
                        ofile.write("\t\t\t- Address: {0}\n".format(address))
                        ofile.write("\t\t\t- Command Sent: {0}\n".format(command))
                        ofile.write("\t\t\t- Respone Received: {0}\n".format(response))
                        print("\t\t- Message ({0})".format(message_type))
                        print("\t\t\t- Duration (s): {0}".format(round(duration_microseconds, 2)))
                        print("\t\t\t- Address: {0}".format(address))
                        print("\t\t\t- Command Sent: {0}".format(command))
                        print("\t\t\t- Respone Received: {0}".format(response))
                    except Exception as e:
                        ofile.write("\t\t- Message ({0}): {1}\n".format(message_type, message))
                        print("\t\t- Message ({0}): {1}".format(message_type, message))
                elif message_type.upper() == 'LOG-START':
                    ofile.write("START [Module: {0} - Function: {1}]\n".format(self.__current_python_file_name, self.__current_function_name_called))
                    ofile.write("\t- Message: {0}\n".format(message))
                    ofile.write("\t- Start Time (H:M:S): {0}\n".format(time_str))
                    print("START [Module: {0} - Function: {1}]".format(self.__current_python_file_name, self.__current_function_name_called))
                    print("\t- Message: {0}".format(message))
                    print("\t- Start Time (H:M:S): {0}".format(time_str))
                elif message_type.upper() == 'LOG-END':
                    ofile.write("END [Module: {0} - Function: {1} - Time (H:M:S): {2}]\n".format(self.__current_python_file_name, self.__current_function_name_called, time_str))
                    print("END [Module: {0} - Function: {1} - Time (H:M:S): {2}]".format(self.__current_python_file_name, self.__current_function_name_called, time_str))
                elif message_type.upper() == 'TIMING':
                    ofile.write('\nTIMING: {0}\n'.format(message))
                    print('\nTIMING: {0}\n'.format(message))
                elif message_type.upper() == 'TIMING-START-A':
                    self.time_start_A = time.time()
                    ofile.write('\t- Timing Starting Now')
                    print('\t- Timing Starting Now')
                elif message_type.upper() == 'TIMING-END-A':
                    message = time.time() - self.time_start_A
                    ofile.write('\t-Elapsed Time (s): {0}'.format(message))
                    print('\t-Elapsed Time (s): {0}'.format(message))
                elif message_type.upper() == 'TIMING-START-B':
                    self.time_start_B = time.time()
                    ofile.write('\t- Timing Starting Now')
                    print('\t- Timing Starting Now')
                elif message_type.upper() == 'TIMING-END-B':
                    message = time.time() - self.time_start_B
                    ofile.write('\t-Elapsed Time (s): {0}'.format(message))
                    print('\t-Elapsed Time (s): {0}'.format(message))
                else:
                    ofile.write("{0}\n".format(message_type))
                    ofile.write("\t- Module: {0}\n".format(self.__current_python_file_name))
                    ofile.write("\t- Function: {0}\n".format(self.__current_function_name_called))
                    ofile.write("\t- Message: {0}\n".format(message))
                    ofile.write("\t- Current Time: {0}\n".format(time_str))
                    print("{0}".format(message_type))
                    print("\t- Module: {0}".format(self.__current_python_file_name))
                    print("\t- Function: {0}".format(self.__current_function_name_called))
                    print("\t- Message: {0}".format(message))
                    print("\t- Current Time: {0}".format(time_str))
            ofile.close()
        except:
            print("Issue Logging from logger.py")
            pass
