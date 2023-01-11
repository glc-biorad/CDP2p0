import os
import threading
import tkinter as tk

# Import the model and view for this controller
from gui.models.optimize_model import OptimizeModel
from gui.util.coordinates_list_to_csv import coordinates_list_to_csv
from gui.views.optimize_frame import OptimizeFrame

# Import the coordinates model
from gui.models.coordinates_model import CoordinatesModel

# Import the upper gantry api
try:
	from api.upper_gantry.upper_gantry import UpperGantry
except:
	print("Cannot import upper gantry to the optimize controller")

# Import utilities
from gui.util.coordinates_list_to_csv import coordinates_list_to_csv

# Constants
NO_TRAY_CONSUMABLES = ["Pre-Amp Thermocycler", "Assay Strip", "Heater/Shaker", "Mag Separator", "Chiller", "Tip Transfer Tray"]
NO_COLUMN_CONSUMABLES = ["Aux Heater", "Sample Rack", "Quant Strip"]
TWELVE_COLUMN_CONSUMABLES = ["Pre-Amp Thermocycler", "Mag Separator", "Chiller", "Reagent Cartridge", "DG8"]
NINE_COLUMN_CONSUMABLES = ["Tip Transfer Tray"]
EIGHT_COLUMN_CONSUMABLES = ["Assay Strip", "Tip Tray"]
FOUR_COLUMN_CONSUMABLES = ["Heater/Shaker"]
THREE_COLUMN_CONSUMABLES = [""]
SPECIAL_CONSUMABLES = ["DG8", "Chip"]

