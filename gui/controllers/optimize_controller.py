import threading

# Import the model and view for this controller
from gui.models.optimize_model import OptimizeModel
from gui.views.optimize_frame import OptimizeFrame

# Import the coordinates model
from gui.models.coordinates_model import CoordinatesModel

# Import the upper gantry api
from api.upper_gantry.upper_gantry import UpperGantry

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

		# Setup the coordinates model
		self.coordinates_model = CoordinatesModel(self.model.db_name, self.model.cursor, self.model.connection)

		# Initialize the upper gantry
		self.upper_gantry = UpperGantry()

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
		self.view.bind_button_drip_plate(self.drip_plate)
		self.view.trace_optionmenu_consumable(self.callback_consumable)

	def print(self, event=None) -> None:
		"""Deals with the on click event for the print button
		"""
		# Determine the position (coordinate in database and current position)
		# Get the current position
		position = self.upper_gantry.get_position()
		print(f"Position: {position}")
		if self.view.consumable_sv.get() != '':
			# Get the coordinate for this location from the coordinates model table
			consumable = self.view.consumable_sv.get()
			tray = self.view.tray_sv.get()
			column = int(self.view.column_sv.get())
			coordinate = self.coordinates_model.select("Unit A Upper Gantry Coordinates", consumable, tray, column)
			x = coordinate[0][4]
			y = coordinate[0][5]
			z1 = coordinate[0][6]
			z2 = coordinate[0][7]
			print(f"Coordinate for {consumable} {tray} {column}: [{x}, {y}, {z1}, {z2}]")

	def home(self, event=None) -> None:
		""" Deals with the on click event for the home button
		"""
		# Home the pipettor
		print('Home')

	def home_z(self, event=None) -> None:
		""" Deals with the on click event for the home z button
		"""
		# Home the pipettor along the z axis
		print('Home Z')

	def home_y(self, event=None) -> None:
		""" Deals with the on click event for the home y button
		"""
		# Home the pipettor along the y axis
		print('Home Y')

	def home_x(self, event=None) -> None:
		""" Deals with the on click event for the home x button
		"""
		# Home the pipettor along the x axis
		print('Home X')

	def move(self, event=None) -> None:
		""" Deals with the on click event for the move button
		"""
		# Get the data
		consumable = self.view.optionmenu_consumable.get()
		tray = self.view.optionmenu_tray.get()
		column = self.view.optionmenu_column.get()
		# Move the pipettor
		print(f"Move to {consumable} tray {tray} column {column}")

	def update(self, event=None) -> None:
		""" Deals with the on click event for the update button
		"""
		# Update the model for the coordinates
		print('Update')

	def drip_plate(self, event=None) -> None:
		"""Deals with the on click event for the drip plate button
		"""
		# Toggle the drip plate
		print("Drip Plate")

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
