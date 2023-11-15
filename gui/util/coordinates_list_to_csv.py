
# Version: Test
def coordinates_list_to_csv(coordinates_list: list, file_name: str):
    """ Take a list of coordinates from a select query on the coordinates model
    and save them into a csv for backup purposes to avoid loss of coordinates

    Parameters
    __________
    coordinates_list : list
        List of the coordinates as expected from the coordinates model
    file_name : str
        Name of the file to be saved (without extension, but extension can be added)
    """
    # Open the file for writing
    try:
        if file_name[-4:] != '.csv':
            file_name = file_name + '.csv'
    except:
        pass
    ofile = open(file_name, 'w')
    # Iterate through the coordinates
    ofile.write('consumable,tray,column,x,y,z1,z2,tip\n')
    for coordinate in coordinates_list:
        # Get the coordinate data
        consumable = coordinate[1]
        tray = coordinate[2]
        column = coordinate[3]
        x = coordinate[4]
        y = coordinate[5]
        z1 = coordinate[6]
        z2 = coordinate[7]
        tip = coordinate[8]
        # Write this coordinate to the file
        ofile.write(f'{consumable},{tray},{column},{x},{y},{z1},{z2},{tip}\n')
    # Close the file
    ofile.close()