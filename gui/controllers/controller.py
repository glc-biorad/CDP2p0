"""
System which passes data from the GUI to the model
"""
import threading

from api.util.controller import Controller as ComPortController

from gui.models.model import Model
from gui.views.view import View

from gui.controllers.image_controller import ImageController
from gui.controllers.thermocycle_controller import ThermocycleController
from gui.controllers.build_protocol_controller import BuildProtocolController
from gui.controllers.optimize_controller import OptimizeController
from gui.controllers.configure_controller import ConfigureController

from gui.views.image_frame import ImageFrame
from gui.views.optimize_frame import OptimizeFrame

# Import utilities
from gui.util.insert_at_selected_row import insert_at_selected_row

# Import the upper gantry
try:
	from api.upper_gantry.upper_gantry import UpperGantry
except:
	print("Upper gantry could not be imported for the Controller")

# Import the reader api
try:
	from api.reader.reader import Reader
except:
	print("Reader could not be imported for the Controller")

class Controller:
	def __init__(self, model: Model, view: View, meerstetter_com_port: ComPortController) -> None:
		self.model = model
		self.view = view
		self.meerstetter_com_port_controller = meerstetter_com_port
		self.image_controller = ImageController(
			model=self.model.get_image_model(),
			view=self.view.image_frame
		)
		self.thermocycle_controller = ThermocycleController(
			model=self.model.get_thermocycle_model(),
			view=self.view.thermocycle_frame,
			controller=self
		)
		self.build_protocol_controller = BuildProtocolController(
			model=self.model.get_build_protocol_model(),
			view=self.view.build_protocol_frame,
			controller=self
		)
		self.optimize_controller = OptimizeController(
			model=self.model.get_optimize_model(),
			view=self.view.optimize_frame
		)
		self.configure_controller = ConfigureController(
			model=self.model.get_configure_model(),
			view=self.view.configure_frame
		)
		try:
			self.upper_gantry = UpperGantry()
		except:
			self.upper_gantry = None
		try: 
			self.reader = Reader()
		except:
			self.reader = None

	def setup_bindings(self) -> None:
		self.image_controller.setup_bindings()
		self.thermocycle_controller.setup_bindings()
		self.build_protocol_controller.setup_bindings()
		self.optimize_controller.setup_bindings()
		self.configure_controller.setup_bindings()

	def run(self) -> None:
		self.view.bind('<Up>', self.backwards)
		self.view.bind('<Down>', self.forwards)
		self.view.bind('<Left>', self.left)
		self.view.bind('<Right>', self.right)
		self.view.bind('<Shift Up>', self.up)
		self.view.bind('<Shift Down>', self.down)
		self.view.bind('<Control-c>', self.copy)
		self.view.bind('<Control-v>', self.paste)
		self.view.bind('<Control-x>', self.cut)
		self.view.bind('<Control-a>', self.all)
		self.view.bind('<Shift H>', self.home_imager)
		self.view.mainloop()

	def thread_relative_reader(self, direction: str, value: int, velocity: str) -> None:
		""" Thread for moving the reader relatively """
		self.reader = Reader()
		self.reader.move_imager_relative(direction, value, velocity)
		self.reader.close()
	def thread_relative_upper_gantry(self, direction: str, value: int, velocity: str) -> None:
		""" Thread for moving the upper gantry relatively """
		self.upper_gantry = UpperGantry()
		self.upper_gantry.move_relative(direction, value, velocity)
		self.upper_gantry.close()

	def backwards(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			y = int(current_frame.dy_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('backwards', y, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			y = int(self.optimize_controller.view.y_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('backwards', y, 'slow',))
			thread.start()
		else:
			return None

	def forwards(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			y = int(current_frame.dy_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('forwards', y, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			y = int(self.optimize_controller.view.y_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('forwards', y, 'slow',))
			thread.start()
		else:
			return None

	def left(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			x = int(current_frame.dx_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('left', x, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			x = int(self.optimize_controller.view.x_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('left', x, 'slow',))
			thread.start()
		else:
			return None

	def right(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			x = int(current_frame.dx_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('right', x, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			x = int(self.optimize_controller.view.x_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('right', x, 'slow',))
			thread.start()
		else:
			return None

	def up(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			z = int(current_frame.dz_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('up', z, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			z = int(self.optimize_controller.view.z_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('up', z, 'slow',))
			thread.start()
		else:
			return None

	def down(self, event):
		""" Deals with moving relative moves
		"""
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			z = int(current_frame.dz_sv.get())
			thread = threading.Thread(target=self.thread_relative_reader, args=('down', z, 'slow',))
			thread.start()
		elif type(current_frame) == OptimizeFrame:
			z = int(self.optimize_controller.view.z_sv.get())
			thread = threading.Thread(target=self.thread_relative_upper_gantry, args=('down', z, 'slow',))
			thread.start()
		else:
			return None

	def copy(self, event) -> None:
		""" Deals with copy functionality """
		# Look for a selected row
		try:
			selected_rows = self.build_protocol_controller.view.treeview.selection()
		except:
			selected_rows = []
		# Iterate through the selected rows
		self.build_protocol_controller.model.clipboard = []
		for selected_row in selected_rows:
			# Get the action message
			action_message = self.build_protocol_controller.view.treeview.item(selected_row)['values'][0]
			# Add the action to a clipboard
			self.build_protocol_controller.model.clipboard.append(action_message)

	def cut(self, event) -> None:
		""" Deals with cut functionality """
		# Look for a selected row
		try:
			selected_rows = self.build_protocol_controller.view.treeview.selection()
		except:
			selected_rows = []
		# Iterate through the selected rows
		self.build_protocol_controller.model.clipboard = []
		for selected_row in selected_rows:
			# Get the action message
			action_message = self.build_protocol_controller.view.treeview.item(selected_row)['values'][0]
			# Add the action to a clipboard
			self.build_protocol_controller.model.clipboard.append(action_message)
			# Remove these actions from the treeview
			self.build_protocol_controller.model.delete(int(selected_row))
		# Update the view
		self.build_protocol_controller.view.update_treeview()

	def paste(self, event) -> None:
		""" Deals with the paste functionality """
		# Look for a selected row
		try:
			selected_row = self.build_protocol_controller.view.treeview.selection()[0]
			# Iterate through the build protocol models clipboard
			action_messages = self.build_protocol_controller.model.clipboard
			action_messages.reverse()
			for action_message in action_messages:
				# Insert below the selected row or at the end of the action treeview
				insert_at_selected_row(action_message, selected_row, self.build_protocol_controller.model)
				# Update the view
				self.build_protocol_controller.view.update_treeview()
		except:
			return None


	def all(self, event) -> None:
		""" Deals with selecting all rows in the treeview for the actions in the BuildProtocolFrame """
		# Select all action items in the treeview of the build protocol tab
		for item in self.build_protocol_controller.view.treeview.get_children():
			self.build_protocol_controller.view.treeview.selection_add(item)


	def home_imager(self, event) -> None:
		""" Homes the imager if H is pressed not h """
		# Make sure we are on the Image Frame
		current_frame = self.view.menu_frame.current_view
		if type(current_frame) == ImageFrame:
			thread = threading.Thread(target=self.thread_home_imager)
			thread.start()
	def thread_home_imager(self) -> None:
		self.reader = Reader()
		self.reader.home_imager()
		self.reader.close()
