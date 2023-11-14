
# Version: Test
'''
'''

from api.util.utils import check_type, check_limit

class UpperGantryVelocity():
    # Public variables
    x = None  # int
    y = None
    z = None
    drip_plate = None

    # Private variables
    __in_bounds = None  # bool

    # Private constants
    __LIMIT_MAX_X = 300000  # ustep/sec
    __LIMIT_MAX_Y = 3200000
    __LIMIT_MAX_Z = 800000
    __LIMIT_MAX_DRIP_PLATE = 2500000
    __LIMIT_MIN_X = 20000  # ustep/sec
    __LIMIT_MIN_Y = 150000
    __LIMIT_MIN_Z = 80000
    __LIMIT_MIN_DRIP_PLATE = 150000

    # Constructor
    def __init__(self, x=0, y=0, z=0, drip_plate=0):
        # Check types.
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(drip_plate, int)
        # Check limits.
        check_limit(x, self.__LIMIT_MAX_X, '<=')
        check_limit(y, self.__LIMIT_MAX_Y, '<=')
        check_limit(z, self.__LIMIT_MAX_Z, '<=')
        check_limit(drip_plate, self.__LIMIT_MAX_DRIP_PLATE, '<=')
        # Store the values.
        self.x = x
        self.y = y
        self.z = z
        self.drip_plate = drip_plate

    def update(self, x, y, z, drip_plate):
        # Check types.
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(drip_plate, int)
        # Check limits.
        check_limit(x, self.__LIMIT_MAX_X, '<=')
        check_limit(y, self.__LIMIT_MAX_Y, '<=')
        check_limit(z, self.__LIMIT_MAX_Z, '<=')
        check_limit(drip_plate, self.__LIMIT_MAX_DRIP_PLATE, '<=')
        # Store the values.
        self.x = x
        self.y = y
        self.z = z
        self.drip_plate = drip_plate

    def get_limit_max(self):
        return self.__LIMIT_MAX_X, self.__LIMIT_MAX_Y, self.__LIMIT_MAX_Z, self.__LIMIT_MAX_DRIP_PLATE
    def get_limit_min(self):
        return self.__LIMIT_MIN_X, self.__LIMIT_MIN_Y, self.__LIMIT_MIN_Z, self.__LIMIT_MIN_DRIP_PLATE