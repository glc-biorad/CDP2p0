import types
import customtkinter as ctk

from controllers.image_controller import ImageController

from models.image_model import ImageModel

# Constants
IMAGER_VIEW_POSX = 10
IMAGER_VIEW_POSY = 20
IMAGER_VIEW_WIDTH = 400
IMAGER_VIEW_HEIGHT = 400
LABEL_FILTER_POSX = 490
LABEL_FILTER_POSY = 10
OPTIONMENU_FILTER_POSX = 425
OPTIONMENU_FILTER_POSY = 40
OPTIONMENU_FILTER_WIDTH = 160
LABEL_LED_POSX = 495
LABEL_LED_POSY = 70
OPTIONMENU_LED_POSX = 425
OPTIONMENU_LED_POSY = 100
OPTIONMENU_LED_WIDTH = 160
LABEL_OPTIONS_POSX = 480
LABEL_OPTIONS_POSY = 140
OPTIONS_BUTTON_DY = 40
OPTIONS_BUTTON_WIDTH = 160
OPTIONS_BUTTON_HEIGHT = 30
OPTIONS_BUTTON_POSX = 425
LABEL_RELATIVE_MOVES_POSX = 150
LABEL_RELATIVE_MOVES_POSY = 440
LABEL_DX_POSX = 30
LABEL_DX_POSY = 475
ENTRY_DX_POSX = 60
ENTRY_DX_POSY = 475
ENTRY_DX_WIDTH = 80
LABEL_DY_POSX = 150
LABEL_DY_POSY = 475
ENTRY_DY_POSX = 180
ENTRY_DY_POSY = 475
ENTRY_DY_WIDTH = 80
LABEL_DZ_POSX = 270
LABEL_DZ_POSY = 475
ENTRY_DZ_POSX = 300
ENTRY_DZ_POSY = 475
ENTRY_DZ_WIDTH = 80
LABEL_LED_INTENSITY_POSX = 455
LABEL_LED_INTENSITY_POSY = 440
SLIDER_LED_INTENSITY_POSX = 440
SLIDER_LED_INTENSITY_POSY = 475
SLIDER_LED_INTENSITY_WIDTH = 140
SLIDER_LED_INTENSITY_HEIGHT = 20

# Label Text (Doesn't change anything in the code)
LABELS_TEXT = [
	'Filter',
	'LED',
	"Relative Moves",
	"LED Intensity",
]

# Button Titles (Only for asserting)
BUTTON_TITLES = [
	'Brightfield',
	'Auto-Focus',
	'Save View',
	'Load View',
	'Scan Chip',
	'Home Imager',
]

