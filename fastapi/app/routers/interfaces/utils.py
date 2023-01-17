import random
import re
from enum import Enum
from typing import List


BUS_PACKET_START = "$"  # BRADx chassis controller message start flag

class BRADxBusModuleType:
    mod_id: int
    resp_len: int
    def __init__(self, mod_id, resp_len) -> None:
        self.mod_id = mod_id
        self.resp_len = resp_len


class BRADxBusPacketType(Enum):
    REQUEST = 0x0D
    RESPONSE = 0x0E

class BRADxBusPacket:
    """
    Packet type used when communicating with the BRADx chassis/bus controller hardware

    The packets have a standard format defined in the project's System Modules API file
    which is duplicated below.

                                    BYTE[256]
        │ 0 │   1  │  2  │   3   │   4    │   5   | 6 │ 7 │   │253│254│255│
        │SOF│SUBSYS│MODID│REQ/RSP│LEN/STAT│RESPLEN|D0 │D1 │...│Dn │CRC│EOF│
        │ $ │      │     │x0D/x0E│        │       |   DATA[0-n]   |   │CR │

    Packets are transmitted between the PC and chassis/bus controller as bytes via a USB
    Virtual COM connection (see BRADxBus.py)
    """

    raw_packet: bytearray
    subsystem_id: int
    module_id: int
    packet_type: BRADxBusPacketType
    data_len: int
    resp_len: int
    data: str
    crc: int

    def __init__(
        self,
        subsystem_id: int,
        module_id: int,
        data: str,
        resp_len: int,
        packet_type: BRADxBusPacketType,
        data_cr: bool = True,
    ):
        self.subsystem_id = subsystem_id
        self.module_id = module_id
        if data_cr and data[-1] != "\r":
            # Append carriage return to data if there isn't one
            data += "\r"
        self.data = data
        self.data_len = len(data)
        self.resp_len = resp_len
        # Build the message section for CRC calculation
        sub_msg = bytearray(
            [subsystem_id, module_id, packet_type.value, self.data_len,self.resp_len]
        ) + bytearray(data, encoding="ascii")
        self.crc = crc16_ccitt(sub_msg)
        # Build the raw packet
        self.raw_packet = bytearray([ord(BUS_PACKET_START)])
        self.raw_packet += sub_msg
        self.raw_packet += bytearray(self.crc.to_bytes(2, "big"))
        self.raw_packet += bytearray([ord("\r")])

    def __str__(self):
        return f"<BRADxBusPacket: {self.subsystem_id}, {self.module_id}, {self.packet_type.name}, '{self.data}'>"

    @classmethod
    def parse(cls, data: bytes):
        """Parse a set of bytes (usually a response packet) and convert to this class type"""
        print(data)
        try:
            sof = chr(data[0])
            if sof != BUS_PACKET_START:
                raise ValueError(f"Incorrect packet start flag ({sof})")
            subsystem_id = int(data[1])
            module_id = int(data[2])
            packet_type = BRADxBusPacketType(int(data[3]))
            dlen = int(data[4])
            resplen = int(data[5])
            # Data starts at byte 6
            subdata = data[6 : (resplen + 6)].decode("ascii")
            # CRC is the last two bytes before the carriage return
            crc = int.from_bytes(data[-3:-1], "little")
            # Create the object
            pkt = BRADxBusPacket(
                subsystem_id, module_id, subdata, resplen, packet_type, data_cr=False
            )
            # Check the crc
            # if pkt.crc != crc:
                # raise ValueError(f"CRC check failed (got {crc:02x}, is {pkt.crc:02x})")
            # Replace the raw packet value with the data
            pkt.raw_packet = bytearray(data)
            return pkt
        except IndexError:
            raise ValueError("Incorrect packet structure (indexing error)")



REQUEST_START_FLAG = ">"  # BRADx system request message start flag
RESPONSE_START_FLAG = "<"  # BRADx system request message start flag
MESSAGE_END_FLAG = "\r"  # BRADx system request message end flag
MESSAGE_MIN_TOKENS = 4  # BRADx system request minimum number of tokens

