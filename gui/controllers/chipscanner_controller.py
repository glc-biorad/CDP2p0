import os
import time
import shutil
import numpy
import tifffile
from tqdm import tqdm
from gui.util.metadatawriter import MetaDataWriter
from api.reader.instrument_interface import Connection_Interface
from gui.util import utils


class ChipScanner:
    """
    Functionalities to perform generic scanning of dPCR or microwell chips on b-radx imager.
    This is to be used in conjunction with CDP2p0_GUI.py for gui interfacing and metadatawriter.py for metadata file generation.
    This includes imager movement, image capture, and metadata file creation.
    """
    def __init__(self, hw_config, fdir, fname):
        """
        Instance method of class.
        Keyword arguments:
        - hw_config : loaded json object of hardware_config.json
        - fdir      : main experiment directory to store all scan instance data (config, heater{}, metadata dirs)
        """
        self.instrument_interface = Connection_Interface()
        self.hw = hw_config
        self.fdir = fdir
        self.fname = fname
        self.DOF = 0.1 # mm
        self.heater_ints = {
            "A" : 0,
            "B" : 1,
            "C" : 2,
            "D" : 3
            }
        self.vantiva_coords = os.path.join("chip_data",f"Unit{self.hw['unit']}_Vantiva_CoordinateMap.csv")
        self.a100k_coords = os.path.join("chip_data", "a100k.csv")
        self.microwell_coords = os.path.join("chip_data", "microwell.csv")

    def load_coords(self, csv):
        """
        Parses csv with coordinates and returns a list of (x,y) coordinates for each heater.
        Keyword arguments:
        - csv : a csv file with the appropriate format and populated with coordinates (x & y only needed)
        """

        coords = numpy.loadtxt(csv, skiprows=1, usecols=(2,3), delimiter=",", dtype=numpy.int32)
        hA_coords = coords[0:8]
        hB_coords = coords[8:16]
        hC_coords = coords[16:24]
        hD_coords = coords[24:32]

        return hA_coords, hB_coords, hC_coords, hD_coords


    def calculate_steps(self, Nchambers, ncol_FOVs, coords):
        """
        Calculates x and y distances between steps and returns dx, dy.
        Keyword arguments:
        - Nchambers : total number of chambers in chip, used to calculate dy
        - ncol_FOVs : total FOVs per chamber, used to calculate dx
        - coords    : list of (x,y) coordinates to find points for calculation of dx and dy
        """

        tl = coords[4]
        tr = coords[5]
        bl = coords[6]
        br = coords[7]

        dx = (tr[0] - tl[0]) / (ncol_FOVs - 1)
        dy = (bl[1] - tl[1]) / (Nchambers - 1)

        return dx, dy

    def create_dir(self, name):
        """
        Overwrites directories if in existence, or creates them if not.
        Keyword arguments:
        - name : name of directory to create/overwrite
        """
        if os.path.exists(name):
            shutil.rmtree(name)
            os.mkdir(name)
        else:
            os.mkdir(name)


    def acquire_targets(self, all_selections):
        """
        Parses all_selections from GUI interface and
        returns the chip type and a populated target map dictionary
        to be used in scanning function
        Keyword arguments:
        - all_selections : dictionary returned from gui with user inputs
        """

        chip = all_selections["chip_type"]

        target_aliases = {
            0 : "A",
            1 : "B",
            2 : "C",
            3 : "D"
            }
        target_map = {}

        for h, c in all_selections['chambers_enabled']:
            # This is coming in as a list of tuples, so alias value to heater str for later
            key = target_aliases.get(h,h)
            if key not in target_map:
                target_map[key] = [c]
            else:
                target_map[key].append(c)

        return chip, target_map

    def acquire_image(self, channel):
        """
        Basic functionality to take an imag of a specified channel.
        Keyword arguments:
        - channel : str of channel name to image, from list of channels matching format found in hardware_config.json
        """
        self.instrument_interface.setExposureTimeMicroseconds(self.hw['default_exposures'][channel])
        self.instrument_interface.moveFilterWheel(channel)
        time.sleep(self.hw['motor_LED_delay'])
        self.instrument_interface.turnOnLED(channel)
        img = self.instrument_interface.captureImage()
        self.instrument_interface.turnOffLED(channel)

        return img


