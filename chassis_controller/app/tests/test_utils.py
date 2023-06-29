import pytest

from app.routers.interfaces.utils import *

#####################################################
# Request Tests - BRADX
#####################################################
def test_bradx_build_request():
    req = BRADXRequest(0xA, 0x0FEF, "name", ["test_name"])
    assert isinstance(req, BRADXRequest)
    assert req.address == 0x0A
    assert req.request_id == 0x0FEF
    assert req.command == "name"
    assert len(req.parameters) == 1
    assert req.parameters[0] == "test_name"
    assert req.crc == 0x9A82


def test_bradx_request_is_valid():
    req = BRADXRequest.parse(">0a,0fef,status?,c9ce\r")
    assert isinstance(req, BRADXRequest)
    assert req.address == 0x0A
    assert req.request_id == 0x0FEF
    assert req.command == "status?"
    assert req.crc == 0xC9CE


def test_bradx_request_with_params_is_valid():
    req = BRADXRequest.parse(">0a,0fef,name,test_name,9a82\r")
    assert isinstance(req, BRADXRequest)
    assert req.address == 0x0A
    assert req.request_id == 0x0FEF
    assert req.command == "name"
    assert len(req.parameters) == 1
    assert req.parameters[0] == "test_name"
    assert req.crc == 0x9A82


def test_bradx_request_missing_start_token():
    with pytest.raises(ValueError):
        BRADXRequest.parse("0a,0fef,status?,0\r")


def test_bradx_request_missing_end_token():
    with pytest.raises(ValueError):
        BRADXRequest.parse(">0a,0fef,status?,0")


def test_bradx_request_missing_address():
    with pytest.raises(ValueError):
        BRADXRequest.parse(">0fef,status?,0\r")


def test_bradx_request_bad_address_value():
    with pytest.raises(ValueError):
        BRADXRequest.parse(">xyz,0fef,status?,0\r")


#####################################################
# Response Tests - BRADX
#####################################################
def test_bradx_response_is_valid():
    resp = BRADXResponse.parse("<0a,0fef,status,0abc,0\r")
    assert isinstance(resp, BRADXResponse)
    assert resp.address == 0x0A
    assert resp.request_id == 0x0FEF
    assert len(resp.response) == 2
    assert resp.response[0] == "status"
    assert resp.response[1] == "0abc"
    assert resp.crc == 0


def test_bradx_response_missing_start_token():
    with pytest.raises(ValueError):
        BRADXResponse.parse("0a,0fef,status,0abc,0\r")


def test_bradx_response_missing_end_token():
    with pytest.raises(ValueError):
        BRADXResponse.parse("<0a,0fef,status,0abc,0")


def test_bradx_response_missing_address():
    with pytest.raises(ValueError):
        BRADXResponse.parse("<0fef,status,0abc,0\r")


def test_bradx_response_bad_address_value():
    with pytest.raises(ValueError):
        BRADXResponse.parse("<xyz,0fef,status,0abc,0\r")


#####################################################
# CRC Tests - BRADX
#####################################################
def test_bradx_crc_conversion():
    crc = crc16_ccitt(b"123456789")
    assert crc == 0x29B1


#####################################################
# Request Tests - Pipettor
#####################################################
def test_pipettor_build_request():
    req = PipettorRequest(0x10, 0x01, 0x13, 0xF12C)
    assert isinstance(req, PipettorRequest)
    assert req.address == 0x10
    assert req.command_lo == 0x01
    assert req.command_hi == 0x13
    assert req.data_lsb == 0x2C
    assert req.data_msb == 0xF1
    assert req.checksum == 0x41


def test_pipettor_request_is_valid():
    req = PipettorRequest.parse("10 03 2D 0 0 40\r")
    assert isinstance(req, PipettorRequest)
    assert req.address == 0x10
    assert req.command_lo == 0x03
    assert req.command_hi == 0x2D
    assert req.data_lsb == 0x00
    assert req.data_msb == 0x00
    assert req.checksum == 0x40


def test_pipettor_request_with_params_is_valid():
    req = PipettorRequest.parse("10 03 2D 14 52 A6\r")
    assert isinstance(req, PipettorRequest)
    assert req.address == 0x10
    assert req.command_lo == 0x03
    assert req.command_hi == 0x2D
    assert req.data_lsb == 0x14
    assert req.data_msb == 0x52
    assert req.checksum == 0xA6


def test_pipettor_request_not_enough_params():
    with pytest.raises(ValueError):
        PipettorRequest.parse("10 03 2D 14 52\r")

def test_pipettor_request_too_many_params():
    with pytest.raises(ValueError):
        PipettorRequest.parse("10 03 2D 14 52 A6 D3\r")


#####################################################
# Response Tests -  Pipettor
#####################################################
def test_pipettor_response_is_valid():
    resp = PipettorResponse.parse("10 01 82 A8 B5\r")
    assert isinstance(resp, PipettorResponse)
    assert resp.address      == 0x10
    assert resp.error_code   == 0x01
    assert resp.data_lsb     == 0x82
    assert resp.data_msb     == 0xA8
    assert resp.checksum     == 0xB5

def test_pipettor_response_not_enough_params():
    with pytest.raises(ValueError):
        PipettorResponse.parse("10 03 2D\r")

def test_pipettor_response_too_many_params():
    with pytest.raises(ValueError):
        PipettorResponse.parse("10 03 2D 14 52 A6 D3\r")



#####################################################
# Checksum Tests -  Pipettor
#####################################################
def test_pipettor_checksum():
    b = bytearray([0x10, 0x01, 0x13, 0xF1, 0x2C])
    crc = msg_checksum(b)
    assert crc == 0x41



#####################################################
# Distance String to Steps Check -  Motor
#####################################################
def test_motor_string_parse():
    test_str = ['200mm','200nm','200 mm','200.123km']
    for s in test_str:
        sign, n1,n2,units = parse_motor_distance_str(s)
        assert n1 == '200'

def test_convert_distance_str_to_steps():

    s = '200.54mm'
    r = 105
    steps = convert_distance_str_to_steps(s,r)

    assert steps == 21056700

    s = '15.5um'
    r = 97
    steps = convert_distance_str_to_steps(s,r)

    print(steps)

    assert steps == 1503