PIPETTOR_REQUEST_NUM_TOKENS = 6  # Pipettor system request expected number of tokens
PIPETTOR_RESPONSE_NUM_TOKENS = 5 # Pipettor system response expected nimum number of tokens

class PipettorRequest:
    """
    Request message type for Seyonic Pipettor hardware

    Request messages have the following format:
      [address],[command_hi],[command_lo],[data_1],[data_2],[checksum]<cr>
    They contain:
      - An address defining which module the request is for (system ctrl, pressure ctrl, dispensers)
      - The command requested : hi - what needs to be done 
      - The command requested : lo - who (which part of the device) is addressed by the command 
      - 2 Data bytes ("parameters" of the command)
      - A checksum value of the address, command, and data bytes
      - A carriage return signifying the end of the request?
    """

    address: int
    command_hi: int
    command_lo: int
    data: int
    data_lsb: int
    data_msb: int
    checksum: int
    raw: str

    def __init__(
        self,
        address: int,
        command_lo: int,
        command_hi: int,
        data: int,
        calc_checksum: bool = True,

    ) -> None:

        self.address = address
        self.command_lo = command_lo
        self.command_hi = command_hi
        self.data = data
        self.data_lsb = data & 0xFF
        self.data_msb = (data >> 8) & 0xFF

        # Calculate checksum value
        if calc_checksum:
            cs_ba = bytearray([address])
            cs_ba += bytearray([command_lo])
            cs_ba += bytearray([command_hi])
            cs_ba += bytearray([self.data_lsb])
            cs_ba += bytearray([self.data_msb])
            self.checksum = msg_checksum(cs_ba)
        else:
            self.checksum = 0

        # Build raw message string
        self.raw = f"{address:01x} {command_lo} {command_hi} {self.data_lsb} {self.data_msb}"
        self.raw += f"{self.checksum:01x}\r"

    def __str__(self):
        return f"<PipettorRequest: {self.raw.strip()}>"

    @classmethod
    def parse(cls, msg: str, checksum: bool = True):
        """Check that the request message string has a valid format for the Pipettor system and convert it to an object"""
        # Strip flags and tokenize comma separated message
        tokens = msg[0:].strip().split(" ")
        if len(tokens) != PIPETTOR_REQUEST_NUM_TOKENS:
            raise ValueError(
                f"Request token count ({len(tokens)}) invalid: (should be {PIPETTOR_REQUEST_NUM_TOKENS}"
            )
        
        # Deconstruct tokens into request
        address    = int(tokens[0], base=16)
        command_lo = int(tokens[1], base=16)
        command_hi = int(tokens[2], base=16)
        data_lsb   = int(tokens[3], base=16)
        data_msb   = int(tokens[4], base=16)
        checksum   = int(tokens[5], base=16)

        data = (data_msb << 8) + data_lsb
        req = PipettorRequest(address, command_lo, command_hi, data)

        if checksum and req.checksum != checksum:
            raise ValueError(f"Checksum failed (got {checksum:01x}, is {req.checksum:01x})")

        return req

class PipettorResponse:
    """
    Response message type for Pipettor hardware modules
    """

    address: int
    error_code: int
    data: int
    data_lsb: int
    data_msb: int

    checksum: int
    raw: str

    def __str__(self):
        return f"<PipettorResponse: {self.raw.strip()}>"

    @classmethod
    def parse(cls, msg: str):
        """Check that the response message string has a valid format for the Pipettor system and convert it to an object"""
        # Strip flags and tokenize comma separated message
        tokens = msg[0:].strip().split(" ")
        if len(tokens) != PIPETTOR_RESPONSE_NUM_TOKENS:
            raise ValueError(
                f"Response token count ({len(tokens)}) invalid: (should be {PIPETTOR_RESPONSE_NUM_TOKENS}"
            )
        # Deconstruct tokens into response
        resp = PipettorResponse()
        resp.raw        = msg
        resp.address    = int(tokens[0], base=16)
        resp.error_code = int(tokens[1], base=16)
        resp.data_lsb   = int(tokens[2], base=16)
        resp.data_msb   = int(tokens[3], base=16)
        resp.data = (resp.data_msb >> 8) + resp.data_lsb

        resp.checksum   = int(tokens[4], base=16)

        return resp