class StartScan(ChipScanner):
    """
    Subclass of ChipScanner to provide actual core scanning/metadata population functionality.
    """

    def Scan_chip(self, all_selections):
        """
        Method to initiate scan of chip and creation of data directory for scan instance.
        Creates:
        - config dir (with hardware_config.json)
        - each heater dir (with chamber and FOV dirs)
        - captures and populates FOV dirs with images
        - creates metadata dir and populates metadata/metadata.json
        Keyword arguments:
        - all_selections : dictionary returned from gui with user inputs
        """

        channels_to_image = all_selections['fluor_channels']
        xconv = self.hw['motor2mm']['x']
        yconv = self.hw['motor2mm']['y']
        zconv = self.hw['motor2mm']['z']
        convmat = numpy.array((xconv, yconv, zconv)).reshape(1, -1) # convert steps to mm

        chip, target_map = self.acquire_targets(all_selections)

        if chip == 'Vantiva':
            hA_coords, hB_coords, hC_coords, hD_coords = self.load_coords(self.vantiva_coords)
        elif chip == 'A100k':
            hA_coords, hB_coords, hC_coords, hD_coords = self.load_coords(self.a100k_coords)
        elif chip == 'Microwell':
            hA_coords, hB_coords, hC_coords, hD_coords = self.load_coords(self.microwell_coords)
        else:
            raise Exception("Chip data not available")

        heater_coords = {
            'A' : hA_coords,
            'B' : hB_coords,
            'C' : hC_coords,
            'D' : hD_coords
            }

        metawriter = MetaDataWriter(self.hw, self.fdir, self.fname)
        experiment_dir, meta_dir = metawriter.make_config_meta_dirs()
        meta = metawriter.metadata

        #--------------------------------------------#
        #------- Main loop for image scanning -------#
        #--------------------------------------------#
        i = 0
        t = 0
        data_index = 0
        start_time = time.time()
        for heater in target_map:
            heater_dir = os.path.join(experiment_dir, f"heater{heater}")
            # heater_dir = heater_dir.replace("\\", "/")
            self.create_dir(heater_dir)

            # move to top left of heater
            print(f"---Starting work on heater {heater}---")
            initial_pos = heater_coords[heater][4]  # Inlet 1
            # Calculate specific steps for heater
            dx, dy = self.calculate_steps(Nchambers=8,
                                          ncol_FOVs=self.hw['ncol_FOVS'][all_selections['chip_type']],
                                          coords=heater_coords[heater])  # We should check if assuming 8 chambers is always True

            self.instrument_interface.moveImagerXY(initial_pos)
            t += 1

            for chamber in tqdm(target_map[heater]):
                chamber_dir = f"heater{heater}/chamber{chamber}"
                chamber_path = os.path.join(heater_dir, f"chamber{chamber}")
                # chamber_dir = chamber_dir.replace("\\","/")
                # chamber_path = chamber_path.replace("\\","/")
                self.create_dir(chamber_path)
                new_block = metawriter.add_data(p_mode=all_selections['drop_type'],
                                                png=False,
                                                chip=all_selections['chip_type'],
                                                chamber=chamber,
                                                heater=heater,
                                                sampleID=all_selections['chamber_ids'][data_index],  # Use data_index to access chamber_ids
                                                test=all_selections['tests'][t],
                                                chamber_dir_path=chamber_dir
                                                )
                meta.append(new_block)
                # Calculate new position
                # Always start at inlet
                if chamber == 0:
                    # We are already at the initial position (chamber 1 inlet) for this heater iteration
                    print(f'---Starting work on chamber {chamber}...---')
                    target_chamber = initial_pos
                    pass
                else:
                    # We need to move to the current chamber iteration value
                    print(f'---Starting work on chamber {chamber}...---')
                    target_chamber = initial_pos + (chamber * dy)
                    target_chamber = [initial_pos[0], initial_pos[1] + (chamber*dy)]
                    self.instrument_interface.moveImagerXY(target_chamber)

                for FOV in tqdm(range(self.hw['ncol_FOVS'][all_selections['chip_type']])):
                    fov_dir = os.path.join(chamber_path, f"FOV{FOV}")
                    fov_dir = fov_dir.replace("\\", "/")
                    fov_metadir = f"{chamber_dir}/FOV{FOV}"
                    fov_metadir = fov_metadir.replace("\\", "/")
                    self.create_dir(fov_dir)
                    x_now, y_now, z_now, fw_now = self.instrument_interface.reader.get_position()
                    # Write metadata
                    metawriter.add_fov_data(data=meta,
                                            data_index=data_index,  # Use data_index here
                                            fov_index=FOV,
                                            fov_dir_path=fov_metadir,
                                            coords={'X': x_now, 'Y': y_now, 'Z': z_now, 'FW': fw_now},
                                            mask_coords=self.hw['mask_coordinates']['coords']
                                            )
                    if FOV == 0:
                        # We are at initial position for this chamber
                        print("")
                        print(f"---Starting work on FOV {FOV}...---")
                        pass
                    else:
                        print("")
                        print(f"---Starting work on FOV {FOV}...---")
                        target_FOV = [target_chamber[0] + (FOV*dx), target_chamber[1]]
                        self.instrument_interface.moveImagerXY(target_FOV)

                    for channel in channels_to_image:
                        print(f"---Imaging {channel}---")
                        e = self.hw['default_exposures'][channel]
                        img_fname = f"{channel}_{e}.tif"
                        img_path = os.path.join(fov_dir, img_fname)
                        img_metapath = f"{fov_metadir}/{img_fname}"

                        # Capture image
                        img = self.acquire_image(channel)
                        tifffile.imwrite(img_path, img)
                        fov_str = str(FOV)
                        meta[data_index]["FOVs"][fov_str]["images"].update(
                            {f"{channel}": {
                                "target": "Unknown",
                                "image_path": img_metapath,
                                "exposure_time": e
                            }
                             }
                        )
                i += 1
                data_index = i  # Reset data_index for the next chamber

                # Move imager to the next FOV, we already did position 0
                # translate x, hold y
                next_fov_target = (x_now + dx, y_now)
                self.instrument_interface.moveImagerXY(next_fov_target)

        # After imaging all channels, all chambers/channel, and all fovs/chamber, write metadata.json
        metawriter.write_metadata(meta=meta, meta_dir=meta_dir)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"---Image scan completed in {elapsed_time}---")
