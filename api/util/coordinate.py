
# Version: Test
'''
DESCRIPTION:
This module contains Coordinate.

NOTES:

AUTHOR:
G.LC

AFFILIATION:
Bio-Rad, CDG, Advanced-Tech Team

CREATED ON:
8/30/2022
'''

import sys

class Coordinate():
    # Public variables.
    x = None
    y = None
    z = None

    # Private variables.

    def __init__(self, location):
        if type(location) == list:
            self.x = location[0]
            self.y = location[1]
            self.z = location[2]

    def move(self, location):
        if type(location) == list:
            self.x = location[0]
            self.y = location[1]
            self.z = location[2]

# The coordinates are in units of microSteps
coordinates = {
    'reader' : {
        'heater_1' : [-300000,-1100000,-300000,0],
        'heater_2' : [-300000,-850000,-295000,0],
        'heater_3' : [0,0,0,0],
        'heater_4' : [0,0,0,0],
        'filter_wheel_home': [0,0,0,0],
        'filter_wheel_alexa405': [0,0,0,-47000],
        'filter_wheel_cy55': [0,0,0,-4000], 
        'filter_wheel_cy5': [0,0,0,-13000],
        'filter_wheel_atto': [0,0,0,-21000], #21500
        'filter_wheel_hex': [0,0,0,-30000],
        'filter_wheel_fam': [0,0,0,-37000],
        },
    'deck_plate' : {
        'custom': [-396300,-936000,-605000,0],  # (-396300, -936000, -605000, -510000)
        'test_0' : [-2500, -1775000, 0, 0],
        'test_1' : [-140000, -337000, -300000, 0],
        'dg8': {
            'dz' : 362000,
            0: {
                0: [0,0,0,0],
                1: [0,0,0,0],
                2: [0,0,0,0], #[-250900, -200000, -1459000, 0], comment out is position without tips, only heads
                },
            1: {
                0: [0,0,0,0],
                1: [0,0,0,0],
                2: [0,0,0,0],
                },
            2: {
                0: [0,0,0,0],
                1: [0,0,0,0],
                2: [0,0,0,0],
                },
            3: {
                0: [0,0,0,0],
                1: [0,0,0,0],
                2: [0,0,0,0]
                },
            },
        'dg8_left': {
            0: [0,0,0,0], #[-250900,-200000,-775000,0] # commented is 1000 uL
            1: [0,0,0,0],
            2: [0,0,0,0],
            3: [0,0,0,0]
            },
        'sample_loading' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [-263850,-683000,-1105000,0],
            },
        'reagent_cartridge' : {
            0 : { # reagent cartridge #D
                0 : [0,0,0,0], # reagent cartridge 0 row 0 [x,y,z,drip_plate]
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0]
                },
            1 : { # reagent cartridge front 2 #C
                0 : [0,0,0,0], # z = -950000
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0],
                },
            2 : { #B
                0 : [0,0,0,0], # z = -950000
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0]
                },
            3 : { # A
                0 : [-246850,-628000,-965000,0],
                1 : [-239850,-628000,-965000,0],
                2 : [-233600,-628000,-860000,0],
                3 : [-228600,-633000,-765000,0],
                4 : [-223350,-633000,-765000,0],
                5 : [-217850,-633000,-765000,0],
                6 : [-212350,-633000,-765000,0],
                7 : [-206850,-633000,-765000,0],
                8 : [-201600,-633000,-765000,0],
                9 : [-196350,-633000,-860000,0],
                10 : [-190100,-633000,-965000,0],
                11 : [-183350,-633000,-965000,0],
                },
            },
        'tip_trays' : {
            0 : { # tip tray 0 (D)
                0 : [0,0,0,0], 
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0]
                },
            1 : { #C
                0 : [0,0,0,0],
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0],
                },
            2 : { #B
                0 : [0,0,0,0],
                1 : [0,0,0,0],
                2 : [0,0,0,0],
                3 : [0,0,0,0],
                4 : [0,0,0,0],
                5 : [0,0,0,0],
                6 : [0,0,0,0],
                7 : [0,0,0,0],
                8 : [0,0,0,0],
                9 : [0,0,0,0],
                10 : [0,0,0,0],
                11 : [0,0,0,0],
                },
            3 : { #A
                0 : [-163150,-628000,-1536000,0],
                1 : [-158150,-628000,-1536000,0],
                2 : [-152750,-628000,-1536000,0],
                3 : [-147250,-628000,-1536000,0],
                4 : [-141850,-628000,-1536000,0],
                5 : [-136450,-628000,-1536000,0],
                6 : [-131050,-628000,-1536000,0],
                7 : [-125650,-628000,-1536000,0],
                8 : [-120250,-628000,-1536000,0],
                9 : [-114850,-628000,-1536000,0],
                10 : [-109450,-628000,-1536000,0],
                11 : [-104050,-628000,-1536000,0],
                },
            },
        'quant_strip' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0]
            },
        'assay_strip' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0],
            4 : [0,0,0,0],
            5 : [0,0,0,0],
            6 : [0,0,0,0],
            7 : [0,0,0,0]
            },
        'staging_deck' : {},
        'rear_space_1' : {},
        'heater_shaker' : {
            0 : [-383450,-948000,-650000,0],
            1 : [-366450,-948000,-650000,0],
            2 : [-347450,-948000,-650000,0],
            3 : [-329450,-948000,-650000,0],
            },
        'mag_separator' : {
            0 : [-386450,-1423000,-780000,0],
            1 : [-381450,-1423000,-780000,0],
            2 : [-375950,-1423000,-780000,0],
            3 : [-370449,-1423000,-780000,0],
            4 : [-364949,-1423000,-780000,0],
            5 : [-359449,-1423000,-780000,0],
            6 : [-353949,-1423000,-780000,0],
            7 : [-348449,-1423000,-780000,0],
            8 : [-342949,-1423000,-780000,0],
            9 : [-337699,-1423000,-780000,0],
            10 : [-332199,-1423000,-780000,0],
            11 : [-326699,-1423000,-780000,0],
            },
        'tip_transfer_tray' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0],
            4 : [0,0,0,0],
            5 : [0,0,0,0],
            6 : [0,0,0,0],
            7 : [0,0,0,0],
            'chips': {
                'microwells': {
                    0: [0,0,0,0],
                    1: [0,0,0,0],
                    2: [0,0,0,0],
                    3: [0,0,0,0], #330000
                    },
                'droplets': {
                    0: [0,0,0,0],
                    1: [0,0,0,0],
                    2: [0,0,0,0],
                    3: [0,0,0,0],
                    },
                }
            },
        'chiller' : {},
        'pre_amp' : {},
        'rna_heater' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0]
            },
        'pcr_thermocycler' : {
            0 : [0,0,0,0],
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0],
            4 : [0,0,0,0],
            5 : [0,0,0,0],
            6 : [0,0,0,0],
            7 : [0,0,0,0],
            8 : [0,0,0,0],
            9 : [0,0,0,0],
            10 : [0,0,0,0],
            11 : [0,0,0,0],
            },
        'tray_out_location' : {
            0 : [0,0,0,0], #[-2300, -1773000, -716000,0] <-- Droplets , [-65300,-1773000,-700000,0] <-- microweels
            1 : [0,0,0,0],
            2 : [0,0,0,0],
            3 : [0,0,0,0],
            'nipt': {
                'D': [0,0,0,0],
                },
            'quant': {
                'D': [0,0,0,0],
                },
            'ff': {
                'D': [0,0,0,0],
                },
            'chips': {
                    0: [0,0,0,0], # Tray CD (D)
                    1: [0,0,0,0], # Tray CD (C)
                    2: [0,0,0,0], # Tray AB (B)
                    3: [0,0,0,0], # Tray AB (A)
                },
            },
        'tray_in_location' : {},
        'lid_tray': {
            0: [0,0,0,0],
            1: [0,0,0,0],
            2: [0,0,0,0],
            3: [0,0,0,0],
            }
        }
    }