class BRADXRequest:
    """
    Request message type for BRADx specific hardware modules (e.g. motor controller, LED controller)

    Request messaged have the following format:
      [startflag][address],[request ID][command],[parameters...],[crc]<cr>
    They contain:
      - A start flag designating that the line is a request
      - An address defining which module the request is for
      - A serialized request ID for mapping requests and responses
      - The command requested
      - A comma separated set of command parameters
      - A CRC check value of the address, request ID, command, and parameters
      - A carriage return signifying the end of the request
    """

    address: int
    request_id: int
    command: str
    parameters: List[str]
    crc: int
    raw: str

    def __init__(
        self,
        address: int,
        request_id: int,
        command: str,
        parameters: List[str],
        calc_crc: bool = True,
    ) -> None:
        self.address = address
        self.request_id = request_id
        self.command = command
        self.parameters = parameters

        # Calculate CRC value
        if calc_crc:
            crc_ba = bytearray([address])
            crc_ba += request_id.to_bytes(2, "big")
            crc_ba += bytearray(command, encoding="ascii")
            crc_ba += bytearray("".join(parameters), encoding="ascii")
            self.crc = crc16_ccitt(crc_ba)
        else:
            self.crc = 0

        # Build raw message string
        self.raw = f"{REQUEST_START_FLAG}{address:01x},{request_id:02x},{command},"
        self.raw += "" if len(parameters) == 0 else f"{','.join(parameters)},"
        self.raw += f"{self.crc:02x}\r"

    def __str__(self):
        return f"<BRADXRequest: {self.raw.strip()}>"

    @classmethod
    def parse(cls, msg: str, check_crc: bool = True):
        """Check that the request message string has a valid format for the BRADx system and convert it to an object"""
        if msg[0] != REQUEST_START_FLAG:
            raise ValueError(
                f"Request start flag incorrect '{msg[0]!r}' (should be {REQUEST_START_FLAG!r})"
            )
        if msg[-1] != MESSAGE_END_FLAG:
            raise ValueError(
                f"Request end flag incorrect '{msg[-1]!r}' (should be {MESSAGE_END_FLAG!r})"
            )
        # Strip flags and tokenize comma separated message
        tokens = msg[1:].strip().split(",")
        if len(tokens) < MESSAGE_MIN_TOKENS:
            raise ValueError(
                f"Request token count ({len(tokens)}) too low (should be at least {MESSAGE_MIN_TOKENS}"
            )
        # Deconstruct tokens into request
        address = int(tokens[0], base=16)
        request_id = int(tokens[1], base=16)
        command = tokens[2]
        if len(tokens) > MESSAGE_MIN_TOKENS:
            parameters = tokens[3:-1]
        else:
            parameters = []
        crc = int(tokens[-1], base=16)
        req = BRADXRequest(address, request_id, command, parameters)

        if check_crc and req.crc != crc:
            raise ValueError(f"CRC check failed (got {crc:02x}, is {req.crc:02x})")

        return req


class BRADXResponse:
    """
    Response message type for BRADx specific hardware modules (e.g. motor controller, LED controller)
    """

    address: int
    request_id: int
    response: List[str]
    crc: int
    raw: str

    def __str__(self):
        return f"<BRADXResponse: {self.raw.strip()}>"

    @classmethod
    def parse(cls, msg: str):
        """Check that the response message string has a valid format for the BRADx system and convert it to an object"""
        if msg[0] != RESPONSE_START_FLAG:
            raise ValueError(
                f"Response start flag incorrect '{msg[0]!r}' (should be {RESPONSE_START_FLAG!r})"
            )
        if msg[-1] != MESSAGE_END_FLAG:
            raise ValueError(
                f"Response end flag incorrect '{msg[-1]!r}' (should be {MESSAGE_END_FLAG!r})"
            )
        # Strip flags and tokenize comma separated message
        tokens = msg[1:].strip().split(",")
        if len(tokens) < MESSAGE_MIN_TOKENS:
            raise ValueError(
                f"Response token count ({len(tokens)}) too low (should be at least {MESSAGE_MIN_TOKENS}"
            )
        # Deconstruct tokens into response
        resp = BRADXResponse()
        resp.raw = msg
        resp.address = int(tokens[0], base=16)
        resp.request_id = int(tokens[1], base=16)
        resp.response = tokens[2:-1]
        resp.crc = int(tokens[-1], base=16)

        return resp

