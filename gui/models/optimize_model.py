import sqlite3

from tkinter import StringVar, IntVar

TABLE_NAME = 'optimize'

# Constants
DEFAULTS = {
	'slow_z': 1,
	'use_z': 1,
	'x': '5000',
	'y': '50000',
	'z': '20000',
}

class OptimizeModel:
	""" Model for the Optimize View
	"""
	def __init__(self, db_name, cursor, connection) -> None:
		# Setup the database connection
		self.unit = db_name[-4]
		self.db_name = db_name
		self.cursor = cursor
		self.connection = connection

		# Initialize the checkboxes and entries
		self.use_z_iv = IntVar()
		self.slow_z_iv = IntVar()
		self.x_sv = StringVar()
		self.y_sv = StringVar()
		self.z_sv = StringVar()
		self.consumable_sv = StringVar()
		self.tray_sv = StringVar()
		self.column_sv = StringVar()

	def get_consumable_sv(self) -> StringVar:
		""" Returns the consumable StringVar
		"""
		return self.consumable_sv

	def get_tray_sv(self) -> StringVar:
		""" Returns the tray StringVar
		"""
		return self.tray_sv

	def get_column_sv(self) -> StringVar:
		""" Returns the column StringVar
		"""
		return self.column_sv
