import types
import tkinter as tk
import customtkinter as ctk

import threading
import time
from PIL import Image
from typing import Any, Callable
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Import the Controller for the Thermocycle View
from gui.controllers.thermocycle_controller import ThermocycleController

# Import the Model for the Thermocycle View
from gui.models.model import Model
from gui.models.thermocycle_model import ThermocycleModel

# Constants
TRAY_N_STEPS=50
FONT = "Segoe UI"
LABEL_THERMOCYCLER_PROTOCOL_POSX = 50
LABEL_THERMOCYCLER_PROTOCOL_POSY = 5
LABEL_THERMOCYCLER_POSX = 10
LABEL_THERMOCYCLER_POSY = 40
OPTIONMENU_THERMOCYCLER_POSX = 150
OPTIONMENU_THERMOCYCLER_POSY = 40
LABEL_CYCLES_POSX = 10
LABEL_CYCLES_POSY = 80
ENTRY_CYCLES_POSX = 150
ENTRY_CYCLES_POSY = 80
IMAGE_THERMOCYCLERS_POSX = 310
IMAGE_THERMOCYCLERS_POSY = 5
IMAGE_THERMOCYCLERS_WIDTH = 250
IMAGE_THERMOCYCLERS_HEIGHT = 470
IMAGE_THERMOCYCLER_RAILS_POSX = 310
IMAGE_THERMOCYCLER_RAILS_POSY = 5
IMAGE_THERMOCYCLER_RAILS_WIDTH = 250
IMAGE_THERMOCYCLER_RAILS_HEIGHT = 470
TRAY_CLOSED_POSX = 435
IMAGE_THERMOCYCLER_TRAY_AB_POSX = 314
IMAGE_THERMOCYCLER_TRAY_AB_POSY = 17
IMAGE_THERMOCYCLER_TRAY_AB_WIDTH = 100
IMAGE_THERMOCYCLER_TRAY_AB_HEIGHT = 225
IMAGE_THERMOCYCLER_BLOCK_A_POSX = 445
IMAGE_THERMOCYCLER_BLOCK_A_POSY = 37
IMAGE_THERMOCYCLER_BLOCK_A_WIDTH = 97
IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT = 92
IMAGE_THERMOCYCLER_BLOCK_B_POSX = 445
IMAGE_THERMOCYCLER_BLOCK_B_POSY = 130
IMAGE_THERMOCYCLER_BLOCK_B_WIDTH = 97
IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT = 92
IMAGE_THERMOCYCLER_TRAY_CD_POSX = 314
IMAGE_THERMOCYCLER_TRAY_CD_POSY = 242
IMAGE_THERMOCYCLER_TRAY_CD_WIDTH = 100
IMAGE_THERMOCYCLER_TRAY_CD_HEIGHT = 225
IMAGE_THERMOCYCLER_BLOCK_C_POSX = 445
IMAGE_THERMOCYCLER_BLOCK_C_POSY = 262
IMAGE_THERMOCYCLER_BLOCK_C_WIDTH = 97
IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT = 92
IMAGE_THERMOCYCLER_BLOCK_D_POSX = 445
IMAGE_THERMOCYCLER_BLOCK_D_POSY = 355
IMAGE_THERMOCYCLER_BLOCK_D_WIDTH = 97
IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT = 92
BUTTON_BLOCK_LEFT_POSX = 418
BUTTON_BLOCK_LEFT_POSY = 13
BUTTON_BLOCK_LEFT_WIDTH = 25
BUTTON_BLOCK_LEFT_HEIGHT = 460
BUTTON_BLOCK_RIGHT_POSX = 542
BUTTON_BLOCK_RIGHT_POSY = 13
BUTTON_BLOCK_RIGHT_WIDTH = 25
BUTTON_BLOCK_RIGHT_HEIGHT = 460
BUTTON_BLOCK_TOP_POSX = 418
BUTTON_BLOCK_TOP_POSY = 13
BUTTON_BLOCK_TOP_WIDTH = 149
BUTTON_BLOCK_TOP_HEIGHT = 12
BUTTON_BLOCK_BOTTOM_POSX = 418
BUTTON_BLOCK_BOTTOM_POSY = 462
BUTTON_BLOCK_BOTTOM_WIDTH = 149
BUTTON_BLOCK_BOTTOM_HEIGHT = 12
BUTTON_START_POSX = 45
BUTTON_START_POSY = 480
BUTTON_START_WIDTH = 55
BUTTON_LOAD_POSX = 105
BUTTON_LOAD_POSY = 480
BUTTON_LOAD_WIDTH = 55
BUTTON_SAVE_POSX = 165
BUTTON_SAVE_POSY = 480
BUTTON_SAVE_WIDTH = 55
BUTTON_HOME_POSX = 225
BUTTON_HOME_POSY = 480
BUTTON_HOME_WIDTH = 55
PROGRESSBAR_THERMOCYCLER_POSX = 30
PROGRESSBAR_THERMOCYCLER_POSY = 432
PROGRESSBAR_THERMOCYCLER_WIDTH = 260
PROGRESSBAR_THERMOCYCLER_HEIGHT = 25
IMAGE_THERMOMETER_POSX = 15
IMAGE_THERMOMETER_POSY = 365
IMAGE_THERMOMETER_WIDTH = 24
IMAGE_THERMOMETER_HEIGHT = 24
IMAGE_CLOCK_POSX = 15
IMAGE_CLOCK_POSY = 395
IMAGE_CLOCK_WIDTH = 24
IMAGE_CLOCK_HEIGHT = 24
LABEL_A_POSX = 577
LABEL_A_POSY = 40
CHECKBOX_A_POSX = 570
CHECKBOX_A_POSY = 70
LABEL_B_POSX = 577
LABEL_B_POSY = 130
CHECKBOX_B_POSX = 570
CHECKBOX_B_POSY = 160
LABEL_C_POSX = 577
LABEL_C_POSY = 270
CHECKBOX_C_POSX = 570
CHECKBOX_C_POSY = 300
LABEL_D_POSX = 577
LABEL_D_POSY = 360
CHECKBOX_D_POSX = 570
CHECKBOX_D_POSY = 390
ENTRY_FIRST_DENATURE_TEMP_POSX = 65
ENTRY_FIRST_DENATURE_TEMP_POSY = 365
ENTRY_FIRST_DENATURE_TEMP_WIDTH = 40
ENTRY_ANNEAL_TEMP_POSX = 145
ENTRY_ANNEAL_TEMP_POSY = 365
ENTRY_ANNEAL_TEMP_WIDTH = 40
ENTRY_SECOND_DENATURE_TEMP_POSX = 225
ENTRY_SECOND_DENATURE_TEMP_POSY = 365
ENTRY_SECOND_DENATURE_TEMP_WIDTH = 40
ENTRY_FIRST_DENATURE_TIME_POSX = 65
ENTRY_FIRST_DENATURE_TIME_POSY = 395
ENTRY_FIRST_DENATURE_TIME_WIDTH = 40
ENTRY_SECOND_DENATURE_TEMP_WIDTH = 40
ENTRY_ANNEAL_TIME_POSX = 145
ENTRY_ANNEAL_TIME_POSY = 395
ENTRY_ANNEAL_TIME_WIDTH = 40
ENTRY_SECOND_DENATURE_TIME_POSX = 225
ENTRY_SECOND_DENATURE_TIME_POSY = 395
ENTRY_SECOND_DENATURE_TIME_WIDTH = 40
FIGURE_WIDTH = 3
FIGURE_HEIGHT = 2.4
FIGURE_FACECOLOR = (43/255, 43/255, 43/255)
FIGURE_TICK_COLOR = 'white'
FIGURE_TICK_LABELCOLOR = 'white'
FIGURE_SPINES_COLOR = 'white'
FIGURE_PLOT_COLOR = (156/255, 61/255, 56/255)
FIGURE_POSX = 10
FIGURE_POSY = 120
LABEL_FIRST_DENATURE_POSX = 35
LABEL_FIRST_DENATURE_POSY = 120
LABEL_FIRST_DENATURE_WIDTH = 100
LABEL_FIRST_DENATURE_COLOR = 'white'
LABEL_ANNEAL_POSX = 135
LABEL_ANNEAL_POSY = 120
LABEL_ANNEAL_WIDTH = 60
LABEL_ANNEAL_COLOR = 'white'
LABEL_SECOND_DENATURE_POSX = 195
LABEL_SECOND_DENATURE_POSY = 120
LABEL_SECOND_DENATURE_WIDTH = 100
LABEL_SECOND_DENATURE_COLOR = 'white'
LABEL_FIRST_DENATURE_TEMPERATURE_UNIT_POSX = 107
LABEL_FIRST_DENATURE_TEMPERATURE_UNIT_POSY = 365
LABEL_ANNEAL_TEMPERATURE_UNIT_POSX = 187
LABEL_ANNEAL_TEMPERATURE_UNIT_POSY = 365
LABEL_SECOND_DENATURE_TEMPERATURE_UNIT_POSX = 267
LABEL_SECOND_DENATURE_TEMPERATURE_UNIT_POSY = 365
LABEL_FIRST_DENATURE_TIME_UNIT_POSX = 107
LABEL_FIRST_DENATURE_TIME_UNIT_POSY = 395
LABEL_ANNEAL_TIME_UNIT_POSX = 187
LABEL_ANNEAL_TIME_UNIT_POSY = 395
LABEL_SECOND_DENATURE_TIME_UNIT_POSX = 267
LABEL_SECOND_DENATURE_TIME_UNIT_POSY = 395
BUTTON_SETTINGS_WIDTH = 100
BUTTON_SETTINGS_POSX = 330
BUTTON_SETTINGS_POSY = 480
BUTTON_TEC_POSX = 435
BUTTON_TEC_POSY = 480
BUTTON_TEC_WIDTH = 100

