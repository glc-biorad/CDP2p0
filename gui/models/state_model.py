
# Version: Test
import sqlite3

TABLE_NAME = 'state'

# Constants
TIP_TRAYS = [
	'A',
	'B', 
	'C', 
	'D',
	"Tip Transfer Tray",
]
TIP_STATES = ['new', 'used', 'na']
TIP_SIZES = ['1000', '50', '200', '']

class StateModel:
	""" Model for maintaining the current state of tip size on the pipettor head
	"""
	def __init__(self, db_name, cursor, connection) -> None:
		# Setup the datebase connection
		self.db_name = db_name
		self.cursor = cursor
		self.connection = connection

	def create_table(self) -> None:
		""" Deals with creating the state table
		"""
		query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
		ID INT PRIMARY KEY NOT NULL,
		TIP TEXT NOT NULL,
		VOLUME INT NOT NULL,
		MODE TEXT NOT NULL
		);
		"""
		self.cursor.execute(query)

	def drop_table(self) -> None:
		""" Deals with dropping the table
		"""
		query = f"""DROP TABLE {TABLE_NAME}
		"""
		self.cursor.execute(query)

	def insert(self, tip: str, volume: int, mode: str) -> None:
		""" Deals with inserting into the table	
		
		Parameters
		tip : str
			Tip size on the pipettor head
		volume : int
			Volume in the tips of the pipettor head
		mode : str
			Mode describes the action (pickup, eject, aspirate dispense, mix)
		"""
		# Get the ID
		if self.select() == []:
			ID = 0
		else:
			ID = self.select()[-1][0] + 1
		query = f"""INSERT INTO {TABLE_NAME}
		(
		ID,
		TIP,
		VOLUME,
		MODE
		)
		VALUES (
		{ID},
		'{tip}',
		{volume},
		'{mode}'
		);
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def update(self, ID: int, tip: str, volume: int, mode: str) -> None:
		""" Deals with updating the table by state id
		"""
		query = f"""UPDATE {TABLE_NAME}
		SET 
		TIP = '{tip}',
		VOLUME = {volume},
		MODE = '{mode}'
		WHERE ID = {ID};
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def select(self, ID: int = None) -> list:
		""" Deals with selection queries
		"""
		query = f"""SELECT * FROM {TABLE_NAME}
		"""
		if ID != None:
			query = query + f" WHERE ID = {ID}"
		self.cursor.execute(query)
		return self.cursor.fetchall()
