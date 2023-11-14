
# Version: Test
""""
Adaptation of MeCom (https://github.com/spomjaksilp/pyMeCom) for integration with AVANT API. 
Data structures and low level comm values were kept and wrapped with
the MeerstetterBusPacket class.
CRC_16_CCITT_XMODEM replaced pycrc
% is used for control type instead of #
"""

from struct import pack, unpack
from enum import Enum
from math import isnan


CRC_16_CCITT_XMODEM = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6, 
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485, 
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d, 
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4, 
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823, 
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b, 
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12, 
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a, 
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41, 
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49, 
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70, 
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78, 
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f, 
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067, 
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e, 
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256, 
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d, 
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405, 
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c, 
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634, 
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab, 
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3, 
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a, 
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92, 
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1, 
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8, 
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]
# fmt: on

def crc16_ccitt_xmodem(buf: bytearray) -> int:

    crc = 0x0000
    for byte in buf:
        crc = (crc << 8) ^ CRC_16_CCITT_XMODEM[(crc >> 8) ^ byte]
        crc &= 0xFFFF  # truncate to 16 bits
    return crc


"""
Definitions of command and error codes as stated in the "Mecom" protocol standard.
https://www.meerstetter.ch/category/35-latest-communication-protocols
"""


TEC_PARAMETERS = [
    {"id": 104, "name": "Device Status", "format": "INT32"},
    {"id": 105, "name": "Error Number", "format": "INT32"},
    {"id": 108, "name": "Save Data to Flash", "format": "INT32"},
    {"id": 109, "name": "Flash Status", "format": "INT32"},

    {"id": 1000, "name": "Object Temperature", "format": "FLOAT32"},
    {"id": 1001, "name": "Sink Temperature", "format": "FLOAT32"},
    {"id": 1010, "name": "Target Object Temperature", "format": "FLOAT32"},
    {"id": 1011, "name": "Ramp Object Temperature", "format": "FLOAT32"},
    {"id": 1020, "name": "Actual Output Current", "format": "FLOAT32"},
    {"id": 1021, "name": "Actual Output Voltage", "format": "FLOAT32"},
    {"id": 1200, "name": "Temperature is Stable", "format": "INT32"},

    {"id": 2010, "name": "Status", "format": "INT32"},
    {"id": 2030, "name": "Current Limitation", "format": "FLOAT32"},
    {"id": 2031, "name": "Voltage Limitation", "format": "FLOAT32"},
    {"id": 2032, "name": "Current Error Threshold", "format": "FLOAT32"},
    {"id": 2033, "name": "Voltage Error Threshold", "format": "FLOAT32"},
    {"id": 2051, "name": "Device Address", "format": "INT32"},

    {"id": 3000, "name": "Target Object Temp (Set)", "format": "FLOAT32"},
    {"id": 6100, "name": "GPIO Function", "format": "INT32"},
    {"id": 6101, "name": "GPIO Level Assignment", "format": "INT32"},
    {"id": 6102, "name": "GPIO Hardware Configuration", "format": "INT32"},
    {"id": 6103, "name": "GPIO Channel", "format": "INT32"},

    {"id": 6300, "name": "Source Selection", "format": "INT32"},
    {"id": 6302, "name": "Observe Mode", "format": "INT32"},
    {"id": 6310, "name": "Delay till Restart", "format": "FLOAT32"},
    {"id": 52100, "name": "Enable Function", "format": "INT32"},
    {"id": 52101, "name": "Set Output to Push-Pull", "format": "INT32"},
    {"id": 52102, "name": "Set Output States", "format": "INT32"},
    {"id": 52103, "name": "Read Input States", "format": "INT32"},

    {"id": 50000, "name": "Live Enable", "format": "INT32"},

    {"id": 52200, "name": "External Object Temperature", "format": "FLOAT32"},
]

    
ERRORS = [
    {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"},
    {"code": 2, "symbol": "EER_DEVICE_BUSY", "description": "Device is busy"},
    {"code": 3, "symbol": "ERR_GENERAL_COM", "description": "General communication error"},
    {"code": 4, "symbol": "EER_FORMAT", "description": "Format error"},
    {"code": 5, "symbol": "EER_PAR_NOT_AVAILABLE", "description": "Parameter is not available"},
    {"code": 6, "symbol": "EER_PAR_NOT_WRITABLE", "description": "Parameter is read only"},
    {"code": 7, "symbol": "EER_PAR_OUT_OF_RANGE", "description": "Value is out of range"},
    {"code": 8, "symbol": "EER_PAR_INST_NOT_AVAILABLE", "description": "Parameter is read only"},
    {"code": 20, "symbol": "MEPORT_ERROR_SET_TIMEOUT", "description": "timeout reached, value cannot be set"},
    {"code": 21, "symbol": "MEPORT_ERROR_QUERY_TIMEOUT", "description": "timeout reached query cannot be served"},
]

"""
Custom exceptions.
"""


class ResponseException(Exception):
    pass


class ResponseTimeout(ResponseException):
    pass


class WrongResponseSequence(ResponseException):
    pass


class WrongChecksum(Exception):
    pass


class UnknownParameter(Exception):
    pass
    
class UnknownMeComType(Exception):
    pass

class MeComError(Exception):
    pass



class Parameter(object):
    """"
    Every parameter dict from commands.py is parsed into a Parameter instance.
    """

    def __init__(self, parameter_dict):
        """
        Takes a dict e.g. {"id": 104, "name": "Device Status", "format": "INT32"} and creates an object which can be
        passed to a Query().
        :param parameter_dict: dict
        """
        self.id = parameter_dict["id"]
        self.name = parameter_dict["name"]
        self.format = parameter_dict["format"]


class Error(object):
    """"
    Every error dict from commands.py is parsed into a Error instance.
    """

    def __init__(self, error_dict):
        """
        Takes a dict e.g. {"code": 1, "symbol": "EER_CMD_NOT_AVAILABLE", "description": "Command not available"} which
        defines a error specified by the protocol.
        :param error_dict: dict
        """
        self.code = error_dict["code"]
        self.symbol = error_dict["symbol"]
        self.description = error_dict["description"]

    def as_list(self):
        """
        Returns a list representation of this object.
        :return: list
        """
        return [self.code, self.description, self.symbol]


class ParameterList(object):
    """
    Contains a list of Parameter() for either TEC (metype = 'TEC') 
    or LDD (metype = 'TEC') controller.
    Provides searching via id or name.
    :param error_dict: dict
    """

    def __init__(self,metype='TEC'):
        """
        Reads the parameter dicts from commands.py.
        """
        self._PARAMETERS = []
        if metype == 'TEC':
            for parameter in TEC_PARAMETERS:
                self._PARAMETERS.append(Parameter(parameter))
        elif metype =='LDD':
            for parameter in LDD_PARAMETERS:
                self._PARAMETERS.append(Parameter(parameter))
        else:
            raise UnknownMeComType

    def get_by_id(self, id):
        """
        Returns a Parameter() identified by it's id.
        :param id: int
        :return: Parameter()
        """
        for parameter in self._PARAMETERS:
            if parameter.id == id:
                return parameter
        raise UnknownParameter

    def get_by_name(self, name):
        """
        Returns a Parameter() identified by it's name.
        :param name: str
        :return: Parameter()
        """
        for parameter in self._PARAMETERS:
            if parameter.name == name:
                return parameter
        raise UnknownParameter


class MeFrame(object):
    """
    Basis structure of a MeCom frame as defined in the specs.
    """
    _TYPES = {"UINT8": "!H", "UINT16": "!L", "INT32": "!i", "FLOAT32": "!f"}
    _SOURCE = ""
    _EOL = "\r"  # carriage return

    def __init__(self):
        self.ADDRESS = 0
        self.SEQUENCE = 0
        self.PAYLOAD = []
        self.CRC = None

    def crc(self, in_crc=None):
        """
        Calculates the checksum of a given frame, if a checksum is given as parameter, the two are compared.
        :param in_crc:
        :return: int
        """
        if self.CRC is None:
            self.CRC = crc16_ccitt_xmodem(self.compose(part=True))

        # crc check
        # print(self.CRC)
        # print(in_crc)
        if in_crc is not None and in_crc != self.CRC:
            raise WrongChecksum

    def compose(self, part=False):
        """
        Returns the frame as bytes, the return-value can be directly send via serial.
        :param part: bool
        :return: bytes
        """
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload can be str or float or int
        for p in self.PAYLOAD:

            if type(p) is str:
                frame += p
            elif type(p) is int:
                frame += "{:08X}".format(p)
            elif type(p) is float:
                # frame += hex(unpack('<I', pack('<f', p))[0])[2:].upper()  # please do not ask
                # if p = 0 CRC fails, e.g. !01000400000000 composes to b'!0100040' / missing zero padding
                frame += '{:08X}'.format(unpack('<I', pack('<f', p))[0])   #still do not aks
        # if we only want a partial frame, return here

        if part:
            return frame.encode()
        # add checksum
        if self.CRC is None:
            self.crc()
        frame += "{:04X}".format(self.CRC)
        # add end of line (carriage return)
        frame += self._EOL
        return frame.encode()

    def _decompose_header(self, frame_bytes):
        """
        Takes bytes as input and decomposes into the instance variables.
        :param frame_bytes: bytes
        :return:
        """
        frame = frame_bytes.decode()

        self._SOURCE = frame[0]
        self.ADDRESS = int(frame[1:3], 16)
        self.SEQUENCE = int(frame[3:7], 16)


class Query(MeFrame):
    """
    Basic structure of a query to get or set a parameter. Has the attribute RESPONSE which contains the answer received
    by the device. The response is set via set_response
    """
    # _SOURCE = "#"
    _SOURCE = "%" # Documentation says #, but official software is sending %.
    _PAYLOAD_START = None

    def __init__(self, parameter=None, sequence=0, address=0, parameter_instance=1):
        """
        To be initialized with a target device address (default=broadcast), the channel, teh sequence number and a
        Parameter() instance of the corresponding parameter.
        :param parameter: Parameter
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        super(Query, self).__init__()

        if hasattr(self, "_PAYLOAD_START"):
            self.PAYLOAD.append(self._PAYLOAD_START)

        self.RESPONSE = None
        self._RESPONSE_FORMAT = None

        self.ADDRESS = address
        self.SEQUENCE = sequence
        if parameter is not None:
            # UNIT16 4 hex digits
            self.PAYLOAD.append("{:04X}".format(parameter.id))

            # # UNIT8 2 hex digits
            self.PAYLOAD.append("{:02X}".format(parameter_instance))

    def set_response(self, response_frame):
        """
        Takes the bytes received from the device as input and creates the corresponding response instance.
        :param response_frame: bytes
        :return:
        """
        # check the type of the response
        # is it an ACK packet?
        if len(response_frame) == 10:
            self.RESPONSE = ACK()
            self.RESPONSE.decompose(response_frame)
        # is it an info string packet/response_frame does not contain source (!)
        elif len(response_frame) == 30:
            self.RESPONSE = IFResponse()
            self.RESPONSE.decompose(response_frame)
        # is it an error packet?
        elif b'+' in response_frame:
            self.RESPONSE = DeviceError()
            self.RESPONSE.decompose(response_frame)
        # nope it's a response to a parameter query
        else:
            self.RESPONSE = VRResponse(self._RESPONSE_FORMAT)
            # if the checksum is wrong, this statement raises
            self.RESPONSE.decompose(response_frame)

        # did we get the right response to our query?
        if self.SEQUENCE != self.RESPONSE.SEQUENCE:
            raise WrongResponseSequence


class VR(Query):
    """
    Implementing query to get a parameter from the device (?VR).
    """
    _PAYLOAD_START = "?VR"

    def __init__(self, parameter, sequence=1, address=0, parameter_instance=1):
        """
        Create a query to get a parameter value.
        :param parameter: Parameter
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        # init header (equal for get and set queries
        super(VR, self).__init__(parameter=parameter,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)
        # initialize response
        self._RESPONSE_FORMAT = parameter.format


class VS(Query):
    """
    Implementing query to set a parameter from the device (VS).
    """
    _PAYLOAD_START = "VS"

    def __init__(self, value, parameter, sequence=1, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param value: int or float
        :param parameter: Parameter
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        # init header (equal for get and set queries)
        super(VS, self).__init__(parameter=parameter,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)

        # the set value
        self.PAYLOAD.append(value)

        # no need to initialize response format, we want ACK
        
        


class RS(Query):
    """
    Implementing system reset.
    """
    _PAYLOAD_START = 'RS'

    def __init__(self, sequence=1, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        
        # init header (equal for get and set queries)
        super(RS, self).__init__(parameter=None,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)

        # no need to initialize response format, we want ACK
        
class IF(Query):
    """
    Implementing device info query.
    """
    _PAYLOAD_START = '?IF'

    def __init__(self, sequence=1, address=0, parameter_instance=1):
        """
        Create a query to set a parameter value.
        :param sequence: int
        :param address: int
        :param parameter_instance: int
        """
        
        # init header (equal for get and set queries)
        super(IF, self).__init__(parameter=None,
                         sequence=sequence,
                         address=address,
                         parameter_instance=parameter_instance)

        # no need to initialize response format, we want ACK


class VRResponse(MeFrame):
    """
    Frame for the device response to a VR() query.
    """
    _SOURCE = "!"
    _RESPONSE_FORMAT = None

    def __init__(self, response_format):
        """
        The format of the response is given via VR.set_response()
        :param response_format: str
        """
        super(VRResponse, self).__init__()
        self._RESPONSE_FORMAT = self._TYPES[response_format]

    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """

        assert self._RESPONSE_FORMAT is not None
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = [unpack(self._RESPONSE_FORMAT, bytes.fromhex(frame[7:15]))[0]]  # convert hex to float or int
        self.crc(int(frame[-4:], 16))  # sets crc or raises


class ACK(MeFrame):
    """
    ACK command sent by the device.
    """
    _SOURCE = "!"
    
    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)
        
        frame = frame_bytes.decode()
        self.CRC = int(frame[-4:], 16)
        

class IFResponse(MeFrame):
    """
    ACK command sent by the device.
    """
    _SOURCE = "!"

    def crc(self, in_crc=None):
        """
        ACK has the same checksum as the VS command.
        :param in_crc: int
        :return:
        """
        pass

    def decompose(self, frame_bytes):
        """
        Takes bytes as input and builds the instance.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)

        frame = frame_bytes.decode()
        self.PAYLOAD = frame[7:-4]
        self.CRC = int(frame[-4:], 16)


class DeviceError(MeFrame):
    """
    Queries failing return a device error, implemented as repsonse by this class.
    """
    _SOURCE = "!"

    def __init__(self):
        """
        Read error codes from command.py and parse into a list of Error() instances.
        """
        super(DeviceError, self).__init__()
        self._ERRORS = []
        for error in ERRORS:
            self._ERRORS.append(Error(error))

    def _get_by_code(self, code):
        """
        Returns a Error() identified by it's error code.
        :param code: int
        :return: Error()
        """
        for error in self._ERRORS:
            if error.code == code:
                return error
        # we do not need to raise here since error are well defined

    def compose(self, part=False):
        """
        Device errors have a different but simple structure.
        :param part: bool
        :return:
        """
        # first part
        frame = self._SOURCE + "{:02X}".format(self.ADDRESS) + "{:04X}".format(self.SEQUENCE)
        # payload is ['+', #_of_error]
        frame += self.PAYLOAD[0]
        frame += "{:02x}".format(self.PAYLOAD[1])
        # if we only want a partial frame, return here
        if part:
            return frame.encode()
        # add checksum
        if self.CRC is None:
            self.crc()
        frame += "{:04X}".format(self.CRC)
        # add end of line (carriage return)
        frame += self._EOL
        return frame.encode()

    def decompose(self, frame_bytes):
        """
        Again, different but consistent structure.
        :param frame_bytes: bytes
        :return:
        """
        frame_bytes = self._SOURCE.encode() + frame_bytes
        self._decompose_header(frame_bytes)
        frame = frame_bytes.decode()
        self.PAYLOAD.append(frame[7])
        self.PAYLOAD.append(int(frame[8:10], 16))
        self.crc(int(frame[-4:], 16))

    def error(self):
        """
        Returns error code, description and symbol as [str,].
        :return: [str, str, str]
        """
        error_code = self.PAYLOAD[1]
        # returns [code, description, symbol]
        return self._get_by_code(error_code).as_list()



TEC_PARAMETER_LIST = ParameterList('TEC')

class MeerstetterBusPacketType(Enum):
    GET_PARAMETER = 0x00
    SET_PARAMETER = 0x01
    SYS_RESET = 0x02
    DEVICE_INFO = 0x03


class MeerstetterBusPacket:
    """
    Packet type used when communicating with the Meerstetter controller hardware

    This is a simple wrapper around the MeCom API which structures the messages
    sent and recived from the Meerstetter controllers. The underlying query classes
    ( VR (get parameter), VS (set parameter), RS (reset device), IF (device info) ) 
    create a query object from the arguments which handles the creation of the TX msg.
    Only VS requires a value ( the set value), and only VS/VR require a parameter name.

    Packet will pass the raw response to the query object which will 
    parse it and put the data payload into the class data variable. 
    """
    raw_packet: bytearray
    query: Query
    packet_type: MeerstetterBusPacketType
    value : int
    parameter : str 
    sequence : int 
    address : int 
    parameter_instance : int
    data : int

    def __init__(
        self,
        packet_type: MeerstetterBusPacketType,
        address : int, 
        sequence : int = 1, 
        parameter : str = "",
        value : int = 0,
    ):
        self.sequence = sequence 
        self.address = address 
        self.packet_type = packet_type

        self.parameter_instance = 1 # Magic number? 1 in all examples
        self.data = 0 # Holds response payload if applicable

        # Initialize the query object and build the raw packet
        if self.packet_type == MeerstetterBusPacketType.GET_PARAMETER:
            self.parameter = TEC_PARAMETER_LIST.get_by_name(parameter)
            self.query = VR(parameter=self.parameter, sequence=self.sequence, address=self.address, parameter_instance=self.parameter_instance)

        elif self.packet_type == MeerstetterBusPacketType.SET_PARAMETER:
            self.parameter = TEC_PARAMETER_LIST.get_by_name(parameter)
            self.value = value
            self.query = VS(value=self.value, parameter=self.parameter, sequence=self.sequence, address=self.address, parameter_instance=self.parameter_instance)
            
        elif self.packet_type == MeerstetterBusPacketType.SYS_RESET:
            self.query = RS(sequence=self.sequence, address=self.address, parameter_instance=self.parameter_instance)
            
        elif self.packet_type == MeerstetterBusPacketType.DEVICE_INFO:
            self.query = IF(sequence=self.sequence, address=self.address, parameter_instance=self.parameter_instance)
        else:
            self.query  = None
        
        try:
            self.raw_packet = self.query.compose()
        except:
            raise ValueError("Invalid Packet Type: {0}".format(self.packet_type))

    def __str__(self):
        return f"<MeerstetterBusPacket: {self.address}, {self.packet_type}, {self.value}, {self.parameter}, '{self.sequence}'>"

    def parse(self, data: bytes):
        """Parse a set of bytes (usually a response packet) using query object and store internally"""
        try:

            # strip source byte (! or #, but for a response always !) and carriage return
            response_frame = data[1:-1]
            self.query.set_response(response_frame)


            # Check for Response Types
            if type(self.query.RESPONSE) == DeviceError:
                raise MeComError("Device Error: {0}".format(self.query.RESPONSE.error))

            elif self.packet_type in [MeerstetterBusPacketType.SYS_RESET, MeerstetterBusPacketType.SET_PARAMETER]  :
                if type(self.query.RESPONSE) != ACK:
                    raise MeComError("Device Not Responsive")

            elif self.packet_type == MeerstetterBusPacketType.DEVICE_INFO:
                if type(self.query.RESPONSE) != IFResponse:
                    raise MeComError("Device Not Responsive")
            
            elif type(self.query.RESPONSE) == VRResponse: # If it was a VR, store the result
                if not isnan(self.query.RESPONSE.PAYLOAD[0]):
                    self.data = self.query.RESPONSE.PAYLOAD[0]
                else:
                    raise MeComError("Response was Nan")
    
            else:
               pass 

        except Exception as e:
            print(e)

