
# Version: Test
import serial
import time
import sys

import api.util.utils

class BioShake3000T():
    def __init__(self):
        self._BAUD_RATE = 9600
        self._PARITY = None
        self._DATA_BITS = 8
        self._STOP_BITS = 1
        self._HANDSHAKE = False

        self._SPEED_VALUE_UNITS = 'rpm'
        self._TEMPERATURE_VALUE_UNITS = 'celsius'
        self._MIN_WAIT_TIME_UNITS = 'seconds'

        self._MIN_WAIT_TIME_GET = 0.1
        self._MIN_WAIT_TIME_SOFF = 6
        self._MIN_WAIT_TIME_ELM = 3
        self._MIN_WAIT_TIME_SGH = 5

        self._MAX_WAIT_TIME_CHANGE_TEMP = 600 # 10 min

        # Serial port connection.
        self._serial_port = serial.Serial(port='COM11')

    def _write_command_and_wait(self, cmd, flush_buffers=True, timeout=0.2):
        if flush_buffers:
            api.util.utils.flush_buffers(self._serial_port)
        self._serial_port.write(cmd + b'\r')
        time_start = time.time()
        while time.time() - time_start < timeout:
            time.sleep(0.1)
        response_bstring = self._serial_port.read(self._serial_port.in_waiting)
        return response_bstring

    # --------------------------------------------------------------------------------
    # Initialization Commands
    # --------------------------------------------------------------------------------

    def info(self, return_mode='string'):
        '''
        Returns a list of general information.
        '''
        # Send command to get info.
        info_bstring = self._write_command_and_wait(b'info', timeout=0.5)

        if return_mode == 'bstring':
            return info_bstring
        elif return_mode == 'string':
            return info_bstring.decode('utf-8')

    def getVersion(self):
        '''
        Returns current firmware version number.
        '''
        # Send command to get the version.
        version_bstring = self._write_command_and_wait(b'v')

        version_string = version_bstring.decode('utf-8')
        version = version_string[len("Q.MTP-BIOSHAKE 3000-T elm v"):]
        return version

    def getDescription(self):
        '''
        Returns current model information.
        '''
        # Send command to get the description.
        description_bstring = self._write_command_and_wait(b'getDescription')

        description_string = description_bstring.decode('utf-8')
        return description_string

    def resetDevice(self, warn=True, verbose=True):
        '''
        Restarts the controller. This takes about 30 seconds.
        '''
        reset = 'y'
        response_string = 'error'
        if warn:
            reset = input("\aWarning (BioShake 3000-T elm): you are about to reset the controller, this takes 30 seconds, continue (y/n)?\n")
        if reset == 'y':
            response_bstring = self._write_command_and_wait(cmd=b'reset', timeout=30)
            response_string = response_bstring.decode('utf-8')
        if verbose:
            if "Initialization complete" in response_string:
                print("BioShake 3000-T elm has been reset")
            else:
                print("BioShake 3000-T elm has not been reset")

    def getErrorList(self):
        return None

    def enableCLED(self, warn=True):
        '''
        Permanent activation of the LED indication lights. The instrument will reset after this command.
        '''
        if warn:
            reset = input("\aWarning (BioShake3000-T.enableCLED): the instrument will reset after this command (takes 30 seconds), continue [y/n]?\n")
        if reset == 'y':
            print("Permanently enabling LED then reseting")
            self._write_command_and_wait(b'enableCLED', timeout=30)
        else:
            print("LED will not be enabled and the instrument will not be reset")

    def disableCLED(self, warn=True):
        '''
        Permanent deactivation of the LED indication lights. The instrument will reset after this command.
        '''
        if warn:
            reset = input("\aWarning (BioShake3000-T.disableCLED): the instrument will reset after this command (takes 30 seconds), continue [y/n]?\n")
        if reset == 'y':
            print("Permanently disabling LED then reseting")
            self._write_command_and_wait(b'disableCLED', timeout=30)
        else:
            print("LED will not be disabled and the instrument will not be reset")

    # --------------------------------------------------------------------------------
    # ECO Mode Commands
    # --------------------------------------------------------------------------------

    def setEcoMode(self, warn=True, verbose=True):
        '''
        Switches the shaker into economical mode. It will reduce electricity
            consumption by deactivation of the solenoid for the homing position
            and deactivation of the ELM function.
        Note: Homing position is not locked!
        '''
        if warn:
            cont = input("\aWarning (BioShake3000-T.setEcoMode): homing zero position is not locked in ECO mode, continue [y/n]?")
            if cont == 'y':
                self._write_command_and_wait(b'sem')
                if verbose:
                    print("\nMode: Economical")
            else:
                if verbose:
                    print("\nMode: Normal")
        else:
            self._write_command_and_wait(b'sem')
            if verbose:
                print("\nMode: Economical")

    def leaveEcoMode(self, verbose=True):
        '''
        Leaves the economical mode and switches into the normal operating state.
        '''
        self._write_command_and_wait(b'lem')
        if verbose:
            print("\nMode: Normal\n")

    # --------------------------------------------------------------------------------
    # Shaking & Homing Commands
    # --------------------------------------------------------------------------------

    def setShakeTargetSpeed(self, value):
        '''
        Sets the target mixing speed.
        Note: value range is [MinRpm] - [MaxRpm] (1 to 4-digit value without a comma)
        '''
        self._write_command_and_wait(b'ssts' + str.encode(str(value)))

    def shakeOn(self, mixing_speed_rpm):
        '''
        Starts the shaking with the current mixing speed.
        '''
        # Send the command to the controller.
        self.setShakeTargetSpeed(mixing_speed_rpm)
        response_bstring = self._write_command_and_wait(b'son', timeout=3)
        response_string = response_bstring.decode('utf-8')

    def shakeOff(self):
        '''
        Stops the shaking, proceeds to the homing position and locks in place.
        Note: minimum response time is 5-6 seconds, depends on specifications.
        Note: target mixing speed is set to 0.
        '''
        # Send the command to the controller.
        response_bstring = self._write_command_and_wait(b'soff', timeout=self._MIN_WAIT_TIME_SOFF)
        response_string = response_bstring.decode('utf-8')

    def shakeOnWithRuntime(self, runtime, mixing_speed_rpm, verbose=True):
        '''
        Starts the shaking with the current mixing speed for a defined time in seconds.
        Note: runtime range: 0 - 99999 (1 to 5-digit value without comma).
        '''
        self.setShakeTargetSpeed(mixing_speed_rpm)
        self._write_command_and_wait(b'sonwr' + str.encode('{0}'.format(runtime)))

    def getShakeRemaingTime(self):
        '''
        Returns the remaining time in seconds of a single program.
        '''
        return None

    def shakeOffWithDeenergizeSolenoid(self, warn=True):
        '''
        Stops the shaking, proceeds to the homing position, locks in place 
            for 1 second, the unlocks zero position.
        Note: minimum response time 5-6 seconds, depends on specifications
        Note: Zero position is not defined
        Note: Prevents unwanted temperature increasing by the solenoid
        '''
        if warn:
            print("Warning (BioShake3000-T.shakeOffWithDeenergizeSolenoid):")
            print("\t - minimum response time is 5-6 seconds")
            print("\t - zero position is not defined")
        self._write_command_and_wait(b'soffwds', timeout=self._MIN_WAIT_TIME_SOFF)

    def shakeGoHome(self):
        '''
        Shaker moves to the homing zero position and locks in place.
        Note: Minimum response time 2-3 seconds (Manual also says 5 seconds so I will use 5 sec).
        '''
        self._write_command_and_wait(b'sgh', timeout=self._MIN_WAIT_TIME_SGH)

    def shakeOffNonZeroPos(self):
        '''
        Fast and safe stopping of all movements!
        Notes: Homing zero position not defined
        Note: target mixing speed is set to 0
        '''
        self._write_command_and_wait(b'soffnzp')

    def shakeEmergencyOff(self):
        '''
        Fast and safe stopping of all movements!
        Notes: Homing zero position not defined
        Note: target mixing speed is set to 0
        '''
        self._write_command_and_wait(b'seoff')

    def getShakeState(self):
        '''
        Returns the state of shaking:
            value   0   Shaking is active
            value   1   Shaker has a stop command detected
            value   2   Shaker in braking mode
            value   3   Arrived in the home position
            value   4   Manual mode for external control
            value   5   Acceleration
            value   6   Deceleration
            value   7   Deceleration with stopping
            value   90  ECO mode
            value   99  Boot process running
        '''
        values = {
            0: "Shaking is active",
            1: "Shaker has a stop command detected",
            2: "Shaker in braking mode",
            3: "Arrived in the home position",
            4: "Manual mode for external control",
            5: "Acceleration",
            6: "Deceleration",
            7: "Deceleration with stopping",
            90: "ECO mode",
            99: "Boot process running",
            }
        return None

    def getShakeStateAsString(self):
        '''
        Return the state of shaking as a string.
            value   RAMP+   Acceleration
            value   RAMP-   Deceleration
            value   RUN     Running
            value   STOP    Arrived in the home position
            value   ESTOP   Emergency stop
        '''
        values = {
            'RAMP+': 'Acceleration',
            'RAMP-': 'Deceleration',
            'RUN': 'Running',
            'STOP': "Arrived in the home position",
            'ESTOP': "Emergency stop",
            }
        return None

    # --------------------------------------------------------------------------------
    # Temperature Control Commands
    # --------------------------------------------------------------------------------

    def tempOn(self):
        '''
        Activates the temperature control and starts heating/cooling.
        Notes: it is trongly recommended to control if desired temperature is reached 
            (see command getTempActual)
        '''
        self._write_command_and_wait(b'ton')

    def tempOff(self):
        '''
        Switches off the temperature control and stops heating/cooling.
        '''
        self._write_command_and_wait(b'toff')

    def getTempState(self):
        '''
        Returns the state of the temperature function.
            value   0   Temperature control is disabled
            value   1   Temperature control is enabled

        returns: 0 or 1
        '''
        values = {
            0: "Temperature control is disabled",
            1: "Temperature control is enabled",
            }

        tempstate_bstring = self._write_command_and_wait(b'gts')
        tempstate_string = tempstate_bstring.decode('utf-8')
        return int(tempstate_string)

    def getTempStateAsString(self):
        '''
        Return the state of the temperature function as string.
            value   off Temperature control is disabled
            value   on  Temperature control is enabled
        '''
        values = {
            'off': "Temperature control is disabled",
            'on': "Temperature control is enabled",
            }

        tempstate_bstring = self._write_command_and_wait(b'gtsas')
        tempstate_string = tempstate_bstring.decode('utf-8')
        return tempstate_string

    def getTempTarget(self):
        '''
        Returns the target temperature.
        '''
        temptarget_bstring = self._write_command_and_wait(b'gtt')
        temptarget_string = temptarget_bstring.decode('utf-8')
        return float(temptarget_string)

    def setTempTarget(self, temp):
        '''
        Set the target temperature 1/10 C between 0 and 99 C.
        Notes: temp range: 000 - 990 (3-digit value without comma)
        '''
        temp = temp * 10
        self._write_command_and_wait(b'stt' + str.encode(str(temp)))

    def changeTemp(self, temp, verbose=True):
        '''
        Change the temperature of the heater/shaker.
        '''
        delta = 0.1 # C
        self.tempOn()
        if verbose:
            print(f"Temperature Control: {self.getTempStateAsString()}")
        self.setTempTarget(temp)
        time_start = time.time()
        while time.time() - time_start < self._MAX_WAIT_TIME_CHANGE_TEMP:
            if self.getTempTarget() >= self.getTempActual():
                if self.getTempActual() >= self.getTempTarget():
                    break
            elif self.getTempTarget() <= self.getTempActual():
                if self.getTempActual() <= self.getTempTarget():
                    break
            if self.getTempActual() <= self.getTempTarget() + delta and self.getTempActual() >= self.getTempTarget() - delta:
                break
            if verbose:
                print("Current Temperature ({0}C): {1} - {2}".format(u"\u00b0", self.getTempActual(), self.getTempStateAsString()))
            time.sleep(0.1)
        self.tempOff()
        if verbose:
            print(f"Temperature Control: {self.getTempStateAsString()}")

    def getTempActual(self):
        '''
        Returns the current temperature.
        '''
        temp_bstring = self._write_command_and_wait(b'gta')
        temp_string = temp_bstring.decode('utf-8')
        return float(temp_string)

    # --------------------------------------------------------------------------------
    # ELM Control Commands
    # --------------------------------------------------------------------------------

    def setElmLockPos(self, warn=True):
        '''
        Closes the Edge Locking Mechanism (ELM).
            The runtime is less than 3000 msec
            The microplate is concentrically centered, aligned and locked
            This position is a current-free static state
        '''
        if warn:
            print("Warning (BioShake3000T.setElmLockPos): this takes about 3 seconds...")
        self._write_command_and_wait(b'selp', timeout=3)

    def setElmUnlockPos(self, warn=True):
        '''
        Opens the Edge Locking Mechanism (ELM).
            The runtime is less than 3000 msec
            The microplate is not locked
            This position is a current-free static state
        '''
        if warn:
            print("Warning (BioShake3000T.setElmLockPos): this takes about 3 seconds...")
        self._write_command_and_wait(b'seup', timeout=3)

    def getElmState(self):
        '''
        Returns the state of the ELM.
            value   0   ELM nor in lock or unlock position
            value   1   ELM in lock position - Microplate is locked
            value   3   ELM in unlock position - Microplate is unlocked
            value   9   Error - detecting ELM state
        '''
        values = {
            0: "ELM nor in lock or unlock position",
            1: "ELM in lock position - Microplate is locked",
            3: "ELM in unlock position - Microplate is unlocked",
            9: "Error - detecting ELM state",
            }

        elmstate_bstring = self._write_command_and_wait(b'ges')
        elmstate_string = elmstate_bstring.decode('utf-8')
        return int(elmstate_string)

    def getElmStateAsString(self):
        '''
        Returns the state of the ELM.
            value   ELMLocked   Microplate is locked
            value   ELMUnlocked Microplate is unlocked
            value   ELMError    Error 
        '''
        values = {
            'ELMLocked': "Microplate is locked",
            'ELMUnlocked': "Microplate is unlocked",
            'ELMError': 'Error',
            }

        elmstate_bstring = self._write_command_and_wait(b'gesas')
        elmstate_string = elmstate_bstring.decode('utf-8')
        return elmstate_string