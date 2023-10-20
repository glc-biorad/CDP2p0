
# Version: Test
'''
DESCIRPITON:
This module contains the Reader Coordinate object
'''

import sys 

from api.util.utils import check_type, check_limit, check_array_size
from api.util.coordinate import coordinates, coordinate_names

class ReaderCoordinate():
    # Public variables.
    x = None
    y = None
    z = None
    filter_wheel = None

    # Private variables.
    __in_bounds = None

    # Private constants.
    __LIMIT_MIN_X = 0  # ustep
    __LIMIT_MIN_Y = 0
    __LIMIT_MIN_Z = 0
    __LIMIT_MIN_FILTER_WHEEL = 0
    __LIMIT_MAX_X = -100000  # ustep
    __LIMIT_MAX_Y = -1200000
    __LIMIT_MAX_Z = -100000
    __LIMIT_MAX_FILTER_WHEEL = -10
    __LIMIT_TRAY_OPEN = 0
    __LIMIT_TRAY_CLOSED = -790000
    __LIMIT_HEATER_OPEN = 0
    #__LIMIT_HEATER_CLOSED = -230000
    __LIMIT_HEATER_CLOSED = -510000

    # Constructor
    def __init__(self, x=0, y=0, z=0, filter_wheel=0):
        # Check types
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(filter_wheel, int)
        # Check limits
        check_limit(x, self.__LIMIT_MIN_X, '<=')
        check_limit(y, self.__LIMIT_MIN_Y, '<=')
        check_limit(z, self.__LIMIT_MIN_Z, '<=')
        check_limit(filter_wheel, self.__LIMIT_MIN_FILTER_WHEEL, '<=')
        check_limit(x, self.__LIMIT_MAX_X, '>=')
        check_limit(y, self.__LIMIT_MAX_Y, '>=')
        check_limit(z, self.__LIMIT_MAX_Z, '>=')
        check_limit(filter_wheel, self.__LIMIT_MAX_FILTER_WHEEL, '>=')
        self.x = x
        self.y = y
        self.z = z
        self.filter_wheel = filter_wheel

    def update(self, x, y, z, filter_wheel):
        # Check types
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(filter_wheel, int)
        # Check limits
        check_limit(x, self.__LIMIT_MIN_X, '>=')
        check_limit(y, self.__LIMIT_MIN_Y, '>=')
        check_limit(z, self.__LIMIT_MIN_Z, '>=')
        check_limit(filter_wheel, self.__LIMIT_MIN_FILTER_WHEEL, '>=')
        check_limit(x, self.__LIMIT_MAX_X, '<=')
        check_limit(y, self.__LIMIT_MAX_Y, '<=')
        check_limit(z, self.__LIMIT_MAX_Z, '<=')
        check_limit(filter_wheel, self.__LIMIT_MAX_FILTER_WHEEL, '<=')
        self.x = x
        self.y = y
        self.z = z
        self.filter_wheel = filter_wheel

    def get_limit_min(self):
        return self.__LIMIT_MIN_X, self.__LIMIT_MIN_Y, self.__LIMIT_MIN_Z, self.__LIMIT_MIN_FILTER_WHEEL
    def get_limit_max(self):
        return self.__LIMIT_MAX_X, self.__LIMIT_MAX_Y, self.__LIMIT_MAX_Z, self.__LIMIT_MAX_FILTER_WHEEL
    def get_limit_tray_open(self):
        return self.__LIMIT_TRAY_OPEN
    def get_limit_tray_closer(self):
        return self.__LIMIT_TRAY_CLOSED
    def get_limit_heater_open(self):
        return self.__LIMIT_HEATER_OPEN
    def get_limit_heater_closed(self):
        return self.__LIMIT_HEATER_CLOSED

def target_to_reader_coordinate(target):
        '''
        Converts a target from a valid type to an upper gantry coordinate object.
        '''
        dtypes = [list, str, ReaderCoordinate]
        dtype = type(target)
        x, y, z, filter_wheel = [None for i in range(4)]

        if dtype in dtypes:
            if dtype == ReaderCoordinate:
                return target
            elif dtype == list:
                check_array_size(target, 4)
                x, y, z, filter_wheel = target
                check_type(x, int)
                check_type(y, int)
                check_type(z, int)
                check_type(filter_wheel, int)
                return ReaderCoordinate(x, y, z, filter_wheel)
            elif dtype == str:
                return get_coordinate_by_name(target)

def get_coordinate_by_name(coordinate_name):
    # Check if the coordinate_name is valid.
    if coordinate_name not in coordinate_names:
        sys.exit("ERROR (coordinate, get_coordinate_by_name): '{0}' is not a valid coordinate name!".format(coordinate_name))
    # Initialize the upper gantry coordinate object.
    rc = ReaderCoordinate()
    # Get the coordinate by name.
    if coordinate_name == 'home':
        x, y, z, filter_wheel = 0, 0, 0, 0
        rc.update(x, y, z, filter_wheel)
        return rc
    elif coordinate_name[0:-2] == 'heater':
        i = int(coordinate_name[-1])
        x, y, z, filter_wheel = coordinates['reader']['heater_{0}'.format(i)]
        rc.update(x, y, z, filter_wheel)
        return rc