# Therocyclers
THERMOCYCLERS = (
	'A',
	'B',
	'C',
	'D',
)

# Thermocycler IDs:
IDS = {
	'A': 1,
	'B': 2,
	'C': 3,
	'D': 4,
	'Pre-Amp Thermocycler': 4,
}

# Addresses:
ADDRESSES = {
	'AB': 6,
	'CD': 7,
	'A': 8,
	'B': 9,
	'C': 10,
	'D': 11,
	'Pre-Amp Thermocycler': 9,
}

# Button Titles
BUTTON_TITLES = [
	'Start',
	'Load',
	'Save',
	'Home',
]

# Image Paths
IMAGE_PATHS = {
	'thermocyclers': 'gui/images/thermocyclers.png',
	'thermocycler_rails': 'gui/images/thermocycler_rails.png',
	'thermocycler_block_raised': 'gui/images/thermocycler_block_raised.png',
	'thermocycler_block_lowered': 'gui/images/thermocycler_block_lowered.png',
	'thermocycler_tray': 'gui/images/thermocycler_tray.png',
	'thermometer': 'gui/images/thermometer.png', # Credit goes to author (Freepik)
	'clock': 'gui/images/clock.png', # Credit goes to author (Freepik)
}

class ThermocycleFrame(ctk.CTkFrame):
	"""
	Thermocycle Frame: UI for the Thermocycle view
	"""
	def __init__(self, master: ctk.CTk, model: Model, width: int, height: int, posx: int, posy: int) -> None:
		self.master = master
		self.width = width
		self.height = height
		self.posx = posx
		self.posy = posy
		self.model = model.get_thermocycle_model()
		self.controller = ThermocycleController(model.get_thermocycle_model(), self)
		self.buttons = {}
		self.IMAGE_PATHS = IMAGE_PATHS
		self.IMAGE_THERMOCYCLER_BLOCK_A_WIDTH = IMAGE_THERMOCYCLER_BLOCK_A_WIDTH
		self.IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT = IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT
		self.IMAGE_THERMOCYCLER_BLOCK_B_WIDTH = IMAGE_THERMOCYCLER_BLOCK_B_WIDTH
		self.IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT = IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT
		self.IMAGE_THERMOCYCLER_BLOCK_C_WIDTH = IMAGE_THERMOCYCLER_BLOCK_C_WIDTH
		self.IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT = IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT
		self.IMAGE_THERMOCYCLER_BLOCK_D_WIDTH = IMAGE_THERMOCYCLER_BLOCK_D_WIDTH
		self.IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT = IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT
		self.IMAGE_THERMOCYCLER_TRAY_AB_POSX = IMAGE_THERMOCYCLER_TRAY_AB_POSX
		self.IMAGE_THERMOCYCLER_TRAY_CD_POSX = IMAGE_THERMOCYCLER_TRAY_CD_POSX
		self.TRAY_CLOSED_POSX = TRAY_CLOSED_POSX
		try:
			from api.interfaces.fast_api_interface import FastAPIInterface
			self.fast_api_interface = FastAPIInterface()
		except Exception as e:
			print(e)
			self.fast_api_interface = None
			print(f"FastAPIInterface could not be used for the ThermocycleFrame")
		super().__init__(
			master=self.master,
			width=self.width,
			height=self.height,
			corner_radius=0,
		)
		self.create_ui()

	def create_ui(self) -> None:
		"""Deals with generation of the ThermocycleView UI"""
		# Place the Thermocycler Protocol Label
		self.label_thermocycler_protocol = ctk.CTkLabel(master=self, text="Thermocycler Protocol", font=(FONT, -20))
		# Place the Thermocycler Option Menu
		self.label_thermocycler = ctk.CTkLabel(master=self, text='Thermocycler', font=(FONT, -16))
		self.thermocycler_sv = self.controller.get_thermocycler_sv(1)
		self.thermocycler_sv.trace('w', self.callback_thermocycler)
		self.optionmenu_thermocycler = ctk.CTkOptionMenu(
			master=self,
			variable=self.thermocycler_sv,
			values=THERMOCYCLERS,
			corner_radius=5,
		)
		# Place the Cycles Entry
		self.label_cycles = ctk.CTkLabel(master=self, text='Cycles', font=(FONT, -16))
		self.cycles_sv = self.controller.get_cycles_sv(1)
		self.cycles_sv.trace('w', self.callback_cycles)
		self.entry_cycles = ctk.CTkEntry(
			master=self,
			textvariable=self.cycles_sv,
			corner_radius=5,
		)
		self.entry_cycles.bind('<FocusOut>', self.callback_cycles)
		# Place the Thermocycler Image
		self.photoimage_thermocycler_rails = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_rails']),
			size=(IMAGE_THERMOCYCLER_RAILS_WIDTH, IMAGE_THERMOCYCLER_RAILS_HEIGHT),
		)
		self.image_thermocycler_rails = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_rails)
		self.image_thermocycler_rails.bind('<Button-1>', self.on_click_rails)
		self.photoimage_thermocycler_tray_ab = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_tray']),
			size=(IMAGE_THERMOCYCLER_TRAY_AB_WIDTH, IMAGE_THERMOCYCLER_TRAY_AB_HEIGHT),
		)
		self.image_thermocycler_tray_ab = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_tray_ab)
		self.image_thermocycler_tray_ab.bind('<Button-1>', self.on_click_tray_ab)
		self.photoimage_thermocycler_block_a = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
			size=(IMAGE_THERMOCYCLER_BLOCK_A_WIDTH, IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT),
		)
		self.image_thermocycler_block_a = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_block_a)
		self.image_thermocycler_block_a.bind('<Button-1>', self.on_click_thermocycler_a)
		self.photoimage_thermocycler_block_b = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
			size=(IMAGE_THERMOCYCLER_BLOCK_B_WIDTH, IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT),
		)
		self.image_thermocycler_block_b = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_block_b)
		self.image_thermocycler_block_b.bind('<Button-1>', self.on_click_thermocycler_b)
		self.photoimage_thermocycler_tray_cd = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_tray']),
			size=(IMAGE_THERMOCYCLER_TRAY_CD_WIDTH, IMAGE_THERMOCYCLER_TRAY_CD_HEIGHT),
		)
		self.image_thermocycler_tray_cd = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_tray_cd)
		self.image_thermocycler_tray_cd.bind('<Button-1>', self.on_click_tray_cd)
		self.photoimage_thermocycler_block_c = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
			size=(IMAGE_THERMOCYCLER_BLOCK_C_WIDTH, IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT),
		)
		self.image_thermocycler_block_c = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_block_c)
		self.image_thermocycler_block_c.bind('<Button-1>', self.on_click_thermocycler_c)
		self.photoimage_thermocycler_block_d = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
			size=(IMAGE_THERMOCYCLER_BLOCK_D_WIDTH, IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT),
		)
		self.image_thermocycler_block_d = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermocycler_block_d)
		self.image_thermocycler_block_d.bind('<Button-1>', self.on_click_thermocycler_d)
		self.button_block_left = ctk.CTkButton(
			master=self,
			text='',
			width=BUTTON_BLOCK_LEFT_WIDTH,
			height=BUTTON_BLOCK_LEFT_HEIGHT,
			corner_radius=0,
			state='disabled',
			fg_color='black',
		
		)
		self.button_block_right = ctk.CTkButton(
			master=self,
			text='',
			width=BUTTON_BLOCK_RIGHT_WIDTH,
			height=BUTTON_BLOCK_RIGHT_HEIGHT,
			corner_radius=0,
			state='disabled',
			fg_color='black',
		
		)
		self.button_block_top = ctk.CTkButton(
			master=self,
			text='',
			width=BUTTON_BLOCK_TOP_WIDTH,
			height=BUTTON_BLOCK_TOP_HEIGHT,
			corner_radius=0,
			state='disabled',
			fg_color='black',
		
		)
		self.button_block_bottom = ctk.CTkButton(
			master=self,
			text='',
			width=BUTTON_BLOCK_BOTTOM_WIDTH,
			height=BUTTON_BLOCK_BOTTOM_HEIGHT,
			corner_radius=0,
			state='disabled',
			fg_color='black',
		
		)
		# Place the Start Button
		self.button_start = ctk.CTkButton(
			master=self,
			text='Start',
			fg_color='#4C7BD3',
			width=BUTTON_START_WIDTH,
			corner_radius=5,
		)
		# Place the Load Button
		self.button_load = ctk.CTkButton(
			master=self,
			text='Load',
			#command=self.on_load,
			width=BUTTON_LOAD_WIDTH,
			corner_radius=5,
		)
		# Place the Save Button
		self.button_save = ctk.CTkButton(
			master=self,
			text='Save',
			#command=self.on_save,
			width=BUTTON_SAVE_WIDTH,
			corner_radius=5,
		)
		# Place the Home Button
		self.button_home = ctk.CTkButton(
			master=self,
			text='Home',
			#command=self.on_home,
			width=BUTTON_HOME_WIDTH,
			corner_radius=5,
		)
		# Place the Thermocycler ProgressBar
		self.progressbar_thermocycler = ctk.CTkProgressBar(
			master=self,
			orientation='horizontal',
			mode='determinate',
			progress_color='green',
			height=PROGRESSBAR_THERMOCYCLER_HEIGHT,
			width=PROGRESSBAR_THERMOCYCLER_WIDTH,
			corner_radius=0,
		)
		self.progressbar_thermocycler.set(0)
		# Place the Thermocycle Protocol Figure (Default is A)
		self.create_thermocycler_protocol_figure_ui(1)
		# Place the Thermometer Icon
		self.photoimage_thermometer = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['thermometer']),
			size=(IMAGE_THERMOMETER_WIDTH, IMAGE_THERMOMETER_HEIGHT),
		)
		self.image_thermometer = ctk.CTkLabel(master=self, text='', image=self.photoimage_thermometer)
		# Place the Temperature Units Label
		self.label_first_denature_temperature_unit = ctk.CTkLabel(master=self, text='C', font=(FONT,-16))
		self.label_anneal_temperature_unit = ctk.CTkLabel(master=self, text='C', font=(FONT,-16))
		self.label_second_denature_temperature_unit = ctk.CTkLabel(master=self, text='C', font=(FONT,-16))
		# Place the Clock Icon
		self.photoimage_clock = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['clock']),
			size=(IMAGE_CLOCK_WIDTH, IMAGE_CLOCK_HEIGHT),
		)
		self.image_clock = ctk.CTkLabel(master=self, text='', image=self.photoimage_clock)
		# Place the Time Units Labels
		self.label_first_denature_time_unit = ctk.CTkLabel(master=self, text='min', font=(FONT,-16))
		self.label_anneal_time_unit = ctk.CTkLabel(master=self, text='sec', font=(FONT,-16))
		self.label_second_denature_time_unit = ctk.CTkLabel(master=self, text='sec', font=(FONT,-16))
		# Place the 1st Denature Temperature Entry
		self.first_denature_temperature_sv = self.controller.get_first_denature_temperature_sv(1)
		self.first_denature_temperature_sv.trace('w', self.callback_first_denature_temperature)
		self.entry_first_denature_temp = ctk.CTkEntry(
			master=self,
			textvariable=self.first_denature_temperature_sv,
			width=ENTRY_FIRST_DENATURE_TEMP_WIDTH,
			corner_radius=5,
		)
		self.entry_first_denature_temp.bind('<FocusOut>', self.focus_out_temperature)
		# Place the Anneal Temperature Entry
		self.anneal_temperature_sv = self.controller.get_anneal_temperature_sv(1)
		self.anneal_temperature_sv.trace('w', self.callback_anneal_temperature)
		self.entry_anneal_temp = ctk.CTkEntry(
			master=self,
			textvariable=self.anneal_temperature_sv,
			width=ENTRY_ANNEAL_TEMP_WIDTH,
			corner_radius=5,
		)
		self.entry_anneal_temp.bind('<FocusOut>', self.focus_out_temperature)
		# Place the 2nd Denature Temperature Entry
		self.second_denature_temperature_sv = self.controller.get_second_denature_temperature_sv(1)
		self.second_denature_temperature_sv.trace('w', self.callback_second_denature_temperature)
		self.entry_second_denature_temp = ctk.CTkEntry(
			master=self,
			textvariable=self.second_denature_temperature_sv,
			width=ENTRY_SECOND_DENATURE_TEMP_WIDTH,
			corner_radius=5,
		)
		self.entry_second_denature_temp.bind('<FocusOut>', self.focus_out_temperature)
		# Place the 1st Denature Time Entry
		self.first_denature_time_sv = self.controller.get_first_denature_time_sv(1)
		self.first_denature_time_sv.trace('w', self.callback_first_denature_time)
		self.entry_first_denature_time = ctk.CTkEntry(
			master=self,
			textvariable=self.first_denature_time_sv,
			width=ENTRY_FIRST_DENATURE_TIME_WIDTH,
			corner_radius=5,
		)
		self.entry_first_denature_time.bind('<FocusOut>', self.focus_out_time)
		# Place the Anneal Time Entry
		self.anneal_time_sv = self.controller.get_anneal_time_sv(1)
		self.anneal_time_sv.trace('w', self.callback_anneal_time)
		self.entry_anneal_time = ctk.CTkEntry(
			master=self,
			textvariable=self.anneal_time_sv,
			width=ENTRY_ANNEAL_TIME_WIDTH,
			corner_radius=5,
		)
		self.entry_anneal_time.bind('<FocusOut>', self.focus_out_time)
		# Place the 2nd Denature Time Entry
		self.second_denature_time_sv = self.controller.get_second_denature_time_sv(1)
		self.second_denature_time_sv.trace('w', self.callback_second_denature_time)
		self.entry_second_denature_time = ctk.CTkEntry(
			master=self,
			textvariable=self.second_denature_time_sv,
			width=ENTRY_SECOND_DENATURE_TIME_WIDTH,
			corner_radius=5,
		)
		self.entry_second_denature_time.bind('<FocusOut>', self.focus_out_time)
		# Place the A Checkbox
		self.label_a = ctk.CTkLabel(master=self, text='A', font=(FONT, -16))
		self.use_a_iv = self.controller.get_use_a_iv(1)
		self.checkbox_a = ctk.CTkCheckBox(
			master=self,
			text='',
			variable=self.use_a_iv,
			onvalue=1,
			offvalue=0,
			corner_radius=5,
		)
		# Place the B Checkbox
		self.label_b = ctk.CTkLabel(master=self, text='B', font=(FONT, -16))
		self.use_b_iv = self.controller.get_use_b_iv(2)
		self.checkbox_b = ctk.CTkCheckBox(
			master=self,
			text='',
			variable=self.use_b_iv,
			onvalue=1,
			offvalue=0,
			corner_radius=5,
		)
		# Place the C Checkbox
		self.label_c = ctk.CTkLabel(master=self, text='C', font=(FONT, -16))
		self.use_c_iv = self.controller.get_use_c_iv(3)
		self.checkbox_c = ctk.CTkCheckBox(
			master=self,
			text='',
			variable=self.use_c_iv,
			onvalue=1,
			offvalue=0,
			corner_radius=5,
		)
		# Place the D Checkbox
		self.label_d = ctk.CTkLabel(master=self, text='D', font=(FONT, -16))
		self.use_d_iv = self.controller.get_use_d_iv(4)
		self.checkbox_d = ctk.CTkCheckBox(
			master=self,
			text='',
			variable=self.use_d_iv,
			onvalue=1,
			offvalue=0,
			corner_radius=5,
		)
		# Create a clamp height label and entry
		self.button_settings = ctk.CTkButton(
			master=self,
			text="Settings",
			corner_radius=2,
			width=BUTTON_SETTINGS_WIDTH,
		)
		# Create a TEC control settings button
		self.button_tec = ctk.CTkButton(
			master=self,
			text='TEC',
			corner_radius=2,
			width=BUTTON_TEC_WIDTH,
		)

	def place_ui(self) -> None:
		"""Deals with generation of the ThermocycleView UI"""
		# Place Thermocycle Frame
		self.place(x=self.posx, y=self.posy)
		# Place the Thermocycler Protocol Label
		self.label_thermocycler_protocol.place(x=LABEL_THERMOCYCLER_PROTOCOL_POSX, y=LABEL_THERMOCYCLER_PROTOCOL_POSY)
		# Place the Thermocycler Option Menu
		self.label_thermocycler.place(x=LABEL_THERMOCYCLER_POSX, y=LABEL_THERMOCYCLER_POSY)
		self.optionmenu_thermocycler.place(x=OPTIONMENU_THERMOCYCLER_POSX, y=OPTIONMENU_THERMOCYCLER_POSY)
		# Place the Cycles Entry
		self.label_cycles.place(x=LABEL_CYCLES_POSX, y=LABEL_CYCLES_POSY)
		self.entry_cycles.place(x=ENTRY_CYCLES_POSX, y=ENTRY_CYCLES_POSY)
		# Place the Thermocycler Image
		self.image_thermocycler_rails.place(x=IMAGE_THERMOCYCLER_RAILS_POSX, y=IMAGE_THERMOCYCLER_RAILS_POSY)
		self.image_thermocycler_tray_ab.place(x=IMAGE_THERMOCYCLER_TRAY_AB_POSX, y=IMAGE_THERMOCYCLER_TRAY_AB_POSY)
		self.image_thermocycler_block_a.place(x=IMAGE_THERMOCYCLER_BLOCK_A_POSX, y=IMAGE_THERMOCYCLER_BLOCK_A_POSY)
		self.image_thermocycler_block_b.place(x=IMAGE_THERMOCYCLER_BLOCK_B_POSX, y=IMAGE_THERMOCYCLER_BLOCK_B_POSY)
		self.image_thermocycler_tray_cd.place(x=IMAGE_THERMOCYCLER_TRAY_CD_POSX, y=IMAGE_THERMOCYCLER_TRAY_CD_POSY)
		self.image_thermocycler_block_c.place(x=IMAGE_THERMOCYCLER_BLOCK_C_POSX, y=IMAGE_THERMOCYCLER_BLOCK_C_POSY)
		self.image_thermocycler_block_d.place(x=IMAGE_THERMOCYCLER_BLOCK_D_POSX, y=IMAGE_THERMOCYCLER_BLOCK_D_POSY)
		self.button_block_left.place(x=BUTTON_BLOCK_LEFT_POSX, y=BUTTON_BLOCK_LEFT_POSY)
		self.button_block_right.place(x=BUTTON_BLOCK_RIGHT_POSX, y=BUTTON_BLOCK_RIGHT_POSY)
		self.button_block_top.place(x=BUTTON_BLOCK_TOP_POSX, y=BUTTON_BLOCK_TOP_POSY)
		self.button_block_bottom.place(x=BUTTON_BLOCK_BOTTOM_POSX, y=BUTTON_BLOCK_BOTTOM_POSY)
		# Place the Start Button
		self.button_start.place(x=BUTTON_START_POSX, y=BUTTON_START_POSY)
		# Place the Load Button
		self.button_load.place(x=BUTTON_LOAD_POSX, y=BUTTON_LOAD_POSY)
		# Place the Save Button
		self.button_save.place(x=BUTTON_SAVE_POSX, y=BUTTON_SAVE_POSY)
		# Place the Home Button
		self.button_home.place(x=BUTTON_HOME_POSX, y=BUTTON_HOME_POSY)
		# Place the Thermocycler ProgressBar
		self.progressbar_thermocycler.place(x=PROGRESSBAR_THERMOCYCLER_POSX, y=PROGRESSBAR_THERMOCYCLER_POSY)
		# Place the Thermocycle Protocol Figure (Default is A)
		self.place_thermocycler_protocol_figure_ui(1)
		# Place the Thermometer Icon
		self.image_thermometer.place(x=IMAGE_THERMOMETER_POSX, y=IMAGE_THERMOMETER_POSY)
		# Place the Temperature Units Label
		self.label_first_denature_temperature_unit.place(
			x=LABEL_FIRST_DENATURE_TEMPERATURE_UNIT_POSX, 
			y=LABEL_FIRST_DENATURE_TEMPERATURE_UNIT_POSY
		)
		self.label_anneal_temperature_unit.place(
			x=LABEL_ANNEAL_TEMPERATURE_UNIT_POSX, 
			y=LABEL_ANNEAL_TEMPERATURE_UNIT_POSY
		)
		self.label_second_denature_temperature_unit.place(
			x=LABEL_SECOND_DENATURE_TEMPERATURE_UNIT_POSX, 
			y=LABEL_SECOND_DENATURE_TEMPERATURE_UNIT_POSY
		)
		# Place the Clock Icon
		self.image_clock.place(x=IMAGE_CLOCK_POSX, y=IMAGE_CLOCK_POSY)
		# Place the Time Units Labels
		self.label_first_denature_time_unit.place(
			x=LABEL_FIRST_DENATURE_TIME_UNIT_POSX, 
			y=LABEL_FIRST_DENATURE_TIME_UNIT_POSY
		)
		self.label_anneal_time_unit.place(
			x=LABEL_ANNEAL_TIME_UNIT_POSX, 
			y=LABEL_ANNEAL_TIME_UNIT_POSY
		)
		self.label_second_denature_time_unit.place(
			x=LABEL_SECOND_DENATURE_TIME_UNIT_POSX, 
			y=LABEL_SECOND_DENATURE_TIME_UNIT_POSY
		)
		# Place the 1st Denature Temperature Entry
		self.entry_first_denature_temp.place(x=ENTRY_FIRST_DENATURE_TEMP_POSX, y=ENTRY_FIRST_DENATURE_TEMP_POSY)
		# Place the Anneal Temperature Entry
		self.entry_anneal_temp.place(x=ENTRY_ANNEAL_TEMP_POSX, y=ENTRY_ANNEAL_TEMP_POSY)
		# Place the 2nd Denature Temperature Entry
		self.entry_second_denature_temp.place(x=ENTRY_SECOND_DENATURE_TEMP_POSX, y=ENTRY_SECOND_DENATURE_TEMP_POSY)
		# Place the 1st Denature Time Entry
		self.entry_first_denature_time.place(x=ENTRY_FIRST_DENATURE_TIME_POSX, y=ENTRY_FIRST_DENATURE_TIME_POSY)
		# Place the Anneal Time Entry
		self.entry_anneal_time.place(x=ENTRY_ANNEAL_TIME_POSX, y=ENTRY_ANNEAL_TIME_POSY)
		# Place the 2nd Denature Time Entry
		self.entry_second_denature_time.place(x=ENTRY_SECOND_DENATURE_TIME_POSX, y=ENTRY_SECOND_DENATURE_TIME_POSY)
		# Place the A Checkbox
		self.label_a.place(x=LABEL_A_POSX, y=LABEL_A_POSY)
		self.checkbox_a.place(x=CHECKBOX_A_POSX, y=CHECKBOX_A_POSY)
		# Place the B Checkbox
		self.label_b.place(x=LABEL_B_POSX, y=LABEL_B_POSY)
		self.checkbox_b.place(x=CHECKBOX_B_POSX, y=CHECKBOX_B_POSY)
		# Place the C Checkbox
		self.label_c.place(x=LABEL_C_POSX, y=LABEL_C_POSY)
		self.checkbox_c.place(x=CHECKBOX_C_POSX, y=CHECKBOX_C_POSY)
		# Place the D Checkbox
		self.label_d.place(x=LABEL_D_POSX, y=LABEL_D_POSY)
		self.checkbox_d.place(x=CHECKBOX_D_POSX, y=CHECKBOX_D_POSY)
		# Place the clamp settings button
		self.button_settings.place(x=BUTTON_SETTINGS_POSX, 
			y=BUTTON_SETTINGS_POSY)
		# Place the TEC control settings button
		self.button_tec.place(x=BUTTON_TEC_POSX,
			y=BUTTON_TEC_POSY)

	def on_click(self, event):
		x, y = event.x, event.y
		print(f"{x}, {y}")

	def on_click_tray_ab(self, event):
		""" Deals with on_click events for Thermocycler Tray AB"""
		# Get the current posx
		posx = int(self.image_thermocycler_tray_ab.place_info()['x'])
		# Make sure the tray is allowed to close
		if True:
			if posx == TRAY_CLOSED_POSX:
				x0 = posx
				x = IMAGE_THERMOCYCLER_TRAY_AB_POSX
				steps = 0
			else:
				x0 = IMAGE_THERMOCYCLER_TRAY_AB_POSX
				x = TRAY_CLOSED_POSX
				steps = -790000
			# Change the posx
			thread = threading.Thread(
				target=self.move_tray, 
				args=(
					ADDRESSES['AB'],
					self.image_thermocycler_tray_ab, 
					x0,
					x,
					steps,
					#IMAGE_THERMOCYCLER_TRAY_AB_POSX,
					#TRAY_CLOSED_POSX, 
				)
			)
			thread.start()

	def on_click_tray_cd(self, event):
		""" Deals with on_click events for Thermocycler Tray CD"""
		# Get the current posx
		posx = int(self.image_thermocycler_tray_cd.place_info()['x'])
		# Make sure the tray is allowed to close
		if True:
			if posx == TRAY_CLOSED_POSX:
				x0 = posx
				x = IMAGE_THERMOCYCLER_TRAY_CD_POSX
				steps = 0
			else:
				x0 = IMAGE_THERMOCYCLER_TRAY_CD_POSX
				x = TRAY_CLOSED_POSX
				steps = -790000
			# Change the posx
			thread = threading.Thread(
				target=self.move_tray, 
				args=(
					ADDRESSES['CD'],
					self.image_thermocycler_tray_cd, 
					x0,
					x,
					steps,
				)
			)
			thread.start()

	def on_click_rails(self, event):
		""" Deals with on_click events for Thermocycler Rails"""
		# Get x and y from the click event
		x, y = event.x, event.y
		# Determine which tray is being clicked
		if x >= 5 and x <= 106 and y >= 16 and y <= 235:
			# Make sure tray ab is allowed to open
			if True:
				# If clicking the rails we most likely want to open the tray
				steps = 0
				# Open the tray (change posx)
				thread = threading.Thread(
					target=self.move_tray, 
					args=(
						ADDRESSES['AB'],
						self.image_thermocycler_tray_ab, 
						TRAY_CLOSED_POSX, 
						IMAGE_THERMOCYCLER_TRAY_AB_POSX,
						steps,
					)
				)
				thread.start()
		elif x >= 5 and x <= 106 and y >= 241 and y <= 463:
			# Make sure tray cd is allowed to open
			if True:
				# If clicking the rails we most likely want to open the tray
				steps = 0
				# Open the tray (change posx)
				thread = threading.Thread(
					target=self.move_tray, 
					args=(
						ADDRESSES['CD'],
						self.image_thermocycler_tray_cd, 
						TRAY_CLOSED_POSX, 
						IMAGE_THERMOCYCLER_TRAY_CD_POSX,
						steps,
					)
				)
				thread.start()

	def on_click_thermocycler_a(self, event):
		""" Deals with on_click events for Thermocycler Block A"""
		# Check if the trays are moving
		posx = int(self.image_thermocycler_tray_ab.place_info()['x'])
		if posx not in [IMAGE_THERMOCYCLER_TRAY_AB_POSX, TRAY_CLOSED_POSX]:
			if tk.messagebox.askyesno(title="Move Thermocycler A Clamp", message="Tray AB is not fully open or closed, this could cause the clamp to hit the Tray, continue anyway?") == False:
				return None
		# Get the current state of the thermocycler
		state = self.controller.get_clamp(1)
		# Lower of Raise the thermocycler
		if state:
			self.fast_api_interface.reader.axis.move('reader', 8, -400000, 100000, False, True)
			self.photoimage_thermocycler_block_a = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_lowered']),
				size=(IMAGE_THERMOCYCLER_BLOCK_A_WIDTH, IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT),
			)
			self.controller.set_clamp(1, 0)
		else:
			self.fast_api_interface.reader.axis.move('reader', 8, 0, 100000, False, True)
			self.photoimage_thermocycler_block_a = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
				size=(IMAGE_THERMOCYCLER_BLOCK_A_WIDTH, IMAGE_THERMOCYCLER_BLOCK_A_HEIGHT),
			)
			self.controller.set_clamp(1, 1)
		self.image_thermocycler_block_a.configure(image=self.photoimage_thermocycler_block_a)

	def on_click_thermocycler_b(self, event):
		""" Deals with on_click events for Thermocycler Block B"""
		# Check if the trays are moving
		posx = int(self.image_thermocycler_tray_ab.place_info()['x'])
		if posx not in [IMAGE_THERMOCYCLER_TRAY_AB_POSX, TRAY_CLOSED_POSX]:
			if tk.messagebox.askyesno(title="Move Thermocycler B Clamp", message="Tray AB is not fully open or closed, this could cause the clamp to hit the Tray, continue anyway?") == False:
				return None
		# Get the current state of the thermocycler
		state = self.controller.get_clamp(2)
		# Lower of Raise the thermocycler
		if state:
			self.fast_api_interface.reader.axis.move('reader', 9, -400000, 100000, False, True)
			self.photoimage_thermocycler_block_b = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_lowered']),
				size=(IMAGE_THERMOCYCLER_BLOCK_B_WIDTH, IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT),
			)
			self.controller.set_clamp(2,0)
		else:
			self.fast_api_interface.reader.axis.move('reader', 9, 0, 100000, False, True)
			self.photoimage_thermocycler_block_b = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
				size=(IMAGE_THERMOCYCLER_BLOCK_B_WIDTH, IMAGE_THERMOCYCLER_BLOCK_B_HEIGHT),
			)
			self.controller.set_clamp(2,1)
		self.image_thermocycler_block_b.configure(image=self.photoimage_thermocycler_block_b)

	def on_click_thermocycler_c(self, event):
		""" Deals with on_click events for Thermocycler Block C"""
		# Check if the trays are moving
		posx = int(self.image_thermocycler_tray_cd.place_info()['x'])
		if posx not in [IMAGE_THERMOCYCLER_TRAY_CD_POSX, TRAY_CLOSED_POSX]:
			if tk.messagebox.askyesno(title="Move Thermocycler C Clamp", message="Tray CD is not fully open or closed, this could cause the clamp to hit the Tray, continue anyway?") == False:
				return None
		# Get the current state of the thermocycler
		state = self.controller.get_clamp(3)
		# Lower of Raise the thermocycler
		if state:
			self.fast_api_interface.reader.axis.move('reader', 10, -400000, 100000, False, True)
			self.photoimage_thermocycler_block_c = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_lowered']),
				size=(IMAGE_THERMOCYCLER_BLOCK_C_WIDTH, IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT),
			)
			self.controller.set_clamp(3,0)
		else:
			self.fast_api_interface.reader.axis.move('reader', 10, 0, 100000, False, True)
			self.photoimage_thermocycler_block_c = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
				size=(IMAGE_THERMOCYCLER_BLOCK_C_WIDTH, IMAGE_THERMOCYCLER_BLOCK_C_HEIGHT),
			)
			self.controller.set_clamp(3,1)
		self.image_thermocycler_block_c.configure(image=self.photoimage_thermocycler_block_c)

	def on_click_thermocycler_d(self, event):
		""" Deals with on_click events for Thermocycler Block D"""
		# Check if the trays are moving
		posx = int(self.image_thermocycler_tray_cd.place_info()['x'])
		if posx not in [IMAGE_THERMOCYCLER_TRAY_CD_POSX, TRAY_CLOSED_POSX]:
			if tk.messagebox.askyesno(title="Move Thermocycler D Clamp", message="Tray CD is not fully open or closed, this could cause the clamp to hit the Tray, continue anyway?") == False:
				return None
		# Get the current state of the thermocycler
		state = self.controller.get_clamp(4)
		# Lower of Raise the thermocycler
		if state:
			self.fast_api_interface.reader.axis.move('reader', 11, -400000, 100000, False, True)
			self.photoimage_thermocycler_block_d = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_lowered']),
				size=(IMAGE_THERMOCYCLER_BLOCK_D_WIDTH, IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT),
			)
			self.controller.set_clamp(4,0)
		else:
			self.fast_api_interface.reader.axis.move('reader', 11, 0, 100000, False, True)
			self.photoimage_thermocycler_block_d = ctk.CTkImage(
				dark_image=Image.open(IMAGE_PATHS['thermocycler_block_raised']),
				size=(IMAGE_THERMOCYCLER_BLOCK_D_WIDTH, IMAGE_THERMOCYCLER_BLOCK_D_HEIGHT),
			)
			self.controller.set_clamp(4,1)
		self.image_thermocycler_block_d.configure(image=self.photoimage_thermocycler_block_d)

	def move_tray(self, address: int, image_tray: ctk.CTkLabel, x0:int , x:int , steps: int = -790000, seconds:int=7, n_steps:int=TRAY_N_STEPS, use_fast_api: bool = True) -> None:
		""" Movement animation for a given tray between an initial position x0 and final x with a given
		number of frames (n_steps)

		Parameters
		----------
		image_tray : ctk.CTkLabel
			The widget which holds the image of the tray being moved
		x0 : int
			The initial x position relative the the master widget
		x : int
			The final x position relative to the master widget
		seconds : int, optional
			Total time for animation
		n_steps : int, optional
			Number of steps / frames for the animation
		"""
		# Import the 
		# Get the animation steps
		dx = (x-x0)/n_steps
		dt = seconds/n_steps
		if steps != 0:
			steps = -abs(steps)
		# Determine the direction to move the tray (open or closed)
		if use_fast_api:
			if steps == 0:
				self.fast_api_interface.reader.axis.move('reader', address, 0, 200000, False, True)
				for i in range(n_steps):
					image_tray.place(x=x0)
					x0 = x0 + dx
					time.sleep(dt)
				image_tray.place(x=x)
				#self.fast_api_interface.reader.axis.home('reader', address, False, True)
				return None
			try:
				if dx < 0:
					# Close the tray (dx is based on position of the tray widget in its parent frame)
					#a = 1
					self.fast_api_interface.reader.axis.move('reader', address, steps, 200000, False, True)
					if steps == 0:
						self.fast_api_interface.reader.axis.home('reader', address, False, True)
				else:
					# Open the tray
					#a = 1
					self.fast_api_interface.reader.axis.move('reader', address, steps, 200000, False, True)
			except:
				pass
		# Animate the tray while the actual tray moves
		for i in range(n_steps):
			image_tray.place(x=x0)
			x0 = x0 + dx
			time.sleep(dt)
		image_tray.place(x=x)

	def callback_thermocycler(self, *args) -> None:
		"""Deals with changes to the thermocycler option"""
		for ID in [1,2,3,4,5]:
			print(self.model.select(ID))
		# Get the ID for the current thermocycler
		ID = IDS[self.thermocycler_sv.get()]
		# Get the protocol data
		cycles = self.controller.get_cycles(ID)
		first_denature_temperature = self.controller.get_first_denature_temperature(ID)
		anneal_temperature = self.controller.get_anneal_temperature(ID)
		second_denature_temperature = self.controller.get_second_denature_temperature(ID)
		first_denature_time = self.controller.get_first_denature_time(ID)
		anneal_time = self.controller.get_anneal_time(ID)
		second_denature_time = self.controller.get_second_denature_time(ID)
		# Update the cycles entry
		self.cycles_sv.set(cycles)
		# Update the protocol temperatures
		self.first_denature_temperature_sv.set(first_denature_temperature)
		self.anneal_temperature_sv.set(anneal_temperature)
		self.second_denature_temperature_sv.set(second_denature_temperature)
		# Update the protocol times
		self.first_denature_time_sv.set(first_denature_time)
		self.anneal_time_sv.set(anneal_time)
		self.second_denature_time_sv.set(second_denature_time)
		# Update the thermocycler protocol figure ui
		self.create_thermocycler_protocol_figure_ui(ID)

	def callback_cycles(self, *args) -> None:
		""" Deals with changes to the number of cycles entry"""
		# Get the current thermocycler
		ID = IDS[self.thermocycler_sv.get()]
		# Get the number of cycles
		try:
			cycles = int(self.cycles_sv.get())
		except:
			pass
		# Update the model
		try:
			self.controller.set_cycles(ID, cycles)
		except:
			pass

	def callback_first_denature_temperature(self, *args) -> None:
		"""Deals with changes to the first denature temperature entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_first_denature_temperature(ID, int(self.first_denature_temperature_sv.get()))
		except:
			pass

	def callback_anneal_temperature(self, *args) -> None:
		"""Deals with changes to the anneal temperature entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_anneal_temperature(ID, int(self.anneal_temperature_sv.get()))
		except:
			pass

	def callback_second_denature_temperature(self, *args) -> None:
		"""Deals with changes to the second denature temperature entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_second_denature_temperature(ID, int(self.second_denature_temperature_sv.get()))
		except:
			pass

	def callback_first_denature_time(self, *args) -> None:
		"""Deals with changes to the first denature time entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_first_denature_time(ID, int(self.first_denature_time_sv.get()))
		except:
			pass

	def callback_anneal_time(self, *args) -> None:
		"""Deals with changes to the anneal time entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_anneal_time(ID, int(self.anneal_time_sv.get()))
		except:
			pass

	def callback_second_denature_time(self, *args) -> None:
		"""Deals with changes to the second denature time entry"""
		# Get the current thermocycler ID
		ID = IDS[self.thermocycler_sv.get()]
		# Update the model
		try:
			self.controller.set_second_denature_time(ID, int(self.second_denature_time_sv.get()))
		except:
			pass

	def focus_out_temperature(self, event) -> None:
		"""Deals with what happens after focus leaves the entry"""
		# Get the ID for the thermocycler 
		ID = IDS[self.thermocycler_sv.get()]
		# Create the thermocycler protocol figure ui
		self.create_thermocycler_protocol_figure_ui(ID)

	def focus_out_time(self, event) -> None:
		"""Deals with what happens after focus leaves the entry"""
		# Get the ID for the thermocycler 
		ID = IDS[self.thermocycler_sv.get()]

	def create_thermocycler_protocol_figure_ui(self, ID: int) -> None:
		"""Deals with creating the thermocycle protocol figure ui

		Parameters
		----------
		ID : int
			ID for the Thermocycler figure to be created 
		"""
		# Make sure the ID is valid
		assert ID in IDS.values()
		# Remove old widgets
		# Get the temperature data for the thermocycler
		first_denature_temperature = self.controller.get_first_denature_temperature(ID)
		anneal_temperature = self.controller.get_anneal_temperature(ID)
		second_denature_temperature = self.controller.get_second_denature_temperature(ID)
		data = [
			first_denature_temperature,
			first_denature_temperature,
			anneal_temperature,
			anneal_temperature,
			second_denature_temperature,
			second_denature_temperature
		]
		# Setup the figure
		fig = Figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT)) 
		fig.set_facecolor(FIGURE_FACECOLOR)
		a = fig.add_subplot(111)
		x = np.array([1,2,3,4,5,6])
		a.set_yticks([data[0], data[2], data[4]])
		a.set_xticks([])
		a.axvline(x=2.5)
		a.axvline(x=4.5)
		a.set_facecolor(FIGURE_FACECOLOR)
		a.tick_params(color=FIGURE_TICK_COLOR, labelcolor=FIGURE_TICK_LABELCOLOR)
		for pos in ['top', 'bottom', 'left', 'right']:
			a.spines[pos].set_edgecolor(FIGURE_SPINES_COLOR)
		a.plot(x, data, color=FIGURE_PLOT_COLOR)
		# Setup the Canvas widget
		self.canvas = FigureCanvasTkAgg(fig, master=self)
		self.canvas.flush_events()
		self.canvas.get_tk_widget().place(x=FIGURE_POSX, y=FIGURE_POSY)
		self.canvas.draw()
		# Add the protocol section labels
		self.label_first_denature = ctk.CTkLabel(
			master=self,
			text="1st Denature",
			text_color=LABEL_FIRST_DENATURE_COLOR,
			font=(FONT, -12),
			width=LABEL_FIRST_DENATURE_WIDTH,
		)
		self.label_first_denature.place(x=LABEL_FIRST_DENATURE_POSX, y=LABEL_FIRST_DENATURE_POSY)
		self.label_anneal = ctk.CTkLabel(
			master=self,
			text='Anneal',
			text_color=LABEL_ANNEAL_COLOR,
			font=(FONT, -12),
			width=LABEL_ANNEAL_WIDTH,
		)
		self.label_anneal.place(x=LABEL_ANNEAL_POSX, y=LABEL_ANNEAL_POSY)
		self.label_second_denature = ctk.CTkLabel(
			master=self,
			text="2nd Denature",
			text_color=LABEL_SECOND_DENATURE_COLOR,
			font=(FONT, -12),
			width=LABEL_SECOND_DENATURE_WIDTH,
		)
		self.label_second_denature.place(x=LABEL_SECOND_DENATURE_POSX, y=LABEL_SECOND_DENATURE_POSY)

	def place_thermocycler_protocol_figure_ui(self, ID: int) -> None:
		"""Deals with creating the thermocycle protocol figure ui

		Parameters
		----------
		ID : int
			ID for the Thermocycler figure to be created 
		"""
		# Make sure the ID is valid
		assert ID in IDS.values()
		self.canvas.get_tk_widget().place(x=FIGURE_POSX, y=FIGURE_POSY)
		# Add the protocol section labels
		self.label_first_denature.place(x=LABEL_FIRST_DENATURE_POSX, y=LABEL_FIRST_DENATURE_POSY)
		self.label_anneal.place(x=LABEL_ANNEAL_POSX, y=LABEL_ANNEAL_POSY)
		self.label_second_denature.place(x=LABEL_SECOND_DENATURE_POSX, y=LABEL_SECOND_DENATURE_POSY)

	def trace_cycles_sv(self, callback: Callable[[tk.Event], None]) -> None: 
		""" Deals with the changing of cycles_sv """
		try:
			self.controller.get_cycles_sv().trace('w', callback)
		except:
			pass
		
	def trace_first_denature_time_sv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the first denature time """
		try:
			self.controller.get_first_denature_time_sv().trace('w', callback)
		except:
			pass

	def trace_anneal_time_sv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the anneal time """
		try:
			self.controller.get_anneal_time_sv().trace('w', callback)
		except:
			pass

	def trace_second_denature_time_sv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the second denature time """
		try:
			self.controller.get_second_denature_time_sv().trace('w', callback)
		except:
			pass

	def trace_use_a_iv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the use checkbox """
		try:
			self.controller.get_use_a_iv().trace('w', callback)
		except:
			pass

	def trace_use_b_iv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the use checkbox """
		try:
			self.controller.get_use_b_iv().trace('w', callback)
		except:
			pass

	def trace_use_c_iv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the use checkbox """
		try:
			self.controller.get_use_c_iv().trace('w', callback)
		except:
			pass

	def trace_use_d_iv(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the changing of the use checkbox """
		try:
			self.controller.get_use_d_iv().trace('w', callback)
		except:
			pass

	def bind_button_start(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the start button to the controller """
		try:
			self.button_start.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_save(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the save button to the controller """
		try:
			self.button_save.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_load(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the load button to the controller """
		try:
			self.button_load.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_home(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the home button to the controller """
		try:
			self.button_home.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_settings(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the settings button """
		try:
			self.button_settings.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_tec(self, callback: Callable[[tk.Event], None]) -> None:
		""" Binds the TEC settings button """
		try:
			self.button_tec.bind('<Button-1>', callback)
		except:
			pass
