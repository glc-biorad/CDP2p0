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
		self.view.mainloop()
