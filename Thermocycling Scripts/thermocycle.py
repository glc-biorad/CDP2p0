
# Version: Test
# Import the meerstetter module to control the peltiers
from api.reader.meerstetter.meerstetter import Meerstetter

# Import the logging tool for a report out after thermocycling is complete
from api.util.log import Log

# Import sys for exiting on errors, time for timing
import sys
import time

# Experiment Name:
experiment_name = 'cnv_test2'

# Protocol
protocol = {
    'HEATERS': 0,
    'PRE-AMP': 0,
}
A = {'address': 1,
     'use': False,
     'steps': [
         {'type': 'hold', 'temperature': 38, 'time': 45},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'cycle', 'cycles': 44, 'temperature_a': 59, 'time_a': 95, 'temperature_b': 91, 'time_b': 40},
         {'type': 'hold', 'temperature': 59, 'time': 95},
         {'type': 'hold', 'temperature': 74, 'time': 15},
         {'type': 'hold', 'temperature': 93, 'time': 10},
         {'type': 'hold', 'temperature': 20, 'time': 1},
     ],
}
B = {'address': 2,
     'use': False,
     'steps': [
         {'type': 'hold', 'temperature': 38, 'time': 45},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'cycle', 'cycles': 44, 'temperature_a': 59, 'time_a': 95, 'temperature_b': 91, 'time_b': 40},
         {'type': 'hold', 'temperature': 59, 'time': 95},
         {'type': 'hold', 'temperature': 74, 'time': 15},
         {'type': 'hold', 'temperature': 93, 'time': 10},
         {'type': 'hold', 'temperature': 20, 'time': 1},
     ],
}
C = {'address': 3,
     'use': False,
     'steps': [
         {'type': 'hold', 'temperature': 38, 'time': 45},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'cycle', 'cycles': 44, 'temperature_a': 59, 'time_a': 95, 'temperature_b': 91, 'time_b': 40},
         {'type': 'hold', 'temperature': 59, 'time': 95},
         {'type': 'hold', 'temperature': 74, 'time': 15},
         {'type': 'hold', 'temperature': 93, 'time': 10},
         {'type': 'hold', 'temperature': 20, 'time': 1},
     ],
}
D = {'address': 4,
     'use': False,
     'steps': [
         {'type': 'hold', 'temperature': 38, 'time': 45},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'hold', 'temperature': 92, 'time': 3*60},
         {'type': 'cycle', 'cycles': 44, 'temperature_a': 59, 'time_a': 95, 'temperature_b': 91, 'time_b': 40},
         {'type': 'hold', 'temperature': 59, 'time': 95},
         {'type': 'hold', 'temperature': 74, 'time': 15},
         {'type': 'hold', 'temperature': 93, 'time': 10},
         {'type': 'hold', 'temperature': 20, 'time': 1},
     ],
}
PRE_AMP = {'address': 9,
           'use': False,
           'steps': [
               {'type': 'hold', 'temperature': 95, 'time': 3*60},
               {'type': 'cycle', 'cycles': 6, 'temperature_a': 60, 'time_a': 240, 'temperature_b': 95, 'time_b': 120},
               {'type': 'hold', 'temperature': 20, 'time': 1},
     ],
}

