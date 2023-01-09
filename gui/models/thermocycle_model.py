import sqlite3

import tkinter as tk

TABLE_NAME = 'thermocycle'

class ThermocycleModel:
	def __init__(self, db_name, cursor, connection) -> None:
		self.db_name = db_name
		self.cursor = cursor
		self.connection = connection
		self.create_table()
		#self.insert(1,'A',40,84,50,84,3,40,30,1,1,1)
		#self.insert(2,'B',40,84,50,84,3,40,30,1,1,1)
		#self.insert(3,'C',40,84,50,84,3,40,30,0,1,1)
		#self.insert(4,'D',40,84,50,84,3,40,30,1,1,1)
		
		# Default String and Int Variables
		self.thermocycler_sv = tk.StringVar()
		self.cycles_sv = tk.StringVar()
		self.use_a_iv = tk.IntVar()
		self.use_b_iv = tk.IntVar()
		self.use_c_iv = tk.IntVar()
		self.use_d_iv = tk.IntVar()
		self.first_denature_temperature_sv = tk.StringVar()
		self.anneal_temperature_sv = tk.StringVar()
		self.second_denature_temperature_sv = tk.StringVar()
		self.first_denature_time_sv = tk.StringVar()
		self.anneal_time_sv = tk.StringVar()
		self.second_denature_time_sv = tk.StringVar()
		self.clamp_a_iv = tk.IntVar()
		self.clamp_b_iv = tk.IntVar()
		self.clamp_c_iv = tk.IntVar()
		self.clamp_d_iv = tk.IntVar()

	def setup_defaults(self, ID: int = 1) -> None:
		"""
		Breaks the MVC since the controller should be doing this type of thing
		"""
		defaults = self.select(ID)
		self.thermocycler_sv.set(str(defaults['thermocycler']))
		self.cycles_sv.set(str(defaults['cycles']))
		self.use_a_iv.set(int(self.select(1)['use']))
		self.use_b_iv.set(int(self.select(2)['use']))
		self.use_c_iv.set(int(self.select(3)['use']))
		self.use_d_iv.set(int(self.select(4)['use']))
		self.first_denature_temperature_sv.set(str(defaults['first_denature_temperature']))
		self.anneal_temperature_sv.set(str(defaults['anneal_temperature']))
		self.second_denature_temperature_sv.set(str(defaults['second_denature_temperature']))
		self.first_denature_time_sv.set(str(defaults['first_denature_time']))
		self.anneal_time_sv.set(str(defaults['anneal_time']))
		self.second_denature_time_sv.set(str(defaults['second_denature_time']))

	def create_table(self):
		query = f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
		ID INT PRIMARY KEY NOT NULL,
		THERMOCYCLER CHAR(1) NOT NULL,
		CYCLES INT NOT NULL,
		FIRST_DENATURE_TEMPERATURE INT NOT NULL,
		ANNEAL_TEMPERATURE INT NOT NULL,
		SECOND_DENATURE_TEMPERATURE INT NOT NULL,
		FIRST_DENATURE_TIME INT NOT NULL,
		ANNEAL_TIME INT NOT NULL,
		SECOND_DENATURE_TIME INT NOT NULL,
		USE INT NOT NULL,
		CLAMP INT NOT NULL,
		TRAY INT NOT NULL
		);
		"""
		self.cursor.execute(query)

	def select(self, ID: int) -> dict:
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Generate the select query based on the ID
		query = f"SELECT * FROM {TABLE_NAME} WHERE ID = {ID};"
		# Execute the query
		self.cursor.execute(query)
		# Get the array
		try:
			arr = self.cursor.fetchall()[0]
		except:
			self.insert(1,'A',40,84,50,84,3,40,30,1,1,1)
			self.insert(2,'B',40,84,50,84,3,40,30,1,1,1)
			self.insert(3,'C',40,84,50,84,3,40,30,0,1,1)
			self.insert(4,'D',40,84,50,84,3,40,30,1,1,1)
			arr = self.cursor.fetchall()[0]
		# Convert to a dictionary to return
		return {
			'ID': int(arr[0]),
			'thermocycler': str(arr[1]),
			'cycles': int(arr[2]),
			'first_denature_temperature': int(arr[3]),
			'anneal_temperature': int(arr[4]),
			'second_denature_temperature': int(arr[5]),
			'first_denature_time': int(arr[6]),
			'anneal_time': int(arr[7]),
			'second_denature_time': int(arr[8]),
			'use': int(arr[9]),
			'clamp': int(arr[10]),
			'tray': int(arr[11]),
		}

	def update(
		self,
		ID: int,
		thermocycler: str = None,
		cycles: int = None,
		first_denature_temperature: int = None,
		anneal_temperature: int = None,
		second_denature_temperature: int = None,
		first_denature_time: int = None,
		anneal_time: int = None,
		second_denature_time: int = None,
		use: int = None,
		clamp: int = None,
		tray: int = None,
	) -> None:
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Create the query based on the kwargs provided
		partial_query = ''
		if thermocycler != None:
			partial_query = partial_query + f"thermocycler = '{thermocycler}',"
		if cycles != None:
			partial_query = partial_query + f"cycles = {cycles},"
		if first_denature_temperature != None:
			partial_query = partial_query + f"first_denature_temperature = {first_denature_temperature},"
		if anneal_temperature != None:
			partial_query = partial_query + f"anneal_temperature = {anneal_temperature},"
		if second_denature_temperature != None:
			partial_query = partial_query + f"second_denature_temperature = {second_denature_temperature},"
		if first_denature_time != None:
			partial_query = partial_query + f"first_denature_time = {first_denature_time},"
		if anneal_time != None:
			partial_query = partial_query + f"anneal_time = {anneal_time},"
		if second_denature_time != None:
			partial_query = partial_query + f"second_denature_time = {second_denature_time},"
		if use != None:
			partial_query = partial_query + f"use = {use},"
		if clamp != None:
			partial_query = partial_query + f"clamp = {clamp},"
		if tray != None:
			partial_query = partial_query + f"tray = {tray},"
		# Finish the query
		if partial_query[-1] == ',':
			partial_query = partial_query[:-1]
		query = f"""UPDATE {TABLE_NAME}
		SET {partial_query}
		WHERE ID = {ID};
		"""
		# Execute the query
		self.cursor.execute(query)
		# Commit to the database
		self.connection.commit()	

	def insert(
		self,
		ID: int,
		thermocycler: str,
		cycles: int,
		first_denature_temperature: int,
		anneal_temperature: int,
		second_denature_temperature: int,
		first_denature_time: int,
		anneal_time: int,
		second_denature_time: int,
		use: int,
		clamp: int,
		tray: int,
	) -> None:
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		query = f"""INSERT INTO {TABLE_NAME} 
		(
		ID,
		THERMOCYCLER,
		CYCLES,
		FIRST_DENATURE_TEMPERATURE,
		ANNEAL_TEMPERATURE,
		SECOND_DENATURE_TEMPERATURE,
		FIRST_DENATURE_TIME,
		ANNEAL_TIME,
		SECOND_DENATURE_TIME,
		USE,
		CLAMP,
		TRAY
		)
		VALUES (
		{ID},
		'{thermocycler}',
		{cycles},
		{first_denature_temperature},
		{anneal_temperature},
		{second_denature_temperature},
		{first_denature_time},
		{anneal_time},
		{second_denature_time},
		{use},
		{clamp},
		{tray}
		);
		"""
		self.cursor.execute(query)
		self.connection.commit()

