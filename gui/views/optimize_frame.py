from typing_extensions import Self
import customtkinter as ctk
import tkinter as tk

from tkinter import StringVar, IntVar

import threading
from PIL import Image
from typing import Any, Callable

# Import the Optimze Model
from gui.models.model import Model

# Constants
FONT = "Segoe UI"
IMAGE_DECK_PLATE_POSX = 0
IMAGE_DECK_PLATE_POSY = 45
IMAGE_DECK_PLATE_WIDTH = 600
IMAGE_DECK_PLATE_HEIGHT = 440
LABEL_CONSUMABLE_POSX = 5
LABEL_CONSUMABLE_POSY = 10
OPTIONMENU_CONSUMABLE_POSX = 100
OPTIONMENU_CONSUMABLE_POSY = 10
OPTIONMENU_CONSUMABLE_WIDTH = 190
LABEL_TRAY_POSX = 300
LABEL_TRAY_POSY = 10
OPTIONMENU_TRAY_POSX = 340 
OPTIONMENU_TRAY_POSY =10
OPTIONMENU_TRAY_WIDTH = 60
LABEL_COLUMN_POSX = 410
LABEL_COLUMN_POSY = 10
OPTIONMENU_COLUMN_POSX = 475
OPTIONMENU_COLUMN_POSY = 10
OPTIONMENU_COLUMN_WIDTH = 90
BUTTON_PRINT_POSX = 5
BUTTON_PRINT_POSY = 485
BUTTON_PRINT_WIDTH = 30
BUTTON_PRINT_COLOR = '#10adfe'
BUTTON_HOME_Z_POSX = 45
BUTTON_HOME_Z_POSY = 485
BUTTON_HOME_Z_WIDTH = 55
BUTTON_HOME_Y_POSX = 105
BUTTON_HOME_Y_POSY = 485
BUTTON_HOME_Y_WIDTH = 55
BUTTON_HOME_X_POSX = 165
BUTTON_HOME_X_POSY = 485
BUTTON_HOME_X_WIDTH = 55
LABEL_X_POSX = 300
LABEL_X_POSY = 485
ENTRY_X_POSX = 320
ENTRY_X_POSY = 485
ENTRY_X_WIDTH = 75
LABEL_Y_POSX = 400
LABEL_Y_POSY = 485
ENTRY_Y_POSX = 419
ENTRY_Y_POSY = 485
ENTRY_Y_WIDTH = 75
LABEL_Z_POSX = 500
LABEL_Z_POSY = 485
ENTRY_Z_POSX = 515
ENTRY_Z_POSY = 485
ENTRY_Z_WIDTH = 75
CHECKBOX_USE_Z_POSX = 230
CHECKBOX_USE_Z_POSY = 80
CHECKBOX_SLOW_Z_POSX = 230
CHECKBOX_SLOW_Z_POSY = 105
BUTTON_HOME_POSX = 10 #215
BUTTON_HOME_POSY = 45 #40
BUTTON_HOME_WIDTH = 60
BUTTON_MOVE_POSX = 75
BUTTON_MOVE_POSY = 45
BUTTON_MOVE_WIDTH = 60
BUTTON_UPDATE_POSX = 140
BUTTON_UPDATE_POSY = 45
BUTTON_UPDATE_WIDTH = 60
BUTTON_UPDATE_COLOR = '#10adfe'
BUTTON_DRIP_PLATE_POSX = 215
BUTTON_DRIP_PLATE_POSY = 45
BUTTON_DRIP_PLATE_WIDTH = 70
OPTIONMENU_TIP_POSX = 225
OPTIONMENU_TIP_POSY = 485
OPTIONMENU_TIP_WIDTH = 70