class OptimizeController:
	"""System for passing data from the view to the model
	"""
	def __init__(
		self,
		model: OptimizeModel,
		view: OptimizeFrame
	) -> None:
		# Set the model and view for the controller
		self.model = model
		self.view = view
		self.unit = self.model.db_name.replace('.db','')[-1]

		# Setup the coordinates model
		self.coordinates_model = CoordinatesModel(self.model.db_name, self.model.cursor, self.model.connection)

		# Initialize the upper gantry
		try:
			self.upper_gantry = UpperGantry()
		except:
			print("No upper gantry control for optimize controller")
			pass

		# Get the unit
		print("Optimize Frame needs to know what unit we are using! (all set to A hardcoded for now)")

	def setup_bindings(self):
		# Setup the bindings between the view and the controller
		self.view.bind_button_print(self.print)
		self.view.bind_button_home_z(self.home_z)
		self.view.bind_button_home_y(self.home_y)
		self.view.bind_button_home_x(self.home_x)
		self.view.bind_button_home(self.home)
		self.view.bind_button_update(self.update)
		self.view.bind_button_move(self.move)
		self.view.bind_button_drip_plate(self.drip_plate)
		self.view.trace_optionmenu_consumable(self.callback_consumable)
		self.view.trace_entry_x(self.callback_x)

	def print(self, event=None) -> None:
		"""Deals with the on click event for the print button
		"""
		# Determine the position (coordinate in database and current position)
		# Get the current position
		try:
			position = self.upper_gantry.get_position()
			print(f"Position: {position}")
		except:
			position = ['?','?','?','?']
			print("Upper Gantry not connected so no position for the pipettor at this moment")
		if self.view.consumable_sv.get() != '':
			# Get the coordinate for this location from the coordinates model table
			consumable = self.view.consumable_sv.get()
			tray = self.view.tray_sv.get()
			column = int(self.view.column_sv.get())
			coordinate = self.coordinates_model.select(f"Unit {self.unit} Upper Gantry Coordinates", consumable, tray, column)
			x = coordinate[0][4]
			y = coordinate[0][5]
			z1 = coordinate[0][6]
			z2 = coordinate[0][7]
			print(f"Coordinate for {consumable} {tray} {column}: [{x}, {y}, {z1}, {z2}]")
			if tray == '':
				message = f"""Pipettor Position: 
{position}

{consumable} Column {column}: 
[{x}, {y}, {z1}, {z2}]
				"""
			elif column == '':
				message = f"""Pipettor Position: 
{position}

{consumable} Tray {tray}: 
[{x}, {y}, {z1}, {z2}]
				"""
			else:
				message = f"""Pipettor Position: 
{position}

{consumable} Tray {tray} Column {column}: 
[{x}, {y}, {z1}, {z2}]
				"""
		else:
			message = f"""Pipettor Position: 
{position}
			"""
		# Show a popup to the user
		tk.messagebox.showinfo(
			title="Pipettor Position and Coordinate for Consumable",
			message = message
		)

	def home(self, event=None) -> None:
		""" Deals with the on click event for the home button
		"""
		# Home the pipettor
		thread = threading.Thread(target=self.thread_home)
		thread.start()

	def thread_home(self):
		self.upper_gantry.home_pipettor()

	def home_z(self, event=None) -> None:
		""" Deals with the on click event for the home z button
		"""
		# Home the pipettor along the z axis
		thread = threading.Thread(target=self.thread_home_z)
		thread.start()

	def thread_home_z(self):
		self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 3)

	def home_y(self, event=None) -> None:
		""" Deals with the on click event for the home y button
		"""
		# Home the pipettor along the y axis
		thread = threading.Thread(target=self.thread_home_y)
		thread.start()

	def thread_home_y(self):
		self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 2)

	def home_x(self, event=None) -> None:
		""" Deals with the on click event for the home x button
		"""
		# Home the pipettor along the x axis
		thread = threading.Thread(target=self.thread_home_x)
		thread.start()

	def thread_home_x(self):
		self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 1)

	def move(self, event=None) -> None:
		""" Deals with the on click event for the move button
		"""
		# Get the data
		consumable = self.view.optionmenu_consumable.get()
		tray = self.view.optionmenu_tray.get()
		column = self.view.optionmenu_column.get()
		# Move the pipettor
		# Get the consumable, tray, and column to move to
		consumable = self.view.consumable_sv.get()
		tray = self.view.tray_sv.get()
		column = self.view.column_sv.get()
		tip = self.view.tip_sv.get()
		if tip == '':
			tip = None
		else:
			tip = int(tip)
			print(tip)
		use_z = self.view.use_z_iv.get()
		slow_z = self.view.slow_z_iv.get()
		use_drip_plate=False
		coordinate = self.coordinates_model.select(f"Unit {self.unit} Upper Gantry Coordinates", consumable, tray, column)
		x = coordinate[0][4]
		y = coordinate[0][5]
		z = coordinate[0][6]
		drip_plate = coordinate[0][7]
		# Start the read
		thread = threading.Thread(target=self.upper_gantry.move, args=(x, y, z, drip_plate, use_z, slow_z, use_drip_plate, tip, ))
		thread.start()


	def update(self, event=None) -> None:
		""" Deals with the on click event for the update button
		"""
		# Make sure that we are about to update an actual coordinate 
		consumable = self.view.consumable_sv.get()
		tray = self.view.tray_sv.get()
		column = self.view.column_sv.get()
		# Generate a warning message
		message = ''
		if self.coordinates_model.check_location_exists(f'Unit {self.unit} Upper Gantry Coordinates', consumable, tray, column):
			if tray != '' and column != '':
				message = f"You are about to update the coordinate for {consumable} Tray {tray} Column {column}, proceed?"
			elif tray == '' and column != '':
				message = f"You are about to update the coordinate for {consumable} Column {column}, proceed?"
			elif tray != '' and column == '':
				message = f"You are about to update the coordinate for {consumable} Tray {tray}, proceed?"
			file_name = r'AppData\unit_{0}_upper_gantry_coordinates'.format(self.unit.upper())
			message = message + f"\n\nPre-update Coordinates will be backed up in {file_name}.bak \n Post-update will be in {file_name}.csv"
			# Create a messagebox warning
			if tk.messagebox.askokcancel(title="Coordinate Update", message=message):
				# Get the X, Y, Z, and Drip Plate coordinates from the current position of the pipettor
				x, y, z1, z2 = self.upper_gantry.get_position()
				# Get the table name for this unit
				table_name = f"Unit {self.unit} Upper Gantry Coordinates"
				# Update the model
				self.coordinates_model.update(table_name, consumable, tray, column, x, y, z1, z2)
				# Overwrite the units coordinates csv file 
				cmd = r"ren {0}.csv {1}.bak".format(file_name, file_name[8:])
				os.system(cmd)
				table_name = f"Unit {self.unit.upper()} Upper Gantry Coordinates"
				coordinates = self.coordinates_model.select(table_name)
				coordinates_list_to_csv(coordinates, file_name)
			else:
				return

	def drip_plate(self, event=None) -> None:
		"""Deals with the on click event for the drip plate button
		"""
		# Toggle the drip plate
		thread = threading.Thread(target=self.thread_drip_plate)
		thread.start()

	def thread_drip_plate(self):
		z2 = self.upper_gantry.get_position_from_axis('Drip Plate')
		if z2 < 0:
			self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, 0, 2500000, True, True)
			self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 4)
		else:
			self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, -1198000, 2500000, False, True)

	def callback_consumable(self, *args) -> None:
		# Get the consumable
		consumable = self.view.consumable_sv.get()
		# Change the tray optionmenu options based on the consumable
		if consumable in NO_TRAY_CONSUMABLES:
			self.model.tray_sv.set('')
			self.view.optionmenu_tray.configure(values=('',))
		else:
			self.model.tray_sv.set('')
			self.view.optionmenu_tray.configure(values=('A', 'B', 'C', 'D',))
		# Change the column optionmenu options based on the consumable
		if consumable in NO_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('',))
		elif consumable in THREE_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('1','2','3',))
		elif consumable in FOUR_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('1','2','3','4',))
		elif consumable in EIGHT_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('1','2','3','4','5','6','7','8',))
		elif consumable in NINE_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('1','2','3','4','5','6','7','8','9',))
		elif consumable in TWELVE_COLUMN_CONSUMABLES:
			self.model.column_sv.set('')
			self.view.optionmenu_column.configure(values=('1','2','3','4','5','6','7','8','9','10','11','12',))


	def callback_x(self, *args) -> None:
		""" Deals with the callback on a change to entry x
		"""
		x = self.view.x_sv.get()
		print(x)
