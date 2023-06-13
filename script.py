import time
import pythonnet
from pythonnet import load

try:
    load("coreclr")
except:
    print("Cannot load coreclr")


from api.util.controller import Controller
from api.reader.reader import Reader
from api.upper_gantry.upper_gantry import UpperGantry
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.reader.meerstetter.meerstetter import Meerstetter
from api.util.utils import delay
from api.util.log import Log

import time

if __name__ == '__main__':
    #c = Controller('COM8', 57600, dont_use_fast_api=True, timeout=1)
    #m = Meerstetter()
    #m.connect_to_opened_port(c)
    
    ug = UpperGantry()
    ug.home_pipettor()
    #fapii = ug.get_fast_api_interface()
    #fapii.pipettor_gantry.axis.move('pipettor_gantry', 1, 300000, 300000)

