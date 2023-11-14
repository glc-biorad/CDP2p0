
# Version: Test
''' This is a file containing a class that controls the Seyonic Pipettor.
For documentation, please check the class docstring in this file, as well as the
README.
'''
# for logging
import os.path as osp
# for tracking time in polling
import time
# for numpy arrays for storing values associated with pipettor
# import numpy as np

# pythonnet
import pythonnet
from pythonnet import load

from api.util.logger import Logger
from api.util.log import Log

#load("coreclr")


import clr
# Seyonic imports
clr.AddReference("Seyonic.Dispenser.6.0")
#from lib.Seyonic.Dispenser import IDispenser, DispenserCommunicator
from Seyonic.Dispenser import IDispenser, DispenserCommunicator



# define defaults
ip_address = '10.0.0.178'
port = 10001
contlr_addr = 208
pip_addr = 16

action_status_lookup = {9: 'Residual Volume Overflow Residual Volume larger \
                            than Requested Volume. Aspirate or Dispense is \
                            performed but Actual Volume may be wrong.',
                        4: 'LLD in progress',
                        3: 'Reserved',
                        2: 'Liquid level detected Status after LLD Action',
                        1: 'Action in progress',
                        0: 'Action completed successfully',
                        -1: 'Unspecified Error',
                        -2: 'Action aborted After Abort Action Command',
                        -3: 'Pressure error Dispense, Aspirate, LLD, \
                            No Action performed',
                        -4: 'Aspiration / dispense / LLD timeout Time \
                            longer than User set limit',
                        -5: 'Sensor zero error Failed Auto-Zero of Flow \
                            Sensor, No Action',
                        -9: 'LLD Offset Error LLD Error, No Action \
                            performed',
                        -10: 'LLD Flow Error Insufficient Flow, \
                            Tip Clogged before Action',
                        -15: 'Dispense Flow Rate too high \
                            Operational Threshold Error',
                        -16: 'Dispense Flow Rate too low \
                            Operational Threshold Error',
                        -18: 'Aspiration Flow Rate too high \
                            Operational Threshold Error',
                        -19: 'Aspiration Flow Rate too low \
                            Operational Threshold Error',
                        -21: 'Aspiration Error: Empty Well \
                            Aspiration of Air',
                        -22: 'Aspiration Error: Short Sample Start in Air, \
                            End in Liquid',
                        -23: 'Aspiration Error: Tracking Error \
                            Start in Liquid, End in Air',
                        -24: 'Clogging Error Aspirate and Dispense',
                        -25: 'Blocked Tip Error Tip Blocked before Pick up',
                        -26: 'Initial Value: Never Polled Instrument.'
                        }

action_modes = {'Disable': 0,
                'Dispense': 1,
                'Aspirate': 2,
                'LLD': 4,
                'Mix': 162,
                }
# TODO: none of these are wrapped in try statemetns to catch any exceptions

