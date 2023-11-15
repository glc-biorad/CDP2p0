
# Version: Test
"""
Main Graphical representation of the GUI
"""

import customtkinter as ctk
import tkinter as tk

from gui.models.model import Model

from gui.views.menu_frame import MenuFrame

from gui.views.image_frame import ImageFrame
from gui.views.thermocycle_frame import ThermocycleFrame
from gui.views.build_protocol_frame import BuildProtocolFrame
from gui.views.optimize_frame import OptimizeFrame
from gui.views.configure_frame import ConfigureFrame

from api.util.server import Server

# Constants
TITLE = "CDP 2.0 Development GUI"
APP_ICON_PATH = 'gui/images/bio-rad-logo.ico'
WIDTH = 780
HEIGHT = 520
RIGHT_FRAME_WIDTH = 600
RIGHT_FRAME_HEIGHT = 520
MENU_WIDTH = 180
MENU_HEIGHT = 520
MENU_POSX = 0
MENU_POSY = 0

# Appearance and Theme
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')

class View(ctk.CTk):
	menu_frame: MenuFrame = None
	image_frame: ImageFrame = None
	thermocycle_frame: ThermocycleFrame = None
	build_protocol_frame: BuildProtocolFrame = None
	optimize_frame: OptimizeFrame = None
	configure_frame: ConfigureFrame = None
	def __init__(self, model: Model) -> None:
		super().__init__()
		self.server = Server()
		self.server.start()
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.model = model
		self.title(TITLE)
		self.geometry(f"{WIDTH}x{HEIGHT}")
		self.maxsize(WIDTH,HEIGHT)
		self.minsize(WIDTH,HEIGHT)
		self.iconbitmap(APP_ICON_PATH)
		# Initialize the Frames
		self.image_frame = ImageFrame(self, model, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.optimize_frame = OptimizeFrame(self, model,RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.build_protocol_frame = BuildProtocolFrame(self, model, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.thermocycle_frame = ThermocycleFrame(self, model, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.configure_frame = ConfigureFrame(self, model, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		frames = {
			'Home': None,
			'Image': self.image_frame,
			'Thermocycle': self.thermocycle_frame,
			"Build Protocol": self.build_protocol_frame,
			'Optimize': self.optimize_frame,
			'Service': None,
			'Status': None,
			'Configure': self.configure_frame,
		}
		self.menu_frame = MenuFrame(self, frames, MENU_WIDTH, MENU_HEIGHT, MENU_POSX, MENU_POSY, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT)
		self.create_ui()
		
	def create_ui(self) -> None:
		# Create the MenuFrame
		self.menu_frame.place_ui()

	def on_closing(self, event=0) -> None:
		""" Deals with the GUI window closing """
		self.server.stop()
		self.destroy()