if __name__ == '__main__':
    # Setup the logger
    log = Log(log_name=experiment_name)
    # Initialize the Meerstetter
    meerstetter = Meerstetter()
    # Start the clock
    start_time = time.time()
    # Check for basic issues
    if PRE_AMP['use'] == True and True in [A['use'], B['use'], C['use'], D['use']]:
        log.log("Currently cannot run Pre-Amp thermocycling protocols with Heaters A, B, C, or D.", time.time() - start_time)
        sys.exit()

    # -----------------------------------------------------------------
    # PRE-AMP
    # -----------------------------------------------------------------
    # Start the Pre-Amp Thermocycler
    if PRE_AMP['use']:
        error_count = 0
        total_expected_time = 0
        log.log(f"Thermocycling on the Pre-Amp Thermocycler with the following protocol, {PRE_AMP['steps']}", time.time() - start_time)
        # Start the thermocycling protocol
        pre_amp_clock = time.time()
        # Iterate through the protocol steps
        for step in PRE_AMP['steps']:
            # Get the type of step
            step_type = step['type']
            # Check if it is a hold or a cycle
            if step_type.lower() == 'hold':
                # Get temperature and time
                temperature = step['temperature']
                t = step['time']
                total_expected_time = total_expected_time + t
                # Change the temperature, block till temperature is reached
                meerstetter.change_temperature(PRE_AMP['address'], temperature, True)
                # Start the thermocycling protocol
                step_time = time.time()
                # Wait till timer is up
                while time.time() - step_time >= t:
                    # Get the device status and log it
                    device_status = meerstetter.get_device_status(PRE_AMP['address'], str)
                    if device_status == 'Error':
                        error_count = error_count + 1
                    if int(time.time() - step_time) % 10== 0:
                        log.log(f"Device Status (address {PRE_AMP['address']}): {device_status}", time.time() - step_time)
                    # Check if there are any errors
                    meerstetter.handle_device_status(PRE_AMP['address'], temperature)
                    # Check the temperature and log it
                    if int(time.time() - step_time) % 10== 0:
                        actual_temperature = meerstetter.get_temperature(PRE_AMP['address'])
                        log.log(f"Device Status (address {PRE_AMP['address']}): {device_status}", time.time() - step_time)
                    # Give the user an update as to where we are in the step
                    if int(time.time() - step_time) % 10 == 0:
                        log.log(f"Step (address {PRE_AMP['address']}): {step}", time.time() - step_time)
                        log.log(f"Time Left on Step (address {PRE_AMP['address']}): {t - (time.time() - step_time)} s", time.time() - step_time)
                # Log the end of this step
                log.log(f"Step is Complete for address {PRE_AMP['address']}", time.time() - step_time)
            elif step_type.lower() == 'cycle':
                # Get the cycles 
                cycles = step['cycles']
                # Get the temperatures and times
                temperature_a = step['temperature_a']
                time_a = step['time_a']
                temperature_b = step['temperature_b']
                time_b = step['time_b']
                # Iterate through the cycles
                for i in range(cycles):
                    # Record the start of the cycle
                    log.log(f"Starting Cycle {i+1} of {cycles} cycles on Thermocycler with address {PRE_AMP['address']}")
                    # Set the temperature and time
                    if i % 2 == 0:
                        temperature = temperature_a
                        t = time_a
                        total_expected_time = total_expected_time + t
                    else:
                        temperature = temperature_b
                        t = time_b
                        total_expected_time = total_expected_time + t
                    # Change the temperature, block till temperature is reached
                    meerstetter.change_temperature(PRE_AMP['address'], temperature, True)
                    # Start the thermocycling protocol
                    step_time = time.time()
                    # Wait till timer is up
                    while time.time() - step_time >= t:
                        # Get the device status and log it
                        device_status = meerstetter.get_device_status(PRE_AMP['address'], str)
                        if device_status == 'Error':
                            error_count = error_count + 1
                        if int(time.time() - step_time) % 10== 0:
                            log.log(f"Device Status (address {PRE_AMP['address']}): {device_status}", time.time() - step_time)
                        # Check if there are any errors
                        meerstetter.handle_device_status(PRE_AMP['address'], temperature)
                        # Check the temperature and log it
                        if int(time.time() - step_time) % 10== 0:
                            actual_temperature = meerstetter.get_temperature(PRE_AMP['address'])
                            log.log(f"Device Status (address {PRE_AMP['address']}): {device_status}", time.time() - step_time)
                        # Give the user an update as to where we are in the step
                        if int(time.time() - step_time) % 10 == 0:
                            log.log(f"Step (address {PRE_AMP['address']}): {step}", time.time() - step_time)
                            log.log(f"Time Left on Step (address {PRE_AMP['address']}): {t - (time.time() - step_time)} s", time.time() - step_time)
                    # Log the end of this step
                    log.log(f"Step is Complete for address {PRE_AMP['address']}", time.time() - step_time)
        # Log the end of the protocol
        log.log(f"Pre-Amp Thermocycling is complete with an error count of {error_count} which were handled and this protocol took {time.time() - start_time} when we expected it to take {total_expected_time} s", time.time() - start_time)

    # -----------------------------------------------------------------
    # Heaters A, B, C, and D
    # -----------------------------------------------------------------
    # Start the Thermocyclers
    if True in [A['use'], B['use'], C['use'], D['use']]:
        # Track error count
        error_count = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        # Keep track of the total expected time for the protocols
        total_expected_time = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        # Start the clocks for the thermocyclers
        start_time = {'A': time.time(), 'B': time.time(), 'C': time.time(), 'D': time.time()}
        # Iterate through the protocol steps
        #for step in 