class Seyonic(object):
    ''' This class interfaces with the Seyonic Pipettor. The Pipettor consists
    of a controller and a pipettor. Commands are sent via ethernet to a
    RaspberryPi inside the controller, which routes the commands to the
    specified hardware. The pipettors should all have the default values
    specified at the top of this (SeyonicPypettor.py) file.

    INPUTS:
        ip_address: string. address of controller unit. Default 10.0.0.178.
        port: int. TCP/IP port to be used. Default 10001.
        controller_address: int. address of controller. Default 208 (dec), 0xD0
        pipettor_address: int. address of pipettor. Default 16 (dec), 0x10
    '''
    def __init__(self, ip_address=ip_address,
                        port=port,
                        controller_address=contlr_addr,
                        pipettor_address=pip_addr,):
        self.IP_ADDRESS = '10.0.0.177'
        # SET/LOAD PARAMETERS
            # set max timeout for polling action status
        self.max_poll_timeout = 10 # sec
            # set max/min pressure
        self.max_pressure = 500 # mbar
        self.min_pressure = -300 # mbar
            # delay time after setting pressure, before triggering for pressure
            # equalization
        self.pressure_delay = 1.5 # this should be loaded from config file
        # initialize pipettor connection
        try:
            self.client = DispenserCommunicator.ConnectClient()
        except Exception as e:
            print(e)
        self.client.EventsAndExceptionsActive = True
        self.client.OpenTcp(ip_address, port)
        self.aspirate_volumes = [0] * 8
        self.dispense_volumes = [0] * 8
        self.cntrl_addr = controller_address
        self.pip_addr = pipettor_address
        self.get_aspirate_volumes()
        self.get_dispense_volumes()
        self.log = Log(log_name='calls', log_path='./logs/seyonic/')
        self.status_log = Log(log_name='status', log_path='./logs/seyonic/')
        self.log.log(f"Seyonic Pipettor Initializing...")

    # temp order things should happen for standard op
        # init,
        # pull aspirate/dispense volumes
        # set pressure based on asp/disp vols
        # set aspirate/dispense resvols based on pressure
        # aspirate/dispense
        # set pressure to 0


    def _calculate_and_set_resvol(self,):
        ''' Internal function used to set the residual aspirate/dispense volumes

        See section 7 (Liquid Handling) of the Seyonic Pipetting Manual for
        detailed discussion. The residual aspirate/dispense are set based on the
        pressure used to aspirate/dispense. This function needs to be called
        everytime the pressure is changed. This fucntion assumes that the
        pressure used will be tracked/stored in the class attributes:
        self.vac_pressure for vacuum pressure
        self.pos_pressure for positive pressure
        '''
        # vacuum: resvol = -0.256 * vac_pressure
        # pressure: resvol = 0.270 * pressure
        self.aspirate_resvol = [0] * 8
        self.dispense_resvol = [0] * 8
        asp_resvol = int(round(-0.256 * self.vac_pressure, 0))
        disp_resvol = int(round(0.270 * self.pos_pressure, 0))
        for chan in range(1, 9):
            self.client.Set("NEW_ASP_RESVOL", self.pip_addr, chan, asp_resvol)
            self.client.Set("NEW_DISP_RESVOL", self.pip_addr, chan, disp_resvol)


    def _calc_pressure(self,):
        ''' Internal function used to set pressure/vacuum based on
        dispense/aspirate volumes.

        See section 7.4 (Pipetting) of the Seyonic Pipetting manual for detailed
        discussion. The accuracy and speed of your aspirate/dispense depends on
        pressure used. This fuction automatically sets the pressure to the
        recommended range based on the aspirate/dispense volumes. This function
        is called after set_aspirate_volumes() & set_dispense_volumes().
        '''
        # manual on vacuum
            # 0.5 to 5uL: ~-15 mbar
            # 2 to 5uL: -15--20 mbar
            # 5 to 25uL: -25-50 mbar
            # greater than 25uL: -50--200mbar
        min_vol = min(self.aspirate_volumes)
        if min_vol <= 50:
            self.vac_pressure = -15 # mbar
        elif min_vol <= 250:
            self.vac_pressure = -32 # mbar
        else:
            self.vac_pressure = -125 # mbar
        # the manual on pressure:
            # 0.5 to 5uL: 15-25mbar (contact mode)
            # 2 to 5uL: 20mbar (jet mode)
            # 5 to 25uL: 50mbar (jet mode)
            # greater than 25uL: 50-200mbar (jet mode)
        max_vol = max(self.dispense_volumes)
        if max_vol <= 50:
            self.pos_pressure = 15 # mbar
        elif max_vol <= 250:
            self.pos_pressure = 50 # mbar
        else:
            self.pos_pressure = 125 # mbar

    def _poll_until_complete(self, max_poll_timeout: int = None, check_for_sum: int = 8):
        ''' Internal function used to poll the pipettor for action status.

        This function polls the pipettor continuously for its status, ending
        after the pipettor reports that it has completed its operation.
        '''
        start = time.time()
        action_status = [-26] * 8 # -26 is init value
        if max_poll_timeout == None:
            max_poll = self.max_poll_timeout
        else:
            max_poll = max_poll_timeout
        while time.time() - start < max_poll:
            for chan in range(1, 9):
                action_status[chan-1] = self.client.Get("Action Status",
                                        self.pip_addr, chan)
            completed_chan = [1 for asval in action_status if asval == 0]
            if sum(completed_chan) == check_for_sum:
                return action_status
        return action_status

    def get_status(self) -> None:
        action_status = [-26] * 8 # -26 is init value
        for chan in range(1,9):
            action_status[chan-1] = self.client.Get("Action Status", self.pip_addr, chan)
        return action_status

    def set_pressure(self, pressure, direction=None, debug=False):
        ''' Function used to change pressure and turn on/off pump.

        INPUTS:
            pressure: int. Pressure in mbar that the pump will be set to.
                Vacuum pressure should be negative.Checks this value is in range
                [self.min_pressure, self.max_pressure]
            direction: int or None. Indicates which position the pressure valve
                should be in. 1 for dispense. 2 for aspirate.
        OUTPUTS:
            none

        This function checks that the specified pressure is within allowable
        range, clips value if not, and turns on/off the pump. Pump is turned off
        by specifying a pressure of 0. Vacuum pressures should be negative,
        positive/dispense pressures should be positive.
        '''

        # safety rails
        self.log.log(f"set_pressure(pressure={pressure}; direction={direction})")
        logger = Logger(__file__, __name__)
        if pressure < self.min_pressure or pressure > self.max_pressure:
            msg = 'WARNING: Specified pressure {0} is outside range {1} to {2}.\
            Value has been clipped to closest allowable value.'
            print(msg.format(pressure, self.min_pressure, self.max_pressure))
        pressure = max(min(pressure, self.max_pressure), self.min_pressure)
        # if direction == None, then we are probably doing droplet generation,
        # but for flexibility, we'll determine which side the valve should be on
        # (positive vs negative) by the pressure. Otherwise, it should be
        # specified
        if direction == None:
        # this block may cause issues in restarting the pump after using it to
        # make droplets
            if pressure >= 0:
                # dispense
                self.client.Set('IO_PORT', self.cntrl_addr, 20, 1)
                self.pos_pressure = pressure
                direction = 1
            else:
                # aspirate
                self.client.Set('IO_PORT', self.cntrl_addr, 20, 0)
                self.vac_pressure = pressure
                direction = 2
        elif direction == 1:
            # dispense
            self.client.Set('IO_PORT', self.cntrl_addr, 20, 1)
            if pressure > 0:
                self.pos_pressure = pressure
        elif direction == 2:
            # aspirate
            self.client.Set('IO_PORT', self.cntrl_addr, 20, 0)
            if pressure < 0:
                self.vac_pressure = pressure
        else:
            print('Invalid direction/position for valve. Can be [None, 1, 2].')
            raise
        # i may move htis in the future
        #if pressure != 0:
            # do not set resvols if we are "turning off" the pressure
            #self._calculate_and_set_resvol()
        # tell controller to change pressure
        self.client.Set("Pressure Setpoint", self.cntrl_addr, direction,
            pressure)

    def change_timeout(self, timeout_in_seconds: int = 65) -> None:
        """ Change the timeout of the Seyonic Controller """
        self.log.log(f"change_timeout(timeout_in_seconds={timeout_in_seconds})")
        try:
            self.client.Set("CONTINUOUS_TIMEOUT", self.cntrl_addr, 0, timeout_in_seconds)
        except Exception as e:
            print(e)
        #print(self.client.Get("CONTINUOUS_TIMEOUT", self.pip_addr, 0))
        timeout = self.client.Get("CONTINUOUS_TIMEOUT", self.cntrl_addr, 0)
        if timeout != timeout_in_seconds:
            print("ERROR: seyonic.change_timeout did not change the timeout for the seyonic controller")

    def change_aspirate_timeout(self, timeout_in_seconds: int = 5) -> None:
        """Change the error timeout for the aspiration action"""
        self.log.log(f"change_aspirate_timeout(timeout_in_seconds={timeout_in_seconds})")
        try:
            self.client.Set("Aspirate Timeout", self.pip_addr, 0, timeout_in_seconds)
        except Exception as e:
            print(e)
        #timeout = self.client.Get("Regulation Timeout", self.cntrl_addr, 0)
        #if timeout != timeout_in_seconds:
        #    print("ERROR: seyonic.change_aspirate_timeout did not change the timeout for the seyonic controller")

    def change_dispense_timeout(self, timeout_in_seconds: int = 5) -> None:
        """Change the error timeout for the dispense action"""
        self.log.log(f"change_dispense_timeout(timeout_in_seconds={timeout_in_seconds})")
        try:
            self.client.Set("Dispense Timeout", self.pip_addr, 0, timeout_in_seconds)
        except Exception as e:
            print(e)
        #timeout = self.client.Get("Regulation Timeout", self.cntrl_addr, 0)
        #if timeout != timeout_in_seconds:
        #    print("ERROR: seyonic.change_dispense_timeout did not change the timeout for the seyonic controller")

    def get_actual_aspirate_volume(self):
        ''' Function that queries the pipettor for measured aspirate volumes in
        last operation.

        INPUTS:
            none.
        OUTPUTS:
            asp_vols: list. List of volumes the pipettor measured during last
                aspirate operation. One volume per channel.
        '''
        # get measured aspirate volume
        asp_vols = [0] * 8
        for chan in range(1, 9):
            asp_vols[chan-1] = self.client.Get("Actual Aspirate Volume",
                self.pip_addr,
                chan)
        return asp_vols

    def get_actual_dispense_volume(self):
        ''' Function that queries the pipettor for measured dispense volumes in
        last operation.

        INPUTS:
            none.
        OUTPUTS:
            disp_vols: list. List of volumes the pipettor measured during last
                dispense operation. One volume per channel.
        '''
        disp_vols = [0] * 8
        for chan in range(1, 9):
            disp_vols[chan-1] = self.client.Get("Actual Dispense Volume",
                self.pip_addr,
                chan)
        return disp_vols



    def set_aspirate_volumes(self, volumes):
        ''' Function used to set aspirate volumes.

        INPUTS:
            volumes: int or list. Either a single value that will be
                assigned to all channels, or 8 values, one per channel.
        OUTPUTS:
            none

        Use this function to set aspirate volumes before aspirating. Can be used
        to set all channel volumes or individual channel volumes. This function
        will also call _calc_pressure() to automatically set an optimal
        pressure, and will call _calculate_and_set_resvol() to set residual
        aspirate volumes.
        '''
        # parse input for single or multiple values
        if type(volumes) == int:
            volumes_to_set = [volumes] * 8
        elif type(volumes) == list:
            volumes_to_set = volumes
            assert len(volumes) == 8, 'Must specify 8 channels.'
        # set volumes
        for chan, val in enumerate(volumes_to_set):
            self.client.Set("Aspirate Volume", self.pip_addr, chan+1, val)
        # update aspirate volumes
        _ = self.get_aspirate_volumes()
        self._calc_pressure() # update pressure based on volumes
        self._calculate_and_set_resvol() # update resvols based on volumes


    def set_dispense_volumes(self, volumes):
        ''' Function used to set dispense volumes.

        INPUTS:
            volumes: int or list. Either a single value that will be
                assigned to all channels, or 8 values, one per channel.
        OUTPUTS:
            none

        Use this function to set dispense volumes before dispensing. Can be used
        to set all channel volumes or individual channel volumes. This function
        will also call _calc_pressure() to automatically set an optimal
        pressure, and will call _calculate_and_set_resvol() to set residual
        dispense volumes.
        '''
        # parse input for single or multiple values
        if type(volumes) == int:
            volumes_to_set = [volumes] * 8
        elif type(volumes) == list:
            volumes_to_set = volumes
            assert len(volumes) == 8, 'Must specify all 8 channels'
        # set volumes
        for chan, val in enumerate(volumes_to_set):
            self.client.Set("Dispense Volume", self.pip_addr, chan+1, val)
        # update aspirate volumes
        _ = self.get_dispense_volumes()
        self._calc_pressure() # update pressure based on volumes
        self._calculate_and_set_resvol() # update resvols based on volumes

    def get_aspirate_volumes(self):
        ''' Query pipettor for current aspirate volumes.

        INPUTS:
            none
        OUTPUTS:
            list. list of aspirate volumes per channel. units are 0.1 uL
        '''
        # should we use controller address or pipettor address?
        for chan in range(1, 9):
            self.aspirate_volumes[chan-1] = self.client.Get("Aspirate Volume",
                                                            self.pip_addr, chan)
        return self.aspirate_volumes


    def get_dispense_volumes(self):
        ''' Query pipettor for current dispense volumes.

        INPUTS:
            none
        OUTPUTS:
            list. list of dispense volumes per channel. units are 0.1 uL
        '''
        # should we use controller address or pipettor address
        for chan in range(1, 9):
            self.dispense_volumes[chan-1] = self.client.Get("Dispense Volume",
                                                            self.pip_addr, chan)
        return self.dispense_volumes


    def old_aspirate(self, pressure=None, debug=True):
        ''' Function used to aspirate volumes

        INPUTS:
            pressure: int or None. Pressure to use for this aspiration. This
                parameter is only used if you want to use a pressure other than
                the recommended accuracy-optimized pressure that is
                automatically set.
            debug: bool. If True, this function will print the action status
                of this operation per channel.
        OUTPUTS:
            none.
        '''
        logger = Logger(__file__, __name__)
        if pressure == None:
            pressure = self.vac_pressure
        # set action mode
        self.client.Set("Action Mode", self.pip_addr,
            0, action_modes['Aspirate'])
        self.set_pressure(pressure=pressure)
        time.sleep(self.pressure_delay) # delay to equalize pressure
        self.client.Trigger(self.pip_addr, 0)
        action_return = self._poll_until_complete()
        self.set_pressure(pressure=0, direction=2)
        if debug:
            for i in range(8):
                asval = action_status_lookup[action_return[i]]
                logger.log('MESSAGE', "The action status for the Seyonic Pipettor channel {0} is '{1}'".format(i+1, asval))
                #print('Channel {0} Action Status: {1}'.format(i, asval))

    def get_current_action_status(self, channels: int):
        _ = []
        for channel in channels:
            _.append(self.client.Get("Action Status", self.pip_addr, channel))
        return _
    def get_current_input_pressure(self, channels: list):
        _ = []
        for channel in channels:
            _.append(self.client.Get("Input Pressure", self.pip_addr, channel))
        return _
    def get_current_output_pressure(self, channels: list = [1,2,3,4,5,6,7,8]):
        _ = []
        for channel in channels:
            _.append(self.client.Get("Output Pressure", self.pip_addr, channel))
        return _
    def get_pressure(self, pressure_type: str = 'vacuum') -> int:
        if pressure_type.lower() in ['vacuum', 'positive', 'v', 'p']:
            if pressure_type[0].lower() == 'p':
                description = 2
            else:
                description = 3
        return int(self.client.Get("Pressure", self.cntrl_addr, description))

    def aspirate(self, pressure: int = None, channels: list = [1,2,3,4,5,6,7,8], pressure_offset: int = 3):
        self.status_log.seyonic_log_header()
        #self.log.log(f"aspirate(pressure={pressure}; channels={str(channels).replace(',',';')})")
        logger = Logger(__file__, __name__)
        if pressure == None:
            pressure = self.vac_pressure
        # Set the action mode to aspirate
        self.client.Set("Action Mode", self.pip_addr, 0, action_modes['Aspirate'])
        # Set the pressure 
        self.set_pressure(pressure=pressure)
        actual_pressure = self.get_pressure('vacuum')
        equalize_start_time = time.time()
        equalize_time = equalize_start_time
        equalize_max_time = 4
        while (actual_pressure + pressure_offset <= pressure) or (actual_pressure - pressure_offset >= pressure):
            elapsed_time = time.time() - equalize_start_time
            print(f"Actual Pressure = {actual_pressure} mbar, target pressure = {pressure} mbar, time = {elapsed_time}")
            self.status_log.seyonic_log('Aspirate', "Actual Pressure (mbar)", actual_pressure, [pressure for i in range(1,9)], elapsed_time)
            actual_pressure = self.get_pressure('vacuum')
        print(f"PRESSURE STABLE IN = {elapsed_time}")
        aspirate_clock_start = time.time()
        # Trigger the action of aspiration
        self.client.Trigger(self.pip_addr, 0)
        self.status_log.seyonic_log('Aspirate', "Trigger", pressure, [1, 1, 1, 1, 1, 1, 1, 1], time.time() - aspirate_clock_start)
        # In real time check for pipettor status to stop if an error is found
        completed_actions = [0 for channel in channels]
        current_action_statuses = self.get_current_action_status(channels)
        while current_action_statuses != completed_actions:
            #print(f"Input: {self.get_current_input_pressure(channels)} -- Output: {self.get_current_output_pressure(channels)}")
            #print(f"")
            # Get the status in real time
            #print(self.get_pressure())
            current_action_statuses = self.get_current_action_status(channels)
            current_action_statuses_strings = [action_status_lookup[current_action_statuses[channel-1]] for channel in channels]
            #self.log.log(f"{str(current_action_statuses_strings).replace(',',';')}")
            self.status_log.seyonic_log('Aspirate', "In Progress", 
                                 pressure, 
                                 [current_action_statuses[0],
                                 current_action_statuses[1],
                                 current_action_statuses[2],
                                 current_action_statuses[3],
                                 current_action_statuses[4],
                                 current_action_statuses[5],
                                 current_action_statuses[6],
                                 current_action_statuses[7]],
                                 time.time() - aspirate_clock_start
            )
            # Check the status for each channel
            for channel in channels:
                if current_action_statuses[channel-1] < 0:
                    #print(f"ERROR: Channel {channel} of the pipettor has an error {action_status_lookup[current_action_statuses[channel-1]]}")
                    #logger.log("ERROR", f"Channel {channel} of the pipettor has an error {action_status_lookup[current_action_statuses[channel-1]]}")
                    #self.log.log(f"ERROR: Channel {channel} of the pipettor has an error {action_status_lookup[current_action_statuses[channel-1]]}")
                    # Close this valve
                    print(self.client.Get("Aspirate Timeout", self.pip_addr, channel))
                    self.close_valve(channel)
                    time.sleep(1)
                    # Stop the pipettor
                    self.set_pressure(pressure=0, direction=2)
                    # Log the error
                    self.status_log.seyonic_log('Aspirate', "Error", 
                                 0, 
                                 [current_action_statuses[0],
                                 current_action_statuses[1],
                                 current_action_statuses[2],
                                 current_action_statuses[3],
                                 current_action_statuses[4],
                                 current_action_statuses[5],
                                 current_action_statuses[6],
                                 current_action_statuses[7]],
                                 time.time() - aspirate_clock_start
                    )
                    current_action_statuses = [0 for channel in channels]
                else:
                    #print(f"OK: Channel {channel} of the pipettor has a status of {action_status_lookup[current_action_statuses[channel-1]]}")
                    #logger.log("MESSAGE", f"Channel {channel} of the pipettor has a status of {action_status_lookup[current_action_statuses[channel-1]]}")
                    #self.log.log(f"MESSAGE: Channel {channel} of the pipettor has a status of {action_status_lookup[current_action_statuses[channel-1]]}")
                    # If aspiration complete in one channel stop aspiration in all other channels after a certain time
                    if current_action_statuses[channel-1] == 0:
                        overtime = 0.2
                        overtime_start = time.time()
                        while time.time() - overtime_start <= overtime:
                            a = 1
                        if time.time() - overtime_start >= overtime:
                            # Close all valves and set the pressure to 0
                            self.close_valve()
                            time.sleep(1)
                            self.set_pressure(pressure=0, direction=2)
                            # Log the completion
                            self.status_log.seyonic_log('Aspirate', "Completed", 
                                         0, 
                                         [current_action_statuses[0],
                                         current_action_statuses[1],
                                         current_action_statuses[2],
                                         current_action_statuses[3],
                                         current_action_statuses[4],
                                         current_action_statuses[5],
                                         current_action_statuses[6],
                                         current_action_statuses[7]],
                                         time.time() - aspirate_clock_start
                            )
                            return
        print(f"WHILE TIME = {time.time() - aspirate_clock_start}")
        self.set_pressure(pressure=0, direction=2)

    def dispense(self, pressure=None, debug=True):
        ''' Function used to dispense volumes

        INPUTS:
            pressure: int or None. Pressure to use for this dispense. This
                parameter is only used if you want to use a pressure other than
                the recommended accuracy-optimized pressure that is
                automatically set.
            debug: bool. If True, this function will print the action status
                of this operation per channel.
        OUTPUTS:
            none.
        '''
        self.log.log(f"dispense(pressure={pressure})")
        logger = Logger(__file__, __name__)
        if pressure == None:
            pressure = self.pos_pressure
        # set action mode
        self.client.Set("Action Mode", self.pip_addr,
            0, action_modes['Dispense'])
        self.set_pressure(pressure=pressure, direction=1)
        time.sleep(self.pressure_delay) # delay to equalize pressure
        self.client.Trigger(self.pip_addr, 0)
        action_return = self._poll_until_complete()
        self.set_pressure(pressure=0, direction=1)
        if debug:
            for i in range(8):
                asval = action_status_lookup[action_return[i]]
                logger.log('MESSAGE', "The action status for the Seyonic Pipettor channel {0} is '{1}'".format(i+1, asval))
                #print('Channel {0} Action Status: {1}'.format(i, asval))

    def set_LLD_action_mode(self) -> None:
        """
        Set the action mode to LLD to allow LLD triggering
        """
        self.client.Set("Action Mode", self.pip_addr, 0, action_modes['LLD'])

    def trigger_LLD(self) -> None:
        """
        Trigger LLD action
        """
        self.client.Trigger(self.pip_addr, 0)

    def liquid_level_detect(self, timeout_seconds=5, debug=True) -> bool:
        """ Liquid Level Detect (LLD): operates through measurement of a small pressure transient 
        when tge dispenser tip touches a liquid surface. The LLD action is terminated with an ABORT_ACTION command.
        """
        # Set the pressure to 20 mbar
        self.set_pressure(pressure=20, direction=1)
        time.sleep(self.pressure_delay) # delay to equalize pressure
        # Set the action mode to LLD
        self.client.Set("Action Mode", self.pip_addr, 0, action_modes['LLD'])
        # Trigger the action
        self.client.Trigger(self.pip_addr, 0)
        # Poll the action status
        print('here before poll')
        action_return = self._poll_until_complete(max_poll_timeout=timeout_seconds, check_for_sum=16)
        print(action_return)
        if sum(action_return) == 16:
            self.set_pressure(pressure=0, direction=1)
            llded = True
            #return True
        else:
            llded = False
        print('here after poll')
        # Check the return action status
        #action_status_values = [0,0,0,0,0,0,0,0]
        #t_start = time.time()
        #action_status_values_sum = 0
        #for i in action_status_values:
        #    action_status_values_sum = action_status_values_sum + 1 
        #while action_status_values_sum > 2 and timeout_seconds > time.time() - t_start:
        #    print(time.time() - t_start)
        #    for channel in range(8):
        #        action_status_values[channel] = action_status_lookup[action_return[channel]]
        #        if debug == True:
        #            print(f"Channel {channel+1} Action Status: {action_status_values[channel]}")
        #    action_status_values_sum = 0
        #    for i in action_status_values:
        #        action_status_values_sum = action_status_values_sum + 1 
        #    if action_status_values_sum > 2:
        #        print('LLDed')
        #        self.set_pressure(pressure=0, direction=1)
        #        return True
        self.set_pressure(pressure=0, direction=1)
        return llded
        #action_status_values_sum = 0
        #for i in action_status_values:
        #    action_status_values_sum = action_status_values_sum + 1 
        #if action_status_values_sum > 2:
        #    print('nope!')
        #    return False

        #logger = Logger(__file__, __name__)
        #if pressure == None:
        #    pressure = self.vac_pressure
        # set action mode
        #self.client.Set("Action Mode", self.pip_addr,
        #    0, action_modes['Aspirate'])
        #self.set_pressure(pressure=pressure)
        #time.sleep(self.pressure_delay) # delay to equalize pressure
        #self.client.Trigger(self.pip_addr, 0)
        #action_return = self._poll_until_complete()
        #self.set_pressure(pressure=0, direction=2)
        #if debug:
        #    for i in range(8):
        #        asval = action_status_lookup[action_return[i]]
        #        logger.log('MESSAGE', "The action status for the Seyonic Pipettor channel {0} is '{1}'".format(i+1, asval))
        #        #print('Channel {0} Action Status: {1}'.format(i, asval))

    def get_flow_rate(self):
        return [0,0,0,0,0,0,0,0]

    def open_valve(self):
        ''' For droplet generation and suction cup function
        '''
        self.log.log(f"open_valve()")
        logger = Logger(__file__, __name__)
        logger.log('MESSAGE', "Opening Seyonic Pipettor valve.")
        self.client.OpenValve(self.pip_addr, 0)
        logger.log('MESSAGE', "Seyonic Pipettor valve should now be open.")

    def close_valve(self, channel: int = 0):
        ''' For droplet generation and suction cup function
        Channel = 0 broadcasts to all channels
        '''
        self.log.log(f"close_valve(channel={channel})")
        logger = Logger(__file__, __name__)
        logger.log('MESSAGE', "Clsoing Seyonic Pipettor valve.")
        self.client.CloseValve(self.pip_addr, channel)
        logger.log('MESSAGE', "Seyonic Pipettor valve should now be closed.")


    def close(self):
        self.client.CloseTcp()