class BRADXRawRequest:
    """
    Request message type for BRADx COTS hardware modules that don't follow BRADx modules packet format(e.g. heater shaker, chiller)

    Request messaged have the following format:
      raw[]\r
    They contain:
          - A raw data array with command and parameters
          - A \r to mark end of command to respective module
    """
    raw: str

    def __init__(
        self,
        command: str
    ) -> None:
        self.command = command
        # Build raw message string
        self.raw = f"{command}\r"

    def __str__(self):
        return f"<BRADXRawRequest: {self.raw.strip()}>"
 
    @classmethod
    def parse(cls, msg: str):
        """Check that the request message string has a valid format for the BRADx system and convert it to an object"""
        # Deconstruct tokens into request
        command = msg.strip()
        req = BRADXRawRequest(command)
        return req


class BRADXRawResponse:
    """
    Response message type for BRADx COTS hardware modules that don't follow BRADx modules packet format(e.g. heater shaker, chiller)
    """
    raw: str
    resp: str

    def __str__(self):
        return f"<BRADXRawResponse: {self.raw.strip()}>"

    @classmethod
    def parse(cls, msg: str):
        """Check that the request message string has a valid format for the BRADx system and convert it to an object"""
        # Deconstruct tokens into response
        resp = BRADXRawResponse()
        resp.raw = msg
        resp.resp = msg.strip()
        return resp


# CRC calculation using the CRC-16-CCITT algorithm parameters
# polynomial: x^16 + x^12 + x^5 + 1
# see: https://crccalc.com/?crc=123456789&method=CRC-16/CCITT-FALSE&datatype=ascii&outtype=0
# fmt: off

CRC_16_CCITT_LUT = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
    0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
    0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
    0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
    0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
    0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
    0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
    0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
    0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
    0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
    0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
    0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
    0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
    0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
    0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
    0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
    0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
    0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
    0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
    0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
    0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
    0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0,
]
# fmt: on


def crc16_ccitt(buf: bytearray) -> int:
    crc = 0xFFFF
    for byte in buf:
        crc = (crc << 8) ^ CRC_16_CCITT_LUT[(crc >> 8) ^ byte]
        crc &= 0xFFFF  # truncate to 16 bits
    return crc


def msg_checksum(buf: bytearray) -> int:
    cs = 0x0000
    for byte in buf:
        cs += byte

    cs &= 0xFF  # truncate to 8 bits
    return cs


def rand_request_id() -> int:
    """Generate a random request ID value"""
    return random.randrange(0, 65535)


def parse_motor_distance_str(s: str) -> str:
    """Return the compenents of a numeric string"""
    # Format expected: [opt: sign][number][opt: decimal point][opt: decimal][unit]
    m = re.search(r"(-)?([0-9]*)[.]?([0-9]+)?([a-zA-Z]*)", s)
    sign, n1,n2,units = m.groups()
    
    return sign, n1, n2, units.lower()


def convert_distance_str_to_steps(s: str, step_to_um_ratio: int) -> int:
    """Parse the distance infomation and return a rounded step amount"""

    sign, n1,n2,units = parse_motor_distance_str(s)

    if (n2 != None):
        steps = float("{0}.{1}".format(n1,n2))
    else:
        steps = float(n1)
    
    if (sign == "-"):
        steps = steps * -1
    
    # Convert everything into um
    if units == 'um':
        pass
    elif units == "mm":
        steps = steps * 1000
    else:
        # Invalid Units
        return 0
    
    # Convert from um to steps
    steps = steps * step_to_um_ratio

    # Round to int
    steps = int(steps)
    
    return steps