import os
import time
import sqlite3
import threading
from tkinter import IntVar, StringVar
import tkinter as tk
import customtkinter as ctk

# Import log utilities
from api.util.log import Log

from gui.util.browse_files import browse_files 
from gui.util.next_action_allowed import next_action_allowed

# Import the model and view for this controller
from gui.models.build_protocol_model import BuildProtocolModel
from gui.views.build_protocol_frame import BuildProtocolFrame

# Import the state model to keep track of tips and volumes
from gui.models.state_model import StateModel

# Import the coordinates model
from gui.models.coordinates_model import CoordinatesModel

# Import the upper gantry api
try:
	from api.upper_gantry.upper_gantry import UpperGantry
except:
	print("Couldn't import upper gantry for BuildProtocolCOntroller")

# Import the reader api
try:
	from api.reader.reader import Reader
except Exception as e:
	print("Couldn't import reader for BuildProtocolController")

# Import the Meerstetter API
try:
	from api.reader.meerstetter.meerstetter import Meerstetter
except Exception as e:
	print(e)
	print("Couldn't import Meerstetter for the BuildProtocolController")

# Import the utilities needed
from api.util.utils import delay
from gui.util.insert_at_selected_row import insert_at_selected_row

# Constants
INITIAL_PROTOCOL_FILENAME = 'protocol.txt'
INITIAL_EXTRACTION_FILENAME = 'extraction.txt'
INITIAL_TRANSFER_PLASMA_FILENAME = 'transfer_plasma.txt'
NO_TRAY_CONSUMABLES = ["Pre-Amp Thermocycler", "Heater/Shaker", "Mag Separator", "Chiller", "Tip Transfer Tray"]
NO_COLUMN_CONSUMABLES = ["Aux Heater", "Sample Rack", "Quant Strip"]
MAIN_ACTION_KEY_WORDS = [
	'Eject',
	'Pickup',
	'Tip-press',
	'Move',
	'Aspirate',
	'Dispense',
	'Mix',
	'Delay',
	'Home',
	'Generate',
	'Transfer',
	'Binding',
	'Pooling',
	'Wash',
	'Pre-Elution',
	'Elution',
	'Extraction',
	'Enrichment',
	'Pre-Amp',
	'Assay',
	'Disengage',
	'Engage',
	'Shake',
	'Thermocycle',
	'Thermocycle:',
	'Close',
	'Open',
	'Lower',
	'Raise',
	'Change',
	'Comment:',
	'Pause',
	'Suction',
	'Extend',
	'LLD',
	'Light',
	'Load',
]
TOPLEVEL_CYCLE_WIDTH = 970
TOPLEVEL_CYCLE_HEIGHT = 210
TOPLEVEL_LABEL_CYCLE_POSX = 40
TOPLEVEL_LABEL_CYCLE_POSY = 10
TOPLEVEL_LABEL_DENATURE_POSX = 170
TOPLEVEL_LABEL_DENATURE_POSY = 10
TOPLEVEL_LABEL_ANNEAL_POSX = 440
TOPLEVEL_LABEL_ANNEAL_POSY = 10
TOPLEVEL_LABEL_EXTENSION_POSX = 710
TOPLEVEL_LABEL_EXTENSION_POSY = 10
TOPLEVEL_LABEL_USE_POSX = 930
TOPLEVEL_LABEL_USE_POSY = 10
TOPLEVEL_LABEL_THERMOCYCLER_A_POSX = 10
TOPLEVEL_LABEL_THERMOCYCLER_A_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_POSX = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_POSX = 120
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_A_DENATURE_POSX = 175
TOPLEVEL_LABEL_C_FOR_A_DENATURE_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_POSX = 220
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_POSX = 280
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_POSY = 40
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_POSX = 390
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_A_ANNEAL_POSX = 445
TOPLEVEL_LABEL_C_FOR_A_ANNEAL_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_POSX = 490
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_POSX = 550
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_POSY = 40
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_POSX = 660
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_A_EXTENSION_POSX = 715
TOPLEVEL_LABEL_C_FOR_A_EXTENSION_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_POSX = 760
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_POSY = 40
TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_POSX = 820
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_POSY = 40
TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_WIDTH = 50
TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_POSX = 935
TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_POSY = 42
TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_WIDTH = 50
TOPLEVEL_LABEL_THERMOCYCLER_B_POSX = 10
TOPLEVEL_LABEL_THERMOCYCLER_B_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_POSX = 40
TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_POSX = 120
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_B_DENATURE_POSX = 175
TOPLEVEL_LABEL_C_FOR_B_DENATURE_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_POSX = 220
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_POSX = 280
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_POSY = 70
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_POSX = 390
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_B_ANNEAL_POSX = 445
TOPLEVEL_LABEL_C_FOR_B_ANNEAL_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_POSX = 490
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_POSX = 550
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_POSY = 70
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_POSX = 660
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_B_EXTENSION_POSX = 715
TOPLEVEL_LABEL_C_FOR_B_EXTENSION_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_POSX = 760
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_POSY = 70
TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_POSX = 820
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_POSY = 70
TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_WIDTH = 50
TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_POSX = 935
TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_POSY = 72
TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_WIDTH = 50
TOPLEVEL_LABEL_THERMOCYCLER_C_POSX = 10
TOPLEVEL_LABEL_THERMOCYCLER_C_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_POSX = 40
TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_POSX = 120
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_C_DENATURE_POSX = 175
TOPLEVEL_LABEL_C_FOR_C_DENATURE_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_POSX = 220
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_POSX = 280
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_POSY = 100
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_POSX = 390
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_C_ANNEAL_POSX = 445
TOPLEVEL_LABEL_C_FOR_C_ANNEAL_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_POSX = 490
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_POSX = 550
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_POSY = 100
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_POSX = 660
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_WIDTH = 50
TOPLEVEL_LABEL_C_FOR_C_EXTENSION_POSX = 715
TOPLEVEL_LABEL_C_FOR_C_EXTENSION_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_POSX = 760
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_POSY = 100
TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_POSX = 820
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_POSY = 100
TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_WIDTH = 50
TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_POSX = 935
TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_POSY = 102
TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_WIDTH = 50
TOPLEVEL_LABEL_THERMOCYCLER_D_POSX = 10
TOPLEVEL_LABEL_THERMOCYCLER_D_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_POSX = 40
TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_POSX = 120
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_WIDTH = 50
TOPLEVEL_LABEL_D_FOR_D_DENATURE_POSX = 175
TOPLEVEL_LABEL_D_FOR_D_DENATURE_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_POSX = 220
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_POSX = 280
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_POSY = 130
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_POSX = 390
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_WIDTH = 50
TOPLEVEL_LABEL_D_FOR_D_ANNEAL_POSX = 445
TOPLEVEL_LABEL_D_FOR_D_ANNEAL_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_POSX = 490
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_POSX = 550
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_POSY = 130
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_WIDTH = 50
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_POSX = 660
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_WIDTH = 50
TOPLEVEL_LABEL_D_FOR_D_EXTENSION_POSX = 715
TOPLEVEL_LABEL_D_FOR_D_EXTENSION_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_POSX = 760
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_POSY = 130
TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_WIDTH = 50
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_POSX = 820
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_POSY = 130
TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_WIDTH = 50
TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_POSX = 935
TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_POSY = 132
TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_WIDTH = 50
TOPLEVEL_BUTTON_CYCLE_ADD_POSX = 840
TOPLEVEL_BUTTON_CYCLE_ADD_POSY = 160
TOPLEVEL_BUTTON_CYCLE_ADD_WIDTH = 100

TOPLEVEL_PRE_AMP_WIDTH = 400
TOPLEVEL_PRE_AMP_HEIGHT = 270
TOPLEVEL_LABEL_FIRST_DENATURE_TEMP_POSX = 35
TOPLEVEL_LABEL_FIRST_DENATURE_TEMP_POSY = 10
TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_POSX = 280
TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_POSY = 10
TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_WIDTH = 100
TOPLEVEL_LABEL_FIRST_DENATURE_TIME_POSX = 75
TOPLEVEL_LABEL_FIRST_DENATURE_TIME_POSY = 40
TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_POSX = 280
TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_POSY = 40
TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_WIDTH = 100
TOPLEVEL_LABEL_CYCLES_POSX = 210
TOPLEVEL_LABEL_CYCLES_POSY = 70
TOPLEVEL_ENTRY_CYCLES_POSX = 280
TOPLEVEL_ENTRY_CYCLES_POSY = 70
TOPLEVEL_ENTRY_CYCLES_WIDTH = 100
TOPLEVEL_LABEL_ANNEAL_TEMP_POSX = 90
TOPLEVEL_LABEL_ANNEAL_TEMP_POSY = 100
TOPLEVEL_ENTRY_ANNEAL_TEMP_POSX = 280 
TOPLEVEL_ENTRY_ANNEAL_TEMP_POSY = 100
TOPLEVEL_ENTRY_ANNEAL_TEMP_WIDTH = 100
TOPLEVEL_LABEL_ANNEAL_TIME_POSX = 130
TOPLEVEL_LABEL_ANNEAL_TIME_POSY = 130
TOPLEVEL_ENTRY_ANNEAL_TIME_POSX = 280
TOPLEVEL_ENTRY_ANNEAL_TIME_POSY = 130
TOPLEVEL_ENTRY_ANNEAL_TIME_WIDTH = 100
TOPLEVEL_LABEL_SECOND_DENATURE_TEMP_POSX = 15
TOPLEVEL_LABEL_SECOND_DENATURE_TEMP_POSY = 160
TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_POSX = 280
TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_POSY = 160
TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_WIDTH = 100
TOPLEVEL_LABEL_SECOND_DENATURE_TIME_POSX = 45
TOPLEVEL_LABEL_SECOND_DENATURE_TIME_POSY = 190
TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_POSX = 280
TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_POSY = 190
TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_WIDTH = 100
TOPLEVEL_BUTTON_ADD_PRE_AMP_POSX = 280
TOPLEVEL_BUTTON_ADD_PRE_AMP_POSY = 230
TOPLEVEL_BUTTON_ADD_PRE_AMP_WIDTH = 100
BUTTON_ADD_COLOR = '#10adfe'
FONT = "Sergio UI"

HEATER_ADDRESSES = {
	'A': 1,
	'B': 2,
	'C': 3,
	'D': 4,
	'Pre-Amp': 9,
}

ADDRESSES = {
	'A': 8,
	'B': 9,
	'C': 10,
	'D': 11,
	'AB': 6,
	'CD': 7,
}

