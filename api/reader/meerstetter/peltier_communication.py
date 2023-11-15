
# Version: Test
'''
'''

from api.util.utils import left_pad_to_str, Logger

from api.util.crc import compute_crc16_xmodem

class PeltierCommunication():
    # Public variables.

    # Private variables.
    __control = None
    __address = None
    __sequence_number = None
    __payload = None
    __checksum = None
    __communication_str = None
    __partial_communication_str = None

    # Private constants.

    # Constructor.
    def __init__(self, control, address, sequence_number, payload, checksum=None, log:bool=True):
        self.__control = str(control)
        self.__address = left_pad_to_str(hex(address)[2:].upper(), 2)
        self.log = log
        #self.__address = left_pad_to_str(address, 2)
        try:
            self.__sequence_number = left_pad_to_str(hex(sequence_number)[2:].upper(), 4) # added hex and stuff
        except:
            self.__sequence_number = ''
        #self.__sequence_number = left_pad_to_str(sequence_number, 4)
        self.__payload = payload.to_string()
        self.__partial_communication_str = self.__control + self.__address + self.__sequence_number + self.__payload

        # If no checksum is given, compute the checksum.
        if checksum == None:
            checksum = compute_crc16_xmodem(self.__partial_communication_str)
        if control != '#':
            checksum = ''
        self.__checksum = str(checksum)
        self.__communication_str = self.__partial_communication_str + self.__checksum + '\r'

    def to_string(self):
        return self.__communication_str

    def compare_with_response(self, response, assert_control=True, assert_address=True, assert_sequence_number=True, assert_checksum=True):
        '''
        Expects response to have similar form.
        '''
        try:
            if response[-1] == '\r':
                response = response[:-1]
            response_control = str(response[0])
            response_address = str(response[1:3])
            response_sequence_number = str(response[3:7])
            response_checksum = str(response[-4:])
            # Check control of response is '!'
            if assert_control:
                assert response_control == '!'
            # Compare the addresses.
            if assert_address:
                assert response_address == self.__address
            # Compare the sequence number.
            if assert_sequence_number:
                assert response_sequence_number == self.__sequence_number
            # Compare the checksum.
            if assert_checksum:
                assert response_checksum == self.__checksum
        except Exception as e:
            try:
                # Setup the logger.
                logger = Logger(__file__, self.compare_with_response.__name__)
                if self.log:
                    logger.log('ERROR', f"Error returned {e} when comparing the response ({response}) received with the Meerstetter. If the response is None this could mean that the board you are trying to communicate with is not connected, not powered, or in an error state and must be reset.")
            except Exception as e:
                if self.log:
                    print(e)