coordinate_names = [
    'home',
    'custom',
    'test_0',
    'test_1',
    'microwells_chip_1',
    'microwells_chip_2',
    'microwells_chip_3',
    'microwells_chip_4',
    'droplets_chip_1',
    'droplets_chip_2',
    'droplets_chip_3',
    'droplets_chip_4',
    'tip_trays_trayA_row1',
    'tip_trays_trayA_row2',
    'tip_trays_trayA_row3',
    'tip_trays_trayA_row4',
    'tip_trays_trayA_row5',
    'tip_trays_trayA_row6',
    'tip_trays_trayA_row7',
    'tip_trays_trayA_row8',
    'tip_trays_trayA_row9',
    'tip_trays_trayA_row10',
    'tip_trays_trayA_row11',
    'tip_trays_trayA_row12',
    'tip_trays_tray1_row1',
    'tip_trays_tray1_row2',
    'tip_trays_tray1_row3',
    'tip_trays_tray1_row4',
    'tip_trays_tray1_row5',
    'tip_trays_tray1_row6',
    'tip_trays_tray1_row7',
    'tip_trays_tray1_row8',
    'tip_trays_tray1_row9',
    'tip_trays_tray1_row10',
    'tip_trays_tray1_row11',
    'tip_trays_tray1_row12',
    'tip_trays_tray2_row1',
    'tip_trays_tray2_row2',
    'tip_trays_tray2_row3',
    'tip_trays_tray2_row4',
    'tip_trays_tray2_row5',
    'tip_trays_tray2_row6',
    'tip_trays_tray2_row7',
    'tip_trays_tray2_row8',
    'tip_trays_tray2_row9',
    'tip_trays_tray2_row10',
    'tip_trays_tray2_row11',
    'tip_trays_tray2_row12',
    'tip_trays_tray3_row1',
    'tip_trays_tray3_row2',
    'tip_trays_tray3_row3',
    'tip_trays_tray3_row4',
    'tip_trays_tray3_row5',
    'tip_trays_tray3_row6',
    'tip_trays_tray3_row7',
    'tip_trays_tray3_row8',
    'tip_trays_tray3_row9',
    'tip_trays_tray3_row10',
    'tip_trays_tray3_row11',
    'tip_trays_tray3_row12',
    'tip_trays_tray4_row1',
    'tip_trays_tray4_row2',
    'tip_trays_tray4_row3',
    'tip_trays_tray4_row4',
    'tip_trays_tray4_row5',
    'tip_trays_tray4_row6',
    'tip_trays_tray4_row7',
    'tip_trays_tray4_row8',
    'tip_trays_tray4_row9',
    'tip_trays_tray4_row10',
    'tip_trays_tray4_row11',
    'tip_trays_tray4_row12',
    'tip_transfer_tray_row1',
    'tip_transfer_tray_row2',
    'tip_transfer_tray_row3',
    'tip_transfer_tray_row4',
    'tip_transfer_tray_row5',
    'tip_transfer_tray_row6',
    'tip_transfer_tray_row7',
    'tip_transfer_tray_row8',
    'reagent_cartridge_tray1_row1',
    'reagent_cartridge_tray1_row2',
    'reagent_cartridge_tray1_row3',
    'reagent_cartridge_tray1_row4',
    'reagent_cartridge_tray1_row5',
    'reagent_cartridge_tray1_row6',
    'reagent_cartridge_tray1_row7',
    'reagent_cartridge_tray1_row8',
    'reagent_cartridge_tray1_row9',
    'reagent_cartridge_tray1_row10',
    'reagent_cartridge_tray1_row11',
    'reagent_cartridge_tray1_row12',
    'reagent_cartridge_tray2_row1',
    'reagent_cartridge_tray2_row2',
    'reagent_cartridge_tray2_row3',
    'reagent_cartridge_tray2_row4',
    'reagent_cartridge_tray2_row5',
    'reagent_cartridge_tray2_row6',
    'reagent_cartridge_tray2_row7',
    'reagent_cartridge_tray2_row8',
    'reagent_cartridge_tray2_row9',
    'reagent_cartridge_tray2_row10',
    'reagent_cartridge_tray2_row11',
    'reagent_cartridge_tray2_row12',
    'reagent_cartridge_tray3_row1',
    'reagent_cartridge_tray3_row2',
    'reagent_cartridge_tray3_row3',
    'reagent_cartridge_tray3_row4',
    'reagent_cartridge_tray3_row5',
    'reagent_cartridge_tray3_row6',
    'reagent_cartridge_tray3_row7',
    'reagent_cartridge_tray3_row8',
    'reagent_cartridge_tray3_row9',
    'reagent_cartridge_tray3_row10',
    'reagent_cartridge_tray3_row11',
    'reagent_cartridge_tray3_row12',
    'reagent_cartridge_tray4_row1',
    'reagent_cartridge_tray4_row2',
    'reagent_cartridge_tray4_row3',
    'reagent_cartridge_tray4_row4',
    'reagent_cartridge_tray4_row5',
    'reagent_cartridge_tray4_row6',
    'reagent_cartridge_tray4_row7',
    'reagent_cartridge_tray4_row8',
    'reagent_cartridge_tray4_row9',
    'reagent_cartridge_tray4_row10',
    'reagent_cartridge_tray4_row11',
    'reagent_cartridge_tray4_row12',
    'heater_shaker_row1',
    'heater_shaker_row2',
    'heater_shaker_row3',
    'heater_shaker_row4',
    'mag_separator_row1',
    'mag_separator_row2',
    'mag_separator_row3',
    'mag_separator_row4',
    'mag_separator_row5',
    'mag_separator_row6',
    'mag_separator_row7',
    'mag_separator_row8',
    'mag_separator_row9',
    'mag_separator_row10',
    'mag_separator_row11',
    'mag_separator_row12',
    'tray_out_location_tray1',
    'tray_out_location_tray2',
    'tray_out_location_tray3',
    'tray_out_location_tray4',
    'tray_out_location_chip1',
    'tray_out_location_chip2',
    'tray_out_location_chip3',
    'tray_out_location_chip4',
    'pcr_thermocycler_row1',
    'pcr_thermocycler_row2',
    'pcr_thermocycler_row3',
    'pcr_thermocycler_row4',
    'pcr_thermocycler_row5',
    'pcr_thermocycler_row6',
    'pcr_thermocycler_row7',
    'pcr_thermocycler_row8',
    'pcr_thermocycler_row9',
    'pcr_thermocycler_row10',
    'pcr_thermocycler_row11',
    'pcr_thermocycler_row12',
    'sample_loading_tray1',
    'sample_loading_tray2',
    'sample_loading_tray3',
    'sample_loading_tray4',
    'lid1',
    'lid2',
    'lid3',
    'lid4',
    'heater_1',
    'heater_2',
    'heater_3',
    'heater_4',
    'dg8_1000_100',
    'dg8_1000_010',
    'dg8_1000_001',
    'dg8_0100_100',
    'dg8_0100_010',
    'dg8_0100_001',
    'dg8_0010_100',
    'dg8_0010_010',
    'dg8_0010_001',
    'dg8_0001_100',
    'dg8_0001_010',
    'dg8_0001_001',
    'assay_strip_row1',
    'assay_strip_row2',
    'assay_strip_row3',
    'assay_strip_row4',
    'assay_strip_row5',
    'assay_strip_row6',
    'assay_strip_row7',
    'assay_strip_row8',
    'tray_out_location_nipt_D',
    'tray_out_location_ff_D',
    'tray_out_location_quant_D',
    ]