import time
import os.path as osp
import pythonnet
from pythonnet import load
import numpy as np

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
from gui.controllers.chipscanner_controller import StartScan
from gui.util.util import import_config_file

def tc_image():
    # -------------------------------------------------------------------------
    # --------------------- DEFINITIONS AND HOUSEKEEPING --- DONT CHANGE ------
    # -------------------------------------------------------------------------
    # define heaters
    heaterA = 1
    heaterB = 2
    heaterC = 3
    heaterD = 4

    allowed_channels = ('alexa405', 'fam', 'hex', 'atto', 'cy5', 'cy55', 'bf')
    fdir = osp.join('D:', 'AdvTechImagingData')

    c = Controller('COM8', 57600, dont_use_fast_api=True, timeout=1)
    m = Meerstetter()
    # ins = instrument_interface.Connection_Interface()
    m.connect_to_opened_port(c)

    # -------------------------------------------------------------------------
    # --------------------- USER DEFINED PARAMETERS ---------------------------
    # -------------------------------------------------------------------------

    # define delay times & cycle number
    # later we can define temperatures, but first we nee da strucutre to convert
    # set temperatures to actual temperatures with offsets
    msre_digest_time = 45 * 60 # seconds
    hotstart_time = 10 * 60  # seconds
    anneal_extend_time = 100 # seconds
    denature_time = 50 # seconds
    final_annealing_time = 100 # seconds
    signal_augmentation_time = 15 * 60 # seconds
    deactivation_time = 600 # seconds
    final_4C_hold_time = 1800 # seconds
    cycles = 45


    # path and channel information
    imaging_period_time_seconds = 15
    channels_pre_scan = ('hex')
    channels_timelapse = ('fam')
    channels_post_scan = ('fam')
    experiment_name_pre = 'EXPERIMENT_NAME'
    experiment_name_post = 'EXPERIMENT_NAME'
    experiment_name_timelapse = 'EXPERIMENT_NAME'
    chambers_to_image = (2,)
    unit_hw_config = import_config_file(osp.join('config', 'unit_config.json'))
    img_list = []
    os.mkdirs(osp.join(fdir, experiment_name_timelapse, 'timelapse_images'))
    os.mkdirs(osp.join(fdir, experiment_name_timelapse, 'temperatures'))


    # TODO FILL THIS OUT LATER MAYBE FROMT HE ACTUAL DICT RETURNED FORMGUI
    selections = {'chip_type': 'Vantiva',
    'drop_type': droplet_type,
    'fluor_channels': channels_pre_scan,
    'chambers_enabled': chambers_to_image,
    'chamber_ids': [],
    'tests': [],
    'proceed_with_imaging': True}

    # pre scan
    scan = StartScan(hw_config=unit_hw_config, fdir=fdir, fname=experiment_name_pre)
    scan.Scan_chip(selections)
    # --------------------------------------------------
    # ------------------BEGIN PROTOCOL------------------
    # --------------------------------------------------

    # # msre digest
    # m.change_temperature(heaterB, 37)
    # m.change_temperature(heaterC, 37)
    # m.change_temperature(heaterD, 37)
    # delay(msre_digest_time)

    # hotstart
    m.change_temperature(heaterB, 93)
    m.change_temperature(heaterC, 94)
    m.change_temperature(heaterD, 95)
    start = time.time()
    now = start + 0.1
    cycle_num = 0
    while now - start < hotstart_time:
        img_related_delay = 0
        for channel in channels_timelapse:
            img_related_delay += unit_hw_config['motor_LED_delay']
            img_related_delay += unit_hw_config['default_exposures'][channel]
            timestamp = int(round(now-start, 0))
            fname = f'{channel}_T{timestamp}.tif'
            fpath = osp.join(fdir, experiment_name_timelapse, 'timelapse_images', fname)
            img = scan.acquire_image(channel)
            tifffile.imwrite(fpath, img)
        fpath_temp = osp.join(fdir, experiment_name_timelapse, 'temperatures', f'T{timestamp}.npy')
        info = [m.get_temperature(h_i) for h_i in range(1, 5)]
        info.append(cycle_num)
        np.save(fpath_temp, np.array(info))
        img_list.append(fpath)

        delay(imaging_period_time_seconds - img_related_delay)

    # delay(hotstart_time)

    # begin cycling
    for cycle in range(cycles):
        print(f"cycle: {cycle+1}")
        # annealing extension
        m.change_temperature(heaterB, 98)
        m.change_temperature(heaterC, 97)
        m.change_temperature(heaterD, 99)
        start = time.time()
        now = start + 0.1
        while now - start < denature_time:
            img_related_delay = 0
            for channel in channels_timelapse:
                img_related_delay += unit_hw_config['motor_LED_delay']
                img_related_delay += unit_hw_config['default_exposures'][channel]
                timestamp = int(round(now-start, 0))
                fname = f'{channel}_T{timestamp}.tif'
                fpath = osp.join(fdir, experiment_name_timelapse, 'timelapse_images', fname)
                img = scan.acquire_image(channel)
                tifffile.imwrite(fpath, img)
            fpath_temp = osp.join(fdir, experiment_name_timelapse, 'temperatures', f'T{timestamp}.npy')
            info = [m.get_temperature(h_i) for h_i in range(1, 5)]
            info.append(cycle+1)
            np.save(fpath_temp, np.array(info))
            img_list.append(fpath)

            delay(imaging_period_time_seconds - img_related_delay)

        # denaturation
        m.change_temperature(heaterB, 58)
        m.change_temperature(heaterC, 58)
        m.change_temperature(heaterD, 60)
        start = time.time()
        now = start + 0.1
        while now - start < anneal_extend_time:
            img_related_delay = 0
            for channel in channels_timelapse:
                img_related_delay += unit_hw_config['motor_LED_delay']
                img_related_delay += unit_hw_config['default_exposures'][channel]
                timestamp = int(round(now-start, 0))
                fname = f'{channel}_T{timestamp}.tif'
                fpath = osp.join(fdir, experiment_name_timelapse, 'timelapse_images', fname)
                img = scan.acquire_image(channel)
                tifffile.imwrite(fpath, img)
            fpath_temp = osp.join(fdir, experiment_name_timelapse, 'temperatures', f'T{timestamp}.npy')
            info = [m.get_temperature(h_i) for h_i in range(1, 5)]
            info.append(cycle+1)
            np.save(fpath_temp, np.array(info))
            img_list.append(fpath)

            delay(imaging_period_time_seconds - img_related_delay)


    # # final extension
    # m.change_temperature(heaterB, 58)
    # m.change_temperature(heaterC, 58)
    # m.change_temperature(heaterD, 60)
    # print(m.get_temperature(heaterD))
    # delay(final_annealing_time)

    # # molecular beacon signal augmentation
    # m.change_temperature(heaterB, 72)
    # m.change_temperature(heaterC, 72)
    # m.change_temperature(heaterD, 72)
    # print(m.get_temperature(heaterD))
    # delay(signal_augmentation_time)

    # enzyme deactivation
    m.change_temperature(heaterB, 93)
    m.change_temperature(heaterC, 94)
    m.change_temperature(heaterD, 95)
    delay(deactivation_time)
    print(m.get_temperature(heaterD))

    # 4C hold
    m.change_temperature(heaterB, 8)
    m.change_temperature(heaterC, 8)
    m.change_temperature(heaterD, 8)
    delay(final_4C_hold_time)
    print(m.get_temperature(heaterD))

    # room temp
    m.change_temperature(heaterB,18)
    m.change_temperature(heaterC,18)
    m.change_temperature(heaterD,18)
    print(m.get_temperature(heaterD))

    # post scan
    scan = StartScan(hw_config=unit_hw_config, fdir=fdir, fname=experiment_name_post)
        selections = {'chip_type': 'Vantiva',
        'drop_type': droplet_type,
        'fluor_channels': channels_pre_scan,
        'chambers_enabled': chambers_to_image,
        'chamber_ids': [],
        'tests': [],
        'proceed_with_imaging': True}

    scan.Scan_chip(selections)

if __name__ == '__main__':
    tc()
