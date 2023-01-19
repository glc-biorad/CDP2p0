import time
from typing import Union

import aioserial
import serial.tools.list_ports
import platform

from chassis_controller.app.routers.interfaces.utils_meerstetter import MeerstetterBusPacket

current_os = platform.system()


class MeerstetterBusRouterInterface:
    """Meerstetter bus router interface class to communicate with modules in the Meerstetter system"""

    def __init__(self, port: str, baud: int = 57600, timeout: float = 1.0) -> None:
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
            raise IOError(f"Meerstetter interface could not connect to port {self.port}")

    def disconnect(self):
        """Disconnect from the interface's port"""
        if self._connection.is_open:
            self._connection.close()

    async def exchange_async(self, message: bytearray) -> Union[IOError, bytes]:
        """Send a request and receive a response on the interface connection"""
        if not self._connection.is_open:
            raise IOError("Meerstetter interface not connected")
        # Write the message, not buffered and non-blocking (see __init__)
        self._connection.write(message)
        # Get response (non-blocking)
        resp = await self._connection.read_async(256)
        return resp

    def exchange(self, message: bytearray) -> Union[IOError, bytes]:
        """Send a request and receive a response on the interface connection"""
        if not self._connection.is_open:
            raise IOError("Meerstetter interface not connected")
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

        if current_os == "Windows": # Send an ask for the device ID
            meerstetter_ports = list(serial.tools.list_ports.comports())
            for port in meerstetter_ports:
                try:

                    conn = cls(port.device)
                    conn.connect()
                    return conn

                except:
                    raise IndexError("Connection Failed")
            
            raise ValueError("No Meerstetter controller device found")




async def meerstetter_bus_timed_exchange(pkt: MeerstetterBusPacket) -> tuple:
    """Return a tuple containing the packet object with a filled in response
    and the elapsed time (in microseconds) to complete the exchange"""
    begin = time.time_ns()

    conn = MeerstetterBusRouterInterface.find_and_connect()
    resp = await conn.exchange_async(pkt.raw_packet)
    pkt.parse(resp) # Fill in the response in the packet
    end = time.time_ns()
    elapsed = (end - begin) // 1000

    return (pkt, elapsed)

