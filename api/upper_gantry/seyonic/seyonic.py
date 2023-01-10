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
        self.client = DispenserCommunicator.ConnectClient()
        self.client.EventsAndExceptionsActive = True
        self.client.OpenTcp(ip_address, port)
        self.aspirate_volumes = [0] * 8
        self.dispense_volumes = [0] * 8
        self.cntrl_addr = controller_address
        self.pip_addr = pipettor_address
        self.get_aspirate_volumes()
        self.get_dispense_volumes()

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

    def _poll_until_complete(self):
        ''' Internal function used to poll the pipettor for action status.

        This function polls the pipettor continuously for its status, ending
        after the pipettor reports that it has completed its operation.
        '''
        start = time.time()
        action_status = [-26] * 8 # -26 is init value
        while time.time() - start < self.max_poll_timeout:
            for chan in range(1, 9):
                action_status[chan-1] = self.client.Get("Action Status",
                                        self.pip_addr, chan)
            completed_chan = [1 for asval in action_status if asval == 0]
            if sum(completed_chan) == 8:
                return action_status
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


    def aspirate(self, pressure=None, debug=True):
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

    def get_flow_rate(self):
        return [0,0,0,0,0,0,0,0]

    def open_valve(self):
        ''' For droplet generation and suction cup function
        '''
        logger = Logger(__file__, __name__)
        logger.log('MESSAGE', "Opening Seyonic Pipettor valve.")
        self.client.OpenValve(self.pip_addr, 0)
        logger.log('MESSAGE', "Seyonic Pipettor valve should now be open.")

    def close_valve(self):
        ''' For droplet generation and suction cup function
        '''
        logger = Logger(__file__, __name__)
        logger.log('MESSAGE', "Clsoing Seyonic Pipettor valve.")
        self.client.CloseValve(self.pip_addr, 0)
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
    sey.set_dispense_volumes(volumes=5000)
    sey.set_aspirate_volumes(volumes=5000)

    print(sey.get_aspirate_volumes())
    # sey.aspirate()
    # print(sey.get_actual_aspirate_volume())
    # time.sleep(2)
    # sey.aspirate()
    # print(sey.get_actual_aspirate_volume())

    # time.sleep(2)
    print(sey.get_dispense_volumes())
    sey.dispense()
    print(sey.get_actual_dispense_volume())
    # time.sleep(10)
    sey.dispense()
    print(sey.get_actual_dispense_volume())
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