"""
System which passes data from the GUI to the model
"""
from gui.models.model import Model
from gui.views.view import View

from gui.controllers.build_protocol_controller import BuildProtocolController
from gui.controllers.optimize_controller import OptimizeController

class Controller:
	def __init__(self, model: Model, view: View) -> None:
		self.model = model
		self.view = view
		self.build_protocol_controller = BuildProtocolController(
			model=self.model.get_build_protocol_model(),
			view=self.view.build_protocol_frame
		)
		self.optimize_controller = OptimizeController(
			model=self.model.get_optimize_model(),
			view=self.view.optimize_frame
		)

	def setup_bindings(self) -> None:
		self.build_protocol_controller.setup_bindings()
		self.optimize_controller.setup_bindings()

	def run(self) -> None:
		self.view.bind('<Up>', self.backwards)
		self.view.bind('<Down>', self.forwards)
		self.view.bind('<Left>', self.left)
		self.view.bind('<Right>', self.right)
		self.view.bind('<Shift Up>', self.up)
		self.view.bind('<Shift Down>', self.down)
		self.view.mainloop()

	def backwards(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the Y value for the relative move backwards
			y = int(self.optimize_controller.view.y_sv.get())
			upper_gantry.move_relative('backwards', y, velocity='slow')

	def forwards(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the Y value for the relative move backwards
			y = int(self.optimize_controller.view.y_sv.get())
			upper_gantry.move_relative('forwards', y, velocity='slow')

	def left(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the X value for the relative move backwards
			x = int(self.optimize_controller.view.x_sv.get())
			upper_gantry.move_relative('left', x, velocity='slow')

	def right(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the X value for the relative move backwards
			x = int(self.optimize_controller.view.x_sv.get())
			upper_gantry.move_relative('right', x, velocity='slow')

	def up(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the Z value for the relative move backwards
			z = int(self.optimize_controller.view.y_sv.get())
			upper_gantry.move_relative('up', z, velocity='slow')

	def down(self, event):
		""" Deals with moving relative moves
		"""
		# Import the upper gantry for the relative move command
		from api.upper_gantry.upper_gantry import UpperGantry
		upper_gantry = UpperGantry()
		# Get the x value of labels on the tabs we are interested to check which tab is open relative to the parent
		x_optimize = self.optimize_controller.view.label_consumable.winfo_x()
		# Determine which tab we are on based on the position of a single widget
		if x_optimize != 0:
			# Get the Z value for the relative move backwards
			z = int(self.optimize_controller.view.z_sv.get())
			upper_gantry.move_relative('down', z, velocity='slow')

