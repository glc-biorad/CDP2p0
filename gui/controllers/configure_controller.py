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
        self.view.trace_tip_1_sv(self.tip_1)
        self.view.trace_tip_2_sv(self.tip_2)
        self.view.trace_tip_3_sv(self.tip_3)
        self.view.trace_tip_4_sv(self.tip_4)
        self.view.trace_tip_5_sv(self.tip_5)
        self.view.trace_tip_6_sv(self.tip_6)
        self.view.trace_tip_7_sv(self.tip_7)
        self.view.trace_tip_8_sv(self.tip_8)
        self.view.trace_tip_9_sv(self.tip_9)
        self.view.trace_tip_10_sv(self.tip_10)
        self.view.trace_tip_11_sv(self.tip_11)
        self.view.trace_tip_12_sv(self.tip_12)

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

    def tip_1(self, *args) -> None:
        """ Trace for tip box 1 configuration """
        val = self.view.tip_1_sv.get()
        self.model.update(ID=1, val1=val)

    def tip_2(self, *args) -> None:
        """ Trace for tip box 2 configuration """
        val = self.view.tip_2_sv.get()
        self.model.update(ID=1, val2=val)

    def tip_3(self, *args) -> None:
        """ Trace for tip box 3 configuration """
        val = self.view.tip_3_sv.get()
        self.model.update(ID=1, val3=val)

    def tip_4(self, *args) -> None:
        """ Trace for tip box 4 configuration """
        val = self.view.tip_4_sv.get()
        self.model.update(ID=1, val4=val)

    def tip_5(self, *args) -> None:
        """ Trace for tip box 5 configuration """
        val = self.view.tip_5_sv.get()
        self.model.update(ID=1, val5=val)

    def tip_6(self, *args) -> None:
        """ Trace for tip box 6 configuration """
        val = self.view.tip_6_sv.get()
        self.model.update(ID=1, val6=val)

    def tip_7(self, *args) -> None:
        """ Trace for tip box 7 configuration """
        val = self.view.tip_7_sv.get()
        self.model.update(ID=1, val7=val)

    def tip_8(self, *args) -> None:
        """ Trace for tip box 8 configuration """
        val = self.view.tip_8_sv.get()
        self.model.update(ID=1, val8=val)

    def tip_9(self, *args) -> None:
        """ Trace for tip box 9 configuration """
        val = self.view.tip_9_sv.get()
        self.model.update(ID=1, val9=val)

    def tip_10(self, *args) -> None:
        """ Trace for tip box 10 configuration """
        val = self.view.tip_10_sv.get()
        self.model.update(ID=1, val10=val)

    def tip_11(self, *args) -> None:
        """ Trace for tip box 11 configuration """
        val = self.view.tip_11_sv.get()
        self.model.update(ID=1, val11=val)

    def tip_12(self, *args) -> None:
        """ Trace for tip box 12 configuration """
        val = self.view.tip_12_sv.get()
        self.model.update(ID=1, val12=val)

