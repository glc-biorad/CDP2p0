import pytest

from app.routers.interfaces.utils_meerstetter import *

#####################################################
# Request Tests - BRADX
#####################################################
def test_meerstetter_build_request():

    pkt =  MeerstetterBusPacket(MeerstetterBusPacketType.DEVICE_INFO, sequence=0x4436, address=0x0)

    assert isinstance(pkt, MeerstetterBusPacket)
    assert pkt.sequence == 0x4436
    assert pkt.address == 0x00
    assert pkt.raw_packet == b'%004436?IF674B\r'

    pkt =  MeerstetterBusPacket(MeerstetterBusPacketType.SYS_RESET, sequence=0x414A, address=0x54)

    assert isinstance(pkt, MeerstetterBusPacket)
    assert pkt.sequence == 0x414A
    assert pkt.address == 0x54
    assert pkt.raw_packet == b'%54414ARS0745\r'


    pkt =  MeerstetterBusPacket(MeerstetterBusPacketType.SET_PARAMETER, sequence=0x4436, address=0x34, parameter="Device Address", value=0x55 )

    assert isinstance(pkt, MeerstetterBusPacket)
    assert pkt.sequence == 0x4436
    assert pkt.address == 0x34
    assert isinstance(pkt.parameter, Parameter)
    assert pkt.parameter.name == "Device Address"
    assert pkt.value == 0x55
    assert pkt.raw_packet == b'%344436VS0803010000005596E7\r'



    pkt =  MeerstetterBusPacket(MeerstetterBusPacketType.GET_PARAMETER, sequence=0xF436, address=0x51, parameter="Target Object Temp (Set)" )

    assert isinstance(pkt, MeerstetterBusPacket)
    assert pkt.sequence == 0xF436
    assert pkt.address == 0x51
    assert isinstance(pkt.parameter, Parameter)
    assert pkt.parameter.name == "Target Object Temp (Set)"

    assert pkt.raw_packet == b'%51F436?VR0BB8016B90\r'

def test_meerstetter_parse_request():

    pkt =  MeerstetterBusPacket(MeerstetterBusPacketType.GET_PARAMETER, sequence=0xF006, address=0x51, parameter="Object Temperature" )
    resp = b'!51F00641B2B852B862'
    
    pkt.parse(resp)

    assert pkt.data > 22.33 # Expected value: 22.34....
    assert pkt.data < 22.35



#####################################################
# CRC Tests - BRADX
#####################################################
def test_meerstetter_crc_conversion():
    crc = crc16_ccitt_xmodem(b"%004436?IF")
    assert crc == 0x674B

