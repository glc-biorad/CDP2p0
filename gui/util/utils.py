'''
'''

import sys
import time
import socket
from ctypes import *
from struct import pack, unpack
import serial
import sys
import glob
import socket
import json
import numpy as np
import os.path as osp

from api.util.logger import Logger
from api.util.logger_xlsx import LoggerXLSX

def get_serial_port_names():
    '''
    Obtains a list of serial port names.
    '''
    # Get the ports
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    # Return the results
    results = []
    for port in ports:
        try:
            sp = serial.Serial(port)
            sp.close()
            results.append(port)
        except (OSError, serial.SerialException):
            pass
    return results

def check_serial_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def flush_buffers(serial_port):
    serial_port.reset_input_buffer()
    serial_port.reset_output_buffer()

def check_type(value, want_type):
    if want_type == int:
        value = int(value)
    elif want_type == float:
        value = int(value)
    if type(value) != want_type:
        sys.exit("ERROR (utils, check_type): value ({0}) is not the valid type ({1})".format(value, want_type))

def seconds_to_minutes(value):
    return value / 60.0
def seconds_to_hours(value):
    return value / 3600.0
def minutes_to_seconds(value):
    return 60.0 * value
def hours_to_seconds(value):
    return 3600.0 * value

def delay(value, unit='seconds', verbose=False):
    units = ['seconds', 'second', 'secs', 'sec', 's',
             'minutes', 'minute', 'mins', 'min', 'm',
             'hours', 'hrs', 'hr', 'h']
    check_type(unit, str)
    unit = unit.lower()
    logger = Logger(__file__, __name__)
    logger.log('MESSAGE', "Delay set for {0} {1}".format(value, unit))
    logger_xlsx = LoggerXLSX()
    time_in_seconds = value
    if unit.lower()[0] == 'm':
        time_in_seconds = time_in_seconds * 60.
    elif unit.lower()[0] == 'h':
        time_in_seconds = time_in_seconds * 60. * 60.
    logger_xlsx.log("Wait {0} {1}".format(value, unit), delay.__name__, time_in_seconds)
    if unit in units:
        if unit[0] == 's':
            if verbose:
                for i in range(value):
                    print("TIMING (utils, delay): {0} of {1} seconds".format(i + 1, value))
                    time.sleep(1)
                print("TIMING (utils, delay): {0}/{0} seconds".format(value))
            else:
                time.sleep(value)
            return
        elif unit[0] == 'm':
            minutes = value
            value = minutes_to_seconds(value)
            if verbose:
                for i in range(minutes):
                    print("TIMING (utils, delay): {0} of {1} minutes left".format(minutes - i, minutes))
                    time.sleep(60)
                print("TIMING (utils, delay): {0}/{0} minutes".format(minutes))
            else:
                time.sleep(value)
            return
        elif unit[0] == 'h':
            hours = value
            value = hours_to_seconds(value)
            if verbose:
                for i in range(hours):
                    print("TIMING (utils, delay): {0} of {1} hours left".format(hours - i, hours))
                    time.sleep(3600)
                print("TIMING (utils, delay): {0}/{0} hours".format(hours))
            else:
                time.sleep(value)
            return

def check_if_dir_valid(direction):
    valid_directions = [1, -1]
    if direction not in valid_directions:
        sys.exit("ERROR (utils, check_if_dir_valid): direction ({0}) is not valid ({1})".format(direction, valid_directions))

def check_array_size(array, size):
    if len(array) != size:
        sys.exit("ERROR (utils, check_array_size): size ({0}) mismatch from actual array size ({1})".format(size, len(array)))

def check_limit(value, limit, mode='<', verbose=True):
    '''
    Check if value {mode} limit
        e.g.  value < limit
    '''
    modes = ['<', '>', '>=', '<=', '==', '=', '!=']

    # Make sure given mode is in the valid modes.
    if mode in modes:
        if mode == '<':
            if value < limit:
                return True
        elif mode == '>':
            if value > limit:
                return True
        elif mode == '>=':
            if value >= limit:
                return True
        elif mode == '<=':
            if value <= limit:
                return True
        elif mode == '==' or mode == '=':
            if value == limit:
                return True
        elif mode == '!=':
            if value != limit:
                return True
        if verbose:
            print("WARNING (utils, check_limit): {0} {1} {2} is False...".format(value, mode, limit))
        return False
    sys.exit("ERROR (utils, check_limit): mode ({0}) is not valid!".format(mode))

def replace_address(command_byte_string, address):
        # Replace address depending on the address.
        if address < 10:
            return command_byte_string.replace(b'address', b'0' + str(address).encode('utf-8'))
        elif address >= 10:
            if address == 11:
                address = '0B'
            elif address == 12:
                address = '0C'
            elif address == 13:
                address = '0D'
            elif address == 14:
                address = '0E'
            elif address == 15:
                address = '0F'
            elif address == 16:
                address = '10'
            return command_byte_string.replace(b'address', str(address).encode('utf-8'))

def replace_word(command_byte_string, word_string, word_value):
        return command_byte_string.replace(word_string.encode('utf-8'), str(word_value).encode('utf-8'))

def wait(controller, wait_for='\r', timeout=10, verbose=True):
    time_start = time.time()
    while time.time() - time_start < timeout:
        response = controller.read().decode()
        if response == wait_for:
            break
    if verbose:
        print("WARNING (utils, wait): timeout ({0} seconds) reached and {1} has not been found....".format(timeout, wait_for))

