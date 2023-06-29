import time
from typing import Union
from chassis_controller.app.config.BRADx_config import *

import aioserial
import serial.tools.list_ports
import platform

from chassis_controller.app.routers.interfaces.utils import BRADxBusPacket, BRADxBusPacketType

current_os = platform.system()
COMM_SUBSYSTEM_ID = 0x00 # Windows needs to send/recieve to the chassis controller to confirm when connecting over COM

class BRADxBusRouterInterface:
    """BRADx bus router interface class to communicate with modules in the BRADx system"""

    def __init__(self, port: str, baud: int = 115200, timeout: float = 30.0) -> None:
        self.port = port
        self.baud = baud
        self.timeout = timeout

        self._connection = aioserial.AioSerial()
        self._connection.write_timeout = 0.0  # make writes non-blocking

    @property
    def is_connected(self) -> bool:
        return self._connection.is_open

    def connect(self) -> Union[IOError, bool]:
        """Connect to the interfaces's port, returns True on successful connection"""
        if self._connection.is_open:
            self._connection.close()
        self._connection.port = self.port
        self._connection.baudrate = self.baud
        self._connection.timeout = self.timeout
        try:
            self._connection.open()
            return True
        except serial.SerialException:
            raise IOError(f"BRADx interface could not connect to port {self.port}")

    def disconnect(self):
        """Disconnect from the interface's port"""
        if self._connection.is_open:
            self._connection.close()

    async def exchange_async(self, message: bytearray) -> Union[IOError, bytes]:
        """Send a request and receive a response on the interface connection"""
        if not self._connection.is_open:
            raise IOError("BRADx chassis interface not connected")
        # Write the message, not buffered and non-blocking (see __init__)
        self._connection.write(message)
        # Get response (non-blocking)
        resp = await self._connection.read_async(256)
        return resp

    def exchange(self, message: bytearray) -> Union[IOError, bytes]:
        """Send a request and receive a response on the interface connection"""
        if not self._connection.is_open:
            raise IOError("BRADx chassis interface not connected")
        # Write the message, not buffered and non-blocking (see __init__)
        self._connection.write(message)
        # Get response (blocking)
        resp = self._connection.read(256)
        return resp

    @staticmethod
    def list_ports():
        """List all the available serial ports in the system"""
        return serial.tools.list_ports.comports()

    @classmethod
    def find_and_connect(cls):
        """Find an attached BRADx chassis controller device and connect to it"""
        bradx_ports = list(serial.tools.list_ports.comports())
        for port in bradx_ports:
            if port.pid == 22336:
                print('Found BRADx Chassis controller on '+str(port.name)+'\n')
                conn = cls(port.device)
                conn.connect()
                return conn
        raise ValueError("No BRADx chassis controller device found")

async def bradx_bus_timed_exchange(req: BRADxBusPacket) -> tuple:
    print(str(req.raw_packet))
    """Return a tuple containing the response packet object
    and the elapsed time (in microseconds) to complete the exchange"""
    begin = time.time_ns()
    conn = BRADxBusRouterInterface.find_and_connect()
    print(conn._connection)

    try:
        resp = await conn.exchange_async(req.raw_packet)
        pkt = BRADxBusPacket.parse(resp)
        end = time.time_ns()
    finally:    
        conn.disconnect() # Close the connection now that we are done with it
    
    elapsed = (end - begin) // 1000

    return (pkt, elapsed)