# Deck Plate Coordinate Bounds
BOUNDS = {
	'quant_strip': {
		'x_min': 571,
		'x_max': 591,
		'y_min': 89,
		'y_max': 435,
	},
	'tip_box': {
		'x_min': 464,
		'x_max': 566,
		'y_min': 91,
		'y_max': 438,
	},
	'reagent_cartridge': {
		'x_min': 327,
		'x_max': 455,
		'y_min': 90,
		'y_max': 438,
	},
	'dg8': {
		'x_min': 335,
		'x_max': 450,
		'y_min': 15,
		'y_max': 84,
	},
	'sample_rack': {
		'x_min': 283,
		'x_max': 317,
		'y_min': 87,
		'y_max': 434,
	},
	'aux_heater': {
		'x_min': 247,
		'x_max': 275,
		'y_min': 89,
		'y_max': 434,
	},
	'heater_shaker': {
		'x_min': 117,
		'x_max': 238,
		'y_min': 176,
		'y_max': 257,
	},
	'mag_separator': {
		'x_min': 116,
		'x_max': 238,
		'y_min': 265,
		'y_max': 342,
	},
	'chiller': {
		'x_min': 114,
		'x_max': 237,
		'y_min': 350,
		'y_max': 428,
	},
	'pre_amp_thermocycler': {
		'x_min': 38,
		'x_max': 166,
		'y_min': 60,
		'y_max': 143,
	},
	'lid_tray': {
		'x_min': 5,
		'x_max': 109,
		'y_min': 174,
		'y_max': 256,
	},
	'tip_transfer_tray': {
		'x_min': 6,
		'x_max': 108,
		'y_min': 262,
		'y_max': 344,
	},
	'asay_strip': {
		'x_min': 3,
		'x_max': 102,
		'y_min': 353,
		'y_max': 433,
	},
}

# Consumables
CONSUMABLES = (
	"Quant Strip",
	"Tip Box",
	"Reagent Cartridge",
	"Sample Rack",
	"Aux Heater",
	"Heater/Shaker",
	"Mag Separator",
	"Chiller",
	"Pre-Amp Thermocycler",
	"Lid Tray",
	"Tip Transfer Tray",
	"Assay Strip",
	"DG8",
	"Chip",
	"",
)
NO_TRAY_CONSUMABLES = ["Pre-Amp Thermocycler", "Assay Strip", "Heater/Shaker", "Mag Separator", "Chiller", "Tip Transfer Tray"]
NO_COLUMN_CONSUMABLES = ["Aux Heater", "Sample Rack", "Quant Strip"]
TWELVE_COLUMN_CONSUMABLES = ["Pre-Amp Thermocycler", "Mag Separator", "Chiller", "Reagent Cartridge", "DG8"]
EIGHT_COLUMN_CONSUMABLES = ["Tip Transfer Tray", "Assay Strip", "Tip Tray"]
FOUR_COLUMN_CONSUMABLES = ["Heater/Shaker"]
THREE_COLUMN_CONSUMABLES = [""]
SPECIAL_CONSUMABLES = ["DG8", "Chip"]

# Image Paths
IMAGE_PATHS = {
	'deck_plate': 'gui/images/deck_plate.png',
}

