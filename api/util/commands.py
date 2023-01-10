'''
DESCRIPTION:
This module contains a data structure of commands based on module and command.

AUTHOR:
G.LC

AFFILIATION:
Bio-Rad, CDG, Advanced-Tech Team

CREATED ON:
8/30/2022
'''

commands = {
    'UpperGantry' : {
        'Pipettor-X' : {
            'home' : b'>01,0,home,<CR>\n',
            'mabs' : b'>01,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>01,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>01,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>01,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>01,0,stop,<CR>\n',
            '?pos' : b'>01,0,?pos,<CR>\n',
            '?mv' : b'>01,0,?mv,<CR>\n'
            },
        'Pipettor-Y' : {
            'home' : b'>02,0,home,<CR>\n',
            'mabs' : b'>02,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>02,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>02,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>02,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>02,0,stop,<CR>\n',
            '?pos' : b'>02,0,?pos,<CR>\n',
            '?mv' : b'>02,0,?mv,<CR>\n'
            },
        'Pipettor-Z' : {
            'home' : b'>03,0,home,<CR>\n',
            'mabs' : b'>03,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>03,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>03,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>03,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>03,0,stop,<CR>\n',
            '?pos' : b'>03,0,?pos,<CR>\n',
            '?mv' : b'>03,0,?mv,<CR>\n'
            },
        'Drip Plate' : {
            'home' : b'>04,0,home,<CR>\n',
            'mabs' : b'>04,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>04,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>04,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>04,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>04,0,stop,<CR>\n',
            '?pos' : b'>04,0,?pos,<CR>\n',
            '?mv' : b'>04,0,?mv,<CR>\n'
            },
        'Air Module' : {}
        },
    'Prep Deck' : {
        'Mag Separator' : {
            'home' : b'>17,0,home,<CR>\n',
            'mabs' : b'>17,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>17,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>17,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>17,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>17,0,stop,<CR>\n',
            '?pos' : b'>17,0,?pos,<CR>\n',
            '?mv' : b'>17,0,?mv,<CR>\n'
            }
        },
    'Reader' : {
        'X Axis' : {
            'home' : b'>06,0,home,<CR>\n',
            'mabs' : b'>06,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>06,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>06,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>06,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>06,0,stop,<CR>\n',
            '?pos' : b'>06,0,?pos,<CR>\n',
            '?mv' : b'>06,0,?mv,<CR>\n'
            },
        'Y Axis' : {
            'home' : b'>07,0,home,<CR>\n',
            'mabs' : b'>07,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>07,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>07,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>07,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>07,0,stop,<CR>\n',
            '?pos' : b'>07,0,?pos,<CR>\n',
            '?mv' : b'>07,0,?mv,<CR>\n'
            },
        'Z Axis' : {
            'home' : b'>08,0,home,<CR>\n',
            'mabs' : b'>08,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>08,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>08,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>08,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>08,0,stop,<CR>\n',
            '?pos' : b'>08,0,?pos,<CR>\n',
            '?mv' : b'>08,0,?mv,<CR>\n'
            },
        'Filter Wheel' : {
            'home' : b'>09,0,home,<CR>\n',
            'mabs' : b'>09,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>09,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>09,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>09,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>09,0,stop,<CR>\n',
            '?pos' : b'>09,0,?pos,<CR>\n',
            '?mv' : b'>09,0,?mv,<CR>\n'
            },
        'LED' : {},
        'Front Tray' : {
            'home' : b'>11,0,home,<CR>\n',
            'mabs' : b'>11,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>11,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>11,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>11,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>11,0,stop,<CR>\n',
            '?pos' : b'>11,0,?pos,<CR>\n',
            '?mv' : b'>11,0,?mv,<CR>\n'
            },
        'Rear Tray' : {
            'home' : b'>12,0,home,<CR>\n',
            'mabs' : b'>12,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>12,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>12,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>12,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>12,0,stop,<CR>\n',
            '?pos' : b'>12,0,?pos,<CR>\n',
            '?mv' : b'>12,0,?mv,<CR>\n'
            },
        'Heater Front-1' : {
            'home' : b'>13,0,home,<CR>\n',
            'mabs' : b'>13,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>13,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>13,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>13,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>13,0,stop,<CR>\n',
            '?pos' : b'>13,0,?pos,<CR>\n',
            '?mv' : b'>13,0,?mv,<CR>\n'
            },
        'Heater Front-2' : {
            'home' : b'>14,0,home,<CR>\n',
            'mabs' : b'>14,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>14,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>14,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>14,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>14,0,stop,<CR>\n',
            '?pos' : b'>14,0,?pos,<CR>\n',
            '?mv' : b'>14,0,?mv,<CR>\n'
            },
        'Heater Rear-1' : {
            'home' : b'>15,0,home,<CR>\n',
            'mabs' : b'>15,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>15,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>15,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>15,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>15,0,stop,<CR>\n',
            '?pos' : b'>15,0,?pos,<CR>\n',
            '?mv' : b'>15,0,?mv,<CR>\n'
            },
        'Heater Rear-2' : {
            'home' : b'>16,0,home,<CR>\n',
            'mabs' : b'>16,0,mabs,steps,velocity,<CR>\n',
            'mrel' : b'>16,0,mrel,steps,velocity,<CR>\n',
            'mlim' : b'>16,0,mlim,limit,velocity,<CR>\n',
            'mgp' : b'>16,0,mpg,IO,velocity,<CR>\n',
            'stop' : b'>16,0,stop,<CR>\n',
            '?pos' : b'>16,0,?pos,<CR>\n',
            '?mv' : b'>16,0,?mv,<CR>\n'
            }
        },
    'motor' : {
        'home' : b'>address,0,home,<CR>\n', 
        'mabs' : b'>address,0,mabs,steps,velocity,<CR>\n',
        'mrel' : b'>address,0,mrel,steps,velocity,<CR>\n',
        'mlim' : b'>address,0,mlim,limit,velocity,<CR>\n',
        'mgp' : b'>address,0,mgp,IO,velocity,<CR>\n',
        'stop' : b'>address,0,stop,<CR>\n',
        '?pos' : b'>address,0,?pos,<CR>\n',
        '?mv' : b'>address,0,?mv,<CR>\n',
        'hdir' : b'>address,0,hdir,direction,<CR>\n',
        'hvel' : b'>address,0,hvel,velocity,<CR>\n',
        'hpol' : b'>address,0,hpol,polarity,<CR>\n'
        },
    'led' : {
        'set' : b'>address,0,set,chan,level,<CR>\n',
        'off' : b'>address,0,off,chan,<CR>\n',
        'setmul' : b'>address,0,setmul,chans,level,<CR>\n', # Set multiple channels on (chans = ???)
        'offmul' : b'>address,0,offmul,chans,<CR>\n',
        '?led' : b'>address,0,?led,chan,<CR>\n' # Get the led level (intensity)
        },
    'coil' : {
        'set' : b'>address,0,set,chan,time,<CR>\n',
        'off' : b'>address,0,<CR>\n',
        'setmul' : b'>address,0,setmul,chans,time,<CR>\n',
        'offmul' : b'>address,0,offmul,chans,time,<CR>\n',
        '?coils' : b'>address,0,?coils,<CR>\n'
        },
    'chassis' : { # Aru temp solution till MAX22200 issue resolved
        'relayon' : b'>address,0,relayon,channel,<CR>\n',
        'relayoff' : b'>address,0,relayoff,channel,<CR>\n'
        }
    }