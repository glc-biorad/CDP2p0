import time
import threading
from tkinter import StringVar

from gui.util.browse_files import browse_files 
from gui.util.next_action_allowed import next_action_allowed

# Import the model and view for this controller
from gui.models.build_protocol_model import BuildProtocolModel
from gui.views.build_protocol_frame import BuildProtocolFrame

# Import the state model to keep track of tips and volumes
from gui.models.state_model import StateModel

# Constants
INITIAL_PROTOCOL_FILENAME = 'protocol.txt'
NO_TRAY_CONSUMABLES = ["Pre-Amp Thermocycler", "Assay Strip", "Heater/Shaker", "Mag Separator", "Chiller", "Tip Transfer Tray"]
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
]

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

		# Get the state model
		self.state = StateModel(self.model.db_name, self.model.cursor, self.model.connection)
	
		# Variable for keeping track of the volume in the pipettor tips
		self.volume = 0

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
			pass
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
						tip = '1000'
					elif column == '2':
						tip = '1000'
					elif column == '3':
						tip = '1000'
					elif column == '4':
						tip = '1000'
					elif column == '5':
						tip = '50'
					elif column == '6':
						tip = '50'
					elif column == '7':
						tip = '50'
					elif column == '8':
						tip = '50'
					elif column == '9':
						tip = '50'
					elif column == '10':
						tip = '50'
					elif column == '11':
						tip = '50'
					elif column == '12':
						tip = '50'
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
			# Inset action into the action list
			self.model.insert(len(self.model.actions), action_message)
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
			pass
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
		# Inset action into the action list
		self.model.insert(len(self.model.actions), action_message)
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
		# Generate the action message
		action_message = f"{action.title()} {volume} uLs with {tip} uL tips at {pressure} pressure {count} {times}"
		# Check if this action is allowed
		if next_action_allowed(self.state, action):
			# Update the state model
			self.state.insert(tip, self.volume, action.lower())
			# Insert action into the action list
			self.model.insert(len(self.model.actions), action_message)
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
		# Generate the action message
		action_message = f"Delay for {time_} {units}"
		# Inset action into the action list
		self.model.insert(len(self.model.actions), action_message)
		# Update the view
		self.view.update_treeview()

	def add_other_action(self, event=None) -> None:
		"""Deals with adding an other action to the model from the view
		"""
		# Get the action data
		other = self.view.other_option_sv.get()
		# Generate the action message
		action_message = other
		# Inset action into the action list
		self.model.insert(len(self.model.actions), action_message)
		# Update the view
		self.view.update_treeview()

	def start(self, event=None) -> None:
		"""Deals with starting the protocol
		"""
		# Set the progress bar to 0
		self.view.progressbar.set(0)
		# Set the action progress label to 0 of N actions
		n_actions = len(self.model.select())
		self.view.label_action_progress.configure(text=f"Action Progress: 0 of {n_actions}")
		# Start the protocol
		thread = threading.Thread(target=self.start_protocol)
		thread.run()

	def start_protocol(self):
		"""Process for starting the protocol
		"""
		# Show a small bit of progress
		n_actions = len(self.model.select())
		if n_actions != 0:
			progress = 100 * 0.5 / n_actions
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
					a = 1
				# Eject tips in {tray} column {column}
				else:
					a = 1
			elif split[0] == 'Pickup':
				# Pickup tips in {tray} column {column}
				time.sleep(1)
			elif split[0] == 'Tip-press':
				time.sleep(1)
			elif split[0] == 'Move':
				# Check if this is just a relative move
				if split[1] == 'relative':
					a = 1
					return None
				# Or a chip move
				elif split[1] == 'chip':
					a = 1
					return None
				# Or a lid move
				elif split[1] == 'lid':
					return None
				# Get the consumable
				i0 = 2
				try:
					# Use the tray to get where the consumable words end
					i1 = split.index('tray')
				except ValueError:
					# Use the column to get where the consumable words end
					i1 = split.index('column')
				consumable = " ".join(split[i0:i1])
				# Get the tray
				try:
					tray = split[split.index('tray') + 1]
				except ValueError:
					tray = None
				# Get the column
				try:
					column = split[split.index('column') + 1]
				except ValueError:
					column = None
				# Get the tip size
				tip = split[split.index('tips') - 2]
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
				# Setup the command
				a = 1
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
						print(f"Aspirate: {volume}, {tip}, {pressure}")
					if action == 'Dispense':
						print(f"Dispense: {volume}, {tip}, {pressure}")
					if action == 'Mix':
						print(f"Aspirate: {volume}, {tip}, {pressure}")
						print(f"Dispense: {volume}, {tip}, {pressure}")
			elif split[0] == 'Delay':
				# Get the time
				value = int(split[2])
				# Get the units
				units = split[3]
				# Setup the command
				print(f"{value}, {units}")
			elif split[0] == 'Home':
				a = 1
			elif split[0] == 'Generate':
				# Get the droplet type
				droplet_type = split[1]
				a = 1
			elif split[0] == 'Pre-Amp':
				a = 1
			elif split[0] == 'Shake':
				# Get the mode
				mode = split[1]
				if mode.lower() == 'on':
					print("Shake On")
				elif mode.lower() == 'off':
					print("Shake off")
			elif split[0] == 'Engage':
				print(action_message)
			elif split[0] == 'Disengage':
				print(action_message)
			# Update the progress bar
			progress = 100 * (int(i) + 1 ) / n_actions
			self.view.progressbar.set(progress)
			print(self.state.select())

	def load(self, event=None) -> None:
		"""Deals with the loading of a protocol into the action treeview
		"""
		# Browse the file system to open a protocol
		file = browse_files('r', "Load Protocol", INITIAL_PROTOCOL_FILENAME, '../protocols/A')
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
		file = browse_files('w', "Save Protocol", INITIAL_PROTOCOL_FILENAME, '../protocols/A')
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
