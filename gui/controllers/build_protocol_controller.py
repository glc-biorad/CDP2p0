import os
import time
import sqlite3
import threading
from tkinter import StringVar
import tkinter as tk
import customtkinter as ctk

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
	'Close',
	'Open',
	'Lower',
	'Raise',
	'Change',
	'Comment:',
	'Pause',
]
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
		except:
			print("No Upper Gantry for BuildProtocolController")
			self.upper_gantry = None

		# Initialize the reader
		try:
			self.reader = Reader()
		except:
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
		elif 'Lower' in action_message.split():
			amount = self.view.other_parameter_sv.get()
			try:
				amount = int(amount)
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
			elif split[0] == 'Tip-press':
				time.sleep(1)
			elif split[0] == 'Move':
				# Check if this is just a relative move
				if split[1] == 'relative':
					amount = int(split[-1])
					direction = split[2]
					self.upper_gantry.move_relative(direction, amount, velocity='fast')
					continue
				# Or a chip move
				elif split[1] == 'chip':
					a = 1
					return None
				# Or a lid move
				elif split[1] == 'lid':
					tray = split[2]
					column=1
					#column = split[2]
					# Get the coordinates for the lid and tray
					unit = self.model.db_name[-4]
					table_name = f"Unit {unit} Upper Gantry Coordinates"
					coordinate = self.coordinates_model.select(table_name, "Lid Tray", tray, column)
					lid = [coordinate[0][4], coordinate[0][5], coordinate[0][6], coordinate[0][7]]
					if column == 1:
						tray = [-18500, -1781750, -552000, -1198000]
					else:
						print("Only Lid D works right now")
					# Move the lid
					self.upper_gantry.move_lid_new(lid, tray)
					continue
				i0 = 2
				try:
					# Use the tray to get where the consumable words end
					i1 = split.index('tray')
				except ValueError:
					# Use the column to get where the consumable words end
					i1 = split.index('column')
				consumable = " ".join(split[i0:i1])
				if consumable in ["Tip Box", "DG8"]:
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
						for i in range(count):
							self.upper_gantry.aspirate(volume, pipette_tip_type=tip, pressure=pressure)
					if action == 'Dispense':
						for i in range(count):
							self.upper_gantry.dispense(volume, pressure=pressure)
					if action == 'Mix':
						for i in range(count):
							print(f'Mix Count: {i+1}/{count}')
							self.upper_gantry.aspirate(volume, pipette_tip_type=tip, pressure=pressure)
							self.upper_gantry.dispense(volume, pressure=pressure)
			elif split[0] == 'Delay':
				# Get the time
				value = int(split[2])
				# Get the units
				units = split[3]
				# Setup the command
				delay(value, units)
			elif split[0] == 'Add':
				# Get the comment
				continue
			elif split[0] == 'Pause':
				# Open a message box for the user 
				if tk.messagebox.askokcancel(title="Protocol Pause", message="Would you like to continue?"):
					continue
				else:
					if tk.messagebox.askyesno(title="Protocol Pause", message="Canceling the protocol now loses all current progress, are you sure you want to cancel?"):
						return None
					else:
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
			elif split[0] == 'Generate':
				# Get the droplet type
				droplet_type = split[1]
				# Generate the droplets
				self.upper_gantry.generate_droplets(droplet_type)
			elif split[0] == 'Pre-Amp':
				a = 1
			elif split[0] == 'Shake':
				# Get the mode
				mode = split[1]
				if mode.lower() == 'on':
					rpm = split[-1]
					self.upper_gantry.turn_on_shake(rpm=rpm)
				elif mode.lower() == 'off':
					self.upper_gantry.turn_off_shake()
			elif split[0] == 'Engage':
				self.upper_gantry.engage_magnet()
			elif split[0] == 'Disengage':
				self.upper_gantry.disengage_magnet()
			elif split[0] == 'Thermocycle':
				# Initialize the Meerstetter
				try:
					self.meerstetter = Meerstetter()
				except Exception as e:
					print(e)
					print("No Meerstetter for BuildProtocolController")
					self.meerstetter = None
				print('Thermocycle')
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
			elif split[0] == 'Open':
				# Open the tray
				self.reader.open_tray(split[2])
			elif split[0] == 'Close':
				# Close the tray
				self.reader.close_thermocycler_tray(split[2], -780000)
			elif split[0] == 'Lower':
				# Get the position to move the heater to
				amount = -abs(int(split[-2]))
				# Lower the thermocycler
				address = ADDRESSES[split[2]]
				self.reader.get_fast_api_interface().reader.axis.move('reader', address, amount, 100000, True, True)
			elif split[0] == 'Raise':
				# Raise the thermocycler
				self.reader.raise_heater(split[2])
			elif split[0] == 'Change':
				# Get the temp
				temp = float(split[-2])
				# Change the Heater/Shaker temperature
				self.upper_gantry.change_heater_shaker_temperature(temp)
			# Update the progress bar
			progress = (int(i) + 1 ) / n_actions
			self.view.progressbar.set(progress)

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
