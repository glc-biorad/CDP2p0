
# Version: Test
from fastapi import APIRouter, HTTPException, Query
from chassis_controller.app.routers.interfaces.utils import convert_distance_str_to_steps
from chassis_controller.app.config.BRADx_config import *

from .interfaces.utils import (
    BRADXRequest,
    BRADxBusPacket,
    BRADxBusPacketType,
    PipettorRequest,
    rand_request_id,
)
from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange
from chassis_controller.app.routers.interfaces.PipettorBus import pipettor_bus_timed_exchange

# Subsystem ID when accessed through the chassis/bus module
PIPETTOR_GANTRY_SUBSYSTEM_ID = 0x01

router = APIRouter(
    prefix="/pipettor_gantry",
    tags=["pipettor_gantry"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/axis/version/{id}")
async def get_version(id: int):
    """Returns the version info of the given axis"""
    if id not in [
        PIPETTOR_X_MOTOR,
        PIPETTOR_Y_MOTOR,
        PIPETTOR_Z_MOTOR,
        PIPETTOR_DRIP_MOTOR,
        PIPETTOR_AIR_SYSTEM,
        TEST
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PIPETTOR_BUS_ADDR[id], rand_request_id(), "?ver", [])
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        version = pkt.data
        print("version: "+pkt.data+"\n\n")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "version": "v"+version[8]+"."+version[9]+"."+version[10]
    }

@router.get("/axis/position/{id}")
async def get_status_and_position(id: int):
    """
    Returns the status and most recent position value of given axis

    Axis Name (Address)

    ____________________

    X (0x01)

    Y (0x02)

    Z (0x03)

    Drip Plate (0x04)

    """
    if id not in [
        PIPETTOR_X_MOTOR,
        PIPETTOR_Y_MOTOR,
        PIPETTOR_Z_MOTOR,
        PIPETTOR_DRIP_MOTOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PIPETTOR_BUS_ADDR[id], rand_request_id(), "?pos", [])
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/home/{id}")
#async def home_axis(id: PipettorGantryAxisOptions):
async def home_axis(id: int):
    """
    Home the axis
    
    Axis Name (Address)

    ____________________

    X (0x01)

    Y (0x02)

    Z (0x03)

    Drip Plate (0x04)

    """
    # Convert string to address
    #id_enum = id
    #id = PipettorGantryAxisOptions.get_id(PipettorGantryAxisOptions, id_enum.value)
    #print(id_enum)
    #print('here')
    #address = PipettorGantryAxisOptions.get_address(PipettorGantryAxisOptions, id_enum.value)
    if id not in [
        PIPETTOR_X_MOTOR,
        PIPETTOR_Y_MOTOR,
        PIPETTOR_Z_MOTOR,
        PIPETTOR_DRIP_MOTOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PIPETTOR_BUS_ADDR[id], rand_request_id(), "home", [])
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/move/{id}")
async def set_axis_position(
    id: int,
    position: int = Query(description="Axis absolute position"),
    velocity: int = Query(description="Velocity to use when moving"),
):
    """
    Set the position of the axis
    
    Axis Name (Address)

    ____________________

    X (0x01)

      - Hard Limit (usteps): 

      - Maximum Velocity (steps):

    Y (0x02)

      - Hard Limit (usteps): 

      - Maximum Velocity (steps):

    Z (0x03)

      - Hard Limit (usteps): 

      - Maximum Velocity (steps):

    Drip Plate (0x04)

      - Hard Limit (usteps): 

      - Maximum Velocity (steps):
    """
    if id not in [
        PIPETTOR_X_MOTOR,
        PIPETTOR_Y_MOTOR,
        PIPETTOR_Z_MOTOR,
        PIPETTOR_DRIP_MOTOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(
        PIPETTOR_BUS_ADDR[id], rand_request_id(), "mabs", [str(position), str(velocity)]
    )
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }



@router.post("/air_valve_on/{chan}")
async def set_valve_on(
    chan: int
    ):
    """
    Turns on the desired air valves

    Returns the status of the addressed Valve
    

    Air Valve Name: Description 

    ---------------------------------

    Valve 1: Tip Eject

    Valve 2: Aspirate/Dispense

    Valve 3: Suction Cups
    """
    if chan < 0 or chan > 3:
        raise HTTPException(status_code=404, detail="Valve channel out of range [0-3]")

    # Build the request message and packet
    message = BRADXRequest(PIPETTOR_AIR_SYSTEM, rand_request_id(), "relayon", [str(chan)])
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, PIPETTOR_AIR_SYSTEM, message.raw, 20, BRADxBusPacketType.REQUEST
        )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": PIPETTOR_AIR_SYSTEM,
        "_duration_us": elapsed,
        "message": "",
        "response": pkt.data,
    }

@router.post("/air_valve_off/{chan}")
async def set_valve_off(
    chan: int
    ):
    """
    Turns off the desired air valve

    Returns the status of the addressed Valve
    
    Air Valve Name: Description 

    ---------------------------------

    Valve 0: Tip Eject

    Valve 1: Aspirate/Dispense

    Valve 2: Suction Cups
    """
    if chan < 0 or chan > 3:
        raise HTTPException(status_code=404, detail="Valve channel out of range [0-3]")

    # Build the request message and packet
    message = BRADXRequest(PIPETTOR_AIR_SYSTEM, rand_request_id(), "relayoff", [str(chan)])
    req = BRADxBusPacket(
        PIPETTOR_GANTRY_SUBSYSTEM_ID, PIPETTOR_AIR_SYSTEM, message.raw, 20, BRADxBusPacketType.REQUEST
        )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PIPETTOR_GANTRY_SUBSYSTEM_ID,
        "_mid": PIPETTOR_AIR_SYSTEM,
        "_duration_us": elapsed,
        "message": "",
        "response": pkt.data,
    }
    