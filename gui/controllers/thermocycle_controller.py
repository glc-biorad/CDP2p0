import os
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image

# Import utility
from api.util.utils import delay
from gui.util.browse_files import browse_files

# Import the fast api interface
try:
	from api.interfaces.fast_api_interface import FastAPIInterface
except:
	print("Can't import FastAPIInterface for the ThermocycleController")

# Import Meerstetter API
try:
	from api.reader.meerstetter.meerstetter import Meerstetter
except:
	print("Couldn't import Meerstetter for the ThermocycleController")

# Constants
INITIAL_PROTOCOL_FILENAME = 'protocol.txt'
THERMOCYCLERS = ['A', 'B', 'C', 'D']
THERMOCYCLER_IDS = {
	'A': 1,
	'B': 2,
	'C': 3,
	'D': 4,
	"Aux Heater A": 5,
	"Aux Heater B": 6,
	"Aux Heater C": 7,
	"Aux Heater D": 8,
	"Pre-Amp Thermocycler": 9,
}
ADDRESSES = {
	'A': 8,
	'B': 9,
	'C': 10,
	'D': 11,
	'AB': 6,
	'CD': 7,
}
THERMOCYCLER_VALUES = (
	'A',
	'B',
	'C',
	'D',
	"Pre-Amp Thermocycler",
)
FONT = "Sergio UI"
TOPLEVEL_SETTINGS_WIDTH = 265
TOPLEVEL_SETTINGS_HEIGHT = 270
TOPLEVEL_LABEL_CLAMPS_POSX = 110
TOPLEVEL_LABEL_CLAMPS_POSY = 10
TOPLEVEL_LABEL_A_POSX = 20 
TOPLEVEL_LABEL_A_POSY = 40
TOPLEVEL_ENTRY_CLAMP_A_POSX = 50
TOPLEVEL_ENTRY_CLAMP_A_POSY = 40
TOPLEVEL_ENTRY_CLAMP_A_WIDTH = 150
TOPLEVEL_BUTTON_A_POSX = 205
TOPLEVEL_BUTTON_A_POSY = 40
TOPLEVEL_BUTTON_A_WIDTH = 35
TOPLEVEL_LABEL_B_POSX = 20 
TOPLEVEL_LABEL_B_POSY = 70
TOPLEVEL_ENTRY_CLAMP_B_POSX = 50
TOPLEVEL_ENTRY_CLAMP_B_POSY = 70
TOPLEVEL_ENTRY_CLAMP_B_WIDTH = 150
TOPLEVEL_BUTTON_B_POSX = 205
TOPLEVEL_BUTTON_B_POSY = 70
TOPLEVEL_BUTTON_B_WIDTH = 35
TOPLEVEL_LABEL_C_POSX = 20 
TOPLEVEL_LABEL_C_POSY = 100
TOPLEVEL_ENTRY_CLAMP_C_POSX = 50
TOPLEVEL_ENTRY_CLAMP_C_POSY = 100
TOPLEVEL_ENTRY_CLAMP_C_WIDTH = 150
TOPLEVEL_BUTTON_C_POSX = 205
TOPLEVEL_BUTTON_C_POSY = 100
TOPLEVEL_BUTTON_C_WIDTH = 35
TOPLEVEL_LABEL_D_POSX = 20 
TOPLEVEL_LABEL_D_POSY = 130
TOPLEVEL_ENTRY_CLAMP_D_POSX = 50
TOPLEVEL_ENTRY_CLAMP_D_POSY = 130
TOPLEVEL_ENTRY_CLAMP_D_WIDTH = 150
TOPLEVEL_BUTTON_D_POSX = 205
TOPLEVEL_BUTTON_D_POSY = 130
TOPLEVEL_BUTTON_D_WIDTH = 35
TOPLEVEL_LABEL_TRAYS_POSX = 120
TOPLEVEL_LABEL_TRAYS_POSY = 170
TOPLEVEL_LABEL_TRAY_AB_POSX = 15
TOPLEVEL_LABEL_TRAY_AB_POSY = 200
TOPLEVEL_ENTRY_TRAY_AB_POSX = 50
TOPLEVEL_ENTRY_TRAY_AB_POSY = 200
TOPLEVEL_ENTRY_TRAY_AB_WIDTH = 150
TOPLEVEL_BUTTON_AB_POSX = 205
TOPLEVEL_BUTTON_AB_POSY = 200
TOPLEVEL_BUTTON_AB_WIDTH = 35
TOPLEVEL_LABEL_TRAY_CD_POSX = 15
TOPLEVEL_LABEL_TRAY_CD_POSY = 230
TOPLEVEL_ENTRY_TRAY_CD_POSX = 50
TOPLEVEL_ENTRY_TRAY_CD_POSY = 230
TOPLEVEL_ENTRY_TRAY_CD_WIDTH = 150
TOPLEVEL_BUTTON_CD_POSX = 205
TOPLEVEL_BUTTON_CD_POSY = 230
TOPLEVEL_BUTTON_CD_WIDTH = 35
TOPLEVEL_TEC_WIDTH = 370
TOPLEVEL_TEC_HEIGHT = 120
TOPLEVEL_LABEL_THERMOCYCLER_POSX = 20
TOPLEVEL_LABEL_THERMOCYCLER_POSY = 5
TOPLEVEL_OPTIONMENU_THERMOCYCLER_POSX = 140
TOPLEVEL_OPTIONMENU_THERMOCYCLER_POSY = 5
TOPLEVEL_OPTIONMENU_THERMOCYCLER_WIDTH = 210
TOPLEVEL_LABEL_TEMPERATURE_POSX = 25
TOPLEVEL_LABEL_TEMPERATURE_POSY = 45
TOPLEVEL_ENTRY_TEMPERATURE_POSX = 140
TOPLEVEL_ENTRY_TEMPERATURE_POSY = 45
TOPLEVEL_ENTRY_TEMPERATURE_WIDTH = 60
TOPLEVEL_LABEL_TEC_C_POSX = 205
TOPLEVEL_LABEL_TEC_C_POSY = 45
TOPLEVEL_BUTTON_GET_POSX = 225
TOPLEVEL_BUTTON_GET_POSY = 45
TOPLEVEL_BUTTON_GET_WIDTH = 60
TOPLEVEL_BUTTON_SET_POSX = 290
TOPLEVEL_BUTTON_SET_POSY = 45
TOPLEVEL_BUTTON_SET_WIDTH = 60
TOPLEVEL_BUTTON_SET_COLOR = '#10adfe' 
TOPLEVEL_BUTTON_RESET_POSX = 140
TOPLEVEL_BUTTON_RESET_POSY = 85
TOPLEVEL_BUTTON_RESET_WIDTH = 210
TOPLEVEL_BUTTON_RESET_COLOR = '#fc0303'

