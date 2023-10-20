
# Version: Test
import sqlite3

from tkinter import StringVar

TABLE_NAME = 'configure'

# Constants

class ConfigureModel:
	""" Model for the Configure Frame """
	def __init__(self, db_name, cursor, connection) -> None:
		# Setup the database connection
		self.db_name = db_name
		self.unit = db_name[-4]
		self.cursor = cursor
		self.connection = connection
		#try:
		#    self.drop_table()
		#except:
		#    pass
		self.create_table()

	def create_table(self) -> None:
        	""" Query for creating the Configure table 
        	This table allows up to 12 values, the point of 12 is because that is the most amount of data necessary for one particular thing on
        	the configure tab (tip box configuration), this table allows for all configuration data to be stored in one table and 
        	it can be looked up by the NAME.
        	"""
        	query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
        	ID INT NOT NULL,
        	NAME TEXT NOT NULL,
        	VAL1 TEXT,
        	VAL2 TEXT,
        	VAL3 TEXT,
        	VAL4 TEXT,
        	VAL5 TEXT,
        	VAL6 TEXT,
        	VAL7 TEXT,
        	VAL8 TEXT,
        	VAL9 TEXT,
        	VAL10 TEXT,
        	VAL11 TEXT,
        	VAL12 TEXT
        	);
        	"""
        	self.cursor.execute(query)

	def drop_table(self) -> None:
		""" Drops the table out of the database """
		query = f"DROP TABLE {TABLE_NAME}"
		self.cursor.execute(query)

	def select(self, ID: int = None, name: str = None, val1: str = None) -> list:
		""" Select query which should be used in 4 ways
		    1. Look up by ID (select(ID))
		    2. Look up by NAME and VAL1 (select(name, val1))
		    3. Look up by NAME (select(name))
		    4. Look up the entire table (select())
		"""
		if ID == None and name == None and val1 == None:
			query = f"SELECT * FROM {TABLE_NAME}"
		elif ID != None and (name == None and val1 == None):
			query = f"""SELECT * FROM {TABLE_NAME}
			WHERE ID = {ID}
			"""
		elif ID == None and (name != None and val1 != None):
			query = f"""SELECT * FROM {TABLE_NAME}
			WHERE NAME = '{name}' AND VAL1 = '{val1}'
			"""
		elif (ID == None and val1 == None) and name != None:
			query = f"""SELECT * FROM {TABLE_NAME}
			WHERE NAME = '{name}'
			"""
		self.cursor.execute(query)
		results = self.cursor.fetchall()
		return results

	def insert(self,
		ID: int,
		name: str,
		val1: str = None,
		val2: str = None,
		val3: str = None,
		val4: str = None,
		val5: str = None,
		val6: str = None,
		val7: str = None,
		val8: str = None,
		val9: str = None,
		val10: str = None,
		val11: str = None,
		val12: str = None
	) -> None:
		""" Insert query for the Configure Table """
		query = f"""INSERT INTO {TABLE_NAME}
		(
		ID,
		NAME,
		VAL1,
		VAL2,
		VAL3,
		VAL4,
		VAL5,
		VAL6,
		VAL7,
		VAL8,
		VAL9,
		VAL10,
		VAL11,
		VAL12
		)
		VALUES (
		{ID},
		'{name}',
		'{val1}',
		'{val2}',
		'{val3}',
		'{val4}',
		'{val5}',
		'{val6}',
		'{val7}',
		'{val8}',
		'{val9}',
		'{val10}',
		'{val11}',
		'{val12}'
		);
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def delete(self, ID: int) -> None:
		""" Query for deleting an item from the Configure Table """
		query = f"""DELETE FROM {TABLE_NAME}
		WHERE ID = {ID}
		"""
		self.cursor.execute(query)
		self.connection.commit()

	def update(self,
		ID: int,
		name: str = None,
		val1: str = None,
		val2: str = None,
		val3: str = None,
		val4: str = None,
		val5: str = None,
		val6: str = None,
		val7: str = None,
		val8: str = None,
		val9: str = None,
		val10: str = None,
		val11: str = None,
		val12: str = None
	) -> None:
		""" Update query for the Configure Table """
		query = f"UPDATE {TABLE_NAME} SET"
		if name != None:
			query = query + f" NAME = '{name}',"
		elif val1 != None:
			query = query + f" VAL1 = '{val1}',"
		elif val2 != None:
			query = query + f" VAL2 = '{val2}',"
		elif val3 != None:
			query = query + f" VAL3 = '{val3}',"
		elif val4 != None:
			query = query + f" VAL4 = '{val4}',"
		elif val5 != None:
			query = query + f" VAL5 = '{val5}',"
		elif val6 != None:
			query = query + f" VAL6 = '{val6}',"
		elif val7 != None:
			query = query + f" VAL7 = '{val7}',"
		elif val8 != None:
			query = query + f" VAL8 = '{val8}',"
		elif val9 != None:
			query = query + f" VAL9 = '{val9}',"
		elif val10 != None:
			query = query + f" VAL10 = '{val10}',"
		elif val11 != None:
			query = query + f" VAL11 = '{val11}',"
		elif val12 != None:
			query = query + f" VAL12 = '{val12}',"
		query = query[:-1]
		query = query + f" WHERE ID = {ID};"
		self.cursor.execute(query)
		self.connection.commit()
