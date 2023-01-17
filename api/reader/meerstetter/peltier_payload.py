'''
'''

from api.util.utils import left_pad_to_str, convert_float32_to_hexidecimal_ieee_754

from api.reader.meerstetter.peltier_parameters import PELTIER_PARAMETERS

class PeltierPayload():
    # Public variables.
    # Private variables.
    __query_type = None
    __parameter_id = None
    __instance = None
    __value = None
    __payload_str = None

    # Private constants.
    __QUERY_TYPES = {
        'get': "?VR",
        'set': "VS",
        'reset': "RS",
        'set_address': "SA"
        }
    __INSTANCES = [
        1,
        2
        ]

    # Constructor.
    def __init__(self, query_type, parameter_id=None, instance=1, value=None):
        # Make sure query type is valid.
        assert query_type in self.__QUERY_TYPES
        self.__query_type = query_type
        # Make sure the parameter id is valid.
        if parameter_id != None:
            assert parameter_id in PELTIER_PARAMETERS
        self.__parameter_id = parameter_id
        # Make sure the instance is valid.
        assert instance in self.__INSTANCES
        self.__instance = instance
        # Make sure the value is valid and that the parameter is Read-Only=False if value != None.
        parameter_value_range = PELTIER_PARAMETERS[parameter_id]["Value Range"]
        # not finished...
        # Get the value.
        self.__value = value
        # Generate the payload.
        self.__generate_payload_str()

    def to_string(self):
        return self.__payload_str

    def __generate_payload_str(self):
        # Get the query.
        query = str(self.__QUERY_TYPES[self.__query_type])
        # Convert the parameter id from int to hex (splice out the 0x).
        parameter_id_hex = left_pad_to_str(hex(self.__parameter_id)[2:], 4).upper()
        # Left pad the instance.
        instance = left_pad_to_str(self.__instance, 2)
        # If there is a value, check the expected type, convert if float32, then left pad.
        if self.__value == None:
            value = ''
        else:
            value = self.__value
            parameter_format = PELTIER_PARAMETERS[self.__parameter_id]["Format"]
            if parameter_format == "FLOAT32":
                value = convert_float32_to_hexidecimal_ieee_754(self.__value)[0][2:]
            value = left_pad_to_str(value, 8)
        self.__payload_str = query + parameter_id_hex + instance + value

