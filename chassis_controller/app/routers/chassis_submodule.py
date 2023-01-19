from fastapi import APIRouter, Query, HTTPException

from chassis_controller.app.routers.interfaces.utils import (
    REQUEST_START_FLAG,
    RESPONSE_START_FLAG,
    BRADXRequest,
    BRADXResponse,
    BRADxBusPacket,
    BRADxBusPacketType,
)
from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange

router = APIRouter(
    prefix="/chassis",
    tags=["chassis"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal error"},
    },
)



# Subsystem module IDs and response lengths when accessed through the chassis/bus module
POWER_MONITORS = 0x01
POWER_RELAYS = 0x02
SYSTEM_MONITORS = 0x03
CHASSIS_GPIO    = 0x04
CHASSIS_VER     = 0x05
REMOTE_PROG     = 0x06

# A dictionary of power supplies and their info based on ID
CHASSIS_POWER_SUPPLIES = {0: "36V, Motors"}

@router.get("/chassis/remoteProg")
async def get_remoteProg():
    """Pushes the chassis module in to bootloader"""
    # Build the request message and packet
    message = BRADXRequest(REMOTE_PROG, rand_request_id(), "rprog", [])
    # Build the request message and packet
    req = BRADxBusPacket(
        CHASSIS_SUBSYSTEM_ID, REMOTE_PROG, message.raw, 25, BRADxBusPacketType.REQUEST)
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": CHASSIS_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw,
        "response": pkt.data
    }

@router.get("/chassis/version")
async def get_chassis_version():
    """Returns the version info of the chassis bus controller FW"""
    # Build the request message and packet
    message = BRADXRequest(CHASSIS_VER, 0, "?ver", [])
    # Build the request message and packet
    req = BRADxBusPacket(
        CHASSIS_SUBSYSTEM_ID, CHASSIS_VER, message.raw, 25, BRADxBusPacketType.REQUEST)
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        version = pkt.data
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": CHASSIS_SUBSYSTEM_ID,
        "_mid": CHASSIS_VER,
        "_duration_us": elapsed,
        "message": message.raw,
        "version": "v"+version[0]+"."+version[1]+"."+version[2]        
    }
    
@router.get("/raw")
async def exchange_raw_request_response(
    subsystem_id: int = Query(description="Subsystem ID to address", ge=0x0, le=0x03),
    module_id: int = Query(
        description="Subsystem module ID to address", ge=0x0, le=0x10
    ),
    message: str = Query(description="Message to send", max_length=247),
    add_cr: bool = Query(
        description="Append carriage return to end of message", default=True
    ),
):
    """Send a raw request to the chassis/bus controller and get the response"""
    # Build the request message, set expected response to max length
    req = BRADxBusPacket(
        subsystem_id, module_id, message, 247, BRADxBusPacketType.REQUEST, add_cr
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": subsystem_id,
        "_mid": module_id,
        "_duration_us": elapsed,
        "message": message,
        "response": pkt.data,
    }


@router.get("/power/{id}")
async def get_power_supply_status(id: int):
    """Returns the status of the addressed power supply"""
    if id not in CHASSIS_POWER_SUPPLIES.keys():
        raise HTTPException(status_code=404, detail="Power supply ID not found")

    # Build the request message (power monitor is module 1 on chassis subsystem)
    req = BRADxBusPacket(
        CHASSIS_SUBSYSTEM_ID,
        POWER_MONITORS,
        f"{id}?",
        15, # Max expected response in bytes
        BRADxBusPacketType.REQUEST,
        data_cr=False,
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": CHASSIS_SUBSYSTEM_ID,
        "_mid": POWER_MONITORS,
        "_duration_us": elapsed,
        "message": "",
        "response": pkt.data,
    }


@router.post("/relay/{chan}")
async def set_power_relay_state(
    chan: int,
    state: bool = Query(description="Relay state (on/off)")
    ):
    """
    Turn on (True) or off (False) the desired relay

    Returns the status of the addressed power supply

    Relay Name (Address): Description

    ------------------------

    PC Power (0x00): 

    Pre-Amp Thermocycler (0x01):

    Thermocycler A (0x02):

    Thermocycler B (0x03):

    Thermocycler C (0x04):

    Thermocycler D (0x05):

    Motion Power (0x06):

    Heater/Shaker and Chiller (0x07):

    Control Relay (0x08): DO NOT CHANGE

	TIP EJECT VALVE (0x08):
	
    Interlock Relay (0x10): DO NOT CHANGE

    """
    if chan < 0 or chan > 15:
        raise HTTPException(status_code=404, detail="Relay channel out of range [0-15]")

    # Build the request message (relay driver is module 2 on chassis subsystem)
    if state:
        dstate = 1
    else:
        dstate = 0
    req = BRADxBusPacket(
        CHASSIS_SUBSYSTEM_ID,
        POWER_RELAYS,
        f"{chan:X}{dstate}",
        0, # Max expected response in bytes
        BRADxBusPacketType.REQUEST,
        data_cr=False,
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": CHASSIS_SUBSYSTEM_ID,
        "_mid": POWER_RELAYS,
        "_duration_us": elapsed,
        "message": "",
        "response": pkt.data,
    }

@router.post("/GPIO Port E/{chan}")
async def set_gpio_state(
    chan: int,
    state: bool = Query(description="GPIO state (on/off)")
    ):
    """Returns the status of the addressed GPIO pin (0-7) on Port E"""
    if chan < 0 or chan > 7:
        raise HTTPException(status_code=404, detail="GPIO channel out of range [0-7]")

    # Build the request message (relay driver is module 2 on chassis subsystem)
    if state:
        dstate = 1
    else:
        dstate = 0
    req = BRADxBusPacket(
        CHASSIS_SUBSYSTEM_ID,
        CHASSIS_GPIO,
        f"{chan:X}{dstate}",
        0, # Max expected response in bytes
        BRADxBusPacketType.REQUEST,
        data_cr=False,
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": CHASSIS_SUBSYSTEM_ID,
        "_mid": CHASSIS_GPIO,
        "_duration_us": elapsed,
        "message": "",
        "response": pkt.data,
    }
@router.get("/utils/module_crc_calc")
def calculate_crc_for_module_message(
    message: str = Query(title="BRADx module message", max_length=100)
):
    """
    Returns the calculated CRC value for the given BRADx module message.

    The message string should include the appropriate start flag for a
    request or response. A carriage return will be appended to the end
    of the message string and the value in the CRC position of the message
    will be ignored.

    Example:
        `>0a,0fef,name,test_name,0`

    Return:
        `{"message": ">a,fef,name,test_name,9a82", "crc": "9a82"}`
    """
    if len(message) <= 0:
        raise HTTPException(status_code=500, detail="No message provided")
    elif message[0] == REQUEST_START_FLAG:
        req = BRADXRequest.parse(f"{message}\r", check_crc=False)
        return {"message": req.raw.strip(), "crc": f"{req.crc:02x}"}
    elif message[0] == RESPONSE_START_FLAG:
        resp = BRADXResponse.parse(f"{message}\r", check_crc=False)
        return {"message": resp.raw.strip(), "crc": f"{resp.crc:02x}"}
    else:
        raise HTTPException(
            status_code=500, detail="Message is not a BRADx request or response type"
        )
