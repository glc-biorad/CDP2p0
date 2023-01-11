'''
DESCIRPITON:
This module contains the Upper Gantry Coordinate object
'''

import sys 

from api.util.logger import Logger

from api.util.utils import check_type, check_limit, check_array_size
from api.util.coordinate import coordinates, coordinate_names

class UpperGantryCoordinate():
    # Public variables.
    x = None
    y = None
    z = None
    drip_plate = None

    # Private variables.
    __in_bounds = None

    # Private constants.
    __LIMIT_MIN_X = 0  # ustep
    __LIMIT_MIN_Y = 0
    __LIMIT_MIN_Z = 0
    __LIMIT_MIN_DRIP_PLATE = 0
    __LIMIT_MAX_X = -480000  # ustep
    __LIMIT_MAX_Y = -1800000
    __LIMIT_MAX_Z = -1530000
    __LIMIT_MAX_DRIP_PLATE = -1198000

    # Constructor
    def __init__(self, x=0, y=0, z=0, drip_plate=0):
        # Check types
        check_type(x, int)
        check_type(y, int)
        check_type(z, int)
        check_type(drip_plate, int)
        # Check limits
        check_limit(x, self.__LIMIT_MIN_X, '<=')
        check_limit(y, self.__LIMIT_MIN_Y, '<=')
        check_limit(z, self.__LIMIT_MIN_Z, '<=')
        check_limit(drip_plate, self.__LIMIT_MIN_DRIP_PLATE, '<=')
        check_limit(x, self.__LIMIT_MAX_X, '>=')
        check_limit(y, self.__LIMIT_MAX_Y, '>=')
        check_limit(z, self.__LIMIT_MAX_Z, '>=')
        check_limit(drip_plate, self.__LIMIT_MAX_DRIP_PLATE, '>=')
        self.x = x
        self.y = y
        self.z = z
        self.drip_plate = drip_plate

    # Overloads
    def __add__(self, ugc):
        return UpperGantryCoordinate(self.x + ugc.x, self.y + ugc.y, self.z + ugc.z, self.drip_plate + ugc.drip_plate)
    def __sub__(self, ugc):
        return UpperGantryCoordinate(self.x - ugc.x, self.y - ugc.y, self.z - ugc.z, self.drip_plate - ugc.drip_plate)

    def update(self, x, y, z, drip_plate):
        # Check types
        check_type(int(x), int)
        check_type(int(y), int)
        check_type(int(z), int)
        check_type(int(drip_plate), int)
        # Check limits
        check_limit(x, self.__LIMIT_MIN_X, '<=')
        check_limit(y, self.__LIMIT_MIN_Y, '<=')
        check_limit(z, self.__LIMIT_MIN_Z, '<=')
        check_limit(drip_plate, self.__LIMIT_MIN_DRIP_PLATE, '<=')
        check_limit(x, self.__LIMIT_MAX_X, '>=')
        check_limit(y, self.__LIMIT_MAX_Y, '>=')
        check_limit(z, self.__LIMIT_MAX_Z, '>=')
        check_limit(drip_plate, self.__LIMIT_MAX_DRIP_PLATE, '>=')
        self.x = x
        self.y = y
        self.z = z
        self.drip_plate = drip_plate

    def get_limit_min(self):
        return self.__LIMIT_MIN_X, self.__LIMIT_MIN_Y, self.__LIMIT_MIN_Z, self.__LIMIT_MIN_DRIP_PLATE
    def get_limit_max(self):
        return self.__LIMIT_MAX_X, self.__LIMIT_MAX_Y, self.__LIMIT_MAX_Z, self.__LIMIT_MAX_DRIP_PLATE

def target_to_upper_gantry_coordinate(target):
        '''
        Converts a target from a valid type to an upper gantry coordinate object.
        '''
        dtypes = [list, str, UpperGantryCoordinate]
        dtype = type(target)
        x, y, z, drip_plate = [None for i in range(4)]

        if isinstance(target, UpperGantryCoordinate):
            return target
        if dtype in dtypes:
            if dtype == UpperGantryCoordinate:
                return target
            elif dtype == list:
                check_array_size(target, 4)
                x, y, z, drip_plate = target
                check_type(int(x), int)
                check_type(int(y), int)
                check_type(int(z), int)
                check_type(drip_plate, int)
                return UpperGantryCoordinate(x, y, z, drip_plate)
            elif dtype == str:
                return get_coordinate_by_name(target)