class ThermocycleController:
	"""
	System for passing data from the Thermocycle View to the Thermocycle Model
	"""
	def __init__(self, model, view) -> None:
		self.model = model
		self.view = view
		
		# Setup the defaults for the loaded view
		self.model.setup_defaults()

		# Initialize the FastAPI interface for controlling the trays and thermocycler clamps
		try:
			self.fast_api_interface = FastAPIInterface()
		except:
			print("Couldn't connect to the FastAPI interface with the ThermocyclerController!")

	def setup_bindings(self):
		""" Setup the binding between this controller and its view """
		self.view.trace_cycles_sv(self.trace_cycles)
		self.view.trace_first_denature_time_sv(self.trace_first_denature_time)
		self.view.trace_anneal_time_sv(self.trace_anneal_time)
		self.view.trace_second_denature_time_sv(self.trace_second_denature_time)
		self.view.trace_use_a_iv(self.trace_use_a)
		self.view.trace_use_b_iv(self.trace_use_b)
		self.view.trace_use_c_iv(self.trace_use_c)
		self.view.trace_use_d_iv(self.trace_use_d)
		self.view.bind_button_start(self.start)
		self.view.bind_button_save(self.save)
		self.view.bind_button_load(self.load)
		self.view.bind_button_home(self.home)
		self.view.bind_button_settings(self.settings)
		self.view.bind_button_tec(self.tec)

	def get_thermocycler_sv(self, id: int = None) -> tk.StringVar:
		return self.model.thermocycler_sv

	def get_cycles_sv(self, id: int = None) -> tk.StringVar:
		return self.model.cycles_sv

	def get_cycles(self, ID: int) -> int:
		"""Gets the number of cycles for a given thermocycler ID"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the cycles
		return int(self.model.select(ID)['cycles'])

	def set_cycles(self, ID: int, cycles: int) -> None:
		self.model.update(ID, cycles=cycles)

	def get_use_a_iv(self, id: int = None) -> tk.IntVar:
		return self.model.use_a_iv

	def get_use_b_iv(self, id: int = None) -> tk.IntVar:
		return self.model.use_b_iv

	def get_use_c_iv(self, id: int = None) -> tk.IntVar:
		return self.model.use_c_iv

	def get_use_d_iv(self, id: int= None) -> tk.IntVar:
		return self.model.use_d_iv

	def get_first_denature_temperature_sv(self, id: int) -> tk.StringVar:
		return self.model.first_denature_temperature_sv

	def get_first_denature_temperature(self, ID: int) -> int:
		"""Gets the first denature temperature value from the ThermocycleModel

		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the temperature
		return int(self.model.select(ID)['first_denature_temperature'])

	def set_first_denature_temperature(self, ID: int, first_denature_temperature: int) -> None:
		"""Sets the First Denature Temperature value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		first_denature_temperature : int
			Temperature value to be set for the thermocycler
		"""
		self.model.update(ID, first_denature_temperature=first_denature_temperature)

	def get_anneal_temperature_sv(self, id: int) -> tk.StringVar:
		return self.model.anneal_temperature_sv

	def get_anneal_temperature(self, ID: int) -> int:
		"""Gets the anneal temperature value from the ThermocycleModel

		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the temperature
		return int(self.model.select(ID)['anneal_temperature'])

	def set_anneal_temperature(self, ID: int, anneal_temperature: int) -> None:
		"""Sets the Anneal Temperature value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		anneal_temperature : int
			Temperature value to be set for the thermocycler
		"""
		self.model.update(ID, anneal_temperature=anneal_temperature)

	def get_second_denature_temperature_sv(self, id: int) -> tk.StringVar:
		return self.model.second_denature_temperature_sv

	def get_second_denature_temperature(self, ID: int) -> int:
		"""Gets the second denature temperature value from the ThermocycleModel

		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the temperature
		return int(self.model.select(ID)['second_denature_temperature'])

	def set_second_denature_temperature(self, ID: int, second_denature_temperature: int) -> None:
		"""Sets the Second Denature Temperature value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		second_denature_temperature : int
			Temperature value to be set for the thermocycler
		"""
		self.model.update(ID, second_denature_temperature=second_denature_temperature)

	def get_first_denature_time_sv(self, id: int=None) -> tk.StringVar:
		return self.model.first_denature_time_sv
	
	def get_first_denature_time(self, ID: int = None) -> int:
		"""Gets the first denature time for the given ID for the thermocycler
	
		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the time
		return int(self.model.select(ID)['first_denature_time'])

	def set_first_denature_time(self, ID: int, value: int) -> None:
		"""Sets the time value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		value : int
			Time value to be set for the thermocycler
		"""
		self.model.update(ID, first_denature_time=value)

	def get_anneal_time_sv(self, id: int = None) -> tk.StringVar:
		return self.model.anneal_time_sv

	def get_anneal_time(self, ID: int = None) -> int:
		"""Gets the anneal time for the given ID for the thermocycler

		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the time
		return int(self.model.select(ID)['anneal_time'])

	def set_anneal_time(self, ID: int, value: int) -> None:
		"""Sets the time value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		value : int
			Time value to be set for the thermocycler
		"""
		self.model.update(ID, anneal_time=value)

	def get_second_denature_time_sv(self, id: int = None) -> tk.StringVar:
		return self.model.second_denature_time_sv

	def get_second_denature_time(self, ID: int) -> int:
		"""Gets the second denature time for the given ID for the thermocycler
	
		Parameters
		----------
		ID : int
			ID for the thermocycler of interest
		"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the time
		return int(self.model.select(ID)['second_denature_time'])

	def set_second_denature_time(self, ID: int, value: int) -> None:
		"""Sets the time value for a thermocycler with an ID

		Parameters
		----------
		ID : int
			ID (primary key) for the thermocycler of interest
		value : int
			Time value to be set for the thermocycler
		"""
		self.model.update(ID, second_denature_time=value)

	def get_clamp(self, ID: int) -> int:
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the IntVar
		return self.model.select(ID)['clamp']

	def set_clamp(self, ID: int, state: int) -> None:
		self.model.update(ID, clamp=state)

	def start(self, event=None) -> None:
		""" Starts the thread for thermocycling on thermocyclers A, B, C, and D """
		# Start the thermocyclers
		thread = threading.Thread(target=self.thread_start)
		thread.start()

	def thread_start(self) -> None:
		""" Starts the thermocyclers with multithreading """
		# Initialize the Meerstetter
		try:
			self.meerstetter = Meerstetter()
		except Exception as e:
			print(e)
			print("Coulnd't connect to the Meerstetter with the ThermocycleController!")
		print('here')
		# Get the thermocycler data
		n_cycles = {
			'A': self.get_cycles(1),
			'B': self.get_cycles(2),
			'C': self.get_cycles(3),
			'D': self.get_cycles(4),
		}
		use = {
			'A': int(self.model.select(ID=1)['use']),
			'B': int(self.model.select(ID=2)['use']),
			'C': int(self.model.select(ID=3)['use']),
			'D': int(self.model.select(ID=4)['use']),
		}
		first_denature_temperatures = {
			'A': self.get_first_denature_temperature(1),
			'B': self.get_first_denature_temperature(2),
			'C': self.get_first_denature_temperature(3),
			'D': self.get_first_denature_temperature(4),
		}
		anneal_temperatures = {
			'A': self.get_anneal_temperature(1),
			'B': self.get_anneal_temperature(2),
			'C': self.get_anneal_temperature(3),
			'D': self.get_anneal_temperature(4),
		}
		second_denature_temperatures = {
			'A': self.get_second_denature_temperature(1),
			'B': self.get_second_denature_temperature(2),
			'C': self.get_second_denature_temperature(3),
			'D': self.get_second_denature_temperature(4),
		}
		first_denature_times = {
			'A': self.get_first_denature_time(1),
			'B': self.get_first_denature_time(2),
			'C': self.get_first_denature_time(3),
			'D': self.get_first_denature_time(4),
		}
		anneal_times = {
			'A': self.get_anneal_time(1),
			'B': self.get_anneal_time(2),
			'C': self.get_anneal_time(3),
			'D': self.get_anneal_time(4),
		}
		second_denature_times = {
			'A': self.get_second_denature_time(1),
			'B': self.get_second_denature_time(2),
			'C': self.get_second_denature_time(3),
			'D': self.get_second_denature_time(4),
		}
		# Start the first denature step
		if use['A']:
			print(f"A goes to {first_denature_temperatures['A']} for {first_denature_times['A']}")
			self.meerstetter.change_temperature(1, first_denature_temperatures['A'], block=False)
		if use['B']:
			print(f"B goes to {first_denature_temperatures['B']} for {first_denature_times['B']}")
			try:
				self.meerstetter.change_temperature(2, first_denature_temperatures['B'], block=False)
			except Exception as e:
				print(e)
		if use['C']:
			print(f"C goes to {first_denature_temperatures['C']} for {first_denature_times['C']}")
			self.meerstetter.change_temperature(3, first_denature_temperatures['C'], block=False)
		if use['D']:
			print(f"D goes to {first_denature_temperatures['D']} for {first_denature_times['D']}")
			self.meerstetter.change_temperature(4, first_denature_temperatures['D'], block=False)
		delay(first_denature_times['A'], 'minutes')
		# Cycle 
		for i in range(n_cycles['A']):
			print(f"Cycles {i+1}/{n_cycles['A']}")
			if use['A']:
				print(f"A goes to {second_denature_temperatures['A']} for {second_denature_times['A']}")
				self.meerstetter.change_temperature(1, second_denature_temperatures['A'], block=False)
			if use['B']:
				print(f"B goes to {second_denature_temperatures['B']} for {second_denature_times['B']}")
				self.meerstetter.change_temperature(2, second_denature_temperatures['B'], block=False)
			if use['C']:
				print(f"C goes to {second_denature_temperatures['C']} for {second_denature_times['C']}")
				self.meerstetter.change_temperature(3, second_denature_temperatures['C'], block=False)
			if use['D']:
				print(f"D goes to {second_denature_temperatures['D']} for {second_denature_times['D']}")
				self.meerstetter.change_temperature(4, second_denature_temperatures['D'], block=False)
			delay(second_denature_times['A'], 'seconds')
			if use['A']:
				print(f"A goes to {anneal_temperatures['A']} for {anneal_times['A']}")
				self.meerstetter.change_temperature(1, anneal_temperatures['A'], block=False)
			if use['B']:
				print(f"B goes to {anneal_temperatures['B']} for {anneal_times['B']}")
				self.meerstetter.change_temperature(2, anneal_temperatures['B'], block=False)
			if use['C']:
				print(f"C goes to {anneal_temperatures['C']} for {anneal_times['C']}")
				self.meerstetter.change_temperature(3, anneal_temperatures['C'], block=False)
			if use['D']:
				print(f"D goes to {anneal_temperatures['D']} for {anneal_times['D']}")
				self.meerstetter.change_temperature(4, anneal_temperatures['D'], block=False)
			delay(anneal_times['A'], 'seconds')
			
		# Lower the temperature to 30 deg C	
		if use['A']:
			print('A goes to 30')
			self.meerstetter.change_temperature(1, 30, block=False)
		if use['B']:
			print('B goes to 30')
			self.meerstetter.change_temperature(2, 30, block=False)
		if use['C']:
			print('C goes to 30')
			self.meerstetter.change_temperature(3, 30, block=False)
		if use['D']:
			print('D goes to 30')
			self.meerstetter.change_temperature(4, 30, block=False)
		# Close the Meerstetter connection
		self.meerstetter.close()

	def trace_cycles(self, *args) -> None:
		""" Deals with the cycles entry changing """
		# Make all cycles this value
		try:
			n_cycles = int(self.view.entry_cycles.get())
			for i in range(1,5):
				self.model.update(ID=i, cycles=n_cycles)
		except:
			pass

	def trace_first_denature_time(self, *args) -> None:
		""" Deals with the changing of the first denature time entry """
		# Make all the times the same """
		try:
			first_denature_time = int(self.view.entry_first_denature_time.get())
			for i in range(1,5):
				self.model.update(ID=i, first_denature_time=first_denature_time)
		except:
			pass

	def trace_anneal_time(self, *args) -> None:
		""" Deals with the changing of the anneal time entry """
		# Make all the times the same """
		try:
			anneal_time = int(self.view.entry_anneal_time.get())
			for i in range(1,5):
				self.model.update(ID=i, anneal_time=anneal_time)
		except:
			pass

	def trace_second_denature_time(self, *args) -> None:
		""" Deals with the changing of the second denature time entry """
		# Make all the times the same """
		try:
			second_denature_time = int(self.view.entry_second_denature_time.get())
			for i in range(1,5):
				self.model.update(ID=i, second_denature_time=second_denature_time)
		except:
			pass

	def trace_use_a(self, *args) -> None:
		""" Deals with the changing of the use a checkbox """
		try:
			# Get the use
			use = int(self.view.checkbox_a.get())
			# Update the model
			self.model.update(ID=1, use=use)
		except:
			pass

	def trace_use_b(self, *args) -> None:
		""" Deals with the changing of the use a checkbox """
		try:
			# Get the use
			use = int(self.view.checkbox_b.get())
			# Update the model
			self.model.update(ID=2, use=use)
		except:
			pass

	def trace_use_c(self, *args) -> None:
		""" Deals with the changing of the use a checkbox """
		try:
			# Get the use
			use = int(self.view.checkbox_c.get())
			# Update the model
			self.model.update(ID=3, use=use)
		except:
			pass

	def trace_use_d(self, *args) -> None:
		""" Deals with the changing of the use a checkbox """
		try:
			# Get the use
			use = int(self.view.checkbox_d.get())
			# Update the model
			self.model.update(ID=4, use=use)
		except:
			pass

	def load(self, event=None) -> None:
		""" Open a file browser to select a file to load """
		# Open the file browser
		file = browse_files('r', "Load Protocol", INITIAL_PROTOCOL_FILENAME, r'protocols\{0}'.format(self.model.unit.upper()))
		# Read line by line through the file
		try:
			lines = [line.rstrip('n') for line in file]
			for line in lines:
				line = line.split(',')
				thermocycler = line[0]
				# Make sure the first column is a valid unit
				if thermocycler in THERMOCYCLERS:
					# Get the data
					use = line[1]
					cycles = line[2]
					first_denature_temperature = line[3]
					first_denature_time = line[4]
					anneal_temperature = line[5]
					anneal_time = line[6]
					second_denature_temperature = line[7]
					second_denature_time = line[8]
					# Store the data
					self.model.update(
						ID = THERMOCYCLER_IDS[thermocycler],
						use=use,
						first_denature_temperature=first_denature_temperature,
						first_denature_time=first_denature_time,
						anneal_temperature=anneal_temperature,
						anneal_time=anneal_time,
						second_denature_temperature=second_denature_temperature,
						second_denature_time=second_denature_time
					)
					if thermocycler == 'A':
						self.view.use_a_iv.set(use)
					elif thermocycler == 'B':
						self.view.use_b_iv.set(use)
					elif thermocycler == 'C':
						self.view.use_c_iv.set(use)
					elif thermocycler == 'D':
						self.view.use_d_iv.set(use)
			# Update the string vars for current selected thermocyclers entries
			ID = THERMOCYCLER_IDS[self.view.thermocycler_sv.get()]
			self.view.entry_cycles.delete(0, tk.END)
			self.view.entry_cycles.insert(0, cycles)
			self.view.entry_first_denature_temp.delete(0, tk.END)
			self.view.entry_first_denature_temp.insert(0, self.model.select(ID)['first_denature_temperature'])
			self.view.entry_first_denature_time.delete(0, tk.END)
			self.view.entry_first_denature_time.insert(0, self.model.select(ID)['first_denature_time'])
			self.view.entry_anneal_temp.delete(0, tk.END)
			self.view.entry_anneal_temp.insert(0, self.model.select(ID)['anneal_temperature'])
			self.view.entry_anneal_time.delete(0, tk.END)
			self.view.entry_anneal_time.insert(0, self.model.select(ID)['anneal_time'])
			self.view.entry_second_denature_temp.delete(0, tk.END)
			self.view.entry_second_denature_temp.insert(0, self.model.select(ID)['second_denature_temperature'])
			self.view.entry_second_denature_time.delete(0, tk.END)
			self.view.entry_second_denature_time.insert(0, self.model.select(ID)['second_denature_time'])
			# Close the file
			file.close()
		except Exception as e:
			print(e)
			print("Could not open file for loading the thermocycling protocols")
			pass

	def home(self, event=None) -> None:
		return None

	def save(self, event=None) -> None:
		""" Save the checked protocols """
		# Open a file browser to save the file (creates a file for each checked file_unit.csv)
		file = browse_files('w', "Save Protocol", INITIAL_PROTOCOL_FILENAME, r'protocols\{0}'.format(self.model.unit.upper()))
		file.write('unit,use,cycles,first denature temperature, first denature time, anneal temperature, anneal time, second denature temperature, second denature time,\n')
		# Save the protocol for each thermocycler
		for thermocycler in THERMOCYCLERS:
			# Get the ID
			ID = THERMOCYCLER_IDS[thermocycler]
			# Get the data for this thermocycler
			cycles = self.model.select(ID)['cycles']
			use = self.model.select(ID)['use']
			first_denature_temperature = self.model.select(ID)['first_denature_temperature']
			first_denature_time = self.model.select(ID)['first_denature_time']
			anneal_temperature = self.model.select(ID)['anneal_temperature']
			anneal_time = self.model.select(ID)['anneal_time']
			second_denature_temperature = self.model.select(ID)['second_denature_temperature']
			second_denature_time = self.model.select(ID)['second_denature_time']
			data = f'{thermocycler},{use},{cycles},{first_denature_temperature},{first_denature_time},{anneal_temperature},{anneal_time},{second_denature_temperature},{second_denature_time},\n'
			file.write(data)
		# Close the file
		file.close()

	def settings(self, event=None) -> None:
		""" Create a Toplevel window to set the settings """
		self.create_settings_toplevel()

	def create_settings_toplevel(self) -> None:
		""" Create a Toplevel window for the settings """
		self.toplevel_settings = ctk.CTkToplevel(self.view.master)
		self.toplevel_settings.geometry(f'{TOPLEVEL_SETTINGS_WIDTH}x{TOPLEVEL_SETTINGS_HEIGHT}')
		self.toplevel_settings.title("Settings")
		# Create and place Clamps label
		self.toplevel_label_clamps = ctk.CTkLabel(master=self.toplevel_settings, text='Clamps', font=(FONT,-16))
		self.toplevel_label_clamps.place(x=TOPLEVEL_LABEL_CLAMPS_POSX, y=TOPLEVEL_LABEL_CLAMPS_POSY)
		# Create and place the Clamp Settings for Thermocycler A
		self.toplevel_label_a = ctk.CTkLabel(master=self.toplevel_settings, text='A', font=(FONT,-16))
		self.toplevel_label_a.place(x=TOPLEVEL_LABEL_A_POSX, y=TOPLEVEL_LABEL_A_POSY)
		self.clamp_a_sv = tk.StringVar()
		self.clamp_a_sv.set('-400000')
		self.toplevel_entry_clamp_a = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.clamp_a_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_CLAMP_A_WIDTH,
		)
		self.toplevel_entry_clamp_a.place(x=TOPLEVEL_ENTRY_CLAMP_A_POSX, y=TOPLEVEL_ENTRY_CLAMP_A_POSY)
		self.toplevel_button_a = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_A_WIDTH,
			command=self.move_a,
		)
		self.toplevel_button_a.place(x=TOPLEVEL_BUTTON_A_POSX, y=TOPLEVEL_BUTTON_A_POSY)
		# Create and place the Clamp Settings for Thermocycler B
		self.toplevel_label_b = ctk.CTkLabel(master=self.toplevel_settings, text='B', font=(FONT,-16))
		self.toplevel_label_b.place(x=TOPLEVEL_LABEL_B_POSX, y=TOPLEVEL_LABEL_B_POSY)
		self.clamp_b_sv = tk.StringVar()
		self.clamp_b_sv.set('-400000')
		self.toplevel_entry_clamp_b = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.clamp_b_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_CLAMP_B_WIDTH,
		)
		self.toplevel_entry_clamp_b.place(x=TOPLEVEL_ENTRY_CLAMP_B_POSX, y=TOPLEVEL_ENTRY_CLAMP_B_POSY)
		self.toplevel_button_b = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_B_WIDTH,
			command=self.move_b,
		)
		self.toplevel_button_b.place(x=TOPLEVEL_BUTTON_B_POSX, y=TOPLEVEL_BUTTON_B_POSY)
		# Create and place the clamp settings for thermocycler C
		self.toplevel_label_c = ctk.CTkLabel(master=self.toplevel_settings, text='C', font=(FONT,-16))
		self.toplevel_label_c.place(x=TOPLEVEL_LABEL_C_POSX, y=TOPLEVEL_LABEL_C_POSY)
		self.clamp_c_sv = tk.StringVar()
		self.clamp_c_sv.set('-400000')
		self.toplevel_entry_clamp_c = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.clamp_c_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_CLAMP_C_WIDTH,
		)
		self.toplevel_entry_clamp_c.place(x=TOPLEVEL_ENTRY_CLAMP_C_POSX, y=TOPLEVEL_ENTRY_CLAMP_C_POSY)
		self.toplevel_button_c = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_C_WIDTH,
			command=self.move_c,
		)
		self.toplevel_button_c.place(x=TOPLEVEL_BUTTON_C_POSX, y=TOPLEVEL_BUTTON_C_POSY)
		# Create and place the clamp settings for thermocycler D
		self.toplevel_label_d = ctk.CTkLabel(master=self.toplevel_settings, text='D', font=(FONT,-16))
		self.toplevel_label_d.place(x=TOPLEVEL_LABEL_D_POSX, y=TOPLEVEL_LABEL_D_POSY)
		self.clamp_d_sv = tk.StringVar()
		self.clamp_d_sv.set('-400000')
		self.toplevel_entry_clamp_d = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.clamp_d_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_CLAMP_D_WIDTH,
		)
		self.toplevel_entry_clamp_d.place(x=TOPLEVEL_ENTRY_CLAMP_D_POSX, y=TOPLEVEL_ENTRY_CLAMP_D_POSY)
		self.toplevel_button_d = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_D_WIDTH,
			command=self.move_d,
		)
		self.toplevel_button_d.place(x=TOPLEVEL_BUTTON_D_POSX, y=TOPLEVEL_BUTTON_D_POSY)
		# Create and place trays label
		self.toplevel_label_tray = ctk.CTkLabel(master=self.toplevel_settings, text='Trays', font=(FONT,-16))
		self.toplevel_label_tray.place(x=TOPLEVEL_LABEL_TRAYS_POSX, y=TOPLEVEL_LABEL_TRAYS_POSY)
		# Create and place tray settings for tray ab
		self.toplevel_label_ab = ctk.CTkLabel(master=self.toplevel_settings, text='AB', font=(FONT,-16))
		self.toplevel_label_ab.place(x=TOPLEVEL_LABEL_TRAY_AB_POSX, y=TOPLEVEL_LABEL_TRAY_AB_POSY)
		self.tray_ab_sv = tk.StringVar()
		self.tray_ab_sv.set('-790000')
		self.toplevel_entry_tray_ab = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.tray_ab_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_TRAY_AB_WIDTH,
		)
		self.toplevel_entry_tray_ab.place(x=TOPLEVEL_ENTRY_TRAY_AB_POSX, y=TOPLEVEL_ENTRY_TRAY_AB_POSY)
		self.toplevel_button_ab = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_AB_WIDTH,
			command=self.move_tray_ab,
		)
		self.toplevel_button_ab.place(x=TOPLEVEL_BUTTON_AB_POSX, y=TOPLEVEL_BUTTON_AB_POSY)
		# Create and place tray settings for tray cd
		self.toplevel_label_cd = ctk.CTkLabel(master=self.toplevel_settings, text='CD', font=(FONT,-16))
		self.toplevel_label_cd.place(x=TOPLEVEL_LABEL_TRAY_CD_POSX, y=TOPLEVEL_LABEL_TRAY_CD_POSY)
		self.tray_cd_sv = tk.StringVar()
		self.tray_cd_sv.set('-790000')
		self.toplevel_entry_tray_cd = ctk.CTkEntry(
			master=self.toplevel_settings,
			textvariable=self.tray_cd_sv,
			font=(FONT,-14),
			corner_radius=2,
			width=TOPLEVEL_ENTRY_TRAY_CD_WIDTH,
		)
		self.toplevel_entry_tray_cd.place(x=TOPLEVEL_ENTRY_TRAY_CD_POSX, y=TOPLEVEL_ENTRY_TRAY_CD_POSY)
		self.toplevel_button_cd = ctk.CTkButton(
			master=self.toplevel_settings,
			text='Move',
			font=(FONT,-14),
			width=TOPLEVEL_BUTTON_CD_WIDTH,
			command=self.move_tray_cd,
		)
		self.toplevel_button_cd.place(x=TOPLEVEL_BUTTON_CD_POSX, y=TOPLEVEL_BUTTON_CD_POSY)

	def move_a(self, event=None) -> None:
		""" Move clamp A from the settings toplevel window """
		thread = threading.Thread(target=self.thread_move_a)
		thread.start()
	def thread_move_a(self) -> None:
		""" Move clamp A on a thread """
		# Get the value to move to
		val = int(self.clamp_a_sv.get())
		# If val is 0 raise the heater
		if abs(val) == 0:
			try:
				self.view.photoimage_thermocycler_block_a = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_raised']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_A_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT),
				)
				self.set_clamp(1, 0)
				self.view.image_thermocycler_block_a.configure(image=self.view.photoimage_thermocycler_block_a)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['A'], 0, 80000, True)
				self.fast_api_interface.reader.axis.home('reader', ADDRESSES['A'])
			except Exception as e:
				pass
		else:
			val = -abs(val)
			try:
				self.view.photoimage_thermocycler_block_a = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_lowered']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_A_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT),
				)
				self.set_clamp(1, 0)
				self.view.image_thermocycler_block_a.configure(image=self.view.photoimage_thermocycler_block_a)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['A'], val, 80000, False)
			except Exception as e:
				pass

	def move_b(self, event=None) -> None:
		""" Move clamp A from the settings toplevel window """
		thread = threading.Thread(target=self.thread_move_b)
		thread.start()
	def thread_move_b(self) -> None:
		""" Move clamp B on a thread """
		# Get the value to move to
		val = int(self.clamp_b_sv.get())
		# If val is 0 raise the heater
		if abs(val) == 0:
			try:
				self.view.photoimage_thermocycler_block_b = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_raised']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_B_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT),
				)
				self.set_clamp(2, 0)
				self.view.image_thermocycler_block_b.configure(image=self.view.photoimage_thermocycler_block_b)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['B'], 0, 80000, True)
				self.fast_api_interface.reader.axis.home('reader', ADDRESSES['B'])
			except Exception as e:
				pass
		else:
			val = -abs(val)
			try:
				self.view.photoimage_thermocycler_block_b = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_lowered']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_B_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT),
				)
				self.set_clamp(2, 0)
				self.view.image_thermocycler_block_b.configure(image=self.view.photoimage_thermocycler_block_b)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['B'], val, 80000, False)
			except Exception as e:
				pass

	def move_c(self, event=None) -> None:
		""" Move clamp C from the settings toplevel window """
		thread = threading.Thread(target=self.thread_move_c)
		thread.start()
	def thread_move_c(self) -> None:
		""" Move clamp C on a thread """
		# Get the value to move to
		val = int(self.clamp_c_sv.get())
		# If val is 0 raise the heater
		if abs(val) == 0:
			try:
				self.view.photoimage_thermocycler_block_c = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_raised']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_C_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT),
				)
				self.set_clamp(3, 0)
				self.view.image_thermocycler_block_c.configure(image=self.view.photoimage_thermocycler_block_c)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['C'], 0, 80000, True)
				self.fast_api_interface.reader.axis.home('reader', ADDRESSES['C'])
			except Exception as e:
				pass
		else:
			val = -abs(val)
			try:
				self.view.photoimage_thermocycler_block_c = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_lowered']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_C_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT),
				)
				self.set_clamp(3, 0)
				self.view.image_thermocycler_block_c.configure(image=self.view.photoimage_thermocycler_block_c)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['C'], val, 80000, False)
			except Exception as e:
				pass

	def move_d(self, event=None) -> None:
		""" Move clamp D from the settings toplevel window """
		thread = threading.Thread(target=self.thread_move_d)
		thread.start()
	def thread_move_d(self) -> None:
		""" Move clamp D on a thread """
		# Get the value to move to
		val = int(self.clamp_d_sv.get())
		# If val is 0 raise the heater
		if abs(val) == 0:
			try:
				self.view.photoimage_thermocycler_block_d = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_raised']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_D_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT),
				)
				self.set_clamp(4, 0)
				self.view.image_thermocycler_block_d.configure(image=self.view.photoimage_thermocycler_block_d)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['D'], 0, 80000, True)
				self.fast_api_interface.reader.axis.home('reader', ADDRESSES['D'])
			except Exception as e:
				pass
		else:
			val = -abs(val)
			try:
				self.view.photoimage_thermocycler_block_d = ctk.CTkImage(
					dark_image=Image.open(self.view.IMAGE_PATHS['thermocycler_block_lowered']),
					size=(self.view.IMAGE_THERMOCYCLER_BLOCK_D_WIDTH, self.view.IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT),
				)
				self.set_clamp(4, 0)
				self.view.image_thermocycler_block_d.configure(image=self.view.photoimage_thermocycler_block_d)
				self.fast_api_interface.reader.axis.move('reader', ADDRESSES['D'], val, 80000, False)
			except Exception as e:
				pass

	def move_tray_ab(self, event=None) -> None:
		""" Move tray ab """
		thread = threading.Thread(target=self.thread_move_tray_ab)
		thread.start()
	def thread_move_tray_ab(self) -> None:
		""" Move Tray AB using a thread """
		# Get the tray position value
		val = int(self.tray_ab_sv.get())
		print(val)
		# If trying to home go fast then force a home
		if abs(val) == 0:
			try:
				# Get the current posx
				posx = int(self.view.image_thermocycler_tray_ab.place_info()['x'])
				if (posx == self.view.IMAGE_THERMOCYCLER_TRAY_AB_POSX):
					return None
				# Make sure the tray is allowed to close
				if True:
					self.view.move_tray(ADDRESSES['AB'],
						self.view.image_thermocycler_tray_ab, 
						posx,
						self.view.IMAGE_THERMOCYCLER_TRAY_AB_POSX,
						steps=0,
					)
				#self.fast_api_interface.reader.axis.move('reader', ADDRESSES['AB'], 0, 200000, True)
				#self.fast_api_interface.reader.axis.home('reader', ADDRESSES['AB'], False)
			except Exception as e:
				pass
		else:
			val = -abs(val)
			try:
				# Get the current posx
				posx = int(self.view.image_thermocycler_tray_ab.place_info()['x'])
				# Compute the new posx based on the real space value given in the tray entry
				posx_diff = abs(self.view.IMAGE_THERMOCYCLER_TRAY_AB_POSX - self.view.TRAY_CLOSED_POSX)
				fully_closed = -790000
				real_ratio = val/fully_closed
				x = int(self.view.IMAGE_THERMOCYCLER_TRAY_AB_POSX + posx_diff * real_ratio)
				if (posx == x):
					return None
				# Make sure the tray is allowed to close
				if True:
					self.view.move_tray(ADDRESSES['AB'],
						self.view.image_thermocycler_tray_ab, 
						posx,
						x,
						steps=val,
					)
				#self.fast_api_interface.reader.axis.move('reader', ADDRESSES['AB'], val, 200000, False)
			except Exception as e:
				pass

	def move_tray_cd(self, event=None) -> None:
		""" Move tray ab """
		thread = threading.Thread(target=self.thread_move_tray_cd)
		thread.start()
	def thread_move_tray_cd(self) -> None:
		""" Move Tray AB using a thread """
		# Get the tray position value
		val = int(self.tray_cd_sv.get())
		print(val)
		# If trying to home go fast then force a home
		if abs(val) == 0:
			try:
				# Get the current posx
				posx = int(self.view.image_thermocycler_tray_cd.place_info()['x'])
				#if (posx == self.view.IMAGE_THERMOCYCLER_TRAY_CD_POSX):
				#	return None
				# Make sure the tray is allowed to open
				if True:
					self.view.move_tray(ADDRESSES['CD'],
						self.view.image_thermocycler_tray_cd, 
						posx,
						self.view.IMAGE_THERMOCYCLER_TRAY_CD_POSX,
						steps=0,
					)
				#self.fast_api_interface.reader.axis.move('reader', ADDRESSES['AB'], 0, 200000, True)
				#self.fast_api_interface.reader.axis.home('reader', ADDRESSES['AB'], False)
			except Exception as e:
				print(e)
				pass
		else:
			val = -abs(val)
			try:
				# Get the current posx
				posx = int(self.view.image_thermocycler_tray_cd.place_info()['x'])
				# Compute the new posx based on the real space value given in the tray entry
				posx_diff = abs(self.view.IMAGE_THERMOCYCLER_TRAY_CD_POSX - self.view.TRAY_CLOSED_POSX)
				fully_closed = -790000
				real_ratio = val/fully_closed
				x = int(self.view.IMAGE_THERMOCYCLER_TRAY_CD_POSX + posx_diff * real_ratio)
				if (posx == x):
					return None
				# Make sure the tray is allowed to close
				if True:
					self.view.move_tray(ADDRESSES['CD'],
						self.view.image_thermocycler_tray_cd, 
						posx,
						x,
						steps=val,
					)
				#self.fast_api_interface.reader.axis.move('reader', ADDRESSES['AB'], val, 200000, False)
			except Exception as e:
				pass

	def tec(self, event=None) -> None:
		""" Create a Toplevel window to deal with the TEC """
		self.create_tec_toplevel()
	def create_tec_toplevel(self) -> None:
		""" Create a Toplevel window for the TEC """
		self.toplevel_tec = ctk.CTkToplevel(self.view.master)
		self.toplevel_tec.geometry(f'{TOPLEVEL_TEC_WIDTH}x{TOPLEVEL_TEC_HEIGHT}')
		self.toplevel_tec.title("TEC")
		# Create and place the Thermocycler label and optionmenu
		self.toplevel_label_thermocycler = ctk.CTkLabel(
			master=self.toplevel_tec, 
			text='Thermocycler:', 
			font=(FONT,-16),
		)
		self.toplevel_label_thermocycler.place(x=TOPLEVEL_LABEL_THERMOCYCLER_POSX, 
			y=TOPLEVEL_LABEL_THERMOCYCLER_POSY)
		self.thermocycler_sv = tk.StringVar()
		self.thermocycler_sv.set('')
		self.toplevel_optionmenu_thermocycler = ctk.CTkOptionMenu(
			master=self.toplevel_tec,
			variable=self.thermocycler_sv,
			values=THERMOCYCLER_VALUES,
			font=(FONT,-12),
			corner_radius=2,
			width=TOPLEVEL_OPTIONMENU_THERMOCYCLER_WIDTH,
		)
		self.toplevel_optionmenu_thermocycler.place(x=TOPLEVEL_OPTIONMENU_THERMOCYCLER_POSX,
			y=TOPLEVEL_OPTIONMENU_THERMOCYCLER_POSY)
		# Create and place the temperature label, entry, and buttons
		self.toplevel_label_temperature = ctk.CTkLabel(
			master=self.toplevel_tec,
			text='Temperature:',
			font=(FONT,-16),
		)
		self.toplevel_label_temperature.place(x=TOPLEVEL_LABEL_TEMPERATURE_POSX,
			y=TOPLEVEL_LABEL_TEMPERATURE_POSY)
		self.temperature_sv = tk.StringVar()
		self.temperature_sv.set('')
		self.toplevel_entry_temperature = ctk.CTkEntry(
			master=self.toplevel_tec,
			textvariable=self.temperature_sv,
			font=(FONT,-16),
			width=TOPLEVEL_ENTRY_TEMPERATURE_WIDTH,
		)
		self.toplevel_entry_temperature.place(x=TOPLEVEL_ENTRY_TEMPERATURE_POSX,
			y=TOPLEVEL_ENTRY_TEMPERATURE_POSY)
		self.toplevel_label_tec_c = ctk.CTkLabel(
			master=self.toplevel_tec,
			text='C',
			font=(FONT,-16),
		)
		self.toplevel_label_tec_c.place(x=TOPLEVEL_LABEL_TEC_C_POSX,
			y=TOPLEVEL_LABEL_TEC_C_POSY)
		self.toplevel_button_get = ctk.CTkButton(
			master=self.toplevel_tec,
			text='Get',
			font=(FONT,-16),
			corner_radius=2,
			width=TOPLEVEL_BUTTON_GET_WIDTH,
			command=self.get,
		)
		self.toplevel_button_get.place(x=TOPLEVEL_BUTTON_GET_POSX,
			y=TOPLEVEL_BUTTON_GET_POSY)
		self.toplevel_button_set = ctk.CTkButton(
			master=self.toplevel_tec,
			text='Set',
			font=(FONT,-16),
			corner_radius=2,
			fg_color=TOPLEVEL_BUTTON_SET_COLOR,
			width=TOPLEVEL_BUTTON_SET_WIDTH,
			command=self.set,
		)
		self.toplevel_button_set.place(x=TOPLEVEL_BUTTON_SET_POSX,
			y=TOPLEVEL_BUTTON_SET_POSY)
		# Create and place the Reset button
		self.toplevel_button_reset = ctk.CTkButton(
			master=self.toplevel_tec,
			text='Reset',
			font=(FONT,-16),
			corner_radius=2,
			fg_color=TOPLEVEL_BUTTON_RESET_COLOR,
			width=TOPLEVEL_BUTTON_RESET_WIDTH,
			command=self.reset,
		)
		self.toplevel_button_reset.place(x=TOPLEVEL_BUTTON_RESET_POSX,
			y=TOPLEVEL_BUTTON_RESET_POSY)

	def reset(self, event=None) -> None:
		""" Reset the desired thermocycler """
		thread = threading.Thread(target=self.thread_reset)
		thread.start()
	def thread_reset(self) -> None:
		""" Function for reseting the Thermocyclers on a Thread """
		# Get the thermocycler selected on the TEC Toplevel window
		thermocycler = self.thermocycler_sv.get()
		if thermocycler != '':
			# Initialize the Meerstetter object
			try:
				self.meerstetter = Meerstetter()
			except Exception as e:
				print(e)
				print("Couldn't initialize Meerstetter for the ThermocycleController")
				return None
			# Reset the meerstetter board based on the thermocycler's address
			address = THERMOCYCLER_IDS[thermocycler]
			self.meerstetter.reset_device(address)
			# Close the Meerstetter connection
			self.meerstetter.close()

	def set(self, event=None) -> None:
		""" Set the temperature for the desired thermocycler """
		thread = threading.Thread(target=self.thread_set)
		thread.start()
	def thread_set(self) -> None:
		""" Function for setting the temperature of the set Thermocycler on a Thread """
		# Get the thermocycler selected on the TEC Toplevel window 
		thermocycler = self.thermocycler_sv.get()
		if thermocycler != '':
			try:
				temperature = int(self.temperature_sv.get())
			except Exception as e:
				print(e)
				print("The temperature entered must be an integer")
				return None
			# Initialize the Meerstetter object
			try:
				self.meerstetter = Meerstetter()
			except Exception as e:
				print(e)
				print("Couldn't initialize Meerstetter for the ThermocycleController")
				return None
			# Set the temperature 
			address = THERMOCYCLER_IDS[thermocycler]
			self.meerstetter.change_temperature(address, temperature, block=False)
			# Close the Meerstetter connection
			self.meerstetter.close()

	def get(self, event=None) -> None:
		""" Get the temperature for the desired thermocycler """
		thread = threading.Thread(target=self.thread_get)
		thread.start()
	def thread_get(self) -> None:
		""" Function for getting the temperature of the set Thermocycler on a Thread """
		# Get the thermocycler selected on the TEC Toplevel window 
		thermocycler = self.thermocycler_sv.get()
		if thermocycler != '':
			# Initialize the Meerstetter object
			try:
				self.meerstetter = Meerstetter()
			except Exception as e:
				print(e)
				print("Couldn't initialize Meerstetter for the ThermocycleController")
				return None
			# Get the temperature 
			address = THERMOCYCLER_IDS[thermocycler]
			temperature = float(self.meerstetter.get_temperature(address))
			self.temperature_sv.set(f'{str(round(temperature,1))}')
			# Close the Meerstetter connection
			self.meerstetter.close()
