
# Version: Test
import types
import tkinter as tk
import customtkinter as ctk
from typing import Any, Callable

from gui.controllers.image_controller import ImageController

from gui.models.model import Model
from gui.models.image_model import ImageModel

# Import the Reader API
from api.reader.reader import Reader

# Constants
IMAGER_VIEW_POSX = 10
IMAGER_VIEW_POSY = 20
IMAGER_VIEW_WIDTH = 400
IMAGER_VIEW_HEIGHT = 400
IMAGER_VIEW_SCALED_WIDTH = 803
IMAGER_VIEW_SCALED_HEIGHT = 803
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
	'Live View',
	'Save View',
	'Load View',
	'Scan Chip',
	'Home Imager',
]

class ImageFrame(ctk.CTkFrame):
	"""
	Image Frame
	"""
	def __init__(self, master: ctk.CTk, model: Model, width: int, height: int, posx: int, posy: int) -> None:
		self.master = master
		self.width = width
		self.height = height
		self.posx = posx
		self.posy = posy
		self.controller = ImageController(model.get_image_model(), self)
		self.buttons = {}
		super().__init__(
			master=self.master,
			width=self.width,
			height=self.height,
			corner_radius=0,
		)
		self.create_ui()

	def create_ui(self) -> None:
		# Place the Imager View
		#self.textbox_imager_view = ctk.CTkTextbox(
		#	master=self,
		#	width=IMAGER_VIEW_WIDTH,
		#	height=IMAGER_VIEW_HEIGHT,
		#	font=("Roboto Medium", -12),
		#	state='disabled',
		#)
		self.textbox_imager_view = tk.Canvas(self, width=IMAGER_VIEW_WIDTH, height=IMAGER_VIEW_HEIGHT, bg='red')
		# Place the Filter Option Menu
		self.label_filter = ctk.CTkLabel(master=self, text='Filter', font=("Roboto Medium", -16))
		self.filter_sv = self.controller.get_filter_sv(1)
		self.optionmenu_filter = ctk.CTkOptionMenu(
			master=self,
			variable=self.filter_sv,
			values=('HEX', 'FAM', 'ATTO590', 'ALEXA405', 'CY5', 'CY5.5', 'Home'),
		)
		# Place the LED Option Menu
		self.label_led = ctk.CTkLabel(master=self, text='LED', font=("Roboto Medium", -16))
		self.led_sv = self.controller.get_led_sv(1)
		self.optionmenu_led = ctk.CTkOptionMenu(
			master=self,
			variable=self.led_sv,
			values=('HEX', 'FAM', 'ATTO590', 'ALEXA405', 'CY5', 'CY5.5', 'Off'),
		)
		# Place the Option Buttons
		self.label_options = ctk.CTkLabel(master=self, text='Options', font=("Roboto Medium", -16))
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
		# Place the Relative Moves
		self.label_relative_moves = ctk.CTkLabel(master=self, text="Relative Moves", font=("Roboto Medium", -16))
		# Place the Relative Moves (dx)
		self.label_dx = ctk.CTkLabel(master=self, text='dx', font=("Roboto Medium", -14))
		self.dx_sv = self.controller.get_dx_sv(1)
		self.entry_dx = ctk.CTkEntry(master=self, textvariable=self.dx_sv, font=("Roboto Medium", -14), width=ENTRY_DX_WIDTH)
		# Place the Relative Moves (dy)
		self.label_dy = ctk.CTkLabel(master=self, text='dy', font=("Roboto Medium", -14))
		self.dy_sv = self.controller.get_dy_sv(1)
		self.entry_dy = ctk.CTkEntry(master=self, textvariable=self.dy_sv, font=("Roboto Medium", -14), width=ENTRY_DY_WIDTH)
		# Place the Relative Moves (dz)
		self.label_dz = ctk.CTkLabel(master=self, text='dz', font=("Roboto Medium", -14))
		self.dz_sv = self.controller.get_dz_sv(1)
		self.entry_dz = ctk.CTkEntry(master=self, textvariable=self.dz_sv, font=("Roboto Medium", -14), width=ENTRY_DZ_WIDTH)
		# Place the LED Intensity slider
		self.label_led_intensity = ctk.CTkLabel(master=self, text="LED Intensity", font=("Roboto Medium", -16))
		self.led_intensity_iv = tk.IntVar()
		self.led_intensity_iv.set(0)
		self.slider_led_intensity = ctk.CTkSlider(
			master=self,
			from_=0,
			to=100,
			variable=self.led_intensity_iv,
			number_of_steps=10,
			progress_color='green',
			width=SLIDER_LED_INTENSITY_WIDTH,
			height=SLIDER_LED_INTENSITY_HEIGHT,
			#command=self.slider_event,
		)
		self.slider_led_intensity.set(0)
		self.slider_led_intensity.configure(state='disabled')

	def place_ui(self) -> None:
		# Place the Image Frame
		self.place(x=self.posx, y=self.posy)
		# Place the Imager View
		self.textbox_imager_view.place(x=IMAGER_VIEW_POSX, y=IMAGER_VIEW_POSY)
		# Place the Filter Option Menu
		self.label_filter.place(x=LABEL_FILTER_POSX, y=LABEL_FILTER_POSY)
		self.optionmenu_filter.place(x=OPTIONMENU_FILTER_POSX, y=OPTIONMENU_FILTER_POSY, width=OPTIONMENU_FILTER_WIDTH)
		# Place the LED Option Menu
		self.label_led.place(x=LABEL_LED_POSX, y=LABEL_LED_POSY)
		self.optionmenu_led.place(x=OPTIONMENU_LED_POSX, y=OPTIONMENU_LED_POSY, width=OPTIONMENU_LED_WIDTH)
		# Place the Option Buttons
		self.label_options.place(x=LABEL_OPTIONS_POSX, y=LABEL_OPTIONS_POSY)
		# Set the initial y position for the buttons
		y = LABEL_OPTIONS_POSY
		for button_title in BUTTON_TITLES:
			# Update the y position of the button
			y = y + OPTIONS_BUTTON_DY
			# Place the button
			self.buttons[button_title].place(x=OPTIONS_BUTTON_POSX, y=y)
		# Place the Relative Moves
		self.label_relative_moves.place(x=LABEL_RELATIVE_MOVES_POSX, y=LABEL_RELATIVE_MOVES_POSY)
		# Place the Relative Moves (dx)
		self.label_dx.place(x=LABEL_DX_POSX, y=LABEL_DX_POSY)
		self.entry_dx.place(x=ENTRY_DX_POSX, y=ENTRY_DX_POSY)
		# Place the Relative Moves (dy)
		self.label_dy.place(x=LABEL_DY_POSX, y=LABEL_DY_POSY)
		self.entry_dy.place(x=ENTRY_DY_POSX, y=ENTRY_DY_POSY)
		# Place the Relative Moves (dz)
		self.label_dz.place(x=LABEL_DZ_POSX, y=LABEL_DZ_POSY)
		self.entry_dz.place(x=ENTRY_DZ_POSX, y=ENTRY_DZ_POSY)
		# Place the LED Intensity slider
		self.label_led_intensity.place(x=LABEL_LED_INTENSITY_POSX, y=LABEL_LED_INTENSITY_POSY)
		self.slider_led_intensity.place(x=SLIDER_LED_INTENSITY_POSX, y=SLIDER_LED_INTENSITY_POSY)

	def on_click(self, button_title: str) -> types.MethodType:
		# Make sure the button title is valid
		assert button_title in BUTTON_TITLES
		# Return the appropriate on click function
		if button_title == 'Brightfield':
			return self.on_click_brightfield
		elif button_title == "Live View":
			return self.on_click_live_view
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

	def on_click_live_view(self) -> None:
		print("Live View")

	def on_click_save_view(self) -> None:
		print("Save View")

	def on_click_load_view(self) -> None:
		from PIL import Image, ImageTk
		try:
			self.reader = Reader()
			# Get the camera
			camcontroller = self.reader.camcontroller
			camera = camcontroller.camera
			# Snap continuously
			camcontroller.snap_continuous_prep()
			#camcontroller.snap_single()
			camcontroller.setExposureTimeMicroseconds(2000)
			image = camera.GetNextImage(1000)
			array = image.GetNDArray()
			array = array / (2**16-1)
			array *= 255
			print(type(array))
			print(array.shape)
			array = array.transpose((0,1))
			_image = Image.fromarray(array)
			width, height = _image.size
			#_image = _image.resize((int(0.1468*width),int(0.220105*height)))
			_image = _image.resize((IMAGER_VIEW_SCALED_WIDTH,IMAGER_VIEW_SCALED_HEIGHT))
			print(_image.size)
			self.img = ImageTk.PhotoImage(image=_image)
			#self.textbox_imager_view.create_image(500,500,anchor='nw', image=img)
			image.Release()
			camera.EndAcquisition()
			self.textbox_imager_view.create_image(0,0, anchor=tk.CENTER, image=self.img)
		except Exception as e:
			print(e)
			tk.messagebox.showwarning(title="Reader Connection Issue", message="Reader could not be initialized")
			self.reader = None
		print("Load View")

	def on_click_scan_chip(self) -> None:
		print("Scan Chip")

	def on_click_home_imager(self) -> None:
		print("Home Imager")

	def slider_event(self, value):
		print(value)

	def trace_led_sv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Adds a trace to the led_sv variable to deal with it changing """
		try:
			self.led_sv.trace('w', callback)
		except:
			pass

	def trace_led_intensity_iv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Adds a trace to the led_intensity_iv to deal with it changing """
		try:
			self.led_intensity_iv.trace('w', callback)
		except:
			pass

	def trace_filter_sv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Adds a trace to the filter_sv to deal with it changing """
		try:
			self.filter_sv.trace('w', callback)
		except:
			pass

	def bind_brightfield(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the brightfield button """
		try:
			self.buttons['Brightfield'].bind('<Button-1>', callback)
		except:
			pass

	def bind_live_view(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the live view button """
		try:
			self.buttons["Live View"].bind('<Button-1>', callback)
		except:
			pass
