import customtkinter as ctk

import time

from gui.views.image_frame import ImageFrame
from gui.views.thermocycle_frame import ThermocycleFrame
from gui.views.build_protocol_frame import BuildProtocolFrame
from gui.views.configure_frame import ConfigureFrame

# Constants
X = 10
DY = 45
LABEL_FONT = ("Segoe UI", -16)
BUTTON_WIDTH = 160
BUTTON_HEIGHT = 30
FONT = "Segoe UI"
BUTTON_FONT = (FONT, -13)
BUTTON_CORNER_RADIUS = 5

# Button Titles
BUTTON_TITLES = [
	'Home',
	'Image',
	'Thermocycle',
	"Build Protocol",
	'Optimize',
	'Service',
	'Status',
	'Configure',
]

class MenuFrame(ctk.CTkFrame):
	"""
	Menu Frame
	"""

	def __init__(self, master: ctk.CTk, frames: dict, width: int, height: int, posx: int, posy: int, right_frame_width: int, right_frame_height: int) -> None:
		self.master = master
		self.width = width
		self.height = height
		self.posx = posx
		self.posy = posy
		self.right_frame_width = right_frame_width
		self.right_frame_height = right_frame_height
		self.current_view: ctk.CTkFrame = None
		self.frames = frames
		self.buttons = {}
		super().__init__(
			master=self.master, 
			width = self.width,
			height = self.height,
			corner_radius=0,
		)
		self.create_ui()

	def create_ui(self) -> None:
		# Place the label for the GUI at the top of the menu
		self.label = ctk.CTkLabel(master=self, text="CDP 2.0", font=LABEL_FONT)
		# Set the initial y value
		y = 20
		# Create and Place the buttons
		for button_title in BUTTON_TITLES:
			y = y + DY
			button = ctk.CTkButton(master=self, 
				text=button_title,
				font=BUTTON_FONT,
				corner_radius=BUTTON_CORNER_RADIUS,
				command=lambda button_text=button_title:self.on_click(button_text)
			)
			self.buttons[button_title] = {
				'button': button,
				'view': self.frames[button_title],
			}
		# Create and Place Firmware and Software Version Labels

	def place_ui(self) -> None:
		# Place the Menu Frame
		self.place(x=self.posx, y=self.posy)
		# Set the initial y value
		y = 20
		self.label.place(x=60,y=y)
		for button_title in BUTTON_TITLES:
			y = y + DY
			button = self.buttons[button_title]['button']
			button.place(x=X, y=y, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

	def on_click(self, button_title: str) -> None:
		# Load the proper view
		frame = self.buttons[button_title]['view']
		# Check if the button was clicked for the same view
		if self.current_view == None:
			self.current_view = frame
		elif self.current_view != frame:
			self.forget_current_view()
			self.current_view = frame
		self.current_view.place_ui()

	def forget_current_view(self) -> None:
		"""For forgetting the root views frames except for the menu frame
		"""
		for frame_widget in self.master.winfo_children():
			if frame_widget != self:
				frame_widget.place_forget()
