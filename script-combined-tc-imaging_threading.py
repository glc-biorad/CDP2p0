import time
import socket
import os.path as osp
import os
import numpy as np
import multiprocessing
import tifffile

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
from api.reader import instrument_interface
from api.util.server import Server
from gui.controllers.chipscanner_controller import StartScan
from gui.util.utils import import_config_file, get_unit_name





def imaging_thread(connection, channels_to_image, imaging_period, fdir, experiment_name):
    unit_hw_config = import_config_file(osp.join('config', 'unit_config.json'))
    start = time.time()
    now = start + 0.01
    index = 0
    scanner = StartScan(unit_hw_config, fdir, experiment_name)
    # create directories if they do not exist
    temperature_dir = osp.join(fdir, experiment_name, 'temperatures')
    timelapseimg_dir = osp.join(fdir, experiment_name, 'timelapse_images')
    if not osp.isdir(temperature_dir):
        os.makedirs(temperature_dir)
    if not osp.isdir(timelapseimg_dir):
        os.makedirs(timelapseimg_dir)
    while True:
        img_related_delay = 0
        now = time.time()
        for channel in channels_to_image:
            img_related_delay += unit_hw_config['motor_LED_delay']
            img_related_delay += int(unit_hw_config['default_exposure'][channel] / 1e6)
            timestamp = int(round(now-start, 0))
            fname = f"{channel}_I{index}_T{timestamp}.tif"
            fpath = osp.join(fdir, experiment_name, 'timelapse_images', fname)
            img = scanner.acquire_image(channel)
            tifffile.imwrite(fpath, img)


        # get temperatures
        connection.send(['get_temps'])
        fpath_temp = osp.join(fdir, experiment_name, 'temperatures', f'Actual_I{index}_T{timestamp}.npy')
        info = connection.recv()
        if info[0] == 'quit':
            return
        np.save(fpath_temp, np.array(info))
        index += 1
        delay_time = imaging_period - img_related_delay
        if delay_time > 0:
            delay(imaging_period - img_related_delay)
        else:
            print(f'IMAGE RELTAED DELAYS add up to longer than the imaging period:\nImaging Period:{imaging_period}\nImage Related Delays: {img_related_delay}')

def temp_control_thread(connection):
    c = Controller('COM4', 57600, dont_use_fast_api=True, timeout=1)
    m = Meerstetter()
    m.connect_to_opened_port(c)
    while True:
        request = connection.recv()
        if request[0] == 'get_temps':
            # info = np.random.randint(0, 95, size=4)
            info = [m.get_temperature(h_i) for h_i in range(1, 5)]
            connection.send(info)
        elif request[0] == 'change_temps':
            m.change_temperature(request[1], request[2])
        elif request[0] == 'quit':
                return

def change_temperature(connection, heater, temp):
    connection.send(['change_temps', heater, temp])




