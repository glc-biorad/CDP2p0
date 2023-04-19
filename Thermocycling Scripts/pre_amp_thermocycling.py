# Import meerstetter to control the TEC board for Pre-Amp
from api.reader.meerstetter.meerstetter import Meerstetter

# Import Logger
from api.util.log import Log

# Import time, sys
import time
import sys

# Constants
# -----------------------------------------------------------------------------------------------------
EXPERIMENT_NAME = 'pre-amp'
ADDRESS = 9
PROTOCOL = [{'type': 'hold', 'temperature': 95, 'time': 3*60},
            {'type': 'cycle', 'cycles': 6, 'temperature_a': 60, 'time_a': 240, 'temperature_b': 95, 'time_b': 50},
            {'type': 'hold', 'temperature': 30, 'time': 10}
    ]
LOG = Log(log_name=EXPERIMENT_NAME)
RESET_TIME = 3
# -----------------------------------------------------------------------------------------------------

# Start a clock for the whole protocol
clock = time.time()

# Make sure the Pre-Amp Thermocycler can be communicated with
try: 
    LOG.log(f":::(MESSAGE)::: Attempting to communicate with the Pre-Amp Thermocycler (address: {ADDRESS})", time.time() - clock)
    # Initialize the meerstetter
    meerstetter = Meerstetter()
    LOG.log(f":::(MESSAGE)::: Meerstetter has been initialized...", time.time() - clock)
    # Get the device status
    device_status = meerstetter.get_device_status(ADDRESS, str)
    if device_status == 'Error':
        LOG.log(f":::(ERROR)::: Pre-Amp Thermocycler after initializtion was found in an error state...", time.time() - clock)
        meerstetter.reset_device(ADDRESS)
        LOG.log(f":::(MESSAGE)::: Pre-Amp Thermocycler reset attempted, waiting {RESET_TIME} seconds before checking...", time.time() - clock)
        t = time.time()
        while time.time() - t <= RESET_TIME:
            # Do nothing
            a = 1
        meerstetter.handle_device_status(ADDRESS, 30)
except Exception as e:
    LOG.log(f":::(MESSAGE)::: Issue communicating with the Pre-Amp Thermocycler due to an exception ({e})", time.time() - clock)
    LOG.log(f":::(FAILURE)::: Attempt to communicate with the Pre-Amp Thermocycler was unsuccessful, exiting....!", time.time() - clock)
    sys.exit()
LOG.log(f":::(MESSAGE)::: Attempt to communicate with the Pre-Amp Thermocycler was successful!", time.time() - clock)

# Start the protocol
LOG.log(f":::(MESSAGE)::: Starting the following protocol", time.time() - clock)
for step in PROTOCOL:
    LOG.log(f":::(MESSAGE)::: - {step}", time.time() - clock)
for step in PROTOCOL:
    LOG.log(f":::(MESSAGE)::: Starting step: {step}")
    # Check device status
    device_status = meerstetter.get_device_status(ADDRESS, str)
    if device_status == 'Error':
        LOG.log(f":::(ERROR)::: Pre-Amp Thermocycler after initializtion was found in an error state...", time.time() - clock)
        meerstetter.reset_device(ADDRESS)
        LOG.log(f":::(MESSAGE)::: Pre-Amp Thermocycler reset attempted, waiting {RESET_TIME} seconds before checking...", time.time() - clock)
        t = time.time()
        while time.time() - t <= RESET_TIME:
            # Do nothing
            a = 1
        meerstetter.handle_device_status(ADDRESS, 30)
    # Get the step data
    if step['type'] == 'hold':
        step_temperature = step['temperature'] 
        step_time = step['time']
        # Change the temperature
        meerstetter.change_temperature(address=ADDRESS, value=step_temperature, block=True)
        # Start the steps clock
        step_clock = time.time()
        # Wait the desired time for this step
        while time.time() - step_clock <= step_time:
            # Every second report the status, temperature, and time left for this point in the step
            a = 1
    elif step['type'] == 'cycle':
        step_cycles = step['cycles']
        step_temperature_a = step['temperature_a']
        step_time_a = step['time_a']
        step_temperature_b = step['temperature_b']
        step_time_b = step['time_b']