def left_pad_to_str(value, length_final):
    length_start = len(str(value))
    length_difference = length_final - length_start
    if length_difference == 0:
        return str(value)
    elif length_difference > 0:
        return str(length_difference * '0' + str(value))
    else:
        print("Warning (utils, __left_pad_to_str): length ({0}) of value ({1}) given is larger than the final length ({2}) desired...".format(length_start, value, length_final))
        return ''

def convert_hexidecimal_to_float32_ieee_754(s):
    i = int(s, 16)                   # convert from hex to a Python int
    cp = pointer(c_int(i))           # make this into a c integer
    fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
    return fp.contents.value         # dereference the pointer, get the float

def convert_float32_to_hexidecimal_ieee_754(value):
    # identifying whether the number is positive or negative
    n = value
    sign = 0
    if n < 0 :
        sign = 1
        n = n * (-1)
    p = 30
    # convert float to binary
    dec = __float_bin(n, places = p)
    dotPlace = dec.find('.')
    onePlace = dec.find('1')
    # finding the mantissa
    if onePlace > dotPlace:
        dec = dec.replace(".","")
        onePlace -= 1
        dotPlace -= 1
    elif onePlace < dotPlace:
        dec = dec.replace(".","")
        dotPlace -= 1
    mantissa = dec[onePlace+1:]
    # calculating the exponent(E)
    exponent = dotPlace - onePlace
    exponent_bits = exponent + 127
    # converting the exponent from decimal to binary
    exponent_bits = bin(exponent_bits).replace("0b",'')
    mantissa = mantissa[0:23]
    # the IEEE754 notation in binary
    final = str(sign) + exponent_bits.zfill(8) + mantissa
    # convert the binary to hexadecimal
    hstr = '0x%0*X' %((len(final) + 3) // 4, int(final, 2))
    return (hstr, final)

def __float_bin(my_number, places=3):
    my_whole, my_dec = str(my_number).split(".")
    my_whole = int(my_whole)
    res = (str(bin(my_whole))+".").replace('0b','')
    for x in range(places):
        my_dec = str('0.')+str(my_dec)
        temp = '%1.20f' %(float(my_dec)*2)
        my_whole, my_dec = temp.split(".")
        res += my_whole
    return res

def seyonic_to_microliters(seyonic_value):
    conversion = 1 / 0.1 # seyonic/microliters
    return int(seyonic_value / conversion)
def microliters_to_seyonic(microliters_value):
    conversion = 1 / 0.1 # seyonic / microliters
    return int(microliters_value * conversion)


def get_unit_name():
    hostname = socket.gethostname()
    with open(osp.join('C:/', 'CDP2p0', 'config', 'unit_hostnames.json'), 'r') as rf:
        hostname_lookup = json.load(rf)
    return hostname_lookup[hostname]

def import_config_file(input_pathname: str) -> dict:
    with open(input_pathname, 'r') as rf:
        config_data = json.load(rf)
    return config_data

def load_A100K_coords(which_unit: str, which_heater: str) -> np.ndarray:
    a100k_coords_fname = 'Unit{0}_A100K_CoordinateMap.csv'.format(which_unit)
    data = np.loadtxt(a100k_coords_fname, skiprows=1, usecols=(2, 3),
                      delimiter=',', dtype=np.int32)
    # pull out individual heater data
    hA = data[:8, :] #/ convmat
    hB = data[8:16, :] #/ convmat
    hC = data[16:24, :] #/ convmat
    hD = data[24:, :] #/ convmat

    if which_heater == 'A':
        locdata = hA
    elif which_heater == 'B':
        locdata = hB
    elif which_heater == 'C':
        locdata = hC
    elif which_heater == 'D':
        locdata = hD

    return locdata


def getXY_from_click(click_pt: tuple, geometry: tuple, htr: str, unit: str):
    # load a100k coords
    locdata = load_A100K_coords(unit, htr)

    topleft = (locdata[4, 0], locdata[4, 1])
    topright = (locdata[5, 0], locdata[5, 1])
    botleft = (locdata[6, 0], locdata[6, 1])
    botright = (locdata[7, 0], locdata[7, 1])

    chamber_delta_y = (botleft[1] - topleft[1]) / 7 # 7 spaces, not 8.
    chamberlength_x = (topleft[1] - topleft[0])

    pt_frac_x, pt_frac_y = click_pt[0] / geometry[0], click_pt[1] / geometry[1]

    # find which chamber the y is closest to
    closest_chamber = int(np.round(pt_frac_y * 7)) # goes from 0 to 7

    y_coord = topleft[1] + chamber_delta_y * closest_chamber
    x_coord = topleft[0] + pt_frac_x * chamberlength_x
    return (x_coord, y_coord)

class MetaDataWriter(object):
    def __init__(self, experiment_fpath):
        experiment_fname = experiment_fpath.split('\\')
        self.meta_path = osp.join(experiment_fpath, 'metadata', 'metadata.json')
        self.meta_name = experiment_fname
        if osp.isfile(self.meta_path):
            with open(self.meta_path, 'r') as rf:
                self.metadata = json.load(rf)
        else:
            self.metadata = {}

    def create_metadata(self, ):
        pass
