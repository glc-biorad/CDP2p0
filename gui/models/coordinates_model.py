import sqlite3

# Constants
VALID_TABLE_NAMES = [
	"Unit A Upper Gantry Coordinates",
	"Unit B Upper Gantry Coordinates",
	"Unit C Upper Gantry Coordinates",
	"Unit D Upper Gantry Coordinates",
	"Unit E Upper Gantry Coordinates",
	"Unit F Upper Gantry Coordinates",
]
CONSUMABLES = [
	"Quant Strip",
	"Tip Box",
	"Reagent Cartridge",
	"Sample Rack",
	"Aux Heater",
	"Heater/Shaker",
	"Mag Separator",
	"Chiller",
	"Pre-Amp Thermocycler",
	"Lid Tray",
	"Tip Transfer Tray",
	"Assay Strip",
	"Tray",
	"DG8",
]

TRAYS = ['A', 'B', 'C', 'D']
COLUMS = [1,2,3,4,5,6,7,8,9,10,11,12]

class CoordinatesModel:
	""" Model for maintaining the coordinates for each unit
	"""
	def __init__(self, db_name, cursor, connection) -> None:
		# Setup the database connection
		self.db_name = db_name
		self.cursor = cursor
		self.connection = connection
		
	def create_table(self, table_name: str):
		""" Query for building a table
		 
		Parameters
		table_name : str
			Name of the table to be created
		"""
		# Make sure the table name is valid
		assert table_name in VALID_TABLE_NAMES
		# Set the query
		query = f"""CREATE TABLE IF NOT EXISTS '{table_name}'(
		ID INT PRIMARY KEY NOT NULL,
		CONSUMABLE TEXT NOT NULL,
		TRAY CHAR(1),
		COLUMN INT,
		X INT NOT NULL,
		Y INT NOT NULL,
		Z1 INT NOT NULL,
		Z2 INT NOT NULL,
		TIP INT
		);
		"""
		self.cursor.execute(query)

	def drop_table(self, table_name: str) -> None:
		""" Query for dropping a table
	
		Parameters
		table_name : str
			Table to be dropped
		"""
		# Make sure the table is valid
		assert table_name in VALID_TABLE_NAMES
		# Set the query
		query = f"""DROP TABLE '{table_name}'
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def select(self, table_name: str, consumable: str = None, tray: str = None, column: int = None) -> list:
		""" Query for selecting from the table

		Parameters
		table_name : str
			Table name to query
		consumable : str
			Consumable of interest
		tray : str
			tray of interest
		column : int
			column of interest
		"""	
		# Make sure the table is valid
		assert table_name in VALID_TABLE_NAMES
		# Set the query
		if consumable == None and tray == None and column == None:
			query = f"SELECT * FROM '{table_name}'"
			self.cursor.execute(query)
			return self.cursor.fetchall()
		if tray == '':
			query = f"""SELECT * FROM '{table_name}'
			WHERE CONSUMABLE = '{consumable}' AND COLUMN = {column};
			"""
			self.cursor.execute(query)
			return self.cursor.fetchall()
		if column == '':
			query = f"""SELECT * FROM '{table_name}'
			WHERE CONSUMABLE = '{consumable}' AND TRAY = '{tray}';
				"""
			self.cursor.execute(query)
			return self.cursor.fetchall()
		query = f"""SELECT * FROM '{table_name}'
		WHERE CONSUMABLE = '{consumable}' AND TRAY = '{tray}' AND COLUMN = {column};
		"""
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def insert(
		self,
		table_name: str,
		ID: int,
		consumable: str,
		tray: str,
		column: int,
		x: int,
		y: int,
		z1: int,
		z2: int,
		tip: int
	) -> None:
		""" Query for inserting a coordinate into the table
			
		Parameters
		----------
		table_name : str
			Table of interest
		consumable : str
			Consumable of interest
		tray : str
			Tray of interest
		column : int 
			Column of interest
		x : int
		y : int
		z1 : int
			Z-axis coordinate value
		z2 : int
			Drip plate (z2-axis) coordinate value
		tip : int
			Tip used to define the coordinate
		"""
		# Make sure the table is valid
		assert table_name in VALID_TABLE_NAMES
		# Set the query
		query = f"""INSERT INTO '{table_name}'
		(
		ID,
		CONSUMABLE,
		TRAY,
		COLUMN,
		X,
		Y,
		Z1,
		Z2,
		TIP
		)
		VALUES (
		{ID},
		'{consumable}',
		'{tray}',
		{column},
		{x},
		{y},
		{z1},
		{z2},
		{tip}
		);
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def delete(self, table_name: str, consumable: str, tray: str, column: int) -> None:
		query = f"""DELETE FROM '{table_name}'
		WHERE CONSUMABLE = '{consumable}' AND TRAY = '{tray}' AND COLUMN = {column};
		"""
		self.cursor.execute(query)
		self.communication.commit()

	def update(
		self,
		table_name: str,
		consumable: str,
		tray: str,
		column: int,
		x: int,
		y: int,
		z1: int,
		z2: int
	) -> None:
		ID = int(self.select(table_name, consumable, tray, column)[0][0])
		query = f"UPDATE '{table_name}' SET X = {x}, Y = {y}, Z1 = {z1}, Z2 = {z2} WHERE ID = {ID};"
		self.cursor.execute(query)
		self.connection.commit()

	def check_location_exists(self, table_name: str, consumable: str, tray: str, column: str) -> None:
		""" Check if a consumable is in the database
		"""
		if tray == '':
			query = f"""SELECT EXISTS (
			SELECT 1 FROM '{table_name}' WHERE CONSUMABLE = '{consumable}' AND COLUMN = {column}
			);
			"""
			self.cursor.execute(query)
			return self.cursor.fetchall()[0][0]
		if column == '':
			query = f"""SELECT EXISTS (
			SELECT 1 FROM '{table_name}' WHERE CONSUMABLE = '{consumable}' AND TRAY = '{tray}'
			);
			"""
			self.cursor.execute(query)
			return self.cursor.fetchall()[0][0]
		if (column == '' and tray == '') or (consumable == ''):
			return False
		query = f"""SELECT EXISTS (
		SELECT 1 FROM '{table_name}' WHERE CONSUMABLE = '{consumable}' AND TRAY = '{tray}' AND COLUMN = {column}
		);
		"""
		self.cursor.execute(query)
		#print(self.cursor.fetchall()[0])
		#print(self.cursor.fetchall()[0][0])
		return self.cursor.fetchall()[0][0]
