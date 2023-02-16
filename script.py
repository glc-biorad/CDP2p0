from api.upper_gantry.upper_gantry import UpperGantry

if __name__ == '__main__':
    ug = UpperGantry()
    ug.get_pipettor().liquid_level_detect()