"""
Model represents the data for the GUI
"""
import sqlite3

from models.thermocycle_model import ThermocycleModel
from models.build_protocol_model import BuildProtocolModel
from models.optimize_model import OptimizeModel

DB_NAME = 'cdp2p0_gui.db'

from models.tip_use_model import TipUseModel
from models.state_model import StateModel

class Model:
	# Models
	thermocycle_model: ThermocycleModel = None

	def __init__(self) -> None:
		self.connection = sqlite3.connect(DB_NAME)
		self.cursor = self.connection.cursor()
		#m = TipUseModel(DB_NAME, self.cursor, self.connection)
		mm = StateModel(DB_NAME, self.cursor, self.connection)
		mm.drop_table()
		mm.create_table()
		#print(mm.select())
		#print(m.select())

	def get_thermocycle_model(self) -> ThermocycleModel:
		self.thermocycle_model = ThermocycleModel(DB_NAME, self.cursor, self.connection)
		return self.thermocycle_model

	def get_build_protocol_model(self) -> BuildProtocolModel:
		self.build_protocol_model = BuildProtocolModel(DB_NAME, self.cursor, self.connection)
		return self.build_protocol_model

	def get_optimize_model(self) -> OptimizeModel:
		self.optimize_model = OptimizeModel(DB_NAME, self.cursor, self.connection)
		return self.optimize_model
