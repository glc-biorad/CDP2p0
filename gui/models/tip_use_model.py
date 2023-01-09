import sqlite3

TABLE_NAME = 'tip_use'

# Constants
TIP_TRAYS = [
	'A',
	'B',
	'C',
	'D',
	"Tip Transfer Tray",
]
TIP_STATES = ['new', 'used', 'empty', 'na']
TIP_SIZES = ['1000', '50', '200', '']

class TipUseModel:
	""" Model for maintaining the Tip Use data table
	"""
	def __init__(self, db_name, cursor, connection) -> None:
		# Setup the database connection
		self.db_name = db_name
		self.cursor = cursor
		self.connection = connection

	def create_table(self) -> None:
		""" Deals with creating the tip use table
		"""
		query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
		TRAY TEXT NOT NULL,
		STATE_1 TEXT NOT NULL,
		SIZE_1 INT,
		STATE_2 TEXT NOT NULL,
		SIZE_2 INT,
		STATE_3 TEXT NOT NULL,
		SIZE_3 INT,
		STATE_4 TEXT NOT NULL,
		SIZE_4 INT,
		STATE_5 TEXT NOT NULL,
		SIZE_5 INT,
		STATE_6 TEXT NOT NULL,
		SIZE_6 INT,
		STATE_7 TEXT NOT NULL,
		SIZE_7 INT,
		STATE_8 TEXT NOT NULL,
		SIZE_8 INT,
		STATE_9 TEXT NOT NULL,
		SIZE_9 INT,
		STATE_10 TEXT NOT NULL,
		SIZE_10 INT,
		STATE_11 TEXT NOT NULL,
		SIZE_11 INT,
		STATE_12 TEXT NOT NULL,
		SIZE_12 INT
		);
		"""
		self.cursor.execute(query)

	def drop_table(self) -> None:
		""" Deals with droping the table
		"""
		query = f"""DROP TABLE {TABLE_NAME}
		"""
		self.cursor.execute(query)

	def insert(
		self,
		tray: str,
		state_1: str,
		size_1: int,
		state_2: str,
		size_2: int,
		state_3: str,
		size_3: int,
		state_4: str,
		size_4: int,
		state_5: str,
		size_5: int,
		state_6: str,
		size_6: int,
		state_7: str,
		size_7: int,
		state_8: str,
		size_8: int,
		state_9: str,
		size_9: int,
		state_10: str,
		size_10: int,
		state_11: str,
		size_11: int,
		state_12: str,
		size_12: int
	) -> None:
		""" Deals with inserting a row into the table after creation
		
		Parameters
		----------
		tray : str
			Tray of interest
		state : str
			State of a column
		size : int
			Tip size in that column
		"""
		query = f"""INSERT INTO {TABLE_NAME}
		(
		TRAY,
		STATE_1,
		SIZE_1,
		STATE_2,
		SIZE_2,
		STATE_3,
		SIZE_3,
		STATE_4,
		SIZE_4,
		STATE_5,
		SIZE_5,
		STATE_6,
		SIZE_6,
		STATE_7,
		SIZE_7,
		STATE_8,
		SIZE_8,
		STATE_9,
		SIZE_9,
		STATE_10,
		SIZE_10,
		STATE_11,
		SIZE_11,
		STATE_12,
		SIZE_12
		)
		VALUES (
		'{tray}',
		'{state_1}',
		{size_1},
		'{state_2}',
		{size_2},
		'{state_3}',
		{size_3},
		'{state_4}',
		{size_4},
		'{state_5}',
		{size_5},
		'{state_6}',
		{size_6},
		'{state_7}',
		{size_7},
		'{state_8}',
		{size_8},
		'{state_9}',
		{size_9},
		'{state_10}',
		{size_10},
		'{state_11}',
		{size_11},
		'{state_12}',
		{size_12}
		);
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def update(
		self,
		tray : str,
		state_1: str,
		size_1: int,
		state_2: str,
		size_2: int,
		state_3: str,
		size_3: int,
		state_4: str,
		size_4: int,
		state_5: str,
		size_5: int,
		state_6: str,
		size_6: int,
		state_7: str,
		size_7: int,
		state_8: str,
		size_8: int,
		state_9: str,
		size_9: int,
		state_10: str,
		size_10: int,
		state_11: str,
		size_11: int,
		state_12: str,
		size_12: int
	) -> None:
		""" Deals with updating a row by the tray
		"""
		query = f"""UPDATE {TABLE_NAME}
		SET
		STATE_1 = '{state_1}',
		SIZE_1 = {size_1},
		STATE_2 = '{state_2}',
		SIZE_2 = {size_2},
		STATE_3 = '{state_3}',
		SIZE_3 = {size_3},
		STATE_4 = '{state4}',
		SIZE_4 = {size_4},
		STATE_5 = '{state_5}',
		SIZE_5 = {size_5},
		STATE_6 = '{state6}',
		SIZE_6 = {size_6},
		STATE_7 = '{state_7}',
		SIZE_7 = {size_7},
		STATE_8 = '{state_8}',
		SIZE_8 = {size_8},
		STATE_9 = '{state9}',
		SIZE_9 = {size_9},
		STATE_10 = '{state_10}',
		SIZE_10 = {size_10},
		STATE_11 = '{state_11}',
		SIZE_11 = {size_11},
		STATE_12 = '{state_12}',
		SIZE_12 = {size_12}
		WHERE TRAY = '{tray}';
		"""

	def select(self, tray: str = None) -> list:
		""" Deals with selection queries
		"""
		query = f"""SELECT * FROM {TABLE_NAME}
		"""	
		if tray != None:
			query = query + f" WHERE TRAY = '{tray}'"
		self.cursor.execute(query)
		return self.cursor.fetchall()
