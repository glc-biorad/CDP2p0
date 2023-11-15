
# Version: Test
'''
'''

from api.util.utils import check_type, check_limit

class ReaderVelocity():
    # Public variables
    x = None  # int
    y = None
    z = None
    filter_wheel = None

    # Private variables
    __in_bounds = None  # bool

    # Private constants
    __LIMIT_MAX_X = 100000  # ustep/sec
    __LIMIT_MAX_Y = 1000000
    __LIMIT_MAX_Z = 100000
    __LIMIT_MAX_FILTER_WHEEL = 80000
    __LIMIT_MAX_TRAY = 200000
    __LIMIT_MAX_HEATER = 100000

    # Constructor
    def __init__(self, x=0, y=0, z=0, filter_wheel=0):
        # Check types.
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(filter_wheel, int)
        # Check limits.
        check_limit(x, self.__LIMIT_MAX_X, '<=')
        check_limit(y, self.__LIMIT_MAX_Y, '<=')
        check_limit(z, self.__LIMIT_MAX_Z, '<=')
        check_limit(filter_wheel, self.__LIMIT_MAX_FILTER_WHEEL, '<=')
        # Store the values.
        self.x = x
        self.y = y
        self.z = z
        self.filter_wheel = filter_wheel

    def update(self, x, y, z, filter_wheel):
        # Check types.
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(filter_wheel, int)
        # Check limits.
        check_limit(x, self.__LIMIT_MAX_X, '<=')
        check_limit(y, self.__LIMIT_MAX_Y, '<=')
        check_limit(z, self.__LIMIT_MAX_Z, '<=')
        check_limit(filter_wheel, self.__LIMIT_MAX_FILTER_WHEEL, '<=')
        # Store the values.
        self.x = x
        self.y = y
        self.z = z
        self.filter_wheel = filter_wheel

    def get_limit_max(self):
        return self.__LIMIT_MAX_X, self.__LIMIT_MAX_Y, self.__LIMIT_MAX_Z, self.__LIMIT_MAX_FILTER_WHEEL, self.__LIMIT_MAX_TRAY, self.__LIMIT_MAX_HEATER