class ImageFrame(ctk.CTkFrame):
	"""
	Image Frame
	"""
	def __init__(self, master: ctk.CTk, width: int, height: int, posx: int, posy: int) -> None:
		self.master = master
		self.width = width
		self.height = height
		self.posx = posx
		self.posy = posy
		self.controller = ImageController(ImageModel(), self)
		self.buttons = {}
		super().__init__(
			master=self.master,
			width=self.width,
			height=self.height,
			corner_radius=0,
		)

	def create_ui(self) -> None:
		# Place the Image Frame
		self.place(x=self.posx, y=self.posy)
		# Place the Imager View
		self.textbox_imager_view = ctk.CTkTextbox(
			master=self,
			width=IMAGER_VIEW_WIDTH,
			height=IMAGER_VIEW_HEIGHT,
			font=("Roboto Medium", -12),
			state='disabled',
		)
		self.textbox_imager_view.place(x=IMAGER_VIEW_POSX, y=IMAGER_VIEW_POSY)
		# Place the Filter Option Menu
		self.label_filter = ctk.CTkLabel(master=self, text='Filter', font=("Roboto Medium", -16))
		sv = self.controller.get_filter_sv(1)
		self.label_filter.place(x=LABEL_FILTER_POSX, y=LABEL_FILTER_POSY)
		self.optionmenu_filter = ctk.CTkOptionMenu(
			master=self,
			variable=sv,
			values=('HEX', 'FAM', 'ATTO590', 'ALEXA405', 'CY5', 'CY5.5', 'Home'),
		)
		self.optionmenu_filter.place(x=OPTIONMENU_FILTER_POSX, y=OPTIONMENU_FILTER_POSY, width=OPTIONMENU_FILTER_WIDTH)
		# Place the LED Option Menu
		self.label_led = ctk.CTkLabel(master=self, text='LED', font=("Roboto Medium", -16))
		self.label_led.place(x=LABEL_LED_POSX, y=LABEL_LED_POSY)
		led_sv = self.controller.get_led_sv(1)
		self.optionmenu_led = ctk.CTkOptionMenu(
			master=self,
			variable=led_sv,
			values=('HEX', 'FAM', 'ATTO590', 'ALEXA405', 'CY5', 'CY5.5', 'Off'),
		)
		self.optionmenu_led.place(x=OPTIONMENU_LED_POSX, y=OPTIONMENU_LED_POSY, width=OPTIONMENU_LED_WIDTH)
		# Place the Option Buttons
		self.label_options = ctk.CTkLabel(master=self, text='Options', font=("Roboto Medium", -16))
		self.label_options.place(x=LABEL_OPTIONS_POSX, y=LABEL_OPTIONS_POSY)
		# Set the initial y position for the buttons
		y = LABEL_OPTIONS_POSY
		for button_title in BUTTON_TITLES:
			# Update the y position of the button
			y = y + OPTIONS_BUTTON_DY
			# Get the on click function
			command = self.on_click(button_title)
			# Create the button
			button = ctk.CTkButton(
				master=self,
				text=button_title.title(),
				font=("Roboto Medium", -16),
				width=OPTIONS_BUTTON_WIDTH,
				height=OPTIONS_BUTTON_HEIGHT,
				command=command,
			)
			self.buttons[button_title] = button
			# Place the button
			button.place(x=OPTIONS_BUTTON_POSX, y=y)
		# Place the Relative Moves
		self.label_relative_moves = ctk.CTkLabel(master=self, text="Relative Moves", font=("Roboto Medium", -16))
		self.label_relative_moves.place(x=LABEL_RELATIVE_MOVES_POSX, y=LABEL_RELATIVE_MOVES_POSY)
		# Place the Relative Moves (dx)
		self.label_dx = ctk.CTkLabel(master=self, text='dx', font=("Roboto Medium", -14))
		self.label_dx.place(x=LABEL_DX_POSX, y=LABEL_DX_POSY)
		dx_sv = self.controller.get_dx_sv(1)
		self.entry_dx = ctk.CTkEntry(master=self, textvariable=dx_sv, font=("Roboto Medium", -14), width=ENTRY_DX_WIDTH)
		self.entry_dx.place(x=ENTRY_DX_POSX, y=ENTRY_DX_POSY)
		# Place the Relative Moves (dy)
		self.label_dy = ctk.CTkLabel(master=self, text='dy', font=("Roboto Medium", -14))
		self.label_dy.place(x=LABEL_DY_POSX, y=LABEL_DY_POSY)
		dy_sv = self.controller.get_dy_sv(1)
		self.entry_dy = ctk.CTkEntry(master=self, textvariable=dy_sv, font=("Roboto Medium", -14), width=ENTRY_DY_WIDTH)
		self.entry_dy.place(x=ENTRY_DY_POSX, y=ENTRY_DY_POSY)
		# Place the Relative Moves (dz)
		self.label_dz = ctk.CTkLabel(master=self, text='dz', font=("Roboto Medium", -14))
		self.label_dz.place(x=LABEL_DZ_POSX, y=LABEL_DZ_POSY)
		dz_sv = self.controller.get_dz_sv(1)
		self.entry_dz = ctk.CTkEntry(master=self, textvariable=dz_sv, font=("Roboto Medium", -14), width=ENTRY_DZ_WIDTH)
		self.entry_dz.place(x=ENTRY_DZ_POSX, y=ENTRY_DZ_POSY)
		# Place the LED Intensity slider
		self.label_led_intensity = ctk.CTkLabel(master=self, text="LED Intensity", font=("Roboto Medium", -16))
		self.label_led_intensity.place(x=LABEL_LED_INTENSITY_POSX, y=LABEL_LED_INTENSITY_POSY)
		self.slider_led_intensity = ctk.CTkSlider(
			master=self,
			from_=0,
			to=100,
			number_of_steps=10,
			progress_color='green',
			width=SLIDER_LED_INTENSITY_WIDTH,
			height=SLIDER_LED_INTENSITY_HEIGHT,
			command=self.slider_event,
		)
		self.slider_led_intensity.set(0)
		self.slider_led_intensity.configure(state='disabled')
		self.slider_led_intensity.place(x=SLIDER_LED_INTENSITY_POSX, y=SLIDER_LED_INTENSITY_POSY)

	def on_click(self, button_title: str) -> types.MethodType:
		# Make sure the button title is valid
		assert button_title in BUTTON_TITLES
		# Return the appropriate on click function
		if button_title == 'Brightfield':
			return self.on_click_brightfield
		elif button_title == 'Auto-Focus':
			return self.on_click_auto_focus
		elif button_title == "Save View":
			return self.on_click_save_view
		elif button_title == "Load View":
			return self.on_click_load_view
		elif button_title == "Scan Chip":
			return self.on_click_scan_chip
		elif button_title == "Home Imager":
			return self.on_click_home_imager

	def on_click_brightfield(self) -> None:
		print('Brightfield')

	def on_click_auto_focus(self) -> None:
		print('Auto-Focus')

	def on_click_save_view(self) -> None:
		print("Save View")

	def on_click_load_view(self) -> None:
		print("Load View")

	def on_click_scan_chip(self) -> None:
		print("Scan Chip")

	def on_click_home_imager(self) -> None:
		print("Home Imager")

	def slider_event(self, value):
		print(value)
