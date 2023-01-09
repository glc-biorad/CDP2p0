import tkinter as tk

class ThermocycleController:
	"""
	System for passing data from the Thermocycle View to the Thermocycle Model
	"""
	def __init__(self, model, view) -> None:
		self.model = model
		self.view = view
		
		# Setup the defaults for the loaded view
		self.model.setup_defaults()

	def get_thermocycler_sv(self, id: int) -> tk.StringVar:
		return self.model.thermocycler_sv

	def get_cycles_sv(self, id: int) -> tk.StringVar:
		return self.model.cycles_sv

	def get_cycles(self, ID: int) -> int:
		"""Gets the number of cycles for a given thermocycler ID"""
		# Make sure the ID is valid
		assert ID in [1,2,3,4]
		# Get the cycles
		return int(self.model.select(ID)['cycles'])

	def set_cycles(self, ID: int, cycles: int) -> None:
		self.model.update(ID, cycles=cycles)

	def get_use_a_iv(self, id: int) -> tk.IntVar:
		return self.model.use_a_iv

	def get_use_b_iv(self, id: int) -> tk.IntVar:
		return self.model.use_b_iv

	def get_use_c_iv(self, id: int) -> tk.IntVar:
		return self.model.use_c_iv

	def get_use_d_iv(self, id: int) -> tk.IntVar:
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

	def get_first_denature_time_sv(self, id: int) -> tk.StringVar:
		return self.model.first_denature_time_sv
	
	def get_first_denature_time(self, ID: int) -> int:
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

	def get_anneal_time_sv(self, id: int) -> tk.StringVar:
		return self.model.anneal_time_sv

	def get_anneal_time(self, ID: int) -> int:
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

	def get_second_denature_time_sv(self, id: int) -> tk.StringVar:
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
