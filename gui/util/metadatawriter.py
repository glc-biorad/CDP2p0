import os
import shutil
import json


class MetaDataWriter:
    """
    Functionalities to generate a dictionary with metadata for images taken with scanning function.
    This is to be used in conjunction with CDP2p0_GUI.py for gui interfacing and chipscanner.py for chip scanning.
    """
    def __init__(self, hw_config, experiment_fpath, experiment_fname):
        """
        Instance method of class.
        Keyword arguments:
        - hw_config : loaded json object of hardware_config.json
        - experiment_fpath      : main experiment directory to store all scan instance data (config, heater{}, metadata dirs)
        """
        self.parentdir = experiment_fpath
        self.fname = experiment_fname
        self.hw_config = hw_config
        self.metadata = []
        self.heater_map = {
            0 : "A",
            1 : "B",
            2 : "C",
            3 : "D"
            }


    def add_data(self, p_mode, png, chip, chamber, heater, sampleID, test, chamber_dir_path):
        """
        Adds data to a dictionary block which is to be appended to metadata.json, returns dict. Inputs should be parsed from gui selections
        Keyword arguments:
        - p_mode           : str partition_mode
        - png              : bool typically False, as std output is tif
        - chip             : str dPCR chip type
        - chamber          : int chamber number
        - heater           : str heater id
        - sampleID         : str name for sample in chamber
        - test             : str test choice
        - chamber_dir_path : str path to chamber directory
        """
        new_data = {
            "unit": self.hw_config["unit"],
            "partition_mode": p_mode,
            "png": png,
            "heater": heater,
            "chip": chip,
            "chamber": chamber,
            "sampleID": sampleID,
            "test_type": test,
            "expected_FOVs": self.hw_config["ncol_FOVS"][chip],
            "chamber_dir_path": chamber_dir_path,
            "FOVs": {}
        }

        return new_data

    def add_fov_data(self, data, data_index, fov_index, fov_dir_path, coords, mask_coords):
        """
        Adds FOV metadata to metadata dict (nested in 'FOVs' in add_data()).
        Keyword arguments:
        - data         : dict with metadata blocks
        - data_index   : index of specific block to update
        - fov_index    : index of current fov to update
        - fov_dir_path : path to fov directory
        - coords       : imager coordinates from system
        - mask_coords  : masking coordinates to be applied

        """
        fov_str = str(fov_index)
        data[data_index]["FOVs"][fov_str] = {
            "fov_dir_path": fov_dir_path,
            "coordinates": coords,
            "mask_coordinates": mask_coords,
            "images": {}
        }

    def make_config_meta_dirs(self):
        """
        Makes config and metadata directories in the experiment parent folder.
        Also copies the current system hardware_config.json to the new config folder.
        """

        # Create config directory and add config json
        data_dir = os.path.join(self.parentdir, 'user_data')
        data_dir = data_dir.replace("\\","/")
        if os.path.exists(data_dir):
            pass
        else:
            os.mkdir(data_dir)
        experiment_dir = os.path.join(data_dir, self.fname)
        experiment_dir = experiment_dir.replace("\\","/")
        if not os.path.exists(experiment_dir):
            os.mkdir(experiment_dir)
        else:
            Exception("Directory already exists")
        config_dir = os.path.join(experiment_dir, 'configs')
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
        else:
            shutil.rmtree(config_dir)
            os.mkdir(config_dir)

        config_filepath = os.path.join(config_dir, 'hardware_config.json')
        shutil.copy('hardware_config.json', config_filepath)

        # Create metadata directory
        meta_dir = os.path.join(experiment_dir, 'metadata')
        if not os.path.isdir(meta_dir):
            os.mkdir(meta_dir)
        else:
            shutil.rmtree(meta_dir)
            os.mkdir(meta_dir)

        return experiment_dir, meta_dir

    def write_metadata(self, meta, meta_dir):
        """
        Writes the metadata dictionary that was populated to a file in the experiment metadata directory.
        Keyword arguments:
        - meta     : dict of metadata
        - meta_dir : path to metadata directory
        """
        meta_json = { "data" : meta }
        meta_path = os.path.join(meta_dir, 'metadata.json')

        with open(meta_path, "w") as json_export:
            json.dump(meta_json, json_export)

        print(f"Metadata written and saved to {meta_path}")
        