def get_coordinate_by_name(coordinate_name):
    # Setup the logger.
    logger = Logger(__file__, __name__)
    #logger.log('LOG-START', "Working on coordinate for {0}".format(coordinate_name))
    # Check if the coordinate_name is valid.
    if coordinate_name not in coordinate_names:
        logger.log('ERROR', "'{0}' is not a valid coordinate name!".format(coordinate_name))
        sys.exit("ERROR (UpperGantrycoordinate, get_coordinate_by_name): '{0}' is not a valid coordinate name!".format(coordinate_name))
    # Initialize the upper gantry coordinate object.
    ugc = UpperGantryCoordinate()
    # Get the coordinate by name.
    if coordinate_name == 'home':
        x, y, z, drip_plate = 0, 0, 0, 0
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name == 'custom':
        x, y, z, drip_plate = coordinates['deck_plate']['custom']
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name == 'test_0':
        x, y, z, drip_plate = coordinates['deck_plate']['test_0']
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name == 'test_1':
        x, y, z, drip_plate = coordinates['deck_plate']['test_1']
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif (coordinate_name[0:14] == 'tip_trays_tray') and (coordinate_name[16:19] == 'row'):
        i = int(coordinate_name[14]) - 1
        if (len(coordinate_name[16:]) == 4):
            j = int(coordinate_name[-1]) - 1
        elif (len(coordinate_name[16:]) == 5):
            j = int(coordinate_name[-2:]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['tip_trays'][i][j]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif (coordinate_name[0:14] == 'tip_tray_tray') and (coordinate_name[16:19] == 'row'):
        i = int(coordinate_name[14]) - 1
        if (len(coordinate_name[16:]) == 4):
            j = int(coordinate_name[-1]) - 1
        elif (len(coordinate_name[16:]) == 5):
            j = int(coordinate_name[-2:]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['tip_trays'][i][j]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tip_transfer_tray_row':
        i = int(coordinate_name[-1]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['tip_transfer_tray'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif (coordinate_name[0:22] == 'reagent_cartridge_tray') and (coordinate_name[24:27] == 'row'):
        i = int(coordinate_name[22]) - 1
        j = int(coordinate_name[27:]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['reagent_cartridge'][i][j]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'heater_shaker_row':
        i = int(coordinate_name[-1]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['heater_shaker'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[:17] == 'mag_separator_row':
        i = int(coordinate_name.replace('mag_separator_row', '')) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['mag_separator'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tray_out_location_tray':
        i = int(coordinate_name[-1]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['tray_out_location'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tray_out_location_nipt_':
        tray = coordinate_name[-1]
        x, y, z, drip_plate = coordinates['deck_plate']['tray_out_location']['nipt'][tray]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tray_out_location_ff_':
        tray = coordinate_name[-1]
        x, y, z, drip_plate = coordinates['deck_plate']['tray_out_location']['ff'][tray]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tray_out_location_quant_':
        tray = coordinate_name[-1]
        x, y, z, drip_plate = coordinates['deck_plate']['tray_out_location']['quant'][tray]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:len('pcr_thermocycler_row')] == 'pcr_thermocycler_row':
        if len(coordinate_name) == len('pcr_thermocycler_row') + 1:
            i = int(coordinate_name[-1]) - 1
        elif len(coordinate_name) == len('pcr_thermocycler_row') + 2:
            i = int(coordinate_name[-2:]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['pcr_thermocycler'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'sample_loading_tray':
        i = int(coordinate_name[-1]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['sample_loading'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'assay_strip_row':
        i = int(coordinate_name[-1]) - 1
        x, y, z, drip_plate = coordinates['deck_plate']['assay_strip'][i]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'microwells_chip_':
        i = int(coordinate_name[-1])
        x, y, z, drip_plate = coordinates['deck_plate']['tip_transfer_tray']['chips']['microwells'][i-1]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'droplets_chip_':
        i = int(coordinate_name[-1])
        x, y, z, drip_plate = coordinates['deck_plate']['tip_transfer_tray']['chips']['droplets'][i-1]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'tray_out_location_chip':
        i = int(coordinate_name[-1])
        x, y, z, drip_plate = coordinates['deck_plate']['tray_out_location']['chips'][i-1]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:-1] == 'lid':
        i = int(coordinate_name[-1])
        x, y, z, drip_plate = coordinates['deck_plate']['lid_tray'][i-1]
        ugc.update(x, y, z, drip_plate)
        return ugc
    elif coordinate_name[0:3] == 'dg8':
        if coordinate_name[4:8] == '1000':
            i = 0
        elif coordinate_name[4:8] == '0100':
            i = 1
        elif coordinate_name[4:8] == '0010':
            i = 2
        elif coordinate_name[4:8] == '0001':
            i = 3
        if coordinate_name[9:] == '100':
            j = 0
        elif coordinate_name[9:] == '010':
            j = 1
        elif coordinate_name[9:] == '001':
            j = 2
        x, y, z, drip_plate = coordinates['deck_plate']['dg8'][i][j]
        ugc.update(x, y, z, drip_plate)
        return ugc
