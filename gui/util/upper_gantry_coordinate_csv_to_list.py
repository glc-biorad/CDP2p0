import pandas as pd

def upper_gantry_coordinate_csv_to_list(file_name: str) -> list:
	""" Converts a backup upper gantry coordinate csv to a list
		for storing in a table

	Parameters:
	file_name : str
		Name of the csv file to convert 
	"""
	# Initialize the empty list
	coordinates = []
	# Open the file for reading into a pandas dataframe
	df = pd.read_csv(file_name)
	# Iterate through the dataframe storing the rows as a list
	for index, row in df.iterrows():
		consumable = row['consumable']
		tray = row['tray']
		column = row['column']
		x = row['x']
		y = row['y']
		z1 = row['z1']
		z2 = row['z2']
		tip = row['tip']
		coordinates.append(
			[consumable, tray, column, x, y, z1, z2, tip]
		)
	return coordinates


#file_name = '../../AppData/unit_A_upper_gantry_coordinates.csv'
#a = upper_gantry_coordinate_csv_to_list(file_name)
