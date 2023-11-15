
# Version: Test
import pythonnet
import clr
clr.AddReference("Seyonic.Dispenser.6.0")

from Seyonic.Dispenser import IDispenser, DispenserCommunicator

# Constants
CONTROLLER_IP_ADDRESS = '10.0.0.178'
TCP_PORT = 10001
CONTROLLER_ADDRESS = 208
PIPETTOR_ADDRESS = 16
CHANNELS = [1,2,3,4,5,6,7,8]

ACTION_STATUS_LOOKUP = {
    9: 'Residual Volume Overflow Residual Volume larger than Requested Volume. Aspirate or Dispense is performed but Actual Volume may be wrong.',
    4: 'LLD in progress',
    3: 'Reserved',
    2: 'Liquid level detected Status after LLD Action',
    1: 'Action in progress',
    0: 'Action completed successfully',
    -1: 'Unspecified Error',
    -2: 'Action aborted After Abort Action Command',
    -3: 'Pressure error Dispense, Aspirate, LLD, No Action performed',
    -4: 'Aspiration / dispense / LLD timeout Time longer than User set limit',
    -5: 'Sensor zero error Failed Auto-Zero of Flow Sensor, No Action',
    -9: 'LLD Offset Error LLD Error, No Action performed',
    -10: 'LLD Flow Error Insufficient Flow, Tip Clogged before Action',
    -15: 'Dispense Flow Rate too high Operational Threshold Error',
    -16: 'Dispense Flow Rate too low Operational Threshold Error',
    -18: 'Aspiration Flow Rate too high Operational Threshold Error',
    -19: 'Aspiration Flow Rate too low Operational Threshold Error',
    -19: 'Aspiration Flow Rate too low Operational Threshold Error',
    -22: 'Aspiration Error: Short Sample Start in Air, End in Liquid',
    -23: 'Aspiration Error: Tracking Error Start in Liquid, End in Air',
    -24: 'Clogging Error Aspirate and Dispense',
    -25: 'Blocked Tip Error Tip Blocked before Pick up',
    -26: 'Initial Value: Never Polled Instrument.'
}

ACTION_MODES = {
    'Disable': 0,
    'Dispense': 1,
    'Aspirate': 2,
    'LLD': 4,
    'Mix': 162,
    }

class Pipettor:
    """ API Interface for controlling the Seyonic pipettor by sending commands to the Seyonic Controller
    via an ethernet.

    Parameters
    ----------
    ip_address : string
        Address of the Controller unit (Default: 10.0.0.178)
    port : int
        TCP/IP port to be used (Default: 10001)
    controller_address : int
        Address of the controller (Default 208 (dex, 0xD0))
    pipettor_address : int
        Address of the pipettor (Default 16 (dec, 0x10))
    """

    def __init__(self,
                 ip_address: str = CONTROLLER_IP_ADDRESS,
                 port: int = TCP_PORT,
                 controller_address: int = CONTROLLER_ADDRESS,
                 pipettor_address: int = PIPETTOR_ADDRESS):
        self.ip_address = ip_address
        self.port = port
        self.controller_address = controller_address
        self.pipettor_address = pipettor_address

        # Set control parameters
        self.max_poll_timeout = 10  # seconds (timeout for polling action status of the pipettor)
        self.max_pressure = 500     # mbar
        self.min_pressure = -300    # mbar
        self.pressure_delay = 1.5   # seconds (*** THIS SHOULD BE LOADED FROM THE CONFIG FILE ***)

        # Initialize the pipettor connection
        try:
            self.client = DispenserCommunicator.ConnectClient()
        except Exception as e: 
            print(e)
        self.client.EventsAndExceptionsActive = True
        self.client.OpenTcp(self.ip_address, self.port)
        self.aspirate_volumes = [0 for channel in CHANNELS]
        self.dispense_volumes = [0 for channel in CHANNELS]
        #self.get_aspirate_volumes()
        #self.get_dispense_volumes()