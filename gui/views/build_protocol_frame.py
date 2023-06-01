from PIL import Image
from typing import Any, Callable
from tkinter import StringVar, IntVar
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk

# Import the BuildProtocolModel
from gui.models.model import Model
from gui.models.build_protocol_model import BuildProtocolModel

# Constants
FONT = "Segoe UI"
IMAGE_CHECK_WIDTH = 20
IMAGE_CHECK_HEIGHT = 20
BUTTON_ADD_COLOR = '#10adfe'
LABEL_TIPS_POSX = 5
LABEL_TIPS_POSY = 40
LABEL_TIPS_TRAY_POSX = 185
LABEL_TIPS_TRAY_POSY = 10
OPTIONMENU_TIPS_TRAY_POSX = 75
OPTIONMENU_TIPS_TRAY_POSY = 40
OPTIONMENU_TIPS_TRAY_WIDTH = 250
LABEL_TIPS_COLUMN_POSX = 340
LABEL_TIPS_COLUMN_POSY = 10
OPTIONMENU_TIPS_COLUMN_POSX = 330
OPTIONMENU_TIPS_COLUMN_POSY = 40
OPTIONMENU_TIPS_COLUMN_WIDTH = 65
LABEL_TIPS_ACTION_POSX = 452
LABEL_TIPS_ACTION_POSY = 10
OPTIONMENU_TIPS_ACTION_POSX = 400
OPTIONMENU_TIPS_ACTION_POSY = 40
OPTIONMENU_TIPS_ACTION_WIDTH = 145
LABEL_TIPS_ADD_POSX = 557
LABEL_TIPS_ADD_POSY = 10
BUTTON_TIPS_ADD_POSX = 550
BUTTON_TIPS_ADD_POSY = 40
BUTTON_TIPS_ADD_WIDTH = 40
LABEL_MOTION_POSX = 5 
LABEL_MOTION_POSY = 100
LABEL_MOTION_CONSUMABLE_POSX = 98
LABEL_MOTION_CONSUMABLE_POSY = 70
OPTIONMENU_MOTION_CONSUMABLE_POSX = 75
OPTIONMENU_MOTION_CONSUMABLE_POSY = 100
OPTIONMENU_MOTION_CONSUMABLE_WIDTH = 135 #235
LABEL_MOTION_TRAY_POSX = 220
LABEL_MOTION_TRAY_POSY = 70
OPTIONMENU_MOTION_TRAY_POSX = 215
OPTIONMENU_MOTION_TRAY_POSY = 100
OPTIONMENU_MOTION_TRAY_WIDTH = 50
LABEL_MOTION_COLUMN_POSX = 270
LABEL_MOTION_COLUMN_POSY = 70
OPTIONMENU_MOTION_COLUMN_POSX = 270
OPTIONMENU_MOTION_COLUMN_POSY = 100
OPTIONMENU_MOTION_COLUMN_WIDTH = 55
LABEL_MOTION_TIP_POSX = 340
LABEL_MOTION_TIP_POSY = 70
OPTIONMENU_MOTION_TIP_POSX = 330
OPTIONMENU_MOTION_TIP_POSY = 100
OPTIONMENU_MOTION_TIP_WIDTH = 70
LABEL_MOTION_DRIP_PLATE_POSX = 517
LABEL_MOTION_DRIP_PLATE_POSY = 70
CHECKBOX_MOTION_DRIP_PLATE_POSX = 520
CHECKBOX_MOTION_DRIP_PLATE_POSY = 102
LABEL_MOTION_DXDYDZ_POSX = 425
LABEL_MOTION_DXDYDZ_POSY = 70
ENTRY_MOTION_DXDYDZ_POSX = 405
ENTRY_MOTION_DXDYDZ_POSY = 100
ENTRY_MOTION_DXDYDZ_WIDTH = 110
LABEL_MOTION_ADD_POSX = 557
LABEL_MOTION_ADD_POSY = 70
BUTTON_MOTION_ADD_POSX = 550
BUTTON_MOTION_ADD_POSY = 100
BUTTON_MOTION_ADD_WIDTH = 40
LABEL_PIPETTOR_POSX = 5
LABEL_PIPETTOR_POSY = 160
LABEL_PIPETTOR_VOLUME_POSX = 87
LABEL_PIPETTOR_VOLUME_POSY = 130
ENTRY_PIPETTOR_VOLUME_POSX = 80
ENTRY_PIPETTOR_VOLUME_POSY = 160
ENTRY_PIPETTOR_VOLUME_WIDTH = 95
LABEL_PIPETTOR_TIP_POSX = 195
LABEL_PIPETTOR_TIP_POSY = 130
OPTIONMENU_PIPETTOR_TIP_POSX = 180
OPTIONMENU_PIPETTOR_TIP_POSY = 160
OPTIONMENU_PIPETTOR_TIP_WIDTH = 70
LABEL_PIPETTOR_ACTION_POSX = 285
LABEL_PIPETTOR_ACTION_POSY = 130
OPTIONMENU_PIPETTOR_ACTION_POSX = 255
OPTIONMENU_PIPETTOR_ACTION_POSY = 160
OPTIONMENU_PIPETTOR_ACTION_WIDTH = 100
LABEL_PIPETTOR_PRESSURE_POSX = 455
LABEL_PIPETTOR_PRESSURE_POSY = 130
OPTIONMENU_PIPETTOR_PRESSURE_POSX = 420
OPTIONMENU_PIPETTOR_PRESSURE_POSY = 160
OPTIONMENU_PIPETTOR_PRESSURE_WIDTH = 125
LABEL_PIPETTOR_COUNT_POSX = 370
LABEL_PIPETTOR_COUNT_POSY = 130
OPTIONMENU_PIPETTOR_COUNT_POSX = 360
OPTIONMENU_PIPETTOR_COUNT_POSY = 160
OPTIONMENU_PIPETTOR_COUNT_WIDTH = 55
LABEL_PIPETTOR_ADD_POSX = 557
LABEL_PIPETTOR_ADD_POSY = 130
BUTTON_PIPETTOR_ADD_POSX = 550
BUTTON_PIPETTOR_ADD_POSY = 160
BUTTON_PIPETTOR_ADD_WIDTH = 40
BUTTON_PIPETTOR_ADD_HEIGHT = 25
LABEL_OTHER_POSX = 5
LABEL_OTHER_POSY = 220
LABEL_OTHER_OPTION_POSX = 210
LABEL_OTHER_OPTION_POSY = 190
OPTIONMENU_OTHER_OPTION_POSX = 80
OPTIONMENU_OTHER_OPTION_POSY = 220
OPTIONMENU_OTHER_OPTION_WIDTH = 300
OPTIONMENU_OTHER_OPTION_HEIGHT = 30
LABEL_OTHER_PARAMETER_POSX = 430
LABEL_OTHER_PARAMETER_POSY = 190
ENTRY_OTHER_PARAMETER_POSX = 385
ENTRY_OTHER_PARAMETER_POSY = 220
ENTRY_OTHER_PARAMETER_WIDTH = 160
LABEL_OTHER_ADD_POSX = 557
LABEL_OTHER_ADD_POSY = 190
BUTTON_OTHER_ADD_POSX = 550
BUTTON_OTHER_ADD_POSY = 220
BUTTON_OTHER_ADD_WIDTH = 40
LABEL_TIME_POSX = 5
LABEL_TIME_POSY = 280
LABEL_TIME_DELAY_POSX = 102
LABEL_TIME_DELAY_POSY = 250
ENTRY_TIME_DELAY_POSX = 80
ENTRY_TIME_DELAY_POSY = 280
ENTRY_TIME_DELAY_WIDTH = 80
LABEL_TIME_UNITS_POSX = 215
LABEL_TIME_UNITS_POSY = 250
OPTIONMENU_TIME_UNITS_POSX = 165
OPTIONMENU_TIME_UNITS_POSY = 280
OPTIONMENU_TIME_UNITS_WIDTH = 120
LABEL_TIME_ADD_POSX = 297
LABEL_TIME_ADD_POSY = 250
BUTTON_TIME_ADD_POSX = 290
BUTTON_TIME_ADD_POSY = 280
BUTTON_TIME_ADD_WIDTH = 40
TREEVIEW_POSX = 5
TREEVIEW_POSY = 320
TREEVIEW_COLUMN_WIDTH = 440
TREEVIEW_WIDTH = 440
TREEVIEW_HEIGHT = 160
SCROLLBAR_POSX = 5
SCROLLBAR_POSY = 480
SCROLLBAR_WIDTH = 440
LABEL_ESTIMATE_TIME_POSX = 380
LABEL_ESTIMATE_TIME_POSY = 215
LABEL_ACTION_PROGRESS_POSX = 380
LABEL_ACTION_PROGRESS_POSY = 250
PROGRESSBAR_POSX = 350
PROGRESSBAR_POSY = 280
PROGRESSBAR_WIDTH = 235
PROGRESSBAR_HEIGHT = 25
BUTTON_START_POSX = 460
BUTTON_START_POSY = 320
BUTTON_START_WIDTH = 130
BUTTON_START_COLOR = '#10adfe'
BUTTON_LOAD_POSX = 460
BUTTON_LOAD_POSY = 350
BUTTON_LOAD_WIDTH = 130
BUTTON_SAVE_POSX = 460
BUTTON_SAVE_POSY = 380
BUTTON_SAVE_WIDTH = 130
BUTTON_EXPAND_POSX = 460
BUTTON_EXPAND_POSY = 410
BUTTON_EXPAND_WIDTH = 130
BUTTON_DELETE_POSX = 460
BUTTON_DELETE_POSY = 440
BUTTON_DELETE_WIDTH = 130
BUTTON_DELETE_COLOR = '#fc0303'
MENU_ICON_IMAGE_SIZE = (25,25)