class OptimizeFrame(ctk.CTkFrame):
	"""Optmize Frame UI for the Optimze View
	"""
	def __init__(self,
		master: ctk.CTk,
		width: int,
		height: int,
		posx: int,
		posy: int
	) -> None:
		model = Model()
		self.model = model.get_optimize_model()
		self.coordinates_model = model.get_coordinates_model('A')
		self.master = master
		self.width = width
		self.height = height
		self.posx = posx
		self.posy = posy
		super().__init__(
			master=self.master,
			width=self.width,
			height=self.height,
			corner_radius=0,
		)
		self.create_ui()
		self.bind('<Up>', self.up)

	def up(self, event):
		print('here')

	def create_ui(self) -> None:
		"""Deals with the creation of the UI
		"""
		# Create the consumable, tray, and column labels and optionmenus
		self.label_consumable = ctk.CTkLabel(master=self, text='Consumable', font=(FONT, -16))
		self.consumable_sv = self.model.get_consumable_sv()
		self.consumable_sv.set('')
		self.optionmenu_consumable = ctk.CTkOptionMenu(
			master=self,
			variable=self.consumable_sv,
			values=CONSUMABLES,
			font=(FONT,-14),
			width=OPTIONMENU_CONSUMABLE_WIDTH,
			corner_radius=5,
		)
		self.label_tray = ctk.CTkLabel(master=self, text='Tray', font=(FONT, -16))
		self.tray_sv = self.model.get_tray_sv()
		self.tray_sv.set('')
		self.optionmenu_tray = ctk.CTkOptionMenu(
			master=self,
			variable=self.tray_sv,
			values=('',),
			font=(FONT,-14),
			width=OPTIONMENU_TRAY_WIDTH,
			corner_radius=5,
		)
		self.label_column = ctk.CTkLabel(master=self, text='Column', font=(FONT, -16))
		self.column_sv = self.model.get_column_sv()
		self.column_sv.set('')
		self.optionmenu_column = ctk.CTkOptionMenu(
                        master=self,
			variable=self.column_sv,
			values=('',),
			font=(FONT,-14),
			width=OPTIONMENU_COLUMN_WIDTH,
			corner_radius=5,
		)
		# Create the deck plate UI
		self.create_deck_plate_ui()
		# Create the use checkboxes
		self.use_z_iv = IntVar()
		self.use_z_iv.set(1)
		self.checkbox_use_z = ctk.CTkCheckBox(
			master=self,
			text="Use Z",
			font=(FONT, -14),
			variable=self.use_z_iv,
			onvalue=1,
			offvalue=0,
		)
		self.slow_z_iv = IntVar()
		self.slow_z_iv.set(1)
		self.checkbox_slow_z = ctk.CTkCheckBox(
			master=self,
			text="Slow Z",
			font=(FONT, -14),
			variable=self.slow_z_iv,
			onvalue=1,
			offvalue=0,
		)
		# Create the home, move, print, and update buttons
		self.button_home = ctk.CTkButton(
			master=self,
			text='Home',
			width=BUTTON_HOME_WIDTH,
			font=(FONT, -16),
		)
		self.button_move = ctk.CTkButton(
			master=self,
			text='Move',
			width=BUTTON_MOVE_WIDTH,
			font=(FONT, -16),
		)
		self.button_update = ctk.CTkButton(
			master=self,
			text='Update',
			width=BUTTON_UPDATE_WIDTH,
			font=(FONT, -16),
			fg_color=BUTTON_UPDATE_COLOR,
		)
		self.button_drip_plate = ctk.CTkButton(
			master=self,
			text="Drip Plate",
			width=BUTTON_DRIP_PLATE_WIDTH,
			font=(FONT, -16),
		)
		self.button_print = ctk.CTkButton(
			master=self,
			text='Print',
			width=BUTTON_PRINT_WIDTH,
			font=(FONT, -12),
			fg_color=BUTTON_PRINT_COLOR,
		)
		self.button_home_z = ctk.CTkButton(
                        master=self,
                        text='Home Z',
			width=BUTTON_HOME_Z_WIDTH,
			font=(FONT,-12),
		)
		self.button_home_y = ctk.CTkButton(
                        master=self,
                        text='Home Y',
			width=BUTTON_HOME_Y_WIDTH,
			font=(FONT,-12),
		)
		self.button_home_x = ctk.CTkButton(
                        master=self,
                        text='Home X',
			width=BUTTON_HOME_X_WIDTH,
			font=(FONT,-12),
		)
		# Create the dx, dy, and dz labels and entries
		self.label_x = ctk.CTkLabel(master=self, text='X', font=(FONT, -16))
		self.x_sv = StringVar()
		self.x_sv.set('5000')
		self.entry_x = ctk.CTkEntry(
			master=self,
			textvariable=self.x_sv,
			font=(FONT,-14),
			width=ENTRY_X_WIDTH,
		)
		self.label_y = ctk.CTkLabel(master=self, text='Y', font=(FONT, -16))
		self.y_sv = StringVar()
		self.y_sv.set('50000')
		self.entry_y = ctk.CTkEntry(
			master=self,
			textvariable=self.y_sv,
			font=(FONT,-14),
			width=ENTRY_Y_WIDTH,
		)
		self.label_z = ctk.CTkLabel(master=self, text='Z', font=(FONT, -16))
		self.z_sv = StringVar()
		self.z_sv.set('50000')
		self.entry_z = ctk.CTkEntry(
			master=self,
			textvariable=self.z_sv,
			font=(FONT,-14),
			width=ENTRY_Z_WIDTH,
		)
		# Create the tip label and optionmenu
		self.tip_sv = StringVar()
		self.tip_sv.set('')
		self.optionmenu_tip = ctk.CTkOptionMenu(
			master=self,
			variable=self.tip_sv,
			values=('1000', '50', '200', ''),
			font=(FONT,-14),
			width=OPTIONMENU_TIP_WIDTH,
			corner_radius=5,
		)

	def place_ui(self) -> None:
		"""Place the UI
		"""
		# Place the frame
		self.place(x=self.posx, y=self.posy)
		# Place the consumable, tray, and column labels and optionmenus
		self.label_consumable.place(x=LABEL_CONSUMABLE_POSX, y=LABEL_CONSUMABLE_POSY)
		self.optionmenu_consumable.place(x=OPTIONMENU_CONSUMABLE_POSX, y=OPTIONMENU_CONSUMABLE_POSY)
		self.label_tray.place(x=LABEL_TRAY_POSX, y=LABEL_TRAY_POSY)
		self.optionmenu_tray.place(x=OPTIONMENU_TRAY_POSX, y=OPTIONMENU_TRAY_POSY)
		self.label_column.place(x=LABEL_COLUMN_POSX, y=LABEL_COLUMN_POSY)
		self.optionmenu_column.place(x=OPTIONMENU_COLUMN_POSX, y=OPTIONMENU_COLUMN_POSY)
		# Place the deck plate UI
		self.place_deck_plate_ui()
		# Place the use checkboxes
		self.checkbox_use_z.place(x=CHECKBOX_USE_Z_POSX, y=CHECKBOX_USE_Z_POSY)
		self.checkbox_slow_z.place(x=CHECKBOX_SLOW_Z_POSX, y=CHECKBOX_SLOW_Z_POSY)
		# Place te home, move, print, and update buttons
		self.button_home.place(x=BUTTON_HOME_POSX, y=BUTTON_HOME_POSY)
		self.button_move.place(x=BUTTON_MOVE_POSX, y=BUTTON_MOVE_POSY)
		self.button_update.place(x=BUTTON_UPDATE_POSX, y=BUTTON_UPDATE_POSY)
		self.button_drip_plate.place(x=BUTTON_DRIP_PLATE_POSX, y=BUTTON_DRIP_PLATE_POSY)
		self.button_print.place(x=BUTTON_PRINT_POSX, y=BUTTON_PRINT_POSY)
		self.button_home_z.place(x=BUTTON_HOME_Z_POSX, y=BUTTON_HOME_Z_POSY)
		self.button_home_y.place(x=BUTTON_HOME_Y_POSX, y=BUTTON_HOME_Y_POSY)
		self.button_home_x.place(x=BUTTON_HOME_X_POSX, y=BUTTON_HOME_X_POSY)
		# Place the dx, dy, dz labels and entries
		self.label_x.place(x=LABEL_X_POSX, y=LABEL_X_POSY)
		self.entry_x.place(x=ENTRY_X_POSX, y=ENTRY_X_POSY)
		self.label_y.place(x=LABEL_Y_POSX, y=LABEL_Y_POSY)
		self.entry_y.place(x=ENTRY_Y_POSX, y=ENTRY_Y_POSY)
		self.label_z.place(x=LABEL_Z_POSX, y=LABEL_Z_POSY)
		self.entry_z.place(x=ENTRY_Z_POSX, y=ENTRY_Z_POSY)
		# Place the tip label and optionmenu
		self.optionmenu_tip.place(x=OPTIONMENU_TIP_POSX, y=OPTIONMENU_TIP_POSY)

	def create_deck_plate_ui(self) -> None:
		""" Create the deck plate UI
		"""
		# Create the image for the deck plate ui
		self.photoimage_deck_plate = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['deck_plate']),
			size=(IMAGE_DECK_PLATE_WIDTH, IMAGE_DECK_PLATE_HEIGHT),
		)
		self.image_deck_plate = ctk.CTkLabel(master=self, text='', image=self.photoimage_deck_plate)
		self.image_deck_plate.bind('<Button-1>', self.on_click_deck_plate)

	def place_deck_plate_ui(self) -> None:
		""" Place the deck plate UI	
		"""
		# Place the image for the deck plate UI
		self.image_deck_plate.place(x=IMAGE_DECK_PLATE_POSX, y=IMAGE_DECK_PLATE_POSY)

	def trace_optionmenu_consumable(self, callback: Callable[[tk.Event], None]) -> None:
		"""Deals with what happens when the consumable optionmenu is changed
		"""
		try:
			self.consumable_sv.trace('w', callback)
		except:
			pass

	def trace_entry_x(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with tracing the x StringVar for the X entry
		"""
		try:
			self.x_sv.trace('w', callback)
		except:
			pass

	def trace_entry_y(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with tracing the x StringVar for the X entry
		"""
		try:
			self.y_sv.trace('w', callback)
		except:
			pass

	def trace_entry_z(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with tracing the x StringVar for the X entry
		"""
		try:
			self.z_sv.trace('w', callback)
		except:
			pass

	def on_click_deck_plate(self, event) -> None:
		"""On click event handler for the deck plate image
		"""
		# Get the coordinates
		x, y = event.x, event.y
		print(f"{x}, {y}")
		self.consumable_sv.set('')
		self.tray_sv.set('')
		self.column_sv.set('')
		# Determine where one the deck plate was clicked
		if x >= BOUNDS['quant_strip']['x_min'] and x <= BOUNDS['quant_strip']['x_max'] and y >= BOUNDS['quant_strip']['y_min'] and y <= BOUNDS['quant_strip']['y_max']:
			# Set the consumable
			self.consumable_sv.set("Quant Strip")
			# Determine the tray
			if y >= BOUNDS['quant_strip']['y_min'] and y <= 169:
				self.tray_sv.set('A')
			elif y >= 175 and y <= 260:
				self.tray_sv.set('B')
			elif y >= 266 and y <= 348:
				self.tray_sv.set('C')
			elif y >= 350 and y <= BOUNDS['quant_strip']['y_max']:
				self.tray_sv.set('D')
		elif x >= BOUNDS['tip_box']['x_min'] and x <= BOUNDS['tip_box']['x_max'] and y >= BOUNDS['tip_box']['y_min'] and y <= BOUNDS['tip_box']['y_max']:
			# Set the consumable
			self.consumable_sv.set("Tip Box")
			# Set the column
			if x >= BOUNDS['tip_box']['x_min'] and x <= 472:
				self.column_sv.set('1')
			elif x >= 473 and x <= 480:
				self.column_sv.set('2')
			elif x >= 481 and x <= 488:
				self.column_sv.set('3')
			elif x >= 489 and x <= 497:
				self.column_sv.set('4')
			elif x >= 498 and x <= 506:
				self.column_sv.set('5')
			elif x >= 507 and x <= 513:
				self.column_sv.set('6')
			elif x >= 514 and x <= 521:
				self.column_sv.set('7')
			elif x >= 522 and x <= 530:
				self.column_sv.set('8')
			elif x >= 531 and x <= 539:
				self.column_sv.set('9')
			elif x >= 540 and x <= 547:
				self.column_sv.set('10')
			elif x >= 548 and x <= 555:
				self.column_sv.set('11')
			elif x >= 556 and x <= BOUNDS['tip_box']['x_max']:
				self.column_sv.set('12')
			# Set the tray
			if y >= BOUNDS['tip_box']['y_min'] and y <= 170:
				self.tray_sv.set('A')
			elif y >= 175 and y <= 258:
				self.tray_sv.set('B')
			elif y >= 266 and y <= 346:
				self.tray_sv.set('C')
			elif y >= 353 and y <= 435:
				self.tray_sv.set('D')
		elif x >= BOUNDS['reagent_cartridge']['x_min'] and x <= BOUNDS['reagent_cartridge']['x_max'] and y >= BOUNDS['reagent_cartridge']['y_min'] and y <= BOUNDS['reagent_cartridge']['y_max']:
			self.consumable_sv.set("Reagent Cartridge")
			# Determine the column
			if x >= BOUNDS['reagent_cartridge']['x_min'] and x <= 338:
				self.column_sv.set('1')
			elif x >= 339 and x <= 348:
				self.column_sv.set('2')
			elif x >= 349 and x <= 359:
				self.column_sv.set('3')
			elif x >= 360 and x <= 369:
				self.column_sv.set('4')
			elif x >= 370 and x <= 379:
				self.column_sv.set('5')
			elif x >= 380 and x <= 390:
				self.column_sv.set('6')
			elif x >= 391 and x <= 401:
				self.column_sv.set('7')
			elif x >= 402 and x <= 411:
				self.column_sv.set('8')
			elif x >= 412 and x <= 422:
				self.column_sv.set('9')
			elif x >= 423 and x <= 433:
				self.column_sv.set('10')
			elif x >= 434 and x <= 443:
				self.column_sv.set('11')
			elif x >= 444 and x <= BOUNDS['reagent_cartridge']['x_max']:
				self.column_sv.set('12')
			# Determine the tray
			if y >= BOUNDS['reagent_cartridge']['y_min'] and y <= 170:
				self.tray_sv.set('A')
			elif y >= 171 and y <= 259:
				self.tray_sv.set('B')
			elif y >= 263 and y <= 348:
				self.tray_sv.set('C')
			elif y >= 350 and y <= 435:
				self.tray_sv.set('D')
		elif x >= BOUNDS['dg8']['x_min'] and x <= BOUNDS['dg8']['x_max'] and y >= BOUNDS['dg8']['y_min'] and y <= BOUNDS['dg8']['y_max']:
			self.consumable_sv.set("DG8")
			self.tray_sv.set('')
			# Determine the column
			if x >= BOUNDS['dg8']['x_min'] and x <= 344:
				self.column_sv.set('1')
			elif x >= 345 and x <= 353:
				self.column_sv.set('2')
			elif x >= 354 and x <= 362:
				self.column_sv.set('3')
			elif x >= 363 and x <= 373:
				self.column_sv.set('4')
			elif x >= 374 and x <= 383:
				self.column_sv.set('5')
			elif x >= 384 and x <= 391:
				self.column_sv.set('6')
			elif x >= 392 and x <= 401:
				self.column_sv.set('7')
			elif x >= 402 and x <= 410:
				self.column_sv.set('8')
			elif x >= 411 and x <= 420:
				self.column_sv.set('9')
			elif x >= 421 and x <= 431:
				self.column_sv.set('10')
			elif x >= 432 and x <= 439:
				self.column_sv.set('11')
			elif x >= 440 and x <= BOUNDS['dg8']['x_max']:
				self.column_sv.set('12')
		elif x >= BOUNDS['sample_rack']['x_min'] and x <= BOUNDS['sample_rack']['x_max'] and y >= BOUNDS['sample_rack']['y_min'] and y <= BOUNDS['sample_rack']['y_max']:
			self.consumable_sv.set("Sample Rack")
			self.column_sv.set('')
			# Get the tray
			if y >= BOUNDS['sample_rack']['y_min'] and y <= 170:
				self.tray_sv.set('A')
			elif y >= 178 and y <= 259:
				self.tray_sv.set('B')
			elif y >= 264 and y <= 348:
				self.tray_sv.set('C')
			elif y >= 352 and y <= 435:
				self.tray_sv.set('D')
		elif x >= BOUNDS['aux_heater']['x_min'] and x <= BOUNDS['aux_heater']['x_max'] and y >= BOUNDS['aux_heater']['y_min'] and y <= BOUNDS['aux_heater']['y_max']:
			self.consumable_sv.set("Aux Heater")
		elif x >= BOUNDS['heater_shaker']['x_min'] and x <= BOUNDS['heater_shaker']['x_max'] and y >= BOUNDS['heater_shaker']['y_min'] and y <= BOUNDS['heater_shaker']['y_max']:
			self.consumable_sv.set("Heater/Shaker")
			self.tray_sv.set('')
			# Get the column
			if x >= BOUNDS['aux_heater']['x_min'] and x <= 148:
				self.column_sv.set('1')
			elif x >= 149 and x <= 180:
				self.column_sv.set('2')
			elif x >= 181 and x <= 210:
				self.column_sv.set('3')
			elif x >= 211 and x <= BOUNDS['aux_heater']['x_max']:
				self.column_sv.set('4')
		elif x >= BOUNDS['mag_separator']['x_min'] and x <= BOUNDS['mag_separator']['x_max'] and y >= BOUNDS['mag_separator']['y_min'] and y <= BOUNDS['mag_separator']['y_max']:
			self.consumable_sv.set("Mag Separator")
			self.tray_sv.set('')
			# Set the column
			if x >= BOUNDS['mag_separator']['x_min'] and x <= 127:
				self.column_sv.set('1')
			elif x >= 128 and x <= 137:
				self.column_sv.set('2')
			elif x >= 138 and x <= 147:
				self.column_sv.set('3')
			elif x >= 148 and x <= 156:
				self.column_sv.set('4')
			elif x >= 157 and x <= 167:
				self.column_sv.set('5')
			elif x >= 168 and x <= 177:
				self.column_sv.set('6')
			elif x >= 178 and x <= 187:
				self.column_sv.set('7')
			elif x >= 188 and x <= 197:
				self.column_sv.set('8')
			elif x >= 198 and x <= 207:
				self.column_sv.set('9')
			elif x >= 208 and x <= 217:
				self.column_sv.set('10')
			elif x >= 218 and x <= 228:
				self.column_sv.set('11')
			elif x >= 229 and x <= BOUNDS['mag_separator']['x_max']:
				self.column_sv.set('12')
		elif x >= BOUNDS['chiller']['x_min'] and x <= BOUNDS['chiller']['x_max'] and y >= BOUNDS['chiller']['y_min'] and y <= BOUNDS['chiller']['y_max']:
			self.consumable_sv.set("Chiller")
		elif x >= BOUNDS['pre_amp_thermocycler']['x_min'] and x <= BOUNDS['pre_amp_thermocycler']['x_max'] and y >= BOUNDS['pre_amp_thermocycler']['y_min'] and y <= BOUNDS['pre_amp_thermocycler']['y_max']:
			self.consumable_sv.set("Pre-Amp Thermocycler")
			self.tray_sv.set('')
			# Determine the column
			if x >= BOUNDS['pre_amp_thermocycler']['x_min'] and x <= 51:
				self.column_sv.set('1')
			elif x >= 52 and x <= 61:
				self.column_sv.set('2')
			elif x >= 62 and x <= 71:
				self.column_sv.set('3')
			elif x >= 72 and x <= 81:
				self.column_sv.set('4')
			elif x >= 82 and x <= 91:
				self.column_sv.set('5')
			elif x >= 92 and x <= 101:
				self.column_sv.set('6')
			elif x >= 102 and x <= 113:
				self.column_sv.set('7')
			elif x >= 114 and x <= 123:
				self.column_sv.set('8')
			elif x >= 124 and x <= 133:
				self.column_sv.set('9')
			elif x >= 134 and x <= 143:
				self.column_sv.set('10')
			elif x >= 144 and x <= 154:
				self.column_sv.set('11')
			elif x >= 155 and x <= BOUNDS['pre_amp_thermocycler']['x_max']:
				self.column_sv.set('12')
		elif x >= BOUNDS['lid_tray']['x_min'] and x <= BOUNDS['lid_tray']['x_max'] and y >= BOUNDS['lid_tray']['y_min'] and y <= BOUNDS['lid_tray']['y_max']:
			self.consumable_sv.set("Lid Tray")
		elif x >= BOUNDS['tip_transfer_tray']['x_min'] and x <= BOUNDS['tip_transfer_tray']['x_max'] and y >= BOUNDS['tip_transfer_tray']['y_min'] and y <= BOUNDS['tip_transfer_tray']['y_max']:
			self.consumable_sv.set("Tip Transfer Tray")
			self.tray_sv.set('')
			# Set the column
			if x >= 11 and x <= 25:
				self.column_sv.set('1')
			elif x >= 26 and x <= 35:
				self.column_sv.set('2')
			elif x >= 36 and x <= 47:
				self.column_sv.set('3')
			elif x >= 48 and x <= 55:
				self.column_sv.set('4')
			elif x >= 56 and x <= 65:
				self.column_sv.set('5')
			elif x >= 66 and x <= 74:
				self.column_sv.set('6')
			elif x >= 75 and x <= 82:
				self.column_sv.set('7')
			elif x >= 83 and x <= 92:
				self.column_sv.set('8')
			elif x >= 93 and x <= 105:
				self.column_sv.set('9')
		elif x >= BOUNDS['asay_strip']['x_min'] and x <= BOUNDS['asay_strip']['x_max'] and y >= BOUNDS['asay_strip']['y_min'] and y <= BOUNDS['asay_strip']['y_max']:
			self.consumable_sv.set("Assay Strip")

	def bind_button_print(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_print.bind('<Button-1>', callback)
		except:
			pass


	def bind_button_home_z(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_home_z.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_home_y(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_home_y.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_home_x(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_home_x.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_home(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_home.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_move(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_move.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_update(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_update.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_drip_plate(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_drip_plate.bind('<Button-1>', callback)
		except:
			pass