class BuildProtocolController:
	"""System for passing data from the Build Protocol Frame view to the Build Protocol Model
	"""
	def __init__(
			self, 
			model: BuildProtocolModel,
			view: BuildProtocolFrame
		) -> None:
		# Set the model and view for the controller
		self.model = model
		self.view = view
		self.db_name = self.model.db_name
		self.unit = self.db_name[-4]

		# Initialize the Coordinates Model
		self.coordinates_model = CoordinatesModel(self.model.db_name, self.model.cursor, self.model.connection)

		# Get the state model
		self.state = StateModel(self.model.db_name, self.model.cursor, self.model.connection)

		# Initialize the upper gantry
		try:
			self.upper_gantry = UpperGantry()
			# Check if the pipettor connected
			if self.upper_gantry.get_pipettor() == None:
				tk.messagebox.showwarning(title="Seyonic Pipettor Connection Issue", message=f"Seyonic pipettor functionality will not be available until the Seyonic pipettor networking connection is fixed and the GUI is relaunched.")
		except Exception as e:
			print(e)
			tk.messagebox.showwarning(title="Upper Gantry Connection Issue", message=f"Warning: {e}")
			print("No Upper Gantry for BuildProtocolController")
			self.upper_gantry = None

		# Initialize the reader
		try:
			self.reader = Reader()
		except Exception as e:
			print(e)
			tk.messagebox.showwarning(title="Reader Connection Issue", message=f"Warning: {e}")
			print("No Reader for BuildProtocolController")
			self.reader = None
	
		# Variable for keeping track of the volume in the pipettor tips
		self.volume = 0

		# Variables for toplevel access
		self.first_denature_temp_sv = StringVar()
		self.first_denature_time_sv = StringVar()
		self.cycles_sv = StringVar()
		self.anneal_temp_sv = StringVar()
		self.anneal_time_sv = StringVar()
		self.second_denature_temp_sv = StringVar()
		self.second_denature_time_sv = StringVar()

	def setup_bindings(self):
		# Set bindings between the view and the controller
		self.view.bind_button_tips_add(self.add_tips_action)
		self.view.bind_button_motion_add(self.add_motion_action)
		self.view.bind_button_pipettor_add(self.add_pipettor_action)
		self.view.bind_button_time_add(self.add_time_action)
		self.view.bind_button_other_add(self.add_other_action)
		self.view.bind_button_start(self.start)
		self.view.bind_button_save(self.save)
		self.view.bind_button_load(self.load)
		self.view.bind_button_delete(self.delete)

	def insert(self, ID: int, action_message: str) -> None:
		"""Insert the action message into the action list of the model in the correct order
		
		Parameters
		----------
		ID : int
			Key used to insert data in the correct order
		action_message : str
			Action to be inserted into the model
		"""
		self.model.insert(ID, action_message)

	def add_tips_action(self, event=None) -> None:
		# Get the action data
		tray = self.view.tips_tray_sv.get()
		column = self.view.tips_column_sv.get()
		action = self.view.tips_action_sv.get()
		tip = None
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Make sure there is an action
		if action == '':
			print(f"Tip action must be specified")
			return None
		# Check the action treeview to make sure you are allowed to add this action
		# Generate the action message
		action_message = ''
		if tray == '':
			action_message = f"{action} tips"
		else:
			if action == 'Eject':
				action_message = f"{action} tips in {tray} column {column}"
				# Set all tip options to ''
				self.view.motion_tip_sv.set('')
				self.view.pipettor_tip_sv.set('')
			elif action == 'Pickup':
				action_message = f"{action} tips from {tray} column {column}"
				# Determine what tip was put on
				if tray in ['A', 'B', 'C', 'D']:
					if column == '1':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][2]
					elif column == '2':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][3]
					elif column == '3':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][4]
					elif column == '4':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][5]
					elif column == '5':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][6]
					elif column == '6':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][7]
					elif column == '7':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][8]
					elif column == '8':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][9]
					elif column == '9':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][10]
					elif column == '10':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][11]
					elif column == '11':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][12]
					elif column == '12':
						tip = self.view.master_model.get_configure_model().select(name="Tip Box")[0][13]
				# Set all tip options to the proper tip
				self.view.motion_tip_sv.set(tip)
				self.view.pipettor_tip_sv.set(tip)
			else:
				action_message = f"{action} tips on the {tray}"
		if tip == None:
			tip = 0
		# Check if this action is allowed
		if next_action_allowed(self.state, action):
			# Update the state mode
			self.state.insert(tip, self.volume, action.lower())
			# Insert below the selected row or at the end of the action treeview
			insert_at_selected_row(action_message, selected_row, self.model)
			# Update the view
			self.view.update_treeview()
		else:
			print(f"{action_message} not allowed")

	def add_motion_action(self, event=None) -> None:
		"""Deals with adding a motion action to the model from the view
		"""
		# Get the action data
		consumable = self.view.motion_consumable_sv.get()
		tray = self.view.motion_tray_sv.get()
		column = self.view.motion_column_sv.get()
		tip = self.view.motion_tip_sv.get()
		dxdydz = self.view.motion_dxdydz_sv.get()
		drip_plate = self.view.motion_drip_plate_iv.get()
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Make sure consumable is not missing
		if consumable != '':
			# Generate the action message
			action_message = f"Move to {consumable}"
			# Check tray
			if tray != '':
				action_message = action_message + f" tray {tray}"
			else:
				# Make sure this is ok
				if consumable not in NO_TRAY_CONSUMABLES:
					print(f"Motion consumable ({consumable}) needs a tray")
					return None
			# Check column
			if column != '':
				action_message = action_message + f" column {column}"
			else:
				# Make sure this is ok
				if consumable not in NO_COLUMN_CONSUMABLES:
					print(f"Motion consumable ({consumable}) needs a column")
					return None
			# Check tip
			if tip != '':
				action_message = action_message + f" with {tip} uL tips"
			else:
				action_message = action_message + " without tips"
			# Check relative moves
			if dxdydz != '0,0,0':
				action_message = action_message + " moving"
				# Check if which directions a relative move is desired
				dirx = int(dxdydz.split(',')[0])
				diry = int(dxdydz.split(',')[1])
				dirz = int(dxdydz.split(',')[2])
				if dirx != 0:
					if dirx < 0:
						action_message = action_message + f" left by {abs(dirx)}"
					else:
						action_message = action_message + f" right by {abs(dirx)}"
				if diry != 0:
					if diry < 0:
						action_message = action_message + f" forwards by {abs(diry)}"
					else:
						action_message = action_message + f" backwards by {abs(diry)}"
				if dirz != 0:
					if dirz < 0:
						action_message = action_message + f" down by {abs(dirz)}"
					else:
						action_message = action_message + f" up by {abs(dirz)}"
			# Check drip plate
			if drip_plate == 1:
				action_message = action_message + " with the drip plate"
		else:
			print("Motion Consumable Option was not selected")
			return None
		# Insert below the selected row or at the end of the action treeview
		insert_at_selected_row(action_message, selected_row, self.model)
		# Update the view
		self.view.update_treeview()

	def add_pipettor_action(self, event=None) -> None:
		"""Deals with adding a pipettor action to the model from the view
		"""
		# Get the action data
		try:
			volume = int(self.view.pipettor_volume_sv.get())
		except:
			print("Pipettor Volume (uL) Entry must be an integer value")
			return None
		tip = int(self.view.pipettor_tip_sv.get())
		count = int(self.view.pipettor_count_sv.get())
		if count == 1:
			times = 'time'
		else:
			times = 'times'
		# Make sure the volume is not greater than the tip size
		assert volume <= tip
		action = self.view.pipettor_action_sv.get()
		pressure = self.view.pipettor_pressure_sv.get()
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Generate the action message
		action_message = f"{action.title()} {volume} uLs with {tip} uL tips at {pressure} pressure {count} {times}"
		# Check if this action is allowed
		if next_action_allowed(self.state, action):
			# Update the state model
			self.state.insert(tip, self.volume, action.lower())
			# Insert below the selected row or at the end of the action treeview
			insert_at_selected_row(action_message, selected_row, self.model)
			if action == 'Aspirate':
				self.volume = self.volume + volume 
			elif action == 'Dispense':
				self.volume = self.volume - volume 
			# Update the view
			self.view.update_treeview()
		else:
			print(f"{action_message} not allowed")

	def add_time_action(self, event=None) -> None:
		"""Deals with adding a time action to the model from the view
		"""
		# Get the action data
		try:
			time_ = int(self.view.time_delay_sv.get())
		except:
			print(f"Time delay entry must be an integer value")
			return None
		units = self.view.time_units_sv.get()
		# Check units plurality
		if time_ == 1:
			units = units[:-1]
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Generate the action message
		action_message = f"Delay for {time_} {units}"
		# Inset action into the action list
		insert_at_selected_row(action_message, selected_row, self.model)
		# Update the view
		self.view.update_treeview()

	def add_other_action(self, event=None) -> None:
		"""Deals with adding an other action to the model from the view
		"""
		# Get the action data
		other = self.view.other_option_sv.get()
		# Generate the action message
		action_message = other
		# Check if the action message is a relative move
		if 'relative' in action_message.split():
			amount = self.view.other_parameter_sv.get()
			try:
				amount = int(amount)
				action_message = action_message + f" by {amount}"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Move relative actions require a value to move in usteps. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Load' in action_message.split():
			transfers = self.view.other_parameter_sv.get()
			tips = []
			try:
				transfers = transfers.replace(' ','').split(',')
				data = self.view.master_model.get_configure_model().select(1)
				_ = ''
				for transfer in transfers:
					transfer = transfer.split('-')
					# Get the column the transfer starts from
					start_column = int(transfer[0])
					# Get the column the transfer ends at
					end_column = int(transfer[-1])
					# Get the tip that should be at the end 
					tips.append(data[0][1+end_column])
					# Create the words to add to the action message for this transfer
					_ = _ + f" {start_column}-{end_column}, "
					print(_)
				_ = _[0:-2]
				action_message = action_message + f"{_}"
			except Exception as e:
				print(e)
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Loading a tip tray requires the columns you wish to load using dashes and commas to separate more than one transfer. An example is as follows, to transfer from tip box X column 4 to Tip Box A column 1 and X column 2 to A column 5 would be 4-1,2-5. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Extend' in action_message.split():
			amount = self.view.other_parameter_sv.get()
			try:
				amount = int(amount)
				action_message = action_message + f" by {amount} usteps"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Extend drip plate actions require a value to move in usteps. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Lower' in action_message.split():
			amount = self.view.other_parameter_sv.get()
			try:
				amount = int(float(amount))
				action_message = action_message + f" to {amount} usteps"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Lower thermocycler actions require a value to move in usteps. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Add' in action_message.split():
			comment = self.view.other_parameter_sv.get()
			if comment == "Enter a comment":
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Add comment actions require a comment. Please enter a comment in the Parameter entry box."
				)
				return None
			else:
				action_message = f"Comment: {comment}"
		elif 'Extraction' in action_message.split():
			# Open the file browser to load the extraction protocol
			file = browse_files(
				'r',
				"Load Extraction Protocol",
				INITIAL_EXTRACTION_FILENAME,
				r'protocols\\common\\extraction\\'
			)
			file_path = file.name
			action_message = action_message + f" ({file_path})"
		elif 'Transfer' in action_message.split():
			# Open the file browser to load the protocol
			file = browse_files(
				'r',
				"Load Transfer Plasma Protocol",
				INITIAL_TRANSFER_PLASMA_FILENAME,
				r'protocols\\common\\extraction\\'
			)
			file_path = file.name
			action_message = action_message + f" ({file_path})"
		elif 'Change' in action_message.split():
			# Get the temp value
			temp = self.view.other_parameter_sv.get()
			try:
				temp = float(temp)
				temp = str(round(temp,1))
				action_message = action_message + f" to {temp} C"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Change temperature actions require a value in C. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Hold' in action_message.split():
			# Get the hold time with units
			hold_time = self.view.other_parameter_sv.get().split()
			try:
				t = int(hold_time[0])
				units = str(hold_time[-1])
				action_message = action_message + f" for {t} {units}"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Thermocycle hold actions require a hold time formated as time units, with time as an integer and units as either second, seconds, minute, or minutes. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Shake' in action_message.split() and 'on' in action_message.split():
			# Get the rpm value
			rpm = self.view.other_parameter_sv.get()
			try:
				rpm = int(rpm)
				action_message = action_message + f" with an RPM of {rpm}"
			except:
				tk.messagebox.showwarning(
					title="Failed to Add Action",
					message="Shake on actions require a RPM value. Please enter a value in the Parameter entry box."
				)
				return None
		elif 'Thermocycle' in action_message.split():
			if 'Protocol' in  action_message.split():
				# Open the file browser to load a file to get the name of the protocol file
				file = browse_files(
					'r', 
					"Load Protocol", 
					INITIAL_PROTOCOL_FILENAME, 
					r'protocols\{0}'.format(self.model.unit.upper())
				)
				file_path = file.name
				action_message = action_message + f" ({file_path})"
			elif 'Pre-Amp' in action_message.split():
				# Open a toplevel window to setup the protocol
				self.create_toplevel_pre_amp()
				return None
		elif 'Cycle' == action_message.split()[-1]:
			# Open a toplevel window to setup the cycling protocol
			self.create_toplevel_cycle()
			return None
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Inset action into the action list
		insert_at_selected_row(action_message, selected_row, self.model)
		# Update the view
		self.view.update_treeview()

	def start(self, event=None) -> None:
		"""Deals with starting the protocol
		"""
		# Start the protocol
		thread = threading.Thread(target=self.start_protocol)
		thread.start()
	
	def start_protocol(self):
		"""Process for starting the protocol
		"""
		try:
			self.upper_gantry = UpperGantry()
		except:
			pass
		# Open a file for logging
		log = Log()
		# Set the progress bar to 0
		self.view.progressbar.set(0)
		# Set the action progress label to 0 of N actions
		n_actions = len(self.model.select())
		self.view.label_action_progress.configure(text=f"Action Progress: 0 of {n_actions}")
		# Show a small bit of progress
		n_actions = len(self.model.select())
		if n_actions != 0:
			progress = 0.5 / n_actions
		else:
			progress = 0
		self.view.progressbar.set(progress)
		# Iterate through the actions in the action treeview
		for i in self.view.treeview.get_children():
			# Start timing this action
			t_start = time.time()
			# Update the progress bar
			progress = (int(i) + 1 ) / n_actions
			self.view.progressbar.set(progress)
			# Select the row
			self.view.treeview.selection_set(i)
			# Update the action progress label
			self.view.label_action_progress.configure(text=f"Action Progress: {int(i) + 1} of {n_actions}")
			# Get the action message
			action_message = self.view.treeview.item(i)['values'][0]
			split = action_message.split()
			# Check for the first key word in the action message
			assert split[0] in MAIN_ACTION_KEY_WORDS
			# Analyze the action message
			if split[0] == 'Eject':
				# Eject tips
				if 'column' not in split:
					self.upper_gantry.tip_eject()
				# Eject tips in {tray} column {column}
				else:
					tray = split[3]
					column = int(split[5])
					# Get the coordinate
					unit = self.model.db_name[-4]
					table_name = f"Unit {unit} Upper Gantry Coordinates"
					coordinate = self.coordinates_model.select(table_name, "Tip Box", tray, column)
					x = int(coordinate[0][4])
					y = int(coordinate[0][5])
					z = int(coordinate[0][6])
					self.upper_gantry.tip_eject_new(x, y, z)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Pickup':
				tray = split[3]
				column = int(split[5])
				if column in [1,2,3,4]:
					tip = 1000
				else:
					tip = 50
				# Get the coordinate
				unit = self.model.db_name[-4]
				table_name = f"Unit {unit} Upper Gantry Coordinates"
				coordinate = self.coordinates_model.select(table_name, "Tip Box", tray, column)
				x = coordinate[0][4]
				y = coordinate[0][5]
				z = coordinate[0][6]
				# Pickup tips in {tray} column {column}
				self.upper_gantry.tip_pickup_new(x,y,z, tip)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Tip-press':
				time.sleep(1)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Extend':
				amount = -abs(int(split[-2]))
				drip_plate_id = 4
				speed = self.upper_gantry.get_limit_max_velocity_drip_plate()
				self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', drip_plate_id, amount, speed, True, True)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Suction':
				action = split[-1]
				if action == 'on':
					self.upper_gantry.turn_on_suction_cups()
				else:
					self.upper_gantry.turn_off_suction_cups()
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Move':
				# Check if this is just a relative move
				if split[1] == 'relative':
					amount = int(split[-1])
					direction = split[2]
					self.upper_gantry.move_relative(direction, amount, velocity='fast')
					# Log
					log.log(action_message, time.time() - t_start)
					continue
				# Or a chip move
				elif split[1] == 'Chip':
					consumable = "Tip Transfer Tray"
					tray = split[-1]
					table_name = f"Unit {self.unit} Upper Gantry Coordinates"
					coordinate = self.coordinates_model.select(table_name, consumable, tray, column=1)
					chip = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					consumable = 'Tray'
					coordinate = self.coordinates_model.select(table_name, consumable, tray, column=0)
					tray = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					# Move the chip from the tip transfer tray to the tray
					self.upper_gantry.move_chip_new(chip, tray)
					# Log
					log.log(action_message, time.time() - t_start)
					continue
				# Or a lid move
				elif split[1] == 'Lid':
					tray = split[2]
					column=1
					#column = split[2]
					# Get the coordinates for the lid and tray
					unit = self.model.db_name[-4]
					table_name = f"Unit {self.unit} Upper Gantry Coordinates"
					coordinate = self.coordinates_model.select(table_name, "Lid Tray", tray, column)
					lid = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					consumable = 'Tray'
					coordinate = self.coordinates_model.select(table_name, consumable, tray, column=0)
					tray = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					# Move the lid
					self.upper_gantry.move_lid_new(lid, tray)
					# Log
					log.log(action_message, time.time() - t_start)
					continue
				# Or an engaged chip/lid move
				elif split[1] == 'Engaged':
					tray = split[-1]
					column=0
					# Get the coordinates for the lid and tray
					unit = self.model.db_name[-4]
					table_name = f"Unit {self.unit} Upper Gantry Coordinates"
					coordinate = self.coordinates_model.select(table_name, "Tray", tray, column)
					chip = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					consumable = 'Tray'
					coordinate = self.coordinates_model.select(table_name, consumable, 'B', column=0)
					tray = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					# Move the lid
					self.upper_gantry.move_chip_and_lid_temporary(chip, tray)
					# Log
					log.log(action_message, time.time() - t_start)
					continue
				i0 = 2
				try:
					# Use the tray to get where the consumable words end
					i1 = split.index('tray')
				except ValueError:
					# Use the column to get where the consumable words end
					i1 = split.index('column')
				consumable = " ".join(split[i0:i1])
				if consumable in ["Tip Box"]:#, "DG8"]:
					ignore_tips = True
				else:
					ignore_tips = False
				# Get the tray
				try:
					tray = split[split.index('tray') + 1]
				except ValueError:
					tray = ''
				# Get the column
				try:
					column = split[split.index('column') + 1]
				except ValueError:
					column = ''
				# Get the tip size
				tip = int(split[split.index('tips') - 2])
				# Get the relative moves
				try:
					dx = -int(split[split.index('left') + 2])
				except ValueError:
					try:
						dx = int(split[split.index('right') + 2])
					except ValueError:
						dx = 0
				try:
					dy = -int(split[split.index('forwards') + 2])
				except ValueError:
					try:
						dy = int(split[split.index('backwards') + 2])
					except ValueError:
						dy = 0
				try:
					dz = -int(split[split.index('down') + 2])
				except ValueError:
					try:
						dz = int(split[split.index('up') + 2])
					except ValueError:
						dz = 0
				# Get the drip plate usage
				try:
					split.index('drip')
					drip_plate = True
				except ValueError:
					drip_plate = False
				# Get the x,y,z1,z2 for this consumable
				model = self.coordinates_model
				unit = self.model.db_name[-4]
				table_name = f"Unit {unit} Upper Gantry Coordinates"
				coordinate = model.select(table_name, consumable, tray, column)
				x = coordinate[0][4]
				y = coordinate[0][5]
				z1 = coordinate[0][6]
				z2 = coordinate[0][7]
				# Setup the command
				self.upper_gantry.move(
					x=x,
					y=y,
					z=z1,
					drip_plate=z2,
					use_drip_plate=drip_plate,
					tip=tip,
					relative_moves=[dx,dy,dz,0],
					ignore_tips=ignore_tips
				)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Open':
				tray = split[-1]
				if tray == 'AB':
					self.reader.get_fast_api_interface().reader.axis.home('reader', 6)
				elif tray == 'CD':
					self.reader.get_fast_api_interface().reader.axis.home('reader', 7)
			elif split[0] == 'Light':
				for i in range(1,7):
					self.reader.turn_on_led(i,200)
					time.sleep(2)
					self.reader.turn_off_led(i)
			elif split[0] in ['Aspirate', 'Dispense', 'Mix']:
				# Get the action
				action = split[0]
				# Get the volume
				volume = int(split[1])
				# Get the tip size
				tip = int(split[4])
				# Get the pressure
				pressure = split[8].lower()
				# Get the action count
				count = int(split[10])
				# Setup the command and do it count times
				for i in range(count):
					if action == 'Aspirate':
						self.upper_gantry.aspirate(volume, pipette_tip_type=tip, pressure=pressure)
					if action == 'Dispense':
						self.upper_gantry.dispense(volume, pressure=pressure)
					if action == 'Mix':
						print(f'Mix Count: {i+1}/{count}')
						self.upper_gantry.aspirate(volume, pipette_tip_type=tip, pressure=pressure)
						self.upper_gantry.dispense(volume, pressure=pressure)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Load':
				# Get the tray
				tray = split[3]
				# Get the number of transfers
				number_of_transfers = len(split) - 4
				# Data for getting the coordiantes
				unit = self.model.db_name[-4]
				table_name = f"Unit {self.unit} Upper Gantry Coordinates"
				# Get the transfers
				for i in range(number_of_transfers):
					columns = split[4+i].replace(',','').replace(' ','').split('-')
					# Get the start of the transfer
					start_column = columns[0]
					# Get the end of the transfer
					end_column = columns[1]
					# Move the pipettor to the start column of Tip Box X
					coordinate = self.coordinates_model.select(table_name, "Tip Box", 'X', start_column)
					x = int(coordinate[0][4])
					y = int(coordinate[0][5])
					z = int(coordinate[0][6])
					self.upper_gantry.move(x,y,z,0,tip=1000)
					# Eject the tips in the end column of Tip Box Tray
					coordinate = self.coordinates_model.select(table_name, "Tip Box", tray, end_column)
					x = int(coordinate[0][4])
					y = int(coordinate[0][5])
					z = int(coordinate[0][6])
					self.upper_gantry.tip_eject_new(x, y, z)
			elif split[0] == 'Delay':
				# Get the time
				value = int(split[2])
				# Get the units
				units = split[3]
				# Setup the command
				delay(value, units)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Add':
				# Get the comment
				# Log
				log.log(action_message, time.time() - t_start)
				continue
			elif split[0] == 'Pause':
				# Open a message box for the user 
				if tk.messagebox.askokcancel(title="Protocol Pause", message="Would you like to continue?"):
					# Log
					log.log(action_message + " -> Ok Pressed", time.time() - t_start)
					continue
				else:
					if tk.messagebox.askyesno(title="Protocol Pause", message="Canceling the protocol now loses all current progress, are you sure you want to cancel?"):
						# Log
						log.log(action_message + " -> Cancel Pressed", time.time() - t_start)
						return None
					else:
						# Log
						log.log(action_message + " -> Cancel Pressed -> Ok Pressed", time.time() - t_start)
						continue
			elif split[0] == 'Home':
				# Determine the type of homing
				if split[-1] == 'pipettor':
					self.upper_gantry.home_pipettor()
				elif split[-1] == 'fast':
					self.upper_gantry.move(x=0,y=0,z=0,drip_plate=0)
					self.upper_gantry.home_pipettor()
				elif split[-1] == 'Z':
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 3, 0, 800000, True, True)
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 3)
				elif split[-1] == 'Y':
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 2, 0, 3200000, True, True)
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 2)
				elif split[-1] == 'X':
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 1, 0, 300000, True, True)
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 1)
				elif split[-1] == 'plate':
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.move('pipettor_gantry', 4, 0, 2500000, True, True)
					self.upper_gantry.get_fast_api_interface().pipettor_gantry.axis.home('pipettor_gantry', 4)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'LLD':
				self.upper_gantry.get_pipettor().liquid_level_detect()
			elif split[0] == 'Generate':
				# Get the droplet type
				droplet_type = split[1]
				# Generate the droplets
				self.upper_gantry.generate_droplets(droplet_type)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Pre-Amp':
				a = 1
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Shake':
				# Get the mode
				mode = split[1]
				if mode.lower() == 'on':
					rpm = split[-1]
					self.upper_gantry.turn_on_shake(rpm=rpm)
				elif mode.lower() == 'off':
					self.upper_gantry.turn_off_shake()
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Engage':
				self.upper_gantry.engage_magnet()
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Disengage':
				self.upper_gantry.disengage_magnet()
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Thermocycle:':
				""" Thermocycle: is different than actions that start with Thermocycle only, this one is for 
				cycling only
				"""
				# Initialize the Meerstetter
				try:
					self.meerstetter = Meerstetter()
				except Exception as e:
					pass
				# Determine which thermocyclers are going to be used
				temp_cutoff = 2 # C
				protocol_data = {
					'A': {
						'use': None,
						'step': None, # [denature, cycle, done]
						'denature': [None, None], # denature_temperature_C, denature_time_s
						'cycle': [None, None, None, None, None], # cycles, extension_temperature_C, extension_time_s, anneal_temperature_C, anneal_time_s
						'done': None,
						'clock': 0,
					},
					'B': {
						'use': None,
						'step': None,
						'denature': [None, None], # denature_temperature_C, denature_time_s
						'cycle': [None, None, None, None, None], # cycles, extension_temperature_C, extension_time_s, anneal_temperature_C, anneal_time_s
						'done': None,
						'clock': 0,
					},
					'C': {
						'use': None,
						'step': None,
						'denature': [None, None], # denature_temperature_C, denature_time_s
						'cycle': [None, None, None, None, None], # cycles, extension_temperature_C, extension_time_s, anneal_temperature_C, anneal_time_s
						'done': None,
						'clock': 0,
					},
					'D': {
						'use': None,
						'step': None,
						'denature': [None, None], # denature_temperature_C, denature_time_s
						'cycle': [None, None, None, None, None], # cycles, extension_temperature_C, extension_time_s, anneal_temperature_C, anneal_time_s
						'done': None,
						'clock': 0,
					},
				}
				if '-A-' in split:
					protocol_data['A']['use'] = True
					if protocol_data['A']['use']:
						protocol_data['A']['step'] = 'denature'
					else:
						protocol_data['A']['step'] = None
					protocol_data['A']['done'] = False
					start_index = split.index('-A-')
					protocol_data['A']['cycle'][0] = int(split[start_index+9])
					protocol_data['A']['denature'][0] = int(split[start_index+3])
					protocol_data['A']['denature'][1] = int(split[start_index+6])
					units = str(split[start_index+7])
					if units == 'minutes':
						protocol_data['A']['denature'][1] = protocol_data['A']['denature'][1] * 60
					protocol_data['A']['cycle'][3] = int(split[start_index+18])
					protocol_data['A']['cycle'][4] = int(split[start_index+21])
					units = str(split[start_index+22])
					if units == 'minutes':
						protocol_data['A']['cycle'][4] = protocol_data['A']['cycle'][4] * 60
					protocol_data['A']['cycle'][1] = int(split[start_index+12])
					protocol_data['A']['cycle'][2] = int(split[start_index+15])
					units = str(split[start_index+16])
					if units == 'minutes':
						protocol_data['A']['cycle'][2] = protocol_data['A']['cycle'][2] * 60
				if '-B-' in split:
					protocol_data['B']['use'] = True
					if protocol_data['B']['use']:
						protocol_data['B']['step'] = 'denature'
					else:
						protocol_data['B']['step'] = None
					protocol_data['B']['done'] = False
					start_index = split.index('-B-')
					protocol_data['B']['cycle'][0] = int(split[start_index+9])
					protocol_data['B']['denature'][0] = int(split[start_index+3])
					protocol_data['B']['denature'][1] = int(split[start_index+6])
					units = str(split[start_index+7])
					if units == 'minutes':
						protocol_data['B']['denature'][1] = protocol_data['B']['denature'][1] * 60
					protocol_data['B']['cycle'][3] = int(split[start_index+18])
					protocol_data['B']['cycle'][4] = int(split[start_index+21])
					units = str(split[start_index+22])
					if units == 'minutes':
						protocol_data['B']['cycle'][4] = protocol_data['B']['cycle'][4] * 60
					protocol_data['B']['cycle'][1] = int(split[start_index+12])
					protocol_data['B']['cycle'][2] = int(split[start_index+15])
					units = str(split[start_index+16])
					if units == 'minutes':
						protocol_data['B']['cycle'][2] = protocol_data['B']['cycle'][2] * 60
				if '-C-' in split:
					protocol_data['C']['use'] = True
					if protocol_data['C']['use']:
						protocol_data['C']['step'] = 'denature'
					else:
						protocol_data['C']['step'] = None
					protocol_data['C']['done'] = False
					start_index = split.index('-C-')
					protocol_data['C']['cycle'][0] = int(split[start_index+9])
					protocol_data['C']['denature'][0] = int(split[start_index+3])
					protocol_data['C']['denature'][1] = int(split[start_index+6])
					units = str(split[start_index+7])
					if units == 'minutes':
						protocol_data['C']['denature'][1] = protocol_data['C']['denature'][1] * 60
					protocol_data['C']['cycle'][3] = int(split[start_index+18])
					protocol_data['C']['cycle'][4] = int(split[start_index+21])
					units = str(split[start_index+22])
					if units == 'minutes':
						protocol_data['C']['cycle'][4] = protocol_data['C']['cycle'][4] * 60
					protocol_data['C']['cycle'][1] = int(split[start_index+12])
					protocol_data['C']['cycle'][2] = int(split[start_index+15])
					units = str(split[start_index+16])
					if units == 'minutes':
						protocol_data['C']['cycle'][2] = protocol_data['C']['cycle'][2] * 60
				if '-D-' in split:
					protocol_data['D']['use'] = True
					if protocol_data['D']['use']:
						protocol_data['D']['step'] = 'denature'
					else:
						protocol_data['D']['step'] = None
					protocol_data['D']['done'] = False
					start_index = split.index('-D-')
					protocol_data['D']['cycle'][0] = int(split[start_index+9])
					protocol_data['D']['denature'][0] = int(split[start_index+3])
					protocol_data['D']['denature'][1] = int(split[start_index+6])
					units = str(split[start_index+7])
					if units == 'minutes':
						protocol_data['D']['denature'][1] = protocol_data['D']['denature'][1] * 60
					protocol_data['D']['cycle'][3] = int(split[start_index+18])
					protocol_data['D']['cycle'][4] = int(split[start_index+21])
					units = str(split[start_index+22])
					if units == 'minutes':
						protocol_data['D']['cycle'][4] = protocol_data['D']['cycle'][4] * 60
					protocol_data['D']['cycle'][1] = int(split[start_index+12])
					protocol_data['D']['cycle'][2] = int(split[start_index+15])
					units = str(split[start_index+16])
					if units == 'minutes':
						protocol_data['D']['cycle'][2] = protocol_data['D']['cycle'][2] * 60
				# Start the cycling
				all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
				while False in all_done: 
					# Step for A
					if protocol_data['A']['use']:
						ID = 'A'
						address = 1
						# Get the step currently on
						step = protocol_data[ID]['step']
						# Get the temperature and time for this step
						if 'cycle' in step:
							whole_message = step.split('_')
							step = whole_message[0]
							cycle = int(whole_message[1])
							action = whole_message[2]
							if action == 'anneal':
								temp_index = 3
								time_index = 4
							elif action == 'extension':
								temp_index = 1
								time_index = 2
						elif 'denature' in step:
							temp_index = 0
							time_index = 1
						temp_a = protocol_data[ID][step][temp_index]
						time_a = protocol_data[ID][step][time_index]
						# Check the state of the board
						self.meerstetter.handle_device_status(address, temp_a)
						# Change the temperature  and start the timer
						if protocol_data[ID]['clock'] == 0:
							print(f'starting clock for {protocol_data[ID]["step"]}')
							self.meerstetter.change_temperature(address, temp_a)
							# Make sure the temperature is reached before starting to time
							actual_temp = self.meerstetter.get_temperature(address)
							if actual_temp - temp_cutoff <= temp_a <= actual_temp + temp_cutoff:
								protocol_data[ID]['clock'] = time.time()
						# Check the timing for this step
						if time.time() - protocol_data[ID]['clock'] >= time_a and protocol_data[ID]['clock'] != 0:
							# Update the step
							if step == 'denature':
								step = 'cycle_1_extension'
								protocol_data[ID]['step'] = step
							if step == 'cycle':
								if cycle > protocol_data[ID]['cycle'][0]:
									if protocol_data[ID]['done'] == False:
										print(f'ID {ID} done')
										self.meerstetter.change_temperature(address, 30)
										protocol_data[ID]['done'] = True
										# Check if all the units are done
										all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
									continue
								if action == 'extension':
									step = f'cycle_{cycle}_anneal'
									protocol_data[ID]['step'] = step
								else:
									# Change cycle number after the annealing step ends
									cycle = cycle + 1
									step = f'cycle_{cycle}_extension'
									protocol_data[ID]['step'] = step
							# Restart the clock
							protocol_data[ID]['clock'] = 0
					# Step for B
					if protocol_data['B']['use']:
						ID = 'B'
						address = 2
						# Get the step currently on
						step = protocol_data[ID]['step']
						# Get the temperature and time for this step
						if 'cycle' in step:
							whole_message = step.split('_')
							step = whole_message[0]
							cycle = int(whole_message[1])
							action = whole_message[2]
							if action == 'anneal':
								temp_index = 3
								time_index = 4
							elif action == 'extension':
								temp_index = 1
								time_index = 2
						elif 'denature' in step:
							temp_index = 0
							time_index = 1
						temp_b = protocol_data[ID][step][temp_index]
						time_b = protocol_data[ID][step][time_index]
						# Check the state of the board
						self.meerstetter.handle_device_status(address, temp_b)
						# Change the temperature  and start the timer
						if protocol_data[ID]['clock'] == 0:
							print(f'starting clock for {protocol_data[ID]["step"]}')
							self.meerstetter.change_temperature(address, temp_b)
							# Make sure the temperature is reached before starting to time
							actual_temp = self.meerstetter.get_temperature(address)
							if actual_temp - temp_cutoff <= temp_b <= actual_temp + temp_cutoff:
								protocol_data[ID]['clock'] = time.time()
						# Check the timing for this step
						if time.time() - protocol_data[ID]['clock'] >= time_b and protocol_data[ID]['clock'] != 0:
							# Update the step
							if step == 'denature':
								step = 'cycle_1_extension'
								protocol_data[ID]['step'] = step
							if step == 'cycle':
								if cycle > protocol_data[ID]['cycle'][0]:
									if protocol_data[ID]['done'] == False:
										print(f'ID {ID} done')
										self.meerstetter.change_temperature(address, 30)
										protocol_data[ID]['done'] = True
										# Check if all the units are done
										all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
									continue
								if action == 'extension':
									step = f'cycle_{cycle}_anneal'
									protocol_data[ID]['step'] = step
								else:
									# Change cycle number after the annealing step ends
									cycle = cycle + 1
									step = f'cycle_{cycle}_extension'
									protocol_data[ID]['step'] = step
							# Restart the clock
							protocol_data[ID]['clock'] = 0
					# Step for C
					if protocol_data['C']['use']:
						ID = 'C'
						address = 3
						# Get the step currently on
						# Get the step currently on
						step = protocol_data[ID]['step']
						# Get the temperature and time for this step
						if 'cycle' in step:
							whole_message = step.split('_')
							step = whole_message[0]
							cycle = int(whole_message[1])
							action = whole_message[2]
							if action == 'anneal':
								temp_index = 3
								time_index = 4
							elif action == 'extension':
								temp_index = 1
								time_index = 2
						elif 'denature' in step:
							temp_index = 0
							time_index = 1
						temp_c = protocol_data[ID][step][temp_index]
						time_c = protocol_data[ID][step][time_index]
						# Check the state of the board
						self.meerstetter.handle_device_status(address, temp_c)
						# Change the temperature  and start the timer
						if protocol_data[ID]['clock'] == 0:
							print(f'starting clock for {protocol_data[ID]["step"]}')
							self.meerstetter.change_temperature(address, temp_c)
							# Make sure the temperature is reached before starting to time
							actual_temp = self.meerstetter.get_temperature(address)
							if actual_temp - temp_cutoff <= temp_c <= actual_temp + temp_cutoff:
								protocol_data[ID]['clock'] = time.time()
						# Check the timing for this step
						if time.time() - protocol_data[ID]['clock'] >= time_c and protocol_data[ID]['clock'] != 0:
							# Update the step
							if step == 'denature':
								step = 'cycle_1_extension'
								protocol_data[ID]['step'] = step
							if step == 'cycle':
								if cycle > protocol_data[ID]['cycle'][0]:
									if protocol_data[ID]['done'] == False:
										print(f'ID {ID} done')
										self.meerstetter.change_temperature(address, 30)
										protocol_data[ID]['done'] = True
										# Check if all the units are done
										all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
									continue
								if action == 'extension':
									step = f'cycle_{cycle}_anneal'
									protocol_data[ID]['step'] = step
								else:
									# Change cycle number after the annealing step ends
									cycle = cycle + 1
									step = f'cycle_{cycle}_extension'
									protocol_data[ID]['step'] = step
							# Restart the clock
							protocol_data[ID]['clock'] = 0
					# Step for D
					if protocol_data['D']['use']:
						ID = 'D'
						address = 4
						# Get the step currently on
						step = protocol_data[ID]['step']
						# Get the temperature and time for this step
						if 'cycle' in step:
							whole_message = step.split('_')
							step = whole_message[0]
							cycle = int(whole_message[1])
							action = whole_message[2]
							if action == 'anneal':
								temp_index = 3
								time_index = 4
							elif action == 'extension':
								temp_index = 1
								time_index = 2
						elif 'denature' in step:
							temp_index = 0
							time_index = 1
						temp_d = protocol_data[ID][step][temp_index]
						time_d = protocol_data[ID][step][time_index]
						# Check the state of the board
						self.meerstetter.handle_device_status(address, temp_d)
						# Change the temperature  and start the timer
						if protocol_data[ID]['clock'] == 0:
							print(f'starting clock for {protocol_data[ID]["step"]}')
							self.meerstetter.change_temperature(address, temp_d)
							# Make sure the temperature is reached before starting to time
							actual_temp = self.meerstetter.get_temperature(address)
							if actual_temp - temp_cutoff <= temp_d <= actual_temp + temp_cutoff:
								print(f" OK NOW START TIMING ON {ID}")
								protocol_data[ID]['clock'] = time.time()
						# Check the timing for this step
						if time.time() - protocol_data[ID]['clock'] >= time_d and protocol_data[ID]['clock'] != 0:
							# Update the step
							if step == 'denature':
								step = 'cycle_1_extension'
								protocol_data[ID]['step'] = step
							if step == 'cycle':
								if cycle > protocol_data[ID]['cycle'][0]:
									if protocol_data[ID]['done'] == False:
										print(f'ID {ID} done')
										self.meerstetter.change_temperature(address, 30)
										protocol_data[ID]['done'] = True
										# Check if all the units are done
										all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
									continue
								if action == 'extension':
									step = f'cycle_{cycle}_anneal'
									protocol_data[ID]['step'] = step
								else:
									# Change cycle number after the annealing step ends
									cycle = cycle + 1
									step = f'cycle_{cycle}_extension'
									protocol_data[ID]['step'] = step
							# Restart the clock
							protocol_data[ID]['clock'] = 0
					# Check if all the units are done
					all_done = [protocol_data[i]['done'] for i in protocol_data.keys()]
				print('ALL DONE')

			elif split[0] == 'Thermocycle':
				# Initialize the Meerstetter
				try:
					self.meerstetter = Meerstetter()
				except Exception as e:
					pass
				if 'Pre-Amp' in split:
					address = 9
					# Get the data
					fdtemp = split[3]
					fdtime = split[6]
					cycles = split[10]
					atemp = split[19]
					atime = split[22]
					sdtemp = split[13]
					sdtime = split[16]
					# Start the Pre-Amp Thermocycler Protocol
					self.meerstetter.change_temperature(address, int(fdtemp), block=False)
					delay(int(fdtime), 'minutes')
					for i in range(int(cycles)):
						print(f"Cycle Progress: {i+1}/{cycles}")
						self.meerstetter.change_temperature(address, int(sdtemp), block=False)
						delay(int(sdtime), 'seconds')
						self.meerstetter.change_temperature(address, int(atemp), block=False)
						delay(int(atime), 'seconds')
					self.meerstetter.change_temperature(address, 30, block=False)
				elif 'Change' in split:
					# Get the heater letter designation
					heater = split[1]
					# Convert to the address
					address = HEATER_ADDRESSES[heater.upper().replace(':','')]
					# Get the temperature 
					temp = int(float(split[-2]))
					# Change the temperature 
					print(address)
					print(temp)
					self.meerstetter.change_temperature(address, temp)
				elif 'Hold' in split:
					# Get the hold time
					t = int(split[-2])
					# Get the units
					units = split[-1]
					# Convert to seconds
					if units[0].lower() == 'm':
						t = t * 60
					elif units[0].lower() == 'h':
						t = t * 60 * 60
					elif units[0].lower() == 's':
						t = t
					# Monitor the TEC boards (addresses 1,2,3,4,9)
					self.meerstetter.monitor_devices([1,2,3,4,9], t)
				elif 'Protocol' == split[1]:
					# Get the protocol file path
					file_path = split[-1].replace('(','').replace(')','')
					# Get protocol info
					with open(file_path, 'r') as ofile:
						lines = ofile.readlines()
						# Read the file line by line
						protocol = {}
						for line in lines:
							line = line.split(',')
							thermocycler = line[0]
							protocol[thermocycler] = {
								'use': line[1],
								'cycles': line[2],
								'first_denature_temperature': line[3],
								'first_denature_time': line[4],
								'anneal_temperature': line[5],
								'anneal_time': line[6],
								'second_denature_temperature': line[7],
								'second_denature_time': line[8],
							}
						# Start the protocol
						print('First Denature Temperature and Time') 
						if int(protocol['A']['use']) == True:
							print(f" - A: {protocol['A']['first_denature_temperature']} C for {protocol['A']['first_denature_time']} min")
							self.meerstetter.change_temperature(1, int(protocol['A']['first_denature_temperature']), block=False)
						elif int(protocol['B']['use']) == True:
							print(f" - B: {protocol['B']['first_denature_temperature']} C for {protocol['B']['first_denature_time']} min")
							self.meerstetter.change_temperature(2, int(protocol['B']['first_denature_temperature']), block=False)
						elif int(protocol['C']['use']) == True:
							print(f" - C: {protocol['C']['first_denature_temperature']} C for {protocol['C']['first_denature_time']} min")
							self.meerstetter.change_temperature(3, int(protocol['C']['first_denature_temperature']), block=False)
						elif int(protocol['D']['use']) == True:
							print(f" - D: {protocol['D']['first_denature_temperature']} C for {protocol['D']['first_denature_time']} min")
							self.meerstetter.change_temperature(4, int(protocol['D']['first_denature_temperature']), block=False)
						delay(int(protocol['A']['first_denature_time']), 'minutes')
						print('Cycles')
						for i in range(int(protocol['A']['cycles'])):
							if int(protocol['A']['use']) == True:
								print(f" - A: {protocol['A']['second_denature_temperature']} C for {protocol['A']['second_denature_time']} sec")
								self.meerstetter.change_temperature(1, int(protocol['A']['second_denature_temperature']), block=False)
							elif int(protocol['B']['use']) == True:
								print(f" - B: {protocol['B']['second_denature_temperature']} C for {protocol['B']['second_denature_time']} sec")
								self.meerstetter.change_temperature(2, int(protocol['B']['second_denature_temperature']), block=False)
							elif int(protocol['C']['use']) == True:
								print(f" - C: {protocol['C']['second_denature_temperature']} C for {protocol['C']['second_denature_time']} sec")
								self.meerstetter.change_temperature(3, int(protocol['C']['second_denature_temperature']), block=False)
							elif int(protocol['D']['use']) == True:
								print(f" - D: {protocol['D']['second_denature_temperature']} C for {protocol['D']['second_denature_time']} sec")
								self.meerstetter.change_temperature(4, int(protocol['D']['second_denature_temperature']), block=False)
							delay(int(protocol['A']['second_denature_time']), 'seconds')
							if int(protocol['A']['use']) == True:
								print(f" - A: {protocol['A']['anneal_temperature']} C for {protocol['A']['anneal_time']} sec")
								self.meerstetter.change_temperature(1, int(protocol['A']['anneal_temperature']), block=False)
							elif int(protocol['B']['use']) == True:
								print(f" - B: {protocol['B']['anneal_temperature']} C for {protocol['B']['anneal_time']} sec")
								self.meerstetter.change_temperature(2, int(protocol['B']['anneal_temperature']), block=False)
							elif int(protocol['C']['use']) == True:
								print(f" - C: {protocol['C']['anneal_temperature']} C for {protocol['C']['anneal_time']} sec")
								self.meerstetter.change_temperature(3, int(protocol['C']['anneal_temperature']), block=False)
							elif int(protocol['D']['use']) == True:
								print(f" - D: {protocol['D']['anneal_temperature']} C for {protocol['D']['anneal_time']} sec")
								self.meerstetter.change_temperature(4, int(protocol['D']['anneal_temperature']), block=False)
							delay(int(protocol['A']['anneal_time']), 'seconds')
				self.meerstetter.close()
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Open':
				# Open the tray
				self.reader.open_tray(split[2])
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Close':
				# Close the tray
				self.reader.close_thermocycler_tray(split[2], -780000)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Lower':
				# Get the position to move the heater to
				amount = -abs(int(split[-2]))
				# Lower the thermocycler
				address = ADDRESSES[split[2]]
				self.reader.get_fast_api_interface().reader.axis.move('reader', address, amount, 100000, True, True)
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Raise':
				# Raise the thermocycler
				self.reader.raise_heater(split[2])
				# Log
				log.log(action_message, time.time() - t_start)
			elif split[0] == 'Change':
				# Get the temp
				temp = float(split[-2])
				# Change the Heater/Shaker temperature
				self.upper_gantry.change_heater_shaker_temperature(temp)
				# Log
				log.log(action_message, time.time() - t_start)	
				
	def __get_protocol_data(self, protocol_data: dict, thermocycler: str, step: str) -> list:
		""" """
		if step == 'denature':
			return protocol_data[thermocycler][step]
		elif step == 'cycle': 
			a = 1
		else:
			a = 1

	def load(self, event=None) -> None:
		"""Deals with the loading of a protocol into the action treeview
		"""
		# Browse the file system to open a protocol
		file = browse_files('r', "Load Protocol", INITIAL_PROTOCOL_FILENAME, r'protocols\{0}'.format(self.model.unit.upper()))
		# Read line by line through the file
		lines = [line.rstrip('n') for line in file]
		# Get the starting ID
		n_actions = len(self.model.select())
		ID = n_actions
		for line in lines:
			# Get the action message (remove the #:)
			action_message = ' '.join(line.split()[1:])
			# Update the model
			self.model.insert(ID, action_message)
			ID = ID + 1
		# Update the treeview
		self.view.update_treeview()

	def save(self, event=None) -> None:
		"""Deals with saving the action treeview to a protocol file
		"""
		# Browse the file system to save the protocol
		file = browse_files('w', "Save Protocol", INITIAL_PROTOCOL_FILENAME, r'protocols\{0}'.format(self.model.unit.upper()))
		# Iterate through the actions in the treeview
		for i in self.view.treeview.get_children():
			# Get the action message
			action_message = self.view.treeview.item(i)['values'][0]
			line = f"{i}: {action_message}\n"
			file.write(line)
		file.close()

	def delete(self, event=None) -> None:
		"""Deals with making deletions from the action treeview
		"""
		# Iterate the selected rows
		for selected_row in self.view.treeview.selection():
			# Update the model
			self.model.delete(int(selected_row))
		# Update the view
		self.view.update_treeview()

	def create_toplevel_cycle(self):
		""" Creates a Toplevel for a cycling protocol for the Build Protocol tab """
		toplevel_cycle = ctk.CTkToplevel(self.view.master)
		toplevel_cycle.geometry(f'{TOPLEVEL_CYCLE_WIDTH}x{TOPLEVEL_CYCLE_HEIGHT}')
		# Create and place the title of the toplevel
		toplevel_cycle.title("Cycle Protocol Builder")
		# Get the thermocycle model
		model = self.view.master_model.get_thermocycle_model()
		# Create and place cycles, denature, anneal, extension, and use labels
		toplevel_label_cycle = ctk.CTkLabel(master=toplevel_cycle, text='Cycles', font=(FONT, -16))
		toplevel_label_cycle.place(x=TOPLEVEL_LABEL_CYCLE_POSX, y=TOPLEVEL_LABEL_CYCLE_POSY)
		toplevel_label_denature = ctk.CTkLabel(master=toplevel_cycle, text="Denature Temperature", font=(FONT, -16))
		toplevel_label_denature.place(x=TOPLEVEL_LABEL_DENATURE_POSX, y=TOPLEVEL_LABEL_DENATURE_POSY)
		toplevel_label_anneal = ctk.CTkLabel(master=toplevel_cycle, text="Anneal Temperature", font=(FONT, -16))
		toplevel_label_anneal.place(x=TOPLEVEL_LABEL_ANNEAL_POSX, y=TOPLEVEL_LABEL_ANNEAL_POSY)
		toplevel_label_extension = ctk.CTkLabel(master=toplevel_cycle, text="Extension Temperature", font=(FONT, -16))
		toplevel_label_extension.place(x=TOPLEVEL_LABEL_EXTENSION_POSX, y=TOPLEVEL_LABEL_EXTENSION_POSY)
		toplevel_label_use = ctk.CTkLabel(master=toplevel_cycle, text='Use', font=(FONT, -16))
		toplevel_label_use.place(x=TOPLEVEL_LABEL_USE_POSX, y=TOPLEVEL_LABEL_USE_POSY)
		# Create and place the label for thermocycler A
		toplevel_label_thermocycler_a = ctk.CTkLabel(
			master=toplevel_cycle,
			text='A',
			font=(FONT,-16)
		)
		toplevel_label_thermocycler_a.place(x=TOPLEVEL_LABEL_THERMOCYCLER_A_POSX, y=TOPLEVEL_LABEL_THERMOCYCLER_A_POSY)
		# Create and place the entry for thermocycler A's cycles
		self.a_cycles_sv = StringVar()
		self.a_cycles_sv.set(model.select(1)['cycles'])
		toplevel_entry_thermocycler_a_cycles = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_cycles_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_WIDTH,
		)
		toplevel_entry_thermocycler_a_cycles.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_CYCLES_POSY)
		# Create and place the label and entry for thermocycler A's denature temp and time
		self.a_first_denature_temp_sv = StringVar()
		self.a_first_denature_temp_sv.set(model.select(1)['first_denature_temperature'])
		toplevel_entry_thermocycler_a_denature_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_first_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_WIDTH,
		)
		toplevel_label_c_for_a = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_a.place(x=TOPLEVEL_LABEL_C_FOR_A_DENATURE_POSX, y=TOPLEVEL_LABEL_C_FOR_A_DENATURE_POSY)
		toplevel_entry_thermocycler_a_denature_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TEMP_POSY)
		self.a_first_denature_time_sv = StringVar()
		self.a_first_denature_time_sv.set(model.select(1)['first_denature_time'])
		toplevel_entry_thermocycler_a_denature_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_first_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_a_denature_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_DENATURE_TIME_POSY)
		self.a_denature_time_units_sv = StringVar()
		self.a_denature_time_units_sv.set('minutes')
		toplevel_optionmenu_thermocycler_a_denature_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.a_denature_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_a_denature_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_DENATURE_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler A's anneal temp
		self.a_anneal_temp_sv = StringVar()
		self.a_anneal_temp_sv.set(model.select(1)['anneal_temperature'])
		toplevel_entry_thermocycler_a_anneal_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_anneal_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_WIDTH,
		)
		toplevel_label_c_for_a_anneal = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_a_anneal.place(x=TOPLEVEL_LABEL_C_FOR_A_ANNEAL_POSX, y=TOPLEVEL_LABEL_C_FOR_A_ANNEAL_POSY)
		toplevel_entry_thermocycler_a_anneal_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TEMP_POSY)
		self.a_anneal_time_sv = StringVar()
		self.a_anneal_time_sv.set(model.select(1)['anneal_time'])
		toplevel_entry_thermocycler_a_anneal_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_anneal_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_a_anneal_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_ANNEAL_TIME_POSY)
		self.a_anneal_time_units_sv = StringVar()
		self.a_anneal_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_a_anneal_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.a_anneal_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_a_anneal_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_ANNEAL_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler A's extension temp
		self.a_second_denature_temp_sv = StringVar()
		self.a_second_denature_temp_sv.set(model.select(1)['second_denature_temperature'])
		toplevel_entry_thermocycler_a_extension_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_second_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_WIDTH,
		)
		toplevel_label_c_for_a_extension = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_a_extension.place(x=TOPLEVEL_LABEL_C_FOR_A_EXTENSION_POSX, y=TOPLEVEL_LABEL_C_FOR_A_EXTENSION_POSY)
		toplevel_entry_thermocycler_a_extension_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TEMP_POSY)
		self.a_second_denature_time_sv = StringVar()
		self.a_second_denature_time_sv.set(model.select(1)['second_denature_time'])
		toplevel_entry_thermocycler_a_extension_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.a_second_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_a_extension_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_A_EXTENSION_TIME_POSY)
		self.a_extension_time_units_sv = StringVar()
		self.a_extension_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_a_extension_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.a_extension_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_a_extension_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_A_EXTENSION_TIME_UNITS_POSY
		)
		# Create and place the label and checkbox for thermocycler A's use
		self.toplevel_checkbox_thermocycler_a_use_iv = IntVar()
		self.toplevel_checkbox_thermocycler_a_use_iv.set(0)
		toplevel_checkbox_thermocycler_a_use = ctk.CTkCheckBox(
			master=toplevel_cycle,
			text='',
			variable=self.toplevel_checkbox_thermocycler_a_use_iv,
			onvalue=1,
			offvalue=0,
			width=TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_WIDTH,
		)
		toplevel_checkbox_thermocycler_a_use.place(x=TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_POSX, y=TOPLEVEL_CHECKBOX_THERMOCYCLER_A_USE_POSY)
		# Create and place the label for thermocycler B
		toplevel_label_thermocycler_b = ctk.CTkLabel(
			master=toplevel_cycle,
			text='B',
			font=(FONT,-16)
		)
		toplevel_label_thermocycler_b.place(x=TOPLEVEL_LABEL_THERMOCYCLER_B_POSX, y=TOPLEVEL_LABEL_THERMOCYCLER_B_POSY)
		# Create and place the entry for thermocycler B's cycles
		self.b_cycles_sv = StringVar()
		self.b_cycles_sv.set(model.select(2)['cycles'])
		toplevel_entry_thermocycler_b_cycles = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_cycles_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_WIDTH,
		)
		toplevel_entry_thermocycler_b_cycles.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_CYCLES_POSY)
		# Create and place the label and entry for thermocycler B's denature temp and time
		self.b_first_denature_temp_sv = StringVar()
		self.b_first_denature_temp_sv.set(model.select(2)['first_denature_temperature'])
		toplevel_entry_thermocycler_b_denature_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_first_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_WIDTH,
		)
		toplevel_label_c_for_b = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_b.place(x=TOPLEVEL_LABEL_C_FOR_B_DENATURE_POSX, y=TOPLEVEL_LABEL_C_FOR_B_DENATURE_POSY)
		toplevel_entry_thermocycler_b_denature_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TEMP_POSY)
		self.b_first_denature_time_sv = StringVar()
		self.b_first_denature_time_sv.set(model.select(2)['first_denature_time'])
		toplevel_entry_thermocycler_b_denature_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_first_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_b_denature_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_DENATURE_TIME_POSY)
		self.b_denature_time_units_sv = StringVar()
		self.b_denature_time_units_sv.set('minutes')
		toplevel_optionmenu_thermocycler_b_denature_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.b_denature_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_b_denature_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_DENATURE_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler B's anneal temp
		self.b_anneal_temp_sv = StringVar()
		self.b_anneal_temp_sv.set(model.select(2)['anneal_temperature'])
		toplevel_entry_thermocycler_b_anneal_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_anneal_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_WIDTH,
		)
		toplevel_label_c_for_b_anneal = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_b_anneal.place(x=TOPLEVEL_LABEL_C_FOR_B_ANNEAL_POSX, y=TOPLEVEL_LABEL_C_FOR_B_ANNEAL_POSY)
		toplevel_entry_thermocycler_b_anneal_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TEMP_POSY)
		self.b_anneal_time_sv = StringVar()
		self.b_anneal_time_sv.set(model.select(2)['anneal_time'])
		toplevel_entry_thermocycler_b_anneal_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_anneal_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_b_anneal_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_ANNEAL_TIME_POSY)
		self.b_anneal_time_units_sv = StringVar()
		self.b_anneal_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_b_anneal_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.b_anneal_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_b_anneal_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_ANNEAL_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler B's extension temp
		self.b_second_denature_temp_sv = StringVar()
		self.b_second_denature_temp_sv.set(model.select(2)['second_denature_temperature'])
		toplevel_entry_thermocycler_b_extension_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_second_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_WIDTH,
		)
		toplevel_label_c_for_b_extension = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_b_extension.place(x=TOPLEVEL_LABEL_C_FOR_B_EXTENSION_POSX, y=TOPLEVEL_LABEL_C_FOR_B_EXTENSION_POSY)
		toplevel_entry_thermocycler_b_extension_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TEMP_POSY)
		self.b_second_denature_time_sv = StringVar()
		self.b_second_denature_time_sv.set(model.select(2)['second_denature_time'])
		toplevel_entry_thermocycler_b_extension_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.b_second_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_b_extension_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_B_EXTENSION_TIME_POSY)
		self.b_extension_time_units_sv = StringVar()
		self.b_extension_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_b_extension_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.b_extension_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_b_extension_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_B_EXTENSION_TIME_UNITS_POSY
		)
		# Create and place the label and checkbox for thermocycler B's use
		self.toplevel_checkbox_thermocycler_b_use_iv = IntVar()
		self.toplevel_checkbox_thermocycler_b_use_iv.set(0)
		toplevel_checkbox_thermocycler_b_use = ctk.CTkCheckBox(
			master=toplevel_cycle,
			text='',
			variable=self.toplevel_checkbox_thermocycler_b_use_iv,
			onvalue=1,
			offvalue=0,
			width=TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_WIDTH,
		)
		toplevel_checkbox_thermocycler_b_use.place(x=TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_POSX, y=TOPLEVEL_CHECKBOX_THERMOCYCLER_B_USE_POSY)
		# Create and place the label for thermocycler C
		toplevel_label_thermocycler_c = ctk.CTkLabel(
			master=toplevel_cycle,
			text='C',
			font=(FONT,-16)
		)
		toplevel_label_thermocycler_c.place(x=TOPLEVEL_LABEL_THERMOCYCLER_C_POSX, y=TOPLEVEL_LABEL_THERMOCYCLER_C_POSY)
		# Create and place the entry for thermocycler C's cycles
		self.c_cycles_sv = StringVar()
		self.c_cycles_sv.set(model.select(3)['cycles'])
		toplevel_entry_thermocycler_c_cycles = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_cycles_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_WIDTH,
		)
		toplevel_entry_thermocycler_c_cycles.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_CYCLES_POSY)
		# Create and place the label and entry for thermocycler C's denature temp and time
		self.c_first_denature_temp_sv = StringVar()
		self.c_first_denature_temp_sv.set(model.select(3)['first_denature_temperature'])
		toplevel_entry_thermocycler_c_denature_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_first_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_WIDTH,
		)
		toplevel_label_c_for_c = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_c.place(x=TOPLEVEL_LABEL_C_FOR_C_DENATURE_POSX, y=TOPLEVEL_LABEL_C_FOR_C_DENATURE_POSY)
		toplevel_entry_thermocycler_c_denature_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TEMP_POSY)
		self.c_first_denature_time_sv = StringVar()
		self.c_first_denature_time_sv.set(model.select(3)['first_denature_time'])
		toplevel_entry_thermocycler_c_denature_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_first_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_c_denature_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_DENATURE_TIME_POSY)
		self.c_denature_time_units_sv = StringVar()
		self.c_denature_time_units_sv.set('minutes')
		toplevel_optionmenu_thermocycler_c_denature_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.c_denature_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_c_denature_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_DENATURE_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler C's anneal temp
		self.c_anneal_temp_sv = StringVar()
		self.c_anneal_temp_sv.set(model.select(3)['anneal_temperature'])
		toplevel_entry_thermocycler_c_anneal_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_anneal_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_WIDTH,
		)
		toplevel_label_c_for_c_anneal = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_c_anneal.place(x=TOPLEVEL_LABEL_C_FOR_C_ANNEAL_POSX, y=TOPLEVEL_LABEL_C_FOR_C_ANNEAL_POSY)
		toplevel_entry_thermocycler_c_anneal_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TEMP_POSY)
		self.c_anneal_time_sv = StringVar()
		self.c_anneal_time_sv.set(model.select(3)['anneal_time'])
		toplevel_entry_thermocycler_c_anneal_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_anneal_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_c_anneal_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_ANNEAL_TIME_POSY)
		self.c_anneal_time_units_sv = StringVar()
		self.c_anneal_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_c_anneal_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.c_anneal_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_c_anneal_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_ANNEAL_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler C's extension temp
		self.c_second_denature_temp_sv = StringVar()
		self.c_second_denature_temp_sv.set(model.select(3)['second_denature_temperature'])
		toplevel_entry_thermocycler_c_extension_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_second_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_WIDTH,
		)
		toplevel_label_c_for_c_extension = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_c_extension.place(x=TOPLEVEL_LABEL_C_FOR_C_EXTENSION_POSX, y=TOPLEVEL_LABEL_C_FOR_C_EXTENSION_POSY)
		toplevel_entry_thermocycler_c_extension_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TEMP_POSY)
		self.c_second_denature_time_sv = StringVar()
		self.c_second_denature_time_sv.set(model.select(3)['second_denature_time'])
		toplevel_entry_thermocycler_c_extension_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.c_second_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_c_extension_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_C_EXTENSION_TIME_POSY)
		self.c_extension_time_units_sv = StringVar()
		self.c_extension_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_c_extension_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.c_extension_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_c_extension_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_C_EXTENSION_TIME_UNITS_POSY
		)
		# Create and place the label and checkbox for thermocycler C's use
		self.toplevel_checkbox_thermocycler_c_use_iv = IntVar()
		self.toplevel_checkbox_thermocycler_c_use_iv.set(0)
		toplevel_checkbox_thermocycler_c_use = ctk.CTkCheckBox(
			master=toplevel_cycle,
			text='',
			variable=self.toplevel_checkbox_thermocycler_c_use_iv,
			onvalue=1,
			offvalue=0,
			width=TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_WIDTH,
		)
		toplevel_checkbox_thermocycler_c_use.place(x=TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_POSX, y=TOPLEVEL_CHECKBOX_THERMOCYCLER_C_USE_POSY)
		# Create and place the label for thermocycler D
		toplevel_label_thermocycler_d = ctk.CTkLabel(
			master=toplevel_cycle,
			text='D',
			font=(FONT,-16)
		)
		toplevel_label_thermocycler_d.place(x=TOPLEVEL_LABEL_THERMOCYCLER_D_POSX, y=TOPLEVEL_LABEL_THERMOCYCLER_D_POSY)
		# Create and place the entry for thermocycler D's cycles
		self.d_cycles_sv = StringVar()
		self.d_cycles_sv.set(model.select(4)['cycles'])
		toplevel_entry_thermocycler_d_cycles = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_cycles_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_WIDTH,
		)
		toplevel_entry_thermocycler_d_cycles.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_CYCLES_POSY)
		# Create and place the label and entry for thermocycler D's denature temp and time
		self.d_first_denature_temp_sv = StringVar()
		self.d_first_denature_temp_sv.set(model.select(4)['first_denature_temperature'])
		toplevel_entry_thermocycler_d_denature_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_first_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_WIDTH,
		)
		toplevel_label_D_for_d = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_D_for_d.place(x=TOPLEVEL_LABEL_D_FOR_D_DENATURE_POSX, y=TOPLEVEL_LABEL_D_FOR_D_DENATURE_POSY)
		toplevel_entry_thermocycler_d_denature_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TEMP_POSY)
		self.d_first_denature_time_sv = StringVar()
		self.d_first_denature_time_sv.set(model.select(4)['first_denature_time'])
		toplevel_entry_thermocycler_d_denature_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_first_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_d_denature_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_DENATURE_TIME_POSY)
		self.d_denature_time_units_sv = StringVar()
		self.d_denature_time_units_sv.set('minutes')
		toplevel_optionmenu_thermocycler_d_denature_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.d_denature_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_d_denature_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_DENATURE_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler D's anneal temp
		self.d_anneal_temp_sv = StringVar()
		self.d_anneal_temp_sv.set(model.select(4)['anneal_temperature'])
		toplevel_entry_thermocycler_d_anneal_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_anneal_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_WIDTH,
		)
		toplevel_label_D_for_d_anneal = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_D_for_d_anneal.place(x=TOPLEVEL_LABEL_D_FOR_D_ANNEAL_POSX, y=TOPLEVEL_LABEL_D_FOR_D_ANNEAL_POSY)
		toplevel_entry_thermocycler_d_anneal_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TEMP_POSY)
		self.d_anneal_time_sv = StringVar()
		self.d_anneal_time_sv.set(model.select(4)['anneal_time'])
		toplevel_entry_thermocycler_d_anneal_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_anneal_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_d_anneal_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_ANNEAL_TIME_POSY)
		self.d_anneal_time_units_sv = StringVar()
		self.d_anneal_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_d_anneal_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.d_anneal_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_d_anneal_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_ANNEAL_TIME_UNITS_POSY
		)
		# Create and place the label and entry for thermocycler D's extension temp
		self.d_second_denature_temp_sv = StringVar()
		self.d_second_denature_temp_sv.set(model.select(4)['second_denature_temperature'])
		toplevel_entry_thermocycler_d_extension_temp = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_second_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_WIDTH,
		)
		toplevel_label_c_for_d_extension = ctk.CTkLabel(master=toplevel_cycle, text="C for", font=(FONT,-16))
		toplevel_label_c_for_d_extension.place(x=TOPLEVEL_LABEL_D_FOR_D_EXTENSION_POSX, y=TOPLEVEL_LABEL_D_FOR_D_EXTENSION_POSY)
		toplevel_entry_thermocycler_d_extension_temp.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TEMP_POSY)
		self.d_second_denature_time_sv = StringVar()
		self.d_second_denature_time_sv.set(model.select(4)['second_denature_time'])
		toplevel_entry_thermocycler_d_extension_time = ctk.CTkEntry(
			master=toplevel_cycle,
			textvariable=self.d_second_denature_time_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_WIDTH,
		)
		toplevel_entry_thermocycler_d_extension_time.place(x=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_POSX,
			y=TOPLEVEL_ENTRY_THERMOCYCLER_D_EXTENSION_TIME_POSY)
		self.d_extension_time_units_sv = StringVar()
		self.d_extension_time_units_sv.set('seconds')
		toplevel_optionmenu_thermocycler_d_extension_time_units = ctk.CTkOptionMenu(
			master=toplevel_cycle,
			values=['seconds', 'minutes',],
			variable=self.d_extension_time_units_sv,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_WIDTH,
		)
		toplevel_optionmenu_thermocycler_d_extension_time_units.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_D_EXTENSION_TIME_UNITS_POSY
		)
		# Create and place the label and checkbox for thermocycler D's use
		self.toplevel_checkbox_thermocycler_d_use_iv = IntVar()
		self.toplevel_checkbox_thermocycler_d_use_iv.set(0)
		toplevel_checkbox_thermocycler_d_use = ctk.CTkCheckBox(
			master=toplevel_cycle,
			text='',
			variable=self.toplevel_checkbox_thermocycler_d_use_iv,
			onvalue=1,
			offvalue=0,
			width=TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_WIDTH,
		)
		toplevel_checkbox_thermocycler_d_use.place(x=TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_POSX, y=TOPLEVEL_CHECKBOX_THERMOCYCLER_D_USE_POSY)
		# Add the add button
		toplevel_button_cycle_add = ctk.CTkButton(
			master=toplevel_cycle,
			text='Add',
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_BUTTON_CYCLE_ADD_WIDTH,
			command=self.add_cycle,
		)
		toplevel_button_cycle_add.place(x=TOPLEVEL_BUTTON_CYCLE_ADD_POSX, y=TOPLEVEL_BUTTON_CYCLE_ADD_POSY)
	
	def add_cycle(self):
		""" Method for add cycle from the toplevel cycle window """
		if self.toplevel_checkbox_thermocycler_a_use_iv.get() == False and self.toplevel_checkbox_thermocycler_b_use_iv.get() == False and self.toplevel_checkbox_thermocycler_c_use_iv.get() == False and self.toplevel_checkbox_thermocycler_d_use_iv.get() == False:
			return
		action_message = "Thermocycle: "
		# Get the data for A
		if self.toplevel_checkbox_thermocycler_a_use_iv.get() == True:
			cycles = self.a_cycles_sv.get()
			dtemp = self.a_first_denature_temp_sv.get()
			dtime = self.a_first_denature_time_sv.get()
			dunits = self.a_denature_time_units_sv.get()
			atemp = self.a_anneal_temp_sv.get()
			atime = self.a_anneal_time_sv.get()
			aunits = self.a_anneal_time_units_sv.get()
			etemp = self.a_second_denature_temp_sv.get()
			etime = self.a_second_denature_time_sv.get()
			eunits = self.a_extension_time_units_sv.get()
			action_message = action_message + f"-A- Denature at {dtemp} C for {dtime} {dunits} cycling {cycles} times between {etemp} C for {etime} {eunits} and {atemp} C for {atime} {aunits} "
		# Get the data for B
		if self.toplevel_checkbox_thermocycler_b_use_iv.get() == True:
			cycles = self.b_cycles_sv.get()
			dtemp = self.b_first_denature_temp_sv.get()
			dtime = self.b_first_denature_time_sv.get()
			dunits = self.b_denature_time_units_sv.get()
			atemp = self.b_anneal_temp_sv.get()
			atime = self.b_anneal_time_sv.get()
			aunits = self.b_anneal_time_units_sv.get()
			etemp = self.b_second_denature_temp_sv.get()
			etime = self.b_second_denature_time_sv.get()
			eunits = self.b_extension_time_units_sv.get()
			action_message = action_message + f"-B- Denature at {dtemp} C for {dtime} {dunits} cycling {cycles} times between {etemp} C for {etime} {eunits} and {atemp} C for {atime} {aunits} "
		# Get the data for C
		if self.toplevel_checkbox_thermocycler_c_use_iv.get() == True:
			cycles = self.c_cycles_sv.get()
			dtemp = self.c_first_denature_temp_sv.get()
			dtime = self.c_first_denature_time_sv.get()
			dunits = self.c_denature_time_units_sv.get()
			atemp = self.c_anneal_temp_sv.get()
			atime = self.c_anneal_time_sv.get()
			aunits = self.c_anneal_time_units_sv.get()
			etemp = self.c_second_denature_temp_sv.get()
			etime = self.c_second_denature_time_sv.get()
			eunits = self.c_extension_time_units_sv.get()
			action_message = action_message + f"-C- Denature at {dtemp} C for {dtime} {dunits} cycling {cycles} times between {etemp} C for {etime} {eunits} and {atemp} C for {atime} {aunits} "
		# Get the data for D
		if self.toplevel_checkbox_thermocycler_d_use_iv.get() == True:
			cycles = self.d_cycles_sv.get()
			dtemp = self.d_first_denature_temp_sv.get()
			dtime = self.d_first_denature_time_sv.get()
			dunits = self.d_denature_time_units_sv.get()
			atemp = self.d_anneal_temp_sv.get()
			atime = self.d_anneal_time_sv.get()
			aunits = self.d_anneal_time_units_sv.get()
			etemp = self.d_second_denature_temp_sv.get()
			etime = self.d_second_denature_time_sv.get()
			eunits = self.d_extension_time_units_sv.get()
			action_message = action_message + f"-D- Denature at {dtemp} C for {dtime} {dunits} cycling {cycles} times between {etemp} C for {etime} {eunits} and {atemp} C for {atime} {aunits} "
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Insert action into the action list
		insert_at_selected_row(action_message, selected_row, self.model)
		# Update the view
		self.view.update_treeview()

	def create_toplevel_pre_amp(self):
		""" Creates a Toplevel for the Pre-Amp """
		toplevel_pre_amp = ctk.CTkToplevel(self.view.master)
		toplevel_pre_amp.geometry(f'{TOPLEVEL_PRE_AMP_WIDTH}x{TOPLEVEL_PRE_AMP_HEIGHT}')
		# Set the ID for the Pre-Amp Thermocycler (Should be found in ThermocycleController, View, and Model)
		ID = 5 
		model = self.view.master_model.get_thermocycle_model()
		# Create and place the title label
		toplevel_pre_amp.title("Pre-Amp Thermocycling Protocol")
		# Create an place the first denature temperature label and entry
		toplevel_label_first_denature_temp = ctk.CTkLabel(
			master=toplevel_pre_amp,
			text="First Denature Temperature (C):",
			font=(FONT,-16),
		)
		toplevel_label_first_denature_temp.place(x=TOPLEVEL_LABEL_FIRST_DENATURE_TEMP_POSX,y=TOPLEVEL_LABEL_FIRST_DENATURE_TEMP_POSY)
		self.first_denature_temp_sv.set(model.select(ID)['first_denature_temperature'])
		toplevel_entry_first_denature_temp = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.first_denature_temp_sv,
			font=(FONT, -16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_WIDTH,
		)
		toplevel_entry_first_denature_temp.place(x=TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_FIRST_DENATURE_TEMP_POSY)
		# Create and place th label and entry for the first denature time
		toplevel_label_first_denature_time = ctk.CTkLabel(master=toplevel_pre_amp,
			text="First Denature Time (min):",
			font=(FONT,-16),
		)
		toplevel_label_first_denature_time.place(x=TOPLEVEL_LABEL_FIRST_DENATURE_TIME_POSX,
			y=TOPLEVEL_LABEL_FIRST_DENATURE_TIME_POSY)
		self.first_denature_time_sv.set(model.select(ID)['first_denature_time'])
		toplevel_entry_first_denature_time = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.first_denature_time_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_first_denature_time.place(x=TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_FIRST_DENATURE_TIME_POSY)
		# Create and place the cycles label and entry
		toplevel_label_cycles = ctk.CTkLabel(master=toplevel_pre_amp, text='Cycles:', font=(FONT,-16))
		toplevel_label_cycles.place(x=TOPLEVEL_LABEL_CYCLES_POSX,
			y=TOPLEVEL_LABEL_CYCLES_POSY)
		self.cycles_sv.set(model.select(ID)['cycles'])
		toplevel_entry_cycles = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.cycles_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_CYCLES_WIDTH,
		)
		toplevel_entry_cycles.place(x=TOPLEVEL_ENTRY_CYCLES_POSX,
			y=TOPLEVEL_ENTRY_CYCLES_POSY)
		# Create and place the anneal temperature label and entry
		toplevel_label_anneal_temp = ctk.CTkLabel(
			master=toplevel_pre_amp,
			text="Anneal Temperature (C):",
			font=(FONT,-16)
		)
		toplevel_label_anneal_temp.place(x=TOPLEVEL_LABEL_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_LABEL_ANNEAL_TEMP_POSY)
		self.anneal_temp_sv.set(model.select(ID)['anneal_temperature'])
		toplevel_entry_anneal_temp = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.anneal_temp_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_ANNEAL_TEMP_WIDTH,
		)
		toplevel_entry_anneal_temp.place(x=TOPLEVEL_ENTRY_ANNEAL_TEMP_POSX,
			y=TOPLEVEL_ENTRY_ANNEAL_TEMP_POSY)
		toplevel_label_anneal_time = ctk.CTkLabel(
			master=toplevel_pre_amp,
			text="Anneal Time (sec):",
			font=(FONT,-16)
		)
		toplevel_label_anneal_time.place(x=TOPLEVEL_LABEL_ANNEAL_TIME_POSX,	
			y=TOPLEVEL_LABEL_ANNEAL_TIME_POSY)
		self.anneal_time_sv.set(model.select(ID)['anneal_time'])
		toplevel_entry_anneal_time = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.anneal_time_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_ANNEAL_TIME_WIDTH,
		)
		toplevel_entry_anneal_time.place(x=TOPLEVEL_ENTRY_ANNEAL_TIME_POSX,
			y=TOPLEVEL_ENTRY_ANNEAL_TIME_POSY)
		# Create and place the second temperature label and entry
		toplevel_label_second_denature_temp = ctk.CTkLabel(
			master=toplevel_pre_amp,
			text="Second Denature Temperature (C):",
			font=(FONT,-16)
		)
		toplevel_label_second_denature_temp.place(x=TOPLEVEL_LABEL_SECOND_DENATURE_TEMP_POSX,
			y=TOPLEVEL_LABEL_SECOND_DENATURE_TEMP_POSY)
		self.second_denature_temp_sv.set(model.select(ID)['second_denature_temperature'])
		toplevel_entry_second_denature_temp = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.second_denature_temp_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_WIDTH
		)
		toplevel_entry_second_denature_temp.place(x=TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_POSX,
			y=TOPLEVEL_ENTRY_SECOND_DENATURE_TEMP_POSY)
		# Create and place the second denature time label and entry
		toplevel_label_second_denature_time = ctk.CTkLabel(
			master=toplevel_pre_amp,
			text="Second Denature Time (sec):",
			font=(FONT,-16)
		)
		toplevel_label_second_denature_time.place(x=TOPLEVEL_LABEL_SECOND_DENATURE_TIME_POSX,
			y=TOPLEVEL_LABEL_SECOND_DENATURE_TIME_POSY)
		self.second_denature_time_sv.set(model.select(ID)['second_denature_time'])
		toplevel_entry_second_denature_time = ctk.CTkEntry(
			master=toplevel_pre_amp,
			textvariable=self.second_denature_time_sv,
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_WIDTH,
		)
		toplevel_entry_second_denature_time.place(x=TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_POSX,
			y=TOPLEVEL_ENTRY_SECOND_DENATURE_TIME_POSY)
		# Create and place the Add button
		self.toplevel_button_add_pre_amp = ctk.CTkButton(
			master=toplevel_pre_amp,
			text='Add',
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_BUTTON_ADD_PRE_AMP_WIDTH,
			command=self.add_pre_amp,
		)
		self.toplevel_button_add_pre_amp.place(x=TOPLEVEL_BUTTON_ADD_PRE_AMP_POSX,
			y=TOPLEVEL_BUTTON_ADD_PRE_AMP_POSY)

	def add_pre_amp(self) -> None:
		""" Updates the Pre-Amp Protocol to be added to the action list """
		# Get the data
		fdtemp = self.first_denature_temp_sv.get()
		fdtime = self.first_denature_time_sv.get()
		cycles = self.cycles_sv.get()
		atemp = self.anneal_temp_sv.get()
		atime = self.anneal_time_sv.get()
		sdtemp = self.second_denature_temp_sv.get()
		sdtime = self.second_denature_time_sv.get()
		action_message = f"Thermocycle Pre-Amp at {fdtemp} C for {fdtime} minutes and cycle {cycles} times between {sdtemp} C for {sdtime} seconds and {atemp} C for {atime} seconds"
		# Determine which if any row of the treeview is selected
		try:
			selected_row = self.view.treeview.selection()[0]
		except:
			selected_row = None
		# Insert action into the action list
		insert_at_selected_row(action_message, selected_row, self.model)
		# Update the view
		self.view.update_treeview()