# Constants Deck Plate 
NO_TRAY_CONSUMABLES = ["Pre-Amp Thermocycler", "Heater/Shaker", "Mag Separator", "Chiller"]
NO_COLUMN_CONSUMABLES = ["Aux Heater", "Sample Rack", "Quant Strip"]
TWELVE_COLUMN_CONSUMABLES = ["Pre-Amp Thermocycler", "Mag Separator", "Chiller", "Reagent Cartridge"]
EIGHT_COLUMN_CONSUMABLES = ["Tip Transfer Tray", "Assay Strip", "Tip Tray"]
FOUR_COLUMN_CONSUMABLES = ["Heater/Shaker"]
THREE_COLUMN_CONSUMABLES = ["DG8", "Tray"]
TWO_COLUMN_CONSUMABLES = ["Assay Strip"]
SPECIAL_CONSUMABLES = ["DG8", "Tray", "Tip Transfer Tray"]

# Constant Other Option Values
CONSUMABLES_OPTION_VALUES = [
	"Quant Strip",
	"Tip Box",
	"Reagent Cartridge",
	"Sample Rack",
	"Aux Heater",
	"Heater/Shaker",
	"Mag Separator",
	"Chiller",
	"Pre-Amp Thermocycler",
	"Assay Strip",
	"DG8",
	"Tray",
	"Tip Transfer Tray",
	"",
]
DG8_TRAY_OPTION_VALUES = ['1000', '0100', '0010', '0000',]
DG8_TRAY_OPTION_VALUES = ['A', 'B', 'C', 'D',]
DG8_COLUMN_OPTION_VALUES = ['1', '2', '3',]
CHIP_TRAY_OPTION_VALUES = ['A', 'B', 'C', 'D',]
CHIP_COLUMN_OPTION_VALUES = ['NIPT','FF','Quant',]
OTHER_OPTIONS = (
	('gui/images/home.png', 'Home', "Home pipettor", "Home imager", "Home pipettor fast", "Home pipettor along Z", "Home pipettor along Y", "Home pipettor along X", "Home the pipettor drip plate"),
	('gui/images/relative.png', "Move relative", "Move relative left", "Move relative right", "Move relative up", "Move relative down", "Move relative forwards", "Move relative backwards"),
	('gui/images/droplets.png', 'Droplets', "Generate Standard Droplets", "Generate Pico Droplets", "Generate Demo Droplets"),
	('gui/images/protocols.png', 'Protocols', 'Extraction', "Transfer Plasma", 'Binding', 'Pooling', 'Pre-Dispense', "Low-Stringent Wash", 'Pre-Elution', 'Elution'),
	('gui/images/magnet.png', 'Magnet', "Engage magnet", "Disengage magnet"),
	('gui/images/heater_shaker.png', 'Heater/Shaker', "Change the Heater/Shaker temperature", "Shake on", "Shake off"),
	('gui/images/thermocycle.png', 'Thermocycling', "Relay A - On", "Relay A - Off", "Relay B - On", "Relay B - Off", "Relay C - On", "Relay C - Off", "Relay D - On", "Relay D - Off", "Thermocycle Hold", "Thermocycle A: Change Temperature", "Thermocycle B: Change Temperature", "Thermocycle C: Change Temperature", "Thermocycle D: Change Temperature", "Thermocycle: Cycle", "Thermocycle Protocol", "Thermocycle Pre-Amp"),
	('gui/images/tray.png', 'Trays', "Open Tray AB", "Open Tray CD", "Close Tray AB", "Close Tray CD"),
	('gui/images/clamp.png', 'Clamps', "Lower Thermocycler A", "Lower Thermocycler B", "Lower Thermocycler C", "Lower Thermocycler D", "Raise Thermocycler A", "Raise Thermocycler B", "Raise Thermocycler C", "Raise Thermocycler D"),
	('gui/images/imager.png', 'Imager', "Home imager", "Move imager", "Image all channels", "Image", "Scan A", "Scan B", "Scan C", "Scan D", "Light Show"),
	('gui/images/other.png', 'Other', "Drip", "LLD", "Add a comment", "Pause for user input", "Load Tip Tray A", "Load Tip Tray B", "Move Lid A", "Move Lid B", "Move Lid C", "Move Lid D", "Move Chip A", "Move Chip B", "Move Chip C", "Move Chip D", "Move Engaged Chip A", "Move Engaged Chip B", "Move Engaged Chip C", "Move Engaged Chip D", "Suction cups on", "Suction cups off", "Extend drip plate"),
)

