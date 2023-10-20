
# Version: Test
from fastapi import APIRouter, Query, HTTPException

from chassis_controller.app.routers.interfaces.utils import BRADxBusPacket, BRADxBusPacketType
from chassis_controller.app.routers.interfaces.BRADxBus import bradx_bus_timed_exchange
from chassis_controller.app.config.BRADx_config import *

router = APIRouter(
    prefix="",
    tags=["Hardware Interface"],
    dependencies=[],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal error"},
    },
)


@router.get("/")
async def root():
    return {"message": "BRADx System Hardware Interface"}
