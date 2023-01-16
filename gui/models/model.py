"""
Model represents the data for the GUI
"""
import sqlite3

from gui.models.thermocycle_model import ThermocycleModel
from gui.models.build_protocol_model import BuildProtocolModel
from gui.models.optimize_model import OptimizeModel
from gui.models.coordinates_model import CoordinatesModel

DB_NAME = 'AppData/unit_'

from gui.models.tip_use_model import TipUseModel
from gui.models.state_model import StateModel

class Model:
	# Models
	thermocycle_model: ThermocycleModel = None

	def __init__(self, unit: str) -> None:
		self.unit = unit
		self.db_name = f'{DB_NAME}{unit.upper()}.db'
		self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
		self.cursor = self.connection.cursor()
		self.setup_thermocycle_table()
		self.setup_build_protocol_table()
		#m = TipUseModel(self.db_name, self.cursor, self.connection)
		self.setup_state_table()
		self.setup_coordinates_table(unit)

	def get_thermocycle_model(self) -> ThermocycleModel:
		self.thermocycle_model = ThermocycleModel(self.db_name, self.cursor, self.connection)
		return self.thermocycle_model

	def setup_thermocycle_table(self) -> None:
		""" Sets up the Thermocycling model with defaults for the thermocycle tab"""
		model = ThermocycleModel(self.db_name, self.cursor, self.connection)
		model.drop_table()
		model.create_table()
		model.insert(1,'A',40,84,50,84,3,40,30,1,1,1)
		model.insert(2,'B',40,84,50,84,3,40,30,1,1,1)
		model.insert(3,'C',40,84,50,84,3,40,30,0,1,1)
		model.insert(4,'D',40,84,50,84,3,40,30,1,1,1)

	def get_build_protocol_model(self) -> BuildProtocolModel:
		self.build_protocol_model = BuildProtocolModel(self.db_name, self.cursor, self.connection)
		return self.build_protocol_model

	def setup_build_protocol_table(self) -> None:
		model = BuildProtocolModel(self.db_name, self.cursor, self.connection)
		model.create_table()

	def get_optimize_model(self) -> OptimizeModel:
		self.optimize_model = OptimizeModel(self.db_name, self.cursor, self.connection)
		return self.optimize_model

	def setup_state_table(self):
		""" Helper for setting up the state model
		"""
		model = StateModel(self.db_name, self.cursor, self.connection)
		try:
			model.drop_table()
		except:
			pass
		model.create_table()

	def get_coordinates_model(self) -> None:
		""" Get the coordinate model for the unit of interest

		Parameters:
		unit : str
			Unit of interest
		"""
		self.coordinates_model = CoordinatesModel(self.db_name, self.cursor, self.connection)
		return self.coordinates_model

	def setup_coordinates_table(self, unit: str) -> None:
		""" Helper for setting up a coordinates table from scratch for a unit

		Parameters
		----------
		unit : str
			Alphabetic (single character) symbol for the CDP unit (A, B, C, D, E, F)
		"""	
		import gui.util.upper_gantry_coordinate_csv_to_list as ugcc2l 
		TABLE_NAMES = {
			'A': {'table_name': "Unit A Upper Gantry Coordinates", 'file_name': 'AppData/unit_A_upper_gantry_coordinates.csv'},
			'B': {'table_name': "Unit B Upper Gantry Coordinates", 'file_name': 'AppData/unit_B_upper_gantry_coordinates.csv'},
			'C': {'table_name': "Unit C Upper Gantry Coordinates", 'file_name': 'AppData/unit_C_upper_gantry_coordinates.csv'},
			'D': {'table_name': "Unit D Upper Gantry Coordinates", 'file_name': 'AppData/unit_D_upper_gantry_coordinates.csv'},
			'E': {'table_name': "Unit E Upper Gantry Coordinates", 'file_name': 'AppData/unit_E_upper_gantry_coordinates.csv'},
			'F': {'table_name': "Unit F Upper Gantry Coordinates", 'file_name': 'AppData/unit_F_upper_gantry_coordinates.csv'},
		}
		# Get the table names
		table_name = TABLE_NAMES[unit.upper()]['table_name']
		file_name = TABLE_NAMES[unit.upper()]['file_name']
		# Initialize the model
		model = CoordinatesModel(self.db_name, self.cursor, self.connection)
		# Create the table
		try:
			model.drop_table(table_name)
		except:
			pass
		model.create_table(table_name)
		# Get the backup coordinate file for this unit as a list
		coordinates = ugcc2l.upper_gantry_coordinate_csv_to_list(file_name)
		# Iterate through the list 
		for ID in range(len(coordinates)):
			# Get the data
			consumable = coordinates[ID][0]
			tray = coordinates[ID][1]
			column = int(coordinates[ID][2])
			x = int(coordinates[ID][3])
			y = int(coordinates[ID][4])
			z1 = int(coordinates[ID][5])
			z2 = int(coordinates[ID][6])
			tip = int(coordinates[ID][7])
			# Add this row to the table
			model.insert(table_name, ID, consumable, tray, column, x, y, z1, z2, tip)
			
		# Check it worked
		#print(model.select(table_name))
