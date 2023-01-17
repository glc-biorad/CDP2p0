'''
'''

PELTIER_PARAMETERS = {
    100: {
        "ID": 100,
        "Name": "Device Type",
        "Format": 'INT32',
        "Value Range": None,
        "Description": 1122,
        "Read-Only": True
        },
    101: {
        "ID": 101,
        "Name": "Hardware Version",
        "Format": "INT32",
        "Value Range": None,
        "Description": 123,
        "Read-Only": True
        },
    102: {
        "ID": 102,
        "Name": "Serial Number",
        "Format": "INT32",
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    103: {
        "ID": 103,
        "Name": "Firmware Version",
        "Format": "INT32",
        "Value Range": None,
        "Description": 123,
        "Read-Only": True
        },
    104: {
        "ID": 104,
        "Name": "Device Status",
        "Format": "INT32",
        "Value Range": None,
        "Description": {
            0: "Init",
            1: "Ready",
            2: "Run",
            3: "Error",
            4: "Bootloader",
            5: "Device will Reset within next 200ms"
            },
        "Read-Only": True
        },
    105: {
        "ID": 105,
        "Name": "Error Number",
        "Format": "INT32",
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    106: {
        "ID": 106,
        "Name": "Error Instance",
        "Format": "INT32",
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    107: {
        "ID": 107,
        "Name": "Error Parameter",
        "Format": "INT32",
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    108: {
        "ID": 108,
        "Name": "Save Data to Flash",
        "Format": "INT32",
        "Value Range": None,
        "Description": {
            0: "Enabled",
            1: "Disabled (All Parameters can then be used as RAM Parameters)"
            },
        "Read-Only": True
        },
    109: {
        "ID": 109,
        "Name": "Parameter System: Flash Status",
        "Format": "INT32",
        "Value Range": None,
        "Description": {
            0: "All Parameters are saved to Flash",
            1: "Save to flash pending or in progress. (Please do not power of the device now)",
            2: "Saving to Flash is disabled"
            },
        "Read-Only": True
        },
    1000: {
        "ID": 1000,
        "Name": "Object Temperature",
        "Format": 'FLOAT32',
        "Value Range": "degC",
        "Description": None,
        "Read-Only": True
        },
    1001: {
        "ID": 1001,
        "Name": "Sink Temperature",
        "Format": 'FLOAT32',
        "Value Range": "degC",
        "Description": None,
        "Read-Only": True
        },
    1010: {
        "ID": 1010,
        "Name": "Target Object Temperature",
        "Format": 'FLOAT32',
        "Value Range": "degC",
        "Description": None,
        "Read-Only": True
        },
    1011: {
        "ID": 1011,
        "Name": "(Ramp) Nominal Object Temperature",
        "Format": 'FLOAT32',
        "Value Range": "degC",
        "Description": None,
        "Read-Only": True
        },
    1012: {
        "ID": 1012,
        "Name": "Thermal Power Model Current",
        "Format": 'FLOAT32',
        "Value Range": "A",
        "Description": None,
        "Read-Only": True
        },
    1020: {
        "ID": 1020,
        "Name": "Actual Output Current",
        "Format": 'FLOAT32',
        "Value Range": "A",
        "Description": None,
        "Read-Only": True
        },
    1021: {
        "ID": 1021,
        "Name": "Actual Output Voltage",
        "Format": 'FLOAT32',
        "Value Range": "V",
        "Description": None,
        "Read-Only": True
        },
    1100: {
        "ID": 1100,
        "Name": "Relative Cooling Power",
        "Format": 'FLOAT32',
        "Value Range": "%",
        "Description": None,
        "Read-Only": True
        },
    1101: {
        "ID": 1101,
        "Name": "Nominal Fan Speed",
        "Format": 'FLOAT32',
        "Value Range": "rpm",
        "Description": None,
        "Read-Only": True
        },
    1102: {
        "ID": 1102,
        "Name": "Actual Fan Speed",
        "Format": 'FLOAT32',
        "Value Range": "rpm",
        "Description": None,
        "Read-Only": True
        },
    1103: {
        "ID": 1103,
        "Name": "Fan PWM Level",
        "Format": 'FLOAT32',
        "Value Range": "%",
        "Description": None,
        "Read-Only": True
        },
    1030: {},
    1031: {},
    1032: {},
    1040: {},
    1046: {},
    1042: {},
    1045: {},
    1041: {},
    1043: {},
    1044: {},
    1050: {},
    1051: {},
    1054: {},
    1052: {},
    1053: {},
    1060: {},
    1061: {},
    1062: {},
    1063: {},
    1110: {
        "ID": 1110,
        "Name": "Maximum Device Temperature",
        "Format": 'FLOAT32',
        "Value Range": "degC",
        "Description": None,
        "Read-Only": True
        },
    1111: {
        "ID": 1111,
        "Name": "Maximum Output Current",
        "Format": 'FLOAT32',
        "Value Range": "A",
        "Description": None,
        "Read-Only": True
        },
    1090: {},
    1070: {
        "ID": 1070,
        "Name": "Error Number",
        "Format": 'INT32',
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    1071: {
        "ID": 1071,
        "Name": "Error Instance",
        "Format": 'INT32',
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    1072: {
        "ID": 1072,
        "Name": "Error Parameter",
        "Format": 'INT32',
        "Value Range": None,
        "Description": None,
        "Read-Only": True
        },
    1080: {
        "ID": 1080,
        "Name": "Driver Status",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Init",
            1: "Ready",
            2: "Run",
            3: "Error",
            4: "Bootloader",
            5: "Device will Reset within the next 200ms"
            },
        "Read-Only": True
        },
    1081: {
        "ID": 1081,
        "Name": "Parameter System: Flash Status",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "All Parameters are saved to Flash",
            1: "Save to flash pending or in progress (Please do not power off the device now)"
            },
        "Read-Only": True
        },
    1200: {
        "ID": 1200,
        "Name": "Temperature is Stable",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Temperature regulation is not active",
            1: "Is not stable",
            2: "Is stable"
            },
        "Read-Only": True
        },
    2000: {},
    2010: {
        "ID": 2010,
        "Name": "Status",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Static OFF",
            1: "Statis ON",
            2: "Live OFF/ON (See ID 50000)",
            3: "HW Enable (Check GPIO Config)"
            },
        "Read-Only": False
        },
    2020: {},
    2021: {},
    2030: {},
    2031: {},
    2032: {},
    2033: {},
    2040: {},
    2051: {
        "ID": 2051,
        "Name": "Device Address",
        "Format": 'INT32',
        "Value Range": [i for i in range(255)],
        "Description": None,
        "Read-Only": False
        },
    2050: {},
    2052: {},
    2060: {},
    3000: {
        "ID": 3000,
        "Name": "Target Object Temp",
        "Format": 'FLOAT32',
        "Value Range": "RNG_TEMP",
        "Description": None,
        "Read-Only": False
        },
    3003: {
        "ID": 3003,
        "Name": "Coarse Temp Ramp",
        "Format": 'FLOAT32',
        "Value Range": [1e-6,50.0],
        "Description": None,
        "Read-Only": False
        },
    3002: {
        "ID": 3002,
        "Name": "Proximity Width",
        "Format": 'FLOAT32',
        "Value Range": [0., 200.],
        "Description": None,
        "Read-Only": False
        },
    3010: {},
    3011: {},
    3012: {},
    3013: {},
    3020: {},
    3030: {},
    3033: {},
    3034: {},
    3040: {
        "ID": 3040,
        "Name": "Resistance",
        "Format": 'FLOAT32',
        "Value Range": [0.001, 10000.],
        "Description": None,
        "Read-Only": False
        },
    3041: {
        "ID": 3041,
        "Name": "Maximal Current",
        "Format": 'FLOAT32',
        "Value Range": [0.01, 1000.],
        "Description": None,
        "Read-Only": False
        },
    3051: {},
    3050: {},
    4001: {},
    4002: {},
    4011: {},
    4010: {},
    4012: {},
    4040: {},
    4041: {},
    4042: {},
    4035: {},
    4036: {},
    4030: {},
    4031: {},
    4032: {},
    4033: {},
    4034: {},
    5001: {},
    5002: {},
    5011: {},
    5010: {},
    5012: {},
    5030: {
        "ID": 5030,
        "Name": "Sink Temperature Selection",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "External",
            1: "Fixed Value"
            },
        "Read-Only": False
        },
    5031: {
        "ID": 5031,
        "Name": "Fixed Temperature",
        "Format": 'FLOAT32',
        "Value Range": "RNG_TEMP",
        "Description": None,
        "Read-Only": False
        },
    5032: {
        "ID": 5032,
        "Name": "Upper ADC Limit Error",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Enabled",
            1: "Disabled"
            },
        "Read-Only": False
        },
    5040: {},
    5041: {},
    5042: {},
    5043: {},
    51000: {},
    51001: {},
    51002: {},
    51010: {},
    51011: {},
    51012: {},
    51013: {},
    51014: {},
    51015: {},
    51016: {},
    51022: {},
    51023: {},
    51024: {},
    51017: {},
    51018: {},
    51020: {},
    51021: {},
    6000: {},
    6007: {},
    6001: {},
    6008: {},
    6009: {},
    6002: {},
    6006: {},
    6003: {},
    6004: {},
    6010: {},
    6013: {},
    6011: {},
    6012: {},
    6005: {},
    4024: {},
    4025: {},
    4022: {},
    4023: {},
    4020: {},
    4021: {},
    6400: {},
    6401: {},
    6402: {},
    5024: {},
    5025: {},
    5022: {},
    5023: {},
    5020: {},
    5021: {},
    6050: {},
    6051: {},
    6052: {},
    6053: {},
    6054: {},
    6055: {},
    52000: {},
    52001: {},
    52002: {},
    52003: {},
    52010: {},
    52012: {},
    6020: {},
    6023: {},
    6024: {},
    6025: {},
    6026: {},
    6100: {},
    6101: {},
    6102: {},
    6103: {},
    6111: {},
    6110: {},
    6112: {},
    6121: {},
    6122: {},
    6130: {},
    6131: {},
    6132: {},
    6200: {
        "ID": 6200,
        "Name": "Fan Control Enable",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Disabled",
            1: "Enabled"
            },
        "Read-Only": False
        },
    6210: {
        "ID": 6210,
        "Name": "Actual Temperature Source",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "CH1 Sink",
            1: "CH1 Object",
            2: "CH2 Sink",
            3: "CH2 Object",
            4: "Device Temperature"
            },
        "Read-Only": False
        },
    6211: {
        "ID": 6211,
        "Name": "Target Temperature",
        "Format": 'FLOAT32',
        "Value Range": "RNG_TEMP",
        "Description": None,
        "Read-Only": False
        },
    6212: {},
    6213: {},
    6214: {},
    6220: {},
    6221: {},
    6227: {},
    6228: {},
    6222: {},
    6223: {},
    6224: {},
    6225: {},
    6226: {},
    6230: {},
    6302: {},
    6301: {},
    6300: {},
    108: {
        "ID": 108,
        "Name": "Save Data to Flash",
        "Format": 'INT32',
        "Value Range": None,
        "Description": {
            0: "Enabled",
            1: "Disabled"
            },
        "Read-Only": True
        },
    6310: {},
    6330: {},
    6320: {},
    }
