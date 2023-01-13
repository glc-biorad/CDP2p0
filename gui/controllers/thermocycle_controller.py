import threading
import tkinter as tk

# Import utility
from api.util.utils import delay


class ThermocycleController:
	"""
	System for passing data from the Thermocycle View to the Thermocycle Model
	"""
	def __init__(self, model, view) -> None:
		self.model = model
		self.view = view
		
		# Setup the defaults for the loaded view
		self.model.setup_defaults()

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
		if use['B']:
			print(f"B goes to {first_denature_temperatures['B']} for {first_denature_times['B']}")
		if use['C']:
			print(f"C goes to {first_denature_temperatures['C']} for {first_denature_times['C']}")
		if use['D']:
			print(f"D goes to {first_denature_temperatures['D']} for {first_denature_times['D']}")
		#delay(first_denature_times['A'], 'minutes')
		# Cycle 
		for i in range(n_cycles['A']):
			print(f"Cycles {i+1}/{n_cycles['A']}")
			if use['A']:
				print(f"A goes to {second_denature_temperatures['A']} for {second_denature_times['A']}")
			if use['B']:
				print(f"B goes to {second_denature_temperatures['B']} for {second_denature_times['B']}")
			if use['C']:
				print(f"C goes to {second_denature_temperatures['C']} for {second_denature_times['C']}")
			if use['D']:
				print(f"D goes to {second_denature_temperatures['D']} for {second_denature_times['D']}")
			#delay(second_denature_times['A'], 'seconds')
			if use['A']:
				print(f"A goes to {anneal_temperatures['A']} for {anneal_times['A']}")
			if use['B']:
				print(f"B goes to {anneal_temperatures['B']} for {anneal_times['B']}")
			if use['C']:
				print(f"C goes to {anneal_temperatures['C']} for {anneal_times['C']}")
			if use['D']:
				print(f"D goes to {anneal_temperatures['D']} for {anneal_times['D']}")
			#delay(anneal_times['A'], 'seconds')
			
		# Lower the temperature to 30 deg C	
		if use['A']:
			print('A goes to 30')
		if use['B']:
			print('B goes to 30')
		if use['C']:
			print('C goes to 30')
		if use['D']:
			print('D goes to 30')

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
