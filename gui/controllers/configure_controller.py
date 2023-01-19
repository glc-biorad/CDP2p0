import threading

# Import the model and view for this controller
from gui.models.configure_model import ConfigureModel
from gui.views.configure_frame import ConfigureFrame

# Import the Meerstetter API
try:
    from api.reader.meerstetter.meerstetter import Meerstetter
except Exception as e:
    print(e)
    print("Coudln't import Meerstetter for the Configure Controller")

# Constants

class ConfigureController:
    """ System for passing data from the Configure Model to the Configure View """
    def __init__(
        self,
        model: ConfigureModel,
        view: ConfigureFrame,
    ) -> None:
        # Set the model and view for the controller
        self.model = model
        self.view = view
        self.db_name = self.model.db_name
        self.unit = self.db_name[-4]

    def setup_bindings(self) -> None:
        """ Setup the bindings between the controller and the view """
        self.view.bind_button_tec_read(self.tec_read)
        self.view.bind_button_tec_write(self.tec_write)

    def tec_read(self, event=None) -> None:
        """ Deals with Reading the TEC address """
        thread = threading.Thread(target=self.thread_tec_read)
        thread.start()

    def thread_tec_read(self) -> None:
        """ TEC Read function for a thread """
        # Initialize Meerstetter 
        try:
            self.meerstetter = Meerstetter()
        except Exception as e:
            print(e)
            print("Couldn't initialize the Meerstetter for the Configure Controller")
        # Get the address of the connected meerstetter
        address = int(self.meerstetter.get_device_address())
        self.view.tec_read_sv.set(str(address))
        # Close the meerstetter connection
        self.meerstetter.close()

    def tec_write(self, event=None) -> None:
        """ Deals with Writing the TEC address """
        thread = threading.Thread(target=self.thread_tec_write)
        thread.start()

    def thread_tec_write(self) -> None:
        """ TEC Write function for a thread """
        # Initialize Meerstetter 
        try:
            self.meerstetter = Meerstetter()
        except Exception as e:
            print(e)
            print("Couldn't initialize the Meerstetter for the Configure Controller")
        # Get the address of the connected meerstetter
        address = int(self.meerstetter.get_device_address())
        # Get the new address
        new_address = int(self.view.tec_write_sv.get())
        # Change the address
        self.meerstetter.set_address(address=address, new_address=new_address)
        # Close the meerstetter connection
        self.meerstetter.close()