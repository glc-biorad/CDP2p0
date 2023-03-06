from api.upper_gantry.upper_gantry import UpperGantry
from api.upper_gantry.seyonic.seyonic import Seyonic
from api.reader.meerstetter.meerstetter import Meerstetter

import time

if __name__ == '__main__':
    #ug = UpperGantry()
    #ug.get_pipettor().liquid_level_detect()
    m = Meerstetter()
    t_start = time.time()
    m.get_temperature(4)
    print(f"Total Time: {time.time() - t_start}")