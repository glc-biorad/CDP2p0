from fastapi import APIRouter, HTTPException, Query
from chassis_controller.app.config.BRADx_config import *

from .interfaces.utils import (
    BRADXRequest,
    BRADXRawRequest,
    BRADxBusPacket,
    BRADxBusPacketType,
    rand_request_id,
)
from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange


router = APIRouter(
    prefix="/prep_deck",
    tags=["prep_deck"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)



@router.get("/chiller-heater-shaker_raw_command/{id,command}")
async def get_version(id: int = Query(description="ID - 1 for Chiller, 2 for Heater/Shaker"),
                      command: str = Query(description="command - string")):
    """Returns the version info of chiller / heater-shaker"""
    if id not in [      
        PREP_PLATE_CHILLER,  
        PREP_HEATER_SHAKER         
    ]:
        raise HTTPException(
            status_code=500, detail=f"Chiller / Heater-shaker ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRawRequest(command)
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 64, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw,
        "response": pkt.data,
    }    



@router.get("/heater_shaker/{id}")
async def get_states(id: int):
    """Returns the on/off state of all coils"""
    if id not in [
        PREP_THERMOCYCLER_1,
        PREP_THERMOCYCLER_2,
        PREP_MARLOW,        
        PREP_HEATER_RNA_1,  
        PREP_HEATER_RNA_2,  
        PREP_HEATER_RNA_3,  
        PREP_HEATER_RNA_4  
    ]:
        raise HTTPException(
            status_code=500, detail=f"Heater at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_BUS_ADDR[id], rand_request_id(), "?coils", [])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 30, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }

@router.post("/heater_shaker/{id}")
async def set_heater_time(
    id: int,
    channel: int = Query(description="Channel ID"),
    set_time: int = Query(description="Set Time"),
):
    """Turn on Heater Channel for a set time"""
    if id not in [
        PREP_PLATE_CHILLER, 
        PREP_HEATER_SHAKER, 
        PREP_THERMOCYCLER_1,
        PREP_THERMOCYCLER_2,
        PREP_MARLOW,         
    ]:
        raise HTTPException(
            status_code=500, detail=f"Heater at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_BUS_ADDR[id], rand_request_id(), "set", [str(channel), str(set_time)])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 30, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.get("/meerstetter/{id}")
async def get_temp(id: int):
    """Returns the current temp of the heater"""
    if id not in [      
        PREP_HEATER_RNA_1,  
        PREP_HEATER_RNA_2,  
        PREP_HEATER_RNA_3,  
        PREP_HEATER_RNA_4  
    ]:
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_BUS_ADDR[id], rand_request_id(), "?temp", [])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 30, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }

@router.post("/meerstetter/{id}")
async def set_meerstetter_setpoint(
    id: int,
    setpoint: int = Query(description="Heater Setpoint"),
):
    """Turn on Heater Channel for a set time"""
    if id not in [      
        PREP_HEATER_RNA_1,  
        PREP_HEATER_RNA_2,  
        PREP_HEATER_RNA_3,  
        PREP_HEATER_RNA_4  
    ]:
        raise HTTPException(
            status_code=500, detail=f"Meerstetter at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_BUS_ADDR[id], rand_request_id(), "set", [str(setpoint)])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 30, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }

@router.get("/axis/version/{id}")
async def get_version(id: int):
    """Returns the version info of the given axis"""
    if id not in [
        PREP_MAG_SEPARATOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_MAG_SEPARATOR, rand_request_id(), "?ver", [])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
        version = pkt.data
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "version": "v"+version[8]+"."+version[9]+"."+version[10]
    }

@router.get("/axis/position/")
async def get_status_and_position():
    """Returns the status and most recent position value of the Mag Separator"""
    id = PREP_MAG_SEPARATOR
    if id not in [
        PREP_MAG_SEPARATOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_BUS_ADDR[id], rand_request_id(), "?pos", [])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 25, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/move/")
async def set_axis_position(
    position: int = Query(description="""
    Axis absolute position (usteps)
     Home (Engage Magnet): 0
     Hard Limit (Disengage Magnet): -140000
    """),
    velocity: int = Query(description="""
    Velocity to use when moving (usteps/sec)
     Homing Velocity: ?
     Max Velocity: 50000
    """),
):
    """Set the position of the Mag Separator"""
    id = PREP_MAG_SEPARATOR
    if id not in [
        PREP_MAG_SEPARATOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(
        PREP_MAG_SEPARATOR , rand_request_id(), "mabs", [str(position), str(velocity)]
    )
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }



@router.post("/axis/jog/{id}")
async def jog_axis(
    id: int,
    distance: str = Query(description="Axis jog distance and direction (units required (mm/um), sign and decimal point optional"),
    velocity: int = Query(description="Velocity to use when moving"),
):
    """Set the position of the axis"""
    if id not in [
        PREP_MAG_SEPARATOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )

    # Convert the string to a step amount
    steps = convert_distance_str_to_steps(distance, PIPETTOR_STEP_RATIO[id])

    # Build the request message and packet
    message = BRADXRequest(PREP_MAG_SEPARATOR , rand_request_id(), "mrel", [str(steps), str(velocity)])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }


@router.post("/axis/home/")
async def home_axis():
    """Home the Mag Separator"""
    id = 6
    if id not in [
        PREP_MAG_SEPARATOR,
    ]:
        raise HTTPException(
            status_code=500, detail=f"Motor axis at ID {id} not available"
        )
    # Build the request message and packet
    message = BRADXRequest(PREP_MAG_SEPARATOR, rand_request_id(), "home", [])
    req = BRADxBusPacket(
        PREP_DECK_SUBSYSTEM_ID, id, message.raw, 20, BRADxBusPacketType.REQUEST
    )
    # Send the request and get the response
    try:
        pkt, elapsed = await bradx_bus_timed_exchange(req)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "_sid": PREP_DECK_SUBSYSTEM_ID,
        "_mid": id,
        "_duration_us": elapsed,
        "message": message.raw.strip(),
        "response": pkt.data,
    }