COUNT_OPTION_VALUES = [f'{i}' for i in range(1,11)]

# Image Paths
IMAGE_PATHS = {
	'check': 'gui/images/check.png'
}

class BuildProtocolFrame(ctk.CTkFrame):
	"""
	BuildProtocolFrame for creating the Build Protocol UI View
	"""
	def __init__(self, master: ctk.CTk, model: Model, width: int, height: int, posx: int, posy: int) -> None:
		"""Constructs the BuildProtocolFrame
	
		Parameters
		----------
		master : ctk.CTk
			The parent widget for this frame
		width : int
			The width of this widget
		height : int
			The height of this widget
		posx : int
			The x position relative to the root origin
		posy : int
			The y position relative to the root origin
		"""
		#self.model = BuildProtocolModel()
		self.master_model = model
		self.model = self.master_model.get_build_protocol_model()
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
		self.menu_images = {}
		self.create_ui()

	def create_ui(self) -> None:
		"""Create the UI for the BuildProtocolFrame
		"""
		# Create the photoimage for the check mark
		self.photoimage_check = ctk.CTkImage(
			dark_image=Image.open(IMAGE_PATHS['check']),
			size=(IMAGE_CHECK_WIDTH, IMAGE_CHECK_HEIGHT),
		)
		# Create the Tips Section
		self.create_tips_ui()
		# Create the Motion Section
		self.create_motion_ui()
		# Create the Pipettor Section
		self.create_pipettor_ui()
		# Create the Time Section
		self.create_time_ui()
		# Create the Other Section
		self.create_other_ui()
		# Create the Protocol Action Treeview
		self.create_treeview_ui()
		# Create the Protocol Progress Bar
		self.create_progress_ui()
		# Create the Start Button
		self.button_start = ctk.CTkButton(
			master=self, 
			text='Start', 
			corner_radius=2, 
			font=(FONT,-16),
			fg_color=BUTTON_START_COLOR,
			hover_color='#003399',
			width=BUTTON_START_WIDTH
		)
		# Create the Load Button
		self.button_load = ctk.CTkButton(
			master=self, 
			text='Load', 
			corner_radius=2, 
			font=(FONT,-16),
			width=BUTTON_LOAD_WIDTH
		)
		# Create the Save Button
		self.button_save = ctk.CTkButton(
			master=self, 
			text='Save', 
			corner_radius=2, 
			font=(FONT,-16),
			width=BUTTON_SAVE_WIDTH
		)
		# Create the Expand Button
		self.button_expand = ctk.CTkButton(
			master=self, 
			text='Expand', 
			corner_radius=2, 
			font=(FONT,-16),
			width=BUTTON_EXPAND_WIDTH
		)
		# Create the Delete Button
		self.button_delete = ctk.CTkButton(
			master=self, 
			text='Delete', 
			corner_radius=2, 
			font=(FONT,-16),
			fg_color=BUTTON_DELETE_COLOR,
			hover_color='#b10202',
			width=BUTTON_DELETE_WIDTH
		)

	def place_ui(self) -> None:
		"""Place the UI for the Build Protocol Frame
		"""
		# Place the build protocol frame
		self.place(x=self.posx, y=self.posy)
		# Place the tips section
		self.place_tips_ui()
		# Place the motion section
		self.place_motion_ui()
		# Place the pipettor section
		self.place_pipettor_ui()
		# Place the time section
		self.place_time_ui()
		# Place the other section
		self.place_other_ui()
		# Place the progress bar
		self.place_progress_ui()
		# Place the start, load, save, delete buttons
		self.button_start.place(x=BUTTON_START_POSX, y=BUTTON_START_POSY)
		self.button_load.place(x=BUTTON_LOAD_POSX, y=BUTTON_LOAD_POSY)
		self.button_save.place(x=BUTTON_SAVE_POSX, y=BUTTON_SAVE_POSY)
		self.button_expand.place(x=BUTTON_EXPAND_POSX, y=BUTTON_EXPAND_POSY)
		self.button_delete.place(x=BUTTON_DELETE_POSX, y=BUTTON_DELETE_POSY)
		# Place the protocol action treeview 
		self.place_treeview_ui()
		

	def create_tips_ui(self) -> None:
		"""Create the UI for the Tips portion of the frame
		"""
		# Create the tips label
		self.label_tips = ctk.CTkLabel(master=self, text='Tips', font=(FONT, -16))
		# Create the tray label and optionmenu
		self.label_tips_tray = ctk.CTkLabel(master=self, text='Tray', font=(FONT, -16))
		self.tips_tray_sv = StringVar()
		self.tips_tray_sv.set('')
		self.tips_tray_sv.trace('w', self.callback_tips_tray)
		self.optionmenu_tips_tray = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tips_tray_sv,
			values=('A', 'B', 'C', 'D', "Tip Transfer Tray", ''),
			font=(FONT, -14),
			width=OPTIONMENU_TIPS_TRAY_WIDTH
		)
		# Create the column label and optionmenu
		self.label_tips_column = ctk.CTkLabel(master=self, text='Column', font=(FONT, -16))
		self.tips_column_sv = StringVar()
		self.tips_column_sv.set('')
		self.tips_column_sv.trace('w', self.callback_tips_column)
		self.optionmenu_tips_column = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tips_column_sv,
			values=(''),
			font=(FONT, -14),
			width=OPTIONMENU_TIPS_COLUMN_WIDTH
		)
		# Create the action label and optionmenu
		self.label_tips_action = ctk.CTkLabel(master=self, text='Action', font=(FONT, -16))
		self.tips_action_sv = StringVar()
		self.tips_action_sv.set('Eject')
		self.optionmenu_tips_action = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tips_action_sv,
			values=('Eject',),
			font=(FONT, -14),
			width=OPTIONMENU_TIPS_ACTION_WIDTH
		)
		# Create the add label and button
		self.label_tips_add = ctk.CTkLabel(master=self, text='Add', font=(FONT, -14))
		self.button_tips_add = ctk.CTkButton(
			master=self,
			text='',
			corner_radius=2,
			#image=self.photoimage_check,
			fg_color=BUTTON_ADD_COLOR,
			hover_color='#003399',
			width=BUTTON_TIPS_ADD_WIDTH
		)

	def place_tips_ui(self) -> None:
		"""Place the UI for the Tips portion of the frame
		"""
		# Place the tips label
		self.label_tips.place(x=LABEL_TIPS_POSX, y=LABEL_TIPS_POSY)
		# Place the tray label and optionmenu
		self.label_tips_tray.place(x=LABEL_TIPS_TRAY_POSX, y=LABEL_TIPS_TRAY_POSY)
		self.optionmenu_tips_tray.place(x=OPTIONMENU_TIPS_TRAY_POSX, y=OPTIONMENU_TIPS_TRAY_POSY)
		# Place the column label and optionmenu
		self.label_tips_column.place(x=LABEL_TIPS_COLUMN_POSX, y=LABEL_TIPS_COLUMN_POSY)
		self.optionmenu_tips_column.place(x=OPTIONMENU_TIPS_COLUMN_POSX, y=OPTIONMENU_TIPS_COLUMN_POSY)
		# Place the action label and optionmenu
		self.label_tips_action.place(x=LABEL_TIPS_ACTION_POSX, y=LABEL_TIPS_ACTION_POSY)
		self.optionmenu_tips_action.place(x=OPTIONMENU_TIPS_ACTION_POSX, y=OPTIONMENU_TIPS_ACTION_POSY)
		# Place the add label and button
		self.label_tips_add.place(x=LABEL_TIPS_ADD_POSX, y=LABEL_TIPS_ADD_POSY)
		self.button_tips_add.place(x=BUTTON_TIPS_ADD_POSX, y=BUTTON_TIPS_ADD_POSY)
		try:
			print(self.button_tips_add.bind())
		except:
			pass

	def create_motion_ui(self) -> None:
		"""Deals with creating the UI for the Motion section of the Build Protocol Frame
		"""
		# Create the motion label
		self.label_motion = ctk.CTkLabel(master=self, text='Motion', font=(FONT, -16))
		# Create the consumable label and optionmenu
		self.label_motion_consumable = ctk.CTkLabel(master=self, text='Consumable', font=(FONT, -16))
		self.motion_consumable_sv = StringVar()
		self.motion_consumable_sv.set('')
		self.motion_consumable_sv.trace('w', self.callback_motion_consumable)
		self.optionmenu_motion_comsumable = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.motion_consumable_sv,
			values=CONSUMABLES_OPTION_VALUES,
			font=(FONT, -12),
			width=OPTIONMENU_MOTION_CONSUMABLE_WIDTH
		)
		# Create the tray label and optionmenu
		self.label_motion_tray = ctk.CTkLabel(master=self, text='Tray', font=(FONT, -16))
		self.motion_tray_sv = StringVar()
		self.motion_tray_sv.set('')
		self.motion_tray_sv.trace('w', self.callback_motion_tray)
		self.optionmenu_motion_tray = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.motion_tray_sv,
			values=('',),
			font=(FONT, -14),
			width=OPTIONMENU_MOTION_TRAY_WIDTH,
		)
		# Create the column label and optionmenu
		self.label_motion_column = ctk.CTkLabel(master=self, text='Column', font=(FONT, -16))
		self.motion_column_sv = StringVar()
		self.motion_column_sv.set('')
		self.optionmenu_motion_column = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.motion_column_sv,
			values=('',),
			font=(FONT, -14),
			width=OPTIONMENU_MOTION_COLUMN_WIDTH
		)
		# Create the tip label and optionmenu
		self.label_motion_tip = ctk.CTkLabel(master=self, text="Tip (uL)", font=(FONT, -16))
		self.motion_tip_sv = StringVar()
		self.motion_tip_sv.set('')
		self.optionmenu_motion_tip = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.motion_tip_sv,
			values=('',),
			font=(FONT, -14),
			width=OPTIONMENU_MOTION_TIP_WIDTH
		)
		# Create the drip plate label and checkbox
		self.label_motion_drip_plate = ctk.CTkLabel(master=self, text="Drip", font=(FONT, -16))
		self.motion_drip_plate_iv = IntVar()
		self.motion_drip_plate_iv.set(0)
		self.checkbox_motion_drip_plate = ctk.CTkCheckBox(
			master=self,
			text='',
			variable=self.motion_drip_plate_iv,
			onvalue=1,
			offvalue=0,
			corner_radius=2,
		)
		# Create the dx, dy, dz label and entry
		self.label_motion_dxdydz = ctk.CTkLabel(master=self, text='dx,dy,dz', font=(FONT, -16))
		self.motion_dxdydz_sv = StringVar()
		self.motion_dxdydz_sv.set('0,0,0')
		self.entry_motion_dxdydz = ctk.CTkEntry(
			master=self,
			corner_radius=2,
			textvariable=self.motion_dxdydz_sv,
			font=(FONT,-12),
			width=ENTRY_MOTION_DXDYDZ_WIDTH
		)
		# Create the add label and button
		self.label_motion_add = ctk.CTkLabel(master=self, text='Add', font=(FONT, -14))
		self.button_motion_add = ctk.CTkButton(
			master=self,
			corner_radius=2,
			text='',
			#image=self.photoimage_check,
			fg_color=BUTTON_ADD_COLOR,
			hover_color='#003399',
			width=BUTTON_MOTION_ADD_WIDTH
		)

	def place_motion_ui(self) -> None:
		"""Deals with placing the UI for the Motion section of the Build Protocol Frame
		"""
		# Place the motion label
		self.label_motion.place(x=LABEL_MOTION_POSX, y=LABEL_MOTION_POSY)
		# Place the consumable label and optionmenu
		self.label_motion_consumable.place(x=LABEL_MOTION_CONSUMABLE_POSX, y=LABEL_MOTION_CONSUMABLE_POSY)
		self.optionmenu_motion_comsumable.place(
			x=OPTIONMENU_MOTION_CONSUMABLE_POSX, 
			y=OPTIONMENU_MOTION_CONSUMABLE_POSY,
			width=OPTIONMENU_MOTION_CONSUMABLE_WIDTH
		)
		# Place the tray label and optionmenu
		self.label_motion_tray.place(x=LABEL_MOTION_TRAY_POSX, y=LABEL_MOTION_TRAY_POSY)
		self.optionmenu_motion_tray.place(x=OPTIONMENU_MOTION_TRAY_POSX, y=OPTIONMENU_MOTION_TRAY_POSY)
		# Place the column label and optionmenu
		self.label_motion_column.place(x=LABEL_MOTION_COLUMN_POSX, y=LABEL_MOTION_COLUMN_POSY)
		self.optionmenu_motion_column.place(
			x=OPTIONMENU_MOTION_COLUMN_POSX, 
			y=OPTIONMENU_MOTION_COLUMN_POSY,
		)
		# Place the tip label and optionmenu
		self.label_motion_tip.place(x=LABEL_MOTION_TIP_POSX, y=LABEL_MOTION_TIP_POSY)
		self.optionmenu_motion_tip.place(x=OPTIONMENU_MOTION_TIP_POSX, y=OPTIONMENU_MOTION_TIP_POSY)
		# Place the drip plate label and checkbox
		self.label_motion_drip_plate.place(x=LABEL_MOTION_DRIP_PLATE_POSX, y=LABEL_MOTION_DRIP_PLATE_POSY)
		self.checkbox_motion_drip_plate.place(
			x=CHECKBOX_MOTION_DRIP_PLATE_POSX, 
			y=CHECKBOX_MOTION_DRIP_PLATE_POSY,
		)
		# Place the dx,dy,dz label and entry
		self.label_motion_dxdydz.place(x=LABEL_MOTION_DXDYDZ_POSX, y=LABEL_MOTION_DXDYDZ_POSY)
		self.entry_motion_dxdydz.place(x=ENTRY_MOTION_DXDYDZ_POSX, y=ENTRY_MOTION_DXDYDZ_POSY)
		# Place the add label and button
		self.label_motion_add.place(x=LABEL_MOTION_ADD_POSX, y=LABEL_MOTION_ADD_POSY)
		self.button_motion_add.place(x=BUTTON_MOTION_ADD_POSX, y=BUTTON_MOTION_ADD_POSY)

	def create_pipettor_ui(self) -> None:
		"""Creates the UI for the pipettor portion of the BuildProtocol view
		"""
		# Create the pipettor label
		self.label_pipettor = ctk.CTkLabel(master=self, text='Pipettor', font=(FONT, -16))
		# Create the volume label and entry
		self.label_pipettor_volume = ctk.CTkLabel(master=self, text='Volume (uL)', font=(FONT, -14))
		self.pipettor_volume_sv = StringVar()
		self.pipettor_volume_sv.set('')
		self.entry_pipettor_volume = ctk.CTkEntry(
			master=self,
			corner_radius=2,
			textvariable=self.pipettor_volume_sv, 
			width=ENTRY_PIPETTOR_VOLUME_WIDTH
		)
		# Create the tip label and optionmenu
		self.label_pipettor_tip = ctk.CTkLabel(master=self, text="Tip (uL)", font=(FONT, -14))
		self.pipettor_tip_sv = StringVar()
		self.pipettor_tip_sv.set('')
		self.optionmenu_pipettor_tip = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.pipettor_tip_sv,
			values=('1000', '50', '200',),
			width=OPTIONMENU_PIPETTOR_TIP_WIDTH
		)
		# Create the action label and optionmenu
		self.label_pipettor_action = ctk.CTkLabel(master=self, text='Action', font=(FONT, -14))
		self.pipettor_action_sv = StringVar()
		self.pipettor_action_sv.set('Aspirate')
		self.optionmenu_pipettor_action = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.pipettor_action_sv,
			values=('Aspirate', 'Dispense', 'Mix'),
			width=OPTIONMENU_PIPETTOR_ACTION_WIDTH
		)
		# Create the count label and entry
		self.label_pipettor_count = ctk.CTkLabel(master=self, text='Count', font=(FONT,-14))
		self.pipettor_count_sv = StringVar()
		self.pipettor_count_sv.set('1')
		self.optionmenu_pipettor_count = ctk.CTkOptionMenu(
			master=self,
			variable=self.pipettor_count_sv,
			values=COUNT_OPTION_VALUES,
			font=(FONT,-14),
			corner_radius=2,
			width=OPTIONMENU_PIPETTOR_COUNT_WIDTH
		)
		# Create the pressure label and optionmenu
		self.label_pipettor_pressure = ctk.CTkLabel(master=self, text='Pressure', font=(FONT, -14))
		self.pipettor_pressure_sv = StringVar()
		self.pipettor_pressure_sv.set('Low')
		self.optionmenu_pipettor_pressure = ctk.CTkOptionMenu(
                        master=self,
			corner_radius=2,
			variable=self.pipettor_pressure_sv,
			values=('Highest', 'High', 'Low', 'Lowest'),
			width=OPTIONMENU_PIPETTOR_PRESSURE_WIDTH
		)
		# Create the add label and button
		self.label_pipettor_add = ctk.CTkLabel(master=self, text='Add', font=(FONT, -14))
		self.button_pipettor_add = ctk.CTkButton(
			master=self,
			corner_radius=2,
			text='',
			#image=self.photoimage_check,
			fg_color=BUTTON_ADD_COLOR,
			hover_color='#003399',
			width=BUTTON_PIPETTOR_ADD_WIDTH
		)

	def place_pipettor_ui(self) -> None:
		"""Places the UI for the pipettor portion of the BuildProtocol view
		"""
		# Place the pipettor label
		self.label_pipettor.place(x=LABEL_PIPETTOR_POSX, y=LABEL_PIPETTOR_POSY)
		# Place the volume label and entry
		self.label_pipettor_volume.place(x=LABEL_PIPETTOR_VOLUME_POSX, y=LABEL_PIPETTOR_VOLUME_POSY)
		self.entry_pipettor_volume.place(x=ENTRY_PIPETTOR_VOLUME_POSX, y=ENTRY_PIPETTOR_VOLUME_POSY)
		# Place the tip label and optionmenu
		self.label_pipettor_tip.place(x=LABEL_PIPETTOR_TIP_POSX, y=LABEL_PIPETTOR_TIP_POSY)
		self.optionmenu_pipettor_tip.place(x=OPTIONMENU_PIPETTOR_TIP_POSX, y=OPTIONMENU_PIPETTOR_TIP_POSY)
		# Place the action label and optionmenu
		self.label_pipettor_action.place(x=LABEL_PIPETTOR_ACTION_POSX, y=LABEL_PIPETTOR_ACTION_POSY)
		self.optionmenu_pipettor_action.place(x=OPTIONMENU_PIPETTOR_ACTION_POSX, y=OPTIONMENU_PIPETTOR_ACTION_POSY)
		# Place the count label and entry
		self.label_pipettor_count.place(x=LABEL_PIPETTOR_COUNT_POSX, y=LABEL_PIPETTOR_COUNT_POSY)
		self.optionmenu_pipettor_count.place(x=OPTIONMENU_PIPETTOR_COUNT_POSX, y=OPTIONMENU_PIPETTOR_COUNT_POSY)
		# Place the pressure label and optionmenu
		self.label_pipettor_pressure.place(x=LABEL_PIPETTOR_PRESSURE_POSX, y=LABEL_PIPETTOR_PRESSURE_POSY)
		self.optionmenu_pipettor_pressure.place(x=OPTIONMENU_PIPETTOR_PRESSURE_POSX, y=OPTIONMENU_PIPETTOR_PRESSURE_POSY)
		# Place the add label and button
		self.label_pipettor_add.place(x=LABEL_PIPETTOR_ADD_POSX, y=LABEL_PIPETTOR_ADD_POSY)
		self.button_pipettor_add.place(x=BUTTON_PIPETTOR_ADD_POSX, y=BUTTON_PIPETTOR_ADD_POSY)

	def create_time_ui(self) -> None:
		"""Creates the UI for the time portion of the Build Protocol Frame view
		"""
		# Create the time label
		self.label_time = ctk.CTkLabel(master=self, text='Time', font=(FONT, -16))
		# Create the delay label and entry
		self.label_time_delay = ctk.CTkLabel(master=self, text='Delay', font=(FONT, -14))
		self.time_delay_sv = StringVar()
		self.time_delay_sv.set('')
		self.entry_time_delay = ctk.CTkEntry(
			master=self,
			corner_radius=2,
			textvariable=self.time_delay_sv, 
			width=ENTRY_TIME_DELAY_WIDTH
		)
		# Create the units label and optionmenu
		self.label_time_units = ctk.CTkLabel(master=self, text='Units', font=(FONT, -14))
		self.time_units_sv = StringVar()
		self.time_units_sv.set('seconds')
		self.optionmenu_time_units = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.time_units_sv,
			values=('seconds', 'minutes'),
			width=OPTIONMENU_TIME_UNITS_WIDTH
		)
		# Create the add label and button
		self.label_time_add = ctk.CTkLabel(master=self, text='Add', font=(FONT, -14))
		self.button_time_add = ctk.CTkButton(
			master=self,
			text='',
			corner_radius=5,
			fg_color=BUTTON_ADD_COLOR,
			hover_color='#003399',
			width=BUTTON_TIME_ADD_WIDTH
		)

	def place_time_ui(self) -> None:
		"""Places the UI for the time portion of the Build Protocol Frame view
		"""
		# Place the time label
		self.label_time.place(x=LABEL_TIME_POSX, y=LABEL_TIME_POSY)
		# Place the delay label and entry
		self.label_time_delay.place(x=LABEL_TIME_DELAY_POSX, y=LABEL_TIME_DELAY_POSY)
		self.entry_time_delay.place(x=ENTRY_TIME_DELAY_POSX, y=ENTRY_TIME_DELAY_POSY)
		# Place the units label and optionmenu
		self.label_time_units.place(x=LABEL_TIME_UNITS_POSX, y=LABEL_TIME_UNITS_POSY)
		self.optionmenu_time_units.place(x=OPTIONMENU_TIME_UNITS_POSX, y=OPTIONMENU_TIME_UNITS_POSY)
		# Place the add label and button
		self.label_time_add.place(x=LABEL_TIME_ADD_POSX, y=LABEL_TIME_ADD_POSY)
		self.button_time_add.place(x=BUTTON_TIME_ADD_POSX, y=BUTTON_TIME_ADD_POSY)

	def create_other_ui(self) -> None:
		"""Create the UI for the other portion of the Build Protocol Frame view
		"""
		# Create the other label
		self.label_other = ctk.CTkLabel(master=self, text='Other', font=(FONT, -16))
		# Create the option label and optionmenu
		self.label_other_option = ctk.CTkLabel(master=self, text='Option', font=(FONT, -16))
		self.other_option_sv = StringVar()
		self.other_option_sv.set("Home pipettor")
		self.other_option_sv.trace('w', self.callback_other_option)
		self.optionmenu_other_option = tk.Menubutton(
			self,
			textvariable=self.other_option_sv,
			font=(FONT,-16),
			indicatoron=False,
			borderwidth=1,
			relief='raised',
			direction='below',
			bg='#2fa572',
			activebackground='#106a43',
			fg='white',
			activeforeground='white',
		)
		self.menu_other_option = tk.Menu(
			self.optionmenu_other_option,
			tearoff=False,
			bg='#2b2b2b', 
			fg='white',
			activeforeground='white',
			font=(FONT,-16),
		)
		self.optionmenu_other_option.config(menu=self.menu_other_option)
		for options in OTHER_OPTIONS:
			image = Image.open(options[0])
			resized_image = image.resize(MENU_ICON_IMAGE_SIZE)
			self.menu_images[options[0]] = ImageTk.PhotoImage(resized_image)
			#menu_image = tk.PhotoImage(file=options[0])
			menu = tk.Menu(self.menu_other_option, tearoff=False, bg='#2b2b2b', fg='white', activeforeground='white', borderwidth=1, font=(FONT,-16))
			self.menu_other_option.add_cascade(
				label=options[1],
				menu=menu,
				image=self.menu_images[options[0]],
				compound=tk.LEFT,
			)
			for option in options[2:]:
				menu.add_radiobutton(
					value=option,
					label=option,
					variable=self.other_option_sv,
					font=(FONT,-16),
				)
		# Create the parameters label and entry
		self.label_other_parameter = ctk.CTkLabel(master=self, text='Parameter', font=(FONT, -16))
		self.other_parameter_sv = StringVar()
		self.other_parameter_sv.set('')
		self.entry_other_parameter = ctk.CTkEntry(
			master=self,
			textvariable=self.other_parameter_sv,
			font=(FONT,-12),
			corner_radius=2,
			state='disabled',
			width=ENTRY_OTHER_PARAMETER_WIDTH,
		)
		self.entry_other_parameter.bind('<Button-1>', self.other_parameter_onclick)
		self.entry_other_parameter.bind('<Key>', self.other_parameter_keys)
		# Create the add label and button
		self.label_other_add = ctk.CTkLabel(master=self, text='Add', font=(FONT, -14))
		self.button_other_add = ctk.CTkButton(
			master=self,
			corner_radius=5,
			text='',
			fg_color=BUTTON_ADD_COLOR,
			hover_color='#003399',
			width=BUTTON_OTHER_ADD_WIDTH
		)

	def place_other_ui(self) -> None:
		"""Place the UI for the other portion of the Build Protocol Frame view
		"""
		# Place the other label
		self.label_other.place(x=LABEL_OTHER_POSX, y=LABEL_OTHER_POSY)
		# Place the option label and optionmenu
		self.label_other_option.place(x=LABEL_OTHER_OPTION_POSX, y=LABEL_OTHER_OPTION_POSY)
		self.optionmenu_other_option.place(
			x=OPTIONMENU_OTHER_OPTION_POSX, 
			y=OPTIONMENU_OTHER_OPTION_POSY,
			width=OPTIONMENU_OTHER_OPTION_WIDTH,
			height=OPTIONMENU_OTHER_OPTION_HEIGHT,
		)
		# Place the parameter label and entry
		self.label_other_parameter.place(x=LABEL_OTHER_PARAMETER_POSX, y=LABEL_OTHER_PARAMETER_POSY)
		self.entry_other_parameter.place(x=ENTRY_OTHER_PARAMETER_POSX, y=ENTRY_OTHER_PARAMETER_POSY)
		self.entry_other_parameter.bind('<FocusIn>', self.other_parameter_focus_in)
		# Place the add label and button
		self.label_other_add.place(x=LABEL_OTHER_ADD_POSX, y=LABEL_OTHER_ADD_POSY)
		self.button_other_add.place(x=BUTTON_OTHER_ADD_POSX, y=BUTTON_OTHER_ADD_POSY)

	def create_progress_ui(self) -> None:
		"""Creates the UI for the progress portion
		"""
		# Create the estimate time label
		#self.label_estimate_time = ctk.CTkLabel(master=self, text="Estimate Time: 00:00:00", font=(FONT,-16))
		# Create the action progress label and progressbar
		self.label_action_progress = ctk.CTkLabel(master=self, text="Action Progress: 0 of 0", font=(FONT, -16))
		self.progressbar = ctk.CTkProgressBar(
			master=self,
			orientation='horizontal',
			mode='determinate',
			width=PROGRESSBAR_WIDTH,
			height=PROGRESSBAR_HEIGHT,
			progress_color='green',
			corner_radius=0
		)
		self.progressbar.set(0)

	def place_progress_ui(self) -> None:
		"""Places the UI for the progress portion
		"""
		# Place the estimate time label
		#self.label_estimate_time.place(x=LABEL_ESTIMATE_TIME_POSX, y=LABEL_ESTIMATE_TIME_POSY)
		# Place the action progress label and progressbar
		self.label_action_progress.place(x=LABEL_ACTION_PROGRESS_POSX, y=LABEL_ACTION_PROGRESS_POSY)
		self.progressbar.place(x=PROGRESSBAR_POSX, y=PROGRESSBAR_POSY)

	def create_treeview_ui(self) -> None:
		"""Create the UI for the actions treeview
		"""
		# Create the scrollbar
		self.scrollbar = tk.Scrollbar(self, orient='horizontal')
		# Create the treeview and link with the scrollbar
		self.treeview = tk.ttk.Treeview(
			self,
			columns=('Action'),
			show='headings',
			xscrollcommand=self.scrollbar.set
		)	
		self.scrollbar.config(command=self.treeview.xview)
		# Setup the treeview
		self.treeview.column('Action', width=TREEVIEW_COLUMN_WIDTH, stretch=False)
		self.treeview.heading('Action', text='Action')
		# Add copy and paste functionality to the treeview

	def place_treeview_ui(self) -> None:
		"""Place the UI for the actions treeview
		"""
		# Place the treeview and scrollbar
		self.treeview.place(x=TREEVIEW_POSX, y=TREEVIEW_POSY, width=TREEVIEW_WIDTH, height=TREEVIEW_HEIGHT)
		self.scrollbar.place(x=SCROLLBAR_POSX, y=SCROLLBAR_POSY, width=SCROLLBAR_WIDTH)

	def callback_tips_tray(self, *args) -> None:
		"""Deals with what happens if the Tips Tray changes
		"""
		# Get the tray
		tray = self.tips_tray_sv.get()
		column = self.tips_column_sv.get()
		# Change the Column optionmenu values based on the tray choice
		if tray in ['A', 'B', 'C', 'D']:
			if column == '':
				self.tips_action_sv.set('')
				self.optionmenu_tips_action.configure(values=('',))
				self.optionmenu_tips_column.configure(values=('1','2','3','4','5','6','7','8','9','10','11','12'))
			else:
				# Make sure the current action is valid
				if self.tips_action_sv.get() not in ['Pickup', 'Eject', "Nub Eject"]:
					self.tips_action_sv.set('Eject')
				self.optionmenu_tips_column.configure(values=('1','2','3','4','5','6','7','8','9','10','11','12'))
				self.optionmenu_tips_action.configure(values=('Pickup','Eject',"Nub Eject",))
		elif tray == "Tip Transfer Tray":
			self.optionmenu_tips_column.configure(values=('1','2','3','4','5','6','7','8',''))
			if column == '':
				self.tips_action_sv.set('Tip-Press')
				self.optionmenu_tips_action.configure(values=('Tip-Press',))
			else:
				# Make sure the current action is valid
				if self.tips_action_sv.get() not in ['Pickup', 'Eject']:
					self.tips_action_sv.set('Eject')
				self.optionmenu_tips_action.configure(values=('Pickup','Eject',))
		else:
			self.tips_column_sv.set('')
			self.optionmenu_tips_column.configure(values=(''))
			self.tips_action_sv.set('Eject')
			self.optionmenu_tips_action.configure(values=('Eject',))

	def callback_tips_column(self, *args) -> None:
		"""Deals with what happens if the Tips Column changes
		"""
		# Get the tray and column
		tray = self.tips_tray_sv.get()
		column = self.tips_column_sv.get()
		# Check if Tip Transfer Tray is selected and if no column is selected
		if column == '':
			if tray == "Tip Transfer Tray":
				# Add the tip press action
				self.tips_action_sv.set('Tip-Press')
				self.optionmenu_tips_action.configure(values=('Tip-Press',))
			else:
				self.tips_action_sv.set('')
				self.optionmenu_tips_action.configure(values=('',))
		else:
			# Make sure the current action is valid
			if self.tips_action_sv.get() not in ['Pickup', 'Eject', "Nub Eject"]:
				self.tips_action_sv.set('Pickup')
			self.optionmenu_tips_action.configure(values=('Pickup','Eject', "Nub Eject",))
			
	def callback_motion_consumable(self, *args) -> None:
		"""Deals with changes to the motion consumable optionmenu
		"""
		# Get the consumable, tray, column, and tip
		consumable = self.motion_consumable_sv.get()
		tray = self.motion_tray_sv.get()
		column = self.motion_column_sv.get()
		tip = self.motion_tip_sv.get()
		# Reset the tray and column optionmenus to default
		self.motion_tray_sv.set('')
		self.motion_column_sv.set('')
		# Check the consumable cases to update the trays, columns, and tips
		if consumable in NO_TRAY_CONSUMABLES:
			# No tray option
			self.motion_tray_sv.set('')
			self.optionmenu_motion_tray.configure(values=('',))
			# Set the column options
			if consumable in TWELVE_COLUMN_CONSUMABLES:
				self.optionmenu_motion_column.configure(values=('1','2','3','4','5','6','7','8','9','10','11','12',))
			elif consumable in EIGHT_COLUMN_CONSUMABLES:
				self.optionmenu_motion_column.configure(values=('1','2','3','4','5','6','7','8',))
			elif consumable in FOUR_COLUMN_CONSUMABLES:
				self.optionmenu_motion_column.configure(values=('1','2','3','4',))
			elif consumable in THREE_COLUMN_CONSUMABLES:
				self.optionmenu_motion_column.configure(values=('1','2','3',))
			elif consumable in TWO_COLUMN_CONSUMABLES:
				self.optionmenu_motion_column.configure(values=('1','2',))
			elif consumable in SPECIAL_CONSUMABLES:
				if consumable == "Tip Transfer Tray":
					self.optionmenu_motion_column.configure(values=('', '1', '2', '3',))
				elif consumable == "Tray":
					self.optionmenu_motion_column.configure(values=('', '1', '2', '3',))
			else:
				self.optionmenu_motion_column.configure(values=('',))
		else:
			# Check for special cases
			if consumable in SPECIAL_CONSUMABLES:
				if consumable == 'DG8':
					# Allow for the possible DG8 tray and column options
					self.optionmenu_motion_tray.configure(values=DG8_TRAY_OPTION_VALUES)
					self.optionmenu_motion_column.configure(values=DG8_COLUMN_OPTION_VALUES)
					self.optionmenu_motion_tip.configure(values=('1000', '50', '200', 'nub', ''))
					return None
				elif consumable == 'Chip':
					# Allow for the possible chip tray and column options
					self.optionmenu_motion_tray.configure(values=CHIP_TRAY_OPTION_VALUES)
					self.optionmenu_motion_column.configure(values=CHIP_COLUMN_OPTION_VALUES)
				elif consumable == "Tip Transfer Tray":
					# Allow for possible tray and column combos
					self.optionmenu_motion_tray.configure(values=('','A','B','C','D'))
					self.optionmenu_motion_column.configure(values=('','1','2','3','4','5','6','7','8','9'))
					self.optionmenu_motion_tip.configure(values=('1000', '50', '200', ''))
				elif consumable == "Tray":
					# Allow for possible tray and column combos
					self.optionmenu_motion_tray.configure(values=('A','B','C','D'))
					self.optionmenu_motion_column.configure(values=('','1','2','3'))
					self.optionmenu_motion_tip.configure(values=('1000', '50', '200', ''))
			else:
				# Allow for tray options
				self.optionmenu_motion_tray.configure(values=('A', 'B', 'C', 'D',))
				# Set the column options
				if consumable in NO_COLUMN_CONSUMABLES:
					self.optionmenu_motion_column.configure(values=('',))
				else:
					self.optionmenu_motion_column.configure(
						values=('1','2','3','4','5','6','7','8','9','10','11','12',)
					)
		# Allow tip options
		self.optionmenu_motion_tip.configure(values=('1000', '50', '200',))

	def callback_motion_tray(self, *args) -> None:
		"""Deals with the tray option changing
		"""
		# Get the consumable, tray, column, and tip
		consumable = self.motion_consumable_sv.get()
		tray = self.motion_tray_sv.get()
		column = self.motion_column_sv.get()
		tip = self.motion_tip_sv.get()

	def callback_other_option(self, *args) -> None:
		""" Deals with the other option changing """
		# Get the option selected
		other_option = self.other_option_sv.get()
		# Change the Parameter hint text based on the other option selected and the entry state
		if "Move relative" in other_option:
			self.other_parameter_sv.set("Enter value in usteps")
			self.entry_other_parameter.configure(state='normal')
		elif "Change" in other_option:
			self.other_parameter_sv.set("Enter value in C")
			self.entry_other_parameter.configure(state='normal')
		elif "Hold" in other_option:
			self.other_parameter_sv.set("Enter hold as time units")
			self.entry_other_parameter.configure(state='normal')
		elif "Shake on" in other_option:
			self.other_parameter_sv.set("Enter the rpm")
			self.entry_other_parameter.configure(state='normal')
		elif 'Lower' in other_option:
			self.other_parameter_sv.set("Enter value in usteps")
			self.entry_other_parameter.configure(state='normal')
		elif 'Add' in other_option:
			self.other_parameter_sv.set("Enter a comment")
			self.entry_other_parameter.configure(state='normal')
		elif 'Load' in other_option:
			self.other_parameter_sv.set("Enter columns (e.g. 1,2,3)")
			self.entry_other_parameter.configure(state='normal')
		elif 'Extend' in other_option:
			self.other_parameter_sv.set("Enter value in usteps")
			self.entry_other_parameter.configure(state='normal')
		elif 'Drip' in other_option:
			self.other_parameter_sv.set("Enter drip time in seconds")
			self.entry_other_parameter.configure(state='normal')
		elif 'Move imager' in other_option:
			self.other_parameter_sv.set("0,0,0")
			self.entry_other_parameter.configure(state='normal')
		elif 'Image' in other_option:
			self.other_parameter_sv.set("Enter an experiment name")
			self.entry_other_parameter.configure(state='normal')
		else:
			self.other_parameter_sv.set('')
			self.entry_other_parameter.configure(state='disabled')
			

	def other_parameter_focus_in(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with the focus in event to the other parameter entry """
		if self.other_option_sv.get() == "Add a comment":
			parameter = self.other_parameter_sv.get()
			self.other_parameter_sv.set(parameter)
		elif self.other_parameter_sv.get() in ["Enter value in usteps", "Enter value in C", "Enter the rpm"]:
			self.entry_other_parameter.delete('0', 'end')
			self.other_parameter_sv.set('')
			try:
				parameter = int(self.other_parameter_sv.get())
				self.other_parameter_sv.set(parameter)
			except:
				self.entry_other_parameter.delete('0', 'end')
				self.other_parameter_sv.set('')
		#else:
		#	try:
		#		parameter = float(self.other_parameter_sv.get())
		#		self.other_parameter_sv.set(parameter)
		#	except:
		#		self.entry_other_parameter.delete('0', 'end')
		#		self.other_parameter_sv.set('')

	def other_parameter_onclick(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with on click events for the entry for the other parameters """
		if self.other_option_sv.get() == "Add a comment":
			parameter = self.other_parameter_sv.get()
			self.other_parameter_sv.set(parameter)
		elif self.other_parameter_sv.get() in ["Enter value in usteps", "Enter value in C", "Enter the rpm"]:
			self.entry_other_parameter.delete('0', 'end')
			self.other_parameter_sv.set('')
			try:
				parameter = int(self.other_parameter_sv.get())
				self.other_parameter_sv.set(parameter)
			except:
				self.entry_other_parameter.delete('0', 'end')
				self.other_parameter_sv.set('')

	def other_parameter_keys(self, callback: Callable[[tk.Event], None]) -> None:
		""" Deals with on click events for the entry for the other parameters """
		if self.other_option_sv.get() == "Add a comment":
			parameter = self.other_parameter_sv.get()
			self.other_parameter_sv.set(parameter)
		elif self.other_parameter_sv.get() in ["Enter value in usteps", "Enter value in C", "Enter the rpm"]:
			self.entry_other_parameter.delete('0', 'end')
			self.other_parameter_sv.set('')
			try:
				parameter = int(self.other_parameter_sv.get())
				self.other_parameter_sv.set(parameter)
			except:
				self.entry_other_parameter.delete('0', 'end')
				self.other_parameter_sv.set('')

	def bind_button_tips_add(self, c):
		try:
			self.button_tips_add.bind('<Button-1>', c)
		except:
			pass

	def bind_button_motion_add(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_motion_add.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_pipettor_add(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_pipettor_add.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_time_add(self, callback: Callable[[tk.Event], None]) -> None:
		try:
			self.button_time_add.bind('<Button-1>', callback)
		except:
			pass
	
	def bind_button_other_add(self, callback: Callable[[tk.Event], None]) -> None:
                try:
                        self.button_other_add.bind('<Button-1>', callback)
                except:
                        pass

	def bind_button_start(self, callback: Callable[[tk.Event], None]) -> None:
		"""Deals with what happens when the start button is clicked
		"""
		try:
			self.button_start.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_load(self, callback: Callable[[tk.Event], None]) -> None:
		"""Deals with what happens when the load button is clicked
		"""
		try: 
			self.button_load.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_save(self, callback: Callable[[tk.Event], None]) -> None:
		"""Deals with what happens when the save button is clicked
		"""
		try:
			self.button_save.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_delete(self, callback: Callable[[tk.Event], None]) -> None:
		"""Deals with what happens when the delete button is clicked
		"""
		try:
			self.button_delete.bind('<Button-1>', callback)
		except:
			pass

	def update_treeview(self) -> None:
		"""Update the treeview based on the build protocol model
		"""
		# Cleanout the treeview
		for i in self.treeview.get_children():
			self.treeview.delete(i)
		# Save the actions
		n_actions = len(self.model.select())
		# Update the action progress label
		self.label_action_progress.configure(text=f"Action Progress: 0 of {n_actions}")
		actions = self.model.select()
		# Delete all actions so the IDs can be reassigned
		self.model.delete_all()
		# Add the actions back to the treeview
		for i in range(n_actions):
			action = actions[i][0]
			self.treeview.insert('', 'end', iid=i, values=(action,))
			self.model.insert(i, action)
