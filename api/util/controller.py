'''
DESCRIPTION:
'''

# pythonnet
#import pythonnet
#from pythonnet import load

#load("coreclr")

import clr

#clr.AddReference('System.IO.Ports')

#from System.IO.Ports import SerialPort as Ports
#from System.IO import Ports
from serial import Serial
class Controller():
    # Public variables.

    # Private variables.

    # Private constants
    __SERIAL_PORT = None
    __COM_PORT = 'COM8'
    __BAUD_RATE = 115200
    __TIMEOUT_READLINE = 1000
    __TIMEOUT_WRITELINE = 1000
    __PARITY = None
    __HANDSHAKE = None
    __DATABITS = 8
    __STOPBITS = 'One'
    __NEWLINE = '\r'

    # Constructor.
    def __init__(self, com_port, baud_rate=115200, timeout=3, dont_use_fast_api=False, open_port=True):
        com_ports = ['COM4', 'COM8', 'COM10']
        if baud_rate != None:
            self.__BAUD_RATE = baud_rate
        #self.__SERIAL_PORT = Ports.SerialPort(PortName=com_port, BaudRate=self.__BAUD_RATE)
        if dont_use_fast_api:
            if open_port:
                self.__SERIAL_PORT = Serial(com_port, baud_rate, timeout=timeout)
        #self.__SERIAL_PORT.ReadTimeout = self.__TIMEOUT_READLINE
        #self.__SERIAL_PORT.WriteTimeout = self.__TIMEOUT_WRITELINE
        #self.__SERIAL_PORT.NewLine = self.__NEWLINE
        if dont_use_fast_api:
            #self.__SERIAL_PORT.Open()
            if open_port:
                if self.__SERIAL_PORT.is_open == False:
                    self.__SERIAL_PORT.open()

    def write(self, command):
        self.__SERIAL_PORT.write(command.encode('utf-8'))
        #self.__SERIAL_PORT.write(command.decode())

    def readline(self):
        response = self.__SERIAL_PORT.readlines()
        try:
            response = response[0].decode()
            if response[-1] == '\r':
                response = response[:-1]
            return response
        except:
            response = b''

    def deprecated_write(self, command):
        self.__SERIAL_PORT.WriteLine(command.decode())

    def deprecated_readline(self):
        response = self.__SERIAL_PORT.ReadLine()
        return response

    def close(self):
        #self.__SERIAL_PORT.Close()
        if self.__SERIAL_PORT != None:
            self.__SERIAL_PORT.close()