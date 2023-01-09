"""
Main Graphical representation of the GUI
"""

import customtkinter as ctk
import tkinter as tk

from models.model import Model

from views.menu_frame import MenuFrame

from views.image_frame import ImageFrame
from views.thermocycle_frame import ThermocycleFrame
from views.build_protocol_frame import BuildProtocolFrame
from views.optimize_frame import OptimizeFrame

# Constants
TITLE = "CDP 2.0 Development GUI"
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
	thermocycle_frame: ThermocycleFrame = None
	build_protocol_frame: BuildProtocolFrame = None
	optimize_frame: OptimizeFrame = None
	def __init__(self, model: Model) -> None:
		super().__init__()
		print("Pass the model to the views!")
		self.model = model
		self.title(TITLE)
		self.geometry(f"{WIDTH}x{HEIGHT}")
		# Initialize the Frames
		self.optimize_frame = OptimizeFrame(self, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.build_protocol_frame = BuildProtocolFrame(self, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		self.thermocycle_frame = ThermocycleFrame(self, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT, MENU_WIDTH, 0)
		frames = {
			'Home': None,
			'Image': None,
			'Thermocycle': self.thermocycle_frame,
			"Build Protocol": self.build_protocol_frame,
			'Optimize': self.optimize_frame,
			'Service': None,
			'Status': None,
			'Configure': None,
		}
		self.menu_frame = MenuFrame(self, frames, MENU_WIDTH, MENU_HEIGHT, MENU_POSX, MENU_POSY, RIGHT_FRAME_WIDTH, RIGHT_FRAME_HEIGHT)
		self.create_ui()
		
	def create_ui(self) -> None:
		# Create the MenuFrame
		self.menu_frame.place_ui()