if __name__ == "__main__":
    # Test Seyonic Class
    # temp order things should happen for standard op
        # init,
        # pull aspirate/dispense volumes
        # set pressure based on asp/disp vols
        # set aspirate/dispense resvols based on pressure
        # aspirate/dispense
        # set pressure to 0
    sey = Seyonic()
    #sey.set_dispense_volumes(volumes=5000)
    #sey.set_aspirate_volumes(volumes=5000)

    #print(sey.get_aspirate_volumes())
    print(sey.get_actual_aspirate_volume())
    # sey.aspirate()
    # print(sey.get_actual_aspirate_volume())
    # time.sleep(2)
    # sey.aspirate()
    # print(sey.get_actual_aspirate_volume())

    # time.sleep(2)
    #print(sey.get_dispense_volumes())
    #sey.dispense()
    #print(sey.get_actual_dispense_volume())
    # time.sleep(10)
    #sey.dispense()
    #print(sey.get_actual_dispense_volume())
    # sey.set_pressure(pressure=100, direction=1)
    # time.sleep(2)
    # sey.set_pressure(pressure=0, direction=1)
    # sey.test_dispense()
    # sey.test_dispense()

    # test droplet generation
    # sey.set_pressure(pressure=100)
    # sey.open_valve()
    # time.sleep(10)
    # sey.close_valve()
    # sey.set_pressure(pressure=0)
    sey.close()