def tc_image():
    # -------------------------------------------------------------------------
    # --------------------- USER DEFINED PARAMETERS ---------------------------
    # -------------------------------------------------------------------------

    # define delay times & cycle number
    # later we can define temperatures, but first we nee da strucutre to convert
    # set temperatures to actual temperatures with offsets
    msre_digest_time = 45 * 60 # seconds
    hotstart_time = 2 * 60  # seconds
    anneal_extend_time = 100 # seconds
    denature_time = 50 # seconds
    final_annealing_time = 100 # seconds
    signal_augmentation_time = 1 * 60 # seconds
    deactivation_time = 60 # seconds
    final_4C_hold_time = 18 # seconds
    cycles = 2


    # path and channel information
    location_to_image = (-232565, -358236, 0, -37000)
    channels_pre_scan = ('hex',)
    channels_timelapse = ('fam',)
    channels_post_scan = ('fam',)
    experiment_name_pre = 'EXPERIMENT_NAME'
    experiment_name_post = 'EXPERIMENT_NAME'
    chambers_to_image = (2,)
    unit_hw_config = import_config_file(osp.join('config', 'unit_config.json'))
    imaging_period_time_seconds = 15

    # -------------------------------------------------------------------------
    # --------------------- END OF USER DEFINED PARAMETERS --------------------
    # -------------------------------------------------------------------------


    # -------------------------------------------------------------------------
    # --------------------- DEFINITIONS AND HOUSEKEEPING --- DONT CHANGE ------
    # -------------------------------------------------------------------------
    # get unit
    which_unit = get_unit_name()
    print(f'USING UNIT {which_unit}')
    # define heaters
    heaterA = 1
    heaterB = 2
    heaterC = 3
    heaterD = 4

    allowed_channels = ('alexa405', 'fam', 'hex', 'atto', 'cy5', 'cy55', 'bf')
    fdir = osp.join('D:/', 'AdvTechImagingData')

    # c = Controller('COM7', 57600, dont_use_fast_api=True, timeout=1)
    # m = Meerstetter()
    # # ins = instrument_interface.Connection_Interface()
    # m.connect_to_opened_port(c)

    # start fastAPI
    #server = Server()
    #server.run()
    #multiprocessing.freeze_support()

    temperature_dir = osp.join(fdir, experiment_name_pre, 'temperatures')
    if not osp.isdir(temperature_dir):
        os.makedirs(temperature_dir)

    # init temp control
    c1, c2 = multiprocessing.Pipe()
    pMonitoring = multiprocessing.Process(target=temp_control_thread, args=(c2,))
    pMonitoring.start()

    
    selections = {'chip_type': 'Vantiva',
    'drop_type': 'pico droplets',
    'fluor_channels': channels_pre_scan,
    'chambers_enabled': [chambers_to_image],
    'chamber_ids': ['test'],
    'tests': ['A22q'],
    'proceed_with_imaging': True}

    ## pre scan
    scan = StartScan(hw_config=unit_hw_config, fdir=fdir, fname=experiment_name_pre)
    #scan.Scan_chip(selections)

    # move imager to
    scan.instrument_interface.moveImager(location_to_image)
    pImaging = multiprocessing.Process(target=imaging_thread, args=(c1,
        channels_timelapse, imaging_period_time_seconds, fdir, experiment_name_pre + '_timelapse'))
    pImaging.start()
    # --------------------------------------------------
    # ------------------BEGIN PROTOCOL------------------
    # --------------------------------------------------

    # # msre digest
    # m.change_temperature(heaterB, 37)
    # m.change_temperature(heaterC, 37)
    # m.change_temperature(heaterD, 37)
    # delay(msre_digest_time)

    # hotstart
    change_temperature(c1, heaterB, 93)
    change_temperature(c1, heaterC, 94)
    change_temperature(c1, heaterD, 95)
    delay(hotstart_time)

    # begin cycling
    for cycle in range(cycles):
        print(f"cycle: {cycle+1}")
        # annealing extension
        change_temperature(c1, heaterB, 98)
        change_temperature(c1, heaterC, 97)
        change_temperature(c1, heaterD, 99)
        delay(denature_time)

        # denaturation
        change_temperature(c1, heaterB, 58)
        change_temperature(c1, heaterC, 58)
        change_temperature(c1, heaterD, 60)
        delay(anneal_extend_time)


    # # final extension
    # m.change_temperature(heaterB, 58)
    # m.change_temperature(heaterC, 58)
    # m.change_temperature(heaterD, 60)
    # delay(final_annealing_time)

    # # molecular beacon signal augmentation
    # m.change_temperature(heaterB, 72)
    # m.change_temperature(heaterC, 72)
    # m.change_temperature(heaterD, 72)
    # delay(signal_augmentation_time)

    # enzyme deactivation
    change_temperature(c1, heaterB, 93)
    change_temperature(c1, heaterC, 94)
    change_temperature(c1, heaterD, 95)
    delay(deactivation_time)

    # stop imaging threads
    c1.send(['quit'])
    c2.send(['quit'])
    pImaging.join()
    pMonitoring.join()

    # 4C hold
    change_temperature(c1, heaterB, 8)
    change_temperature(c1, heaterC, 8)
    change_temperature(c1, heaterD, 8)
    delay(final_4C_hold_time)

    # room temp
    change_temperature(c1, heaterB,18)
    change_temperature(c1, heaterC,18)
    change_temperature(c1, heaterD,18)

    ## post scan
    #scan = StartScan(hw_config=unit_hw_config, fdir=fdir, fname=experiment_name_post)
    #selections = {'chip_type': 'Vantiva',
    #'drop_type': 'pico droplets',
    #'fluor_channels': channels_post_scan,
    #'chambers_enabled': [chambers_to_image],
    #'chamber_ids': [chambers_to_image],
    #'tests': ['A22q'],
    #'proceed_with_imaging': True}

    #scan.Scan_chip(selections)

if __name__ == '__main__':
    tc_image()
