
# Version: Test
from api.util.logger import Logger

from api.util.utils import check_type

import sys

class PipetteTip():
    # Public variables.
    # Private variables.
    __type = None

    # Private constants.
    __DELTA_Z1 = 305000 # Difference in Z1 height between 1000 and 50/200 microliter tips in microsteps.
    __DELTA_Z2 = 500000 # for drip plate
    __TYPES = [None, 50, 200, 1000] # in microliters.

    # Constructor.
    def __init__(self, type=None):
        # Check the type.
        if type != None:
            check_type(type, int)
        # Make sure type is valid.
        if type in self.__TYPES:
            self.__type = type
        else:
            sys.exit("ERROR (pipette_tip, __init__): {0} is not a valid tip type, exiting!".format(type))

    # Get Type Method.
    def get_type(self):
        return self.__type

    # Change Tip Method.
    def change_tip(self, type):
        # Check the type.
        if type != None:
            check_type(type, int)
        # Make sure type is valid.
        if type in self.__TYPES:
            self.__type = type
        else:
            sys.exit("ERROR (pipette_tip, change_tip): {0} is not a valid tip type, exiting!".format(type))

    # Get Z1 Method.
    def get_z1(self, target_ugc):
        if self.__type == None:
            return 0
        elif self.__type == 1000:
            return target_ugc.z
        elif self.__type == 50 or self.__type == 200:
            return target_ugc.z - self.__DELTA_Z1

    # Get Z2 Method.
    def get_z2(self, target_ugc):
        if self.__type == None:
            return 0
        elif self.__type == 1000:
            return target_ugc.drip_plate
        elif self.__type == 50 or self.__type == 200:
            return target_ugc.drip_plate + self.__DELTA_Z2
