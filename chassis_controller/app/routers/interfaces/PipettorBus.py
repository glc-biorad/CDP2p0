
# Version: Test
import time
from typing import Union

import aioserial
import serial.tools.list_ports

from chassis_controller.app.routers.interfaces.utils import PipettorResponse, PipettorRequest


class PipettorBusRouterInterface:
    """Pipettor bus router interface class to communicate with modules in the Pipettor system"""

    def __init__(self, port: str, baud: int = 115200, timeout: float = 1.0) -> None:
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
            raise IOError(f"Pipettor interface could not connect to port {self.port}")

    def disconnect(self):
        """Disconnect from the interface's port"""
        if self._connection.is_open:
            self._connection.close()

    async def exchange(self, message: bytearray) -> Union[IOError, bytes]:
        """Send a request and receive a response on the interface connection"""
        if not self._connection.is_open:
            raise IOError("Pipettor controller not connected")
        # Write the message, not buffered and non-blocking (see __init__)
        self._connection.write(message)
        # Get response (blocking)
        resp = await self._connection.read_async(256)
        return resp

    @staticmethod
    def list_ports():
        """List all the available serial ports in the system"""
        return serial.tools.list_ports.comports()

    @classmethod
    def find_and_connect(cls):
        """Find an attached Pipettor controller device and connect to it"""
        # Find ports with "Pipettor" in their description
        pipettor_ports = list(serial.tools.list_ports.grep("Pipettor.*"))
        if len(pipettor_ports) > 0:
            conn = cls(pipettor_ports[0].device)
            conn.connect()
            return conn
        else:
            raise ValueError("No Pipettor controller device found")


async def pipettor_bus_timed_exchange(req: PipettorRequest) -> tuple:
    """Return a tuple containing the response packet object
    and the elapsed time (in microseconds) to complete the exchange"""
    begin = time.time_ns()
    conn = PipettorBusRouterInterface.find_and_connect()
    resp = await conn.exchange(req.raw_packet)
    pkt = PipettorResponse.parse(resp)
    end = time.time_ns()
    elapsed = (end - begin) // 1000

    return (pkt, elapsed)
