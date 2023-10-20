
# Version: Test
from typing import Any, Callable
from tkinter import StringVar, IntVar
import tkinter as tk
import customtkinter as ctk

# Import the model
from gui.models.model import Model

# Import the Controller

# Constants
FONT = "Sergio UI"
LABEL_POSX = 200
LABEL_POSY = 5
LABEL_TEC_POSX = 30
LABEL_TEC_POSY = 40
ENTRY_TEC_READ_POSX = 165
ENTRY_TEC_READ_POSY = 40
ENTRY_TEC_READ_WIDTH = 45
BUTTON_TEC_READ_POSX = 215
BUTTON_TEC_READ_POSY = 40
BUTTON_TEC_READ_WIDTH = 150
ENTRY_TEC_WRITE_POSX = 370
ENTRY_TEC_WRITE_POSY = 40
ENTRY_TEC_WRITE_WIDTH = 45
BUTTON_TEC_WRITE_POSX = 420
BUTTON_TEC_WRITE_POSY = 40
BUTTON_TEC_WRITE_WIDTH = 150
BUTTON_WRITE_COLOR = '#10adfe'
LABEL_FW_POSX = 90
LABEL_FW_POSY = 80
ENTRY_FW_POSX = 165
ENTRY_FW_POSY = 80
ENTRY_FW_WIDTH = 200
BUTTON_FW_BROWSE_POSX = 370
BUTTON_FW_BROWSE_POSY = 80
BUTTON_FW_BROWSE_WIDTH = 90
BUTTON_FW_WRITE_POSX = 465
BUTTON_FW_WRITE_POSY = 80
BUTTON_FW_WRITE_WIDTH = 105
LABEL_TIP_BOX_POSX = 100
LABEL_TIP_BOX_POSY = 160
LABEL_1_POSX = 165
LABEL_1_POSY = 120
LABEL_2_POSX = 265
LABEL_2_POSY = 120
LABEL_3_POSX = 365
LABEL_3_POSY = 120
LABEL_4_POSX = 465
LABEL_4_POSY = 120
LABEL_5_POSX = 165
LABEL_5_POSY = 160
LABEL_6_POSX = 265
LABEL_6_POSY = 160
LABEL_7_POSX = 365
LABEL_7_POSY = 160
LABEL_8_POSX = 465
LABEL_8_POSY = 160
LABEL_9_POSX = 165
LABEL_9_POSY = 200
LABEL_10_POSX = 261
LABEL_10_POSY = 200
LABEL_11_POSX = 361
LABEL_11_POSY = 200
LABEL_12_POSX = 461
LABEL_12_POSY = 200
OPTIONMENU_1_POSX = 185
OPTIONMENU_1_POSY = 120
OPTIONMENU_2_POSX = 285
OPTIONMENU_2_POSY = 120
OPTIONMENU_3_POSX = 385
OPTIONMENU_3_POSY = 120
OPTIONMENU_4_POSX = 485
OPTIONMENU_4_POSY = 120
OPTIONMENU_5_POSX = 185
OPTIONMENU_5_POSY = 160
OPTIONMENU_6_POSX = 285
OPTIONMENU_6_POSY = 160
OPTIONMENU_7_POSX = 385
OPTIONMENU_7_POSY = 160
OPTIONMENU_8_POSX = 485
OPTIONMENU_8_POSY = 160
OPTIONMENU_9_POSX = 185
OPTIONMENU_9_POSY = 200
OPTIONMENU_10_POSX = 285
OPTIONMENU_10_POSY = 200
OPTIONMENU_11_POSX = 385
OPTIONMENU_11_POSY = 200
OPTIONMENU_12_POSX = 485
OPTIONMENU_12_POSY = 200
OPTIONMENU_TIP_WIDTH = 70

class ConfigureFrame(ctk.CTkFrame):
	""" Configure Frame for creating the Configure Tab UI """
	def __init__(self, master: ctk.CTk, model: Model, width: int, height: int, posx: int, posy: int) -> None:
		""" Construct the Configure Frame """
		self.master_model = model
		self.model = self.master_model.get_configure_model()
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

	def create_ui(self) -> None:
		""" Create the UI for the Configure Tab """
		# Create the main configuration settings label
		self.label = ctk.CTkLabel(master=self, text="Configuration Settings", font=(FONT,-16))
		# Create the TEC Address label, entries, and buttons
		self.label_tec = ctk.CTkLabel(master=self, text="Set TEC Address:", font=(FONT,-16))
		self.tec_read_sv = StringVar()
		self.tec_read_sv.set('')
		self.entry_tec_read = ctk.CTkEntry(
			master=self,
			textvariable=self.tec_read_sv,
			state='disabled',
			font=(FONT,-16),
			width=ENTRY_TEC_READ_WIDTH,
		)
		self.button_tec_read = ctk.CTkButton(
			master=self,
			text='Read',
			font=(FONT,-16),
			width=BUTTON_TEC_READ_WIDTH,
		)
		self.tec_write_sv = StringVar()
		self.tec_write_sv.set('')
		self.entry_tec_write = ctk.CTkEntry(
			master=self,
			textvariable=self.tec_write_sv,
			font=(FONT,-16),
			width=ENTRY_TEC_WRITE_WIDTH,
		)
		self.button_tec_write = ctk.CTkButton(
			master=self,
			text='Write',
			font=(FONT,-16),
			width=BUTTON_TEC_WRITE_WIDTH,
			fg_color = BUTTON_WRITE_COLOR,
		)
		# Create the FW lable, entry, and buttons
		self.label_fw = ctk.CTkLabel(master=self, text="Load FW:", font=(FONT,-16))
		self.fw_sv = StringVar()
		self.fw_sv.set(r"firmware\v.1.0.0\\")
		self.entry_fw = ctk.CTkEntry(
			master=self,
			textvariable=self.fw_sv,
			font=(FONT,-12),
			width=ENTRY_FW_WIDTH,
		)
		self.button_fw_browse = ctk.CTkButton(
			master=self,
			text='Browse',
			font=(FONT,-16),
			width=BUTTON_FW_BROWSE_WIDTH,
		)
		self.button_fw_write = ctk.CTkButton(
			master=self,
			text='Write',
			font=(FONT,-16),
			width=BUTTON_FW_WRITE_WIDTH,
			fg_color = BUTTON_WRITE_COLOR,
		)
		# Create the tip box configuration labels and entries
		self.label_tip_box = ctk.CTkLabel(master=self, text="Tip Box:", font=(FONT,-16))
		self.label_1 = ctk.CTkLabel(master=self, text='1' , font=(FONT,-16))
		self.label_2 = ctk.CTkLabel(master=self, text='2' , font=(FONT,-16))
		self.label_3 = ctk.CTkLabel(master=self, text='3' , font=(FONT,-16))
		self.label_4 = ctk.CTkLabel(master=self, text='4' , font=(FONT,-16))
		self.label_5 = ctk.CTkLabel(master=self, text='5' , font=(FONT,-16))
		self.label_6 = ctk.CTkLabel(master=self, text='6' , font=(FONT,-16))
		self.label_7 = ctk.CTkLabel(master=self, text='7' , font=(FONT,-16))
		self.label_8 = ctk.CTkLabel(master=self, text='8' , font=(FONT,-16))
		self.label_9 = ctk.CTkLabel(master=self, text='9' , font=(FONT,-16))
		self.label_10 = ctk.CTkLabel(master=self, text='10' , font=(FONT,-16))
		self.label_11 = ctk.CTkLabel(master=self, text='11' , font=(FONT,-16))
		self.label_12 = ctk.CTkLabel(master=self, text='12' , font=(FONT,-16))
		self.tip_1_sv = StringVar()
		self.tip_1_sv.set(self.model.select(name="Tip Box")[0][2])
		#self.tip_1_sv.trace('w', self.trace_tip_1_sv)
		self.optionmenu_1 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_1_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_2_sv = StringVar()
		self.tip_2_sv.set(self.model.select(name="Tip Box")[0][3])
		self.optionmenu_2 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_2_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_3_sv = StringVar()
		self.tip_3_sv.set(self.model.select(name="Tip Box")[0][4])
		self.optionmenu_3 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_3_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_4_sv = StringVar()
		self.tip_4_sv.set(self.model.select(name="Tip Box")[0][5])
		self.optionmenu_4 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_4_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_5_sv = StringVar()
		self.tip_5_sv.set(self.model.select(name="Tip Box")[0][6])
		self.optionmenu_5 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_5_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_6_sv = StringVar()
		self.tip_6_sv.set(self.model.select(name="Tip Box")[0][7])
		self.optionmenu_6 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_6_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_7_sv = StringVar()
		self.tip_7_sv.set(self.model.select(name="Tip Box")[0][8])
		self.optionmenu_7 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_7_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_8_sv = StringVar()
		self.tip_8_sv.set(self.model.select(name="Tip Box")[0][9])
		self.optionmenu_8 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_8_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_9_sv = StringVar()
		self.tip_9_sv.set(self.model.select(name="Tip Box")[0][10])
		self.optionmenu_9 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_9_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_10_sv = StringVar()
		self.tip_10_sv.set(self.model.select(name="Tip Box")[0][11])
		self.optionmenu_10 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_10_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_11_sv = StringVar()
		self.tip_11_sv.set(self.model.select(name="Tip Box")[0][12])
		self.optionmenu_11 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_11_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)
		self.tip_12_sv = StringVar()
		self.tip_12_sv.set(self.model.select(name="Tip Box")[0][13])
		self.optionmenu_12 = ctk.CTkOptionMenu(
			master=self,
			corner_radius=2,
			variable=self.tip_12_sv,
			values=('1000', '50', '200', ''),
			width=OPTIONMENU_TIP_WIDTH,
		)

	def place_ui(self) -> None:
		""" Place the UI for the Configuration Tab """
		# Place the configure frame
		self.place(x=self.posx, y=self.posy)
		# Place the main label
		self.label.place(x=LABEL_POSX, y=LABEL_POSY)
		# Place the TEC address label, entries, and buttons
		self.label_tec.place(x=LABEL_TEC_POSX, y=LABEL_TEC_POSY)
		self.entry_tec_read.place(x=ENTRY_TEC_READ_POSX, y=ENTRY_TEC_READ_POSY)
		self.button_tec_read.place(x=BUTTON_TEC_READ_POSX, y=BUTTON_TEC_READ_POSY)
		self.entry_tec_write.place(x=ENTRY_TEC_WRITE_POSX, y=ENTRY_TEC_WRITE_POSY)
		self.button_tec_write.place(x=BUTTON_TEC_WRITE_POSX, y=BUTTON_TEC_WRITE_POSY)
		# Place the FW label, entry, and button widgets
		self.label_fw.place(x=LABEL_FW_POSX, y=LABEL_FW_POSY)
		self.entry_fw.place(x=ENTRY_FW_POSX, y=ENTRY_FW_POSY)
		self.button_fw_browse.place(x=BUTTON_FW_BROWSE_POSX, y=BUTTON_FW_BROWSE_POSY)
		self.button_fw_write.place(x=BUTTON_FW_WRITE_POSX, y=BUTTON_FW_WRITE_POSY)
		self.label_tip_box.place(x=LABEL_TIP_BOX_POSX, y=LABEL_TIP_BOX_POSY)
		self.label_1.place(x=LABEL_1_POSX, y=LABEL_1_POSY)
		self.label_2.place(x=LABEL_2_POSX, y=LABEL_2_POSY) 
		self.label_3.place(x=LABEL_3_POSX, y=LABEL_3_POSY) 
		self.label_4.place(x=LABEL_4_POSX, y=LABEL_4_POSY) 
		self.label_5.place(x=LABEL_5_POSX, y=LABEL_5_POSY) 
		self.label_6.place(x=LABEL_6_POSX, y=LABEL_6_POSY) 
		self.label_7.place(x=LABEL_7_POSX, y=LABEL_7_POSY) 
		self.label_8.place(x=LABEL_8_POSX, y=LABEL_8_POSY) 
		self.label_9.place(x=LABEL_9_POSX, y=LABEL_9_POSY) 
		self.label_10.place(x=LABEL_10_POSX, y=LABEL_10_POSY)
		self.label_11.place(x=LABEL_11_POSX, y=LABEL_11_POSY)
		self.label_12.place(x=LABEL_12_POSX, y=LABEL_12_POSY)
		self.optionmenu_1.place(x=OPTIONMENU_1_POSX, y=OPTIONMENU_1_POSY)
		self.optionmenu_2.place(x=OPTIONMENU_2_POSX, y=OPTIONMENU_2_POSY)
		self.optionmenu_3.place(x=OPTIONMENU_3_POSX, y=OPTIONMENU_3_POSY)
		self.optionmenu_4.place(x=OPTIONMENU_4_POSX, y=OPTIONMENU_4_POSY)
		self.optionmenu_5.place(x=OPTIONMENU_5_POSX, y=OPTIONMENU_5_POSY)
		self.optionmenu_6.place(x=OPTIONMENU_6_POSX, y=OPTIONMENU_6_POSY)
		self.optionmenu_7.place(x=OPTIONMENU_7_POSX, y=OPTIONMENU_7_POSY)
		self.optionmenu_8.place(x=OPTIONMENU_8_POSX, y=OPTIONMENU_8_POSY)
		self.optionmenu_9.place(x=OPTIONMENU_9_POSX, y=OPTIONMENU_9_POSY)
		self.optionmenu_10.place(x=OPTIONMENU_10_POSX, y=OPTIONMENU_10_POSY)
		self.optionmenu_11.place(x=OPTIONMENU_11_POSX, y=OPTIONMENU_11_POSY)
		self.optionmenu_12.place(x=OPTIONMENU_12_POSX, y=OPTIONMENU_12_POSY)

	def bind_button_tec_read(self, callback: Callable[[tk.Event], None]) -> None:
		""" Bind the TEC Read Button to the controller """
		try:
			self.button_tec_read.bind('<Button-1>', callback)
		except:
			pass

	def bind_button_tec_write(self, callback: Callable[[tk.Event], None]) -> None:
		""" Bind the TEC Write Button to the controller """
		try:
			self.button_tec_write.bind('<Button-1>', callback)
		except:
			pass

	def trace_tip_1_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_1_sv.trace('w', callback)
		except:
			pass

	def trace_tip_2_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_2_sv.trace('w', callback)
		except:
			pass

	def trace_tip_3_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_3_sv.trace('w', callback)
		except:
			pass

	def trace_tip_4_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_4_sv.trace('w', callback)
		except:
			pass

	def trace_tip_5_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_5_sv.trace('w', callback)
		except:
			pass

	def trace_tip_6_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_6_sv.trace('w', callback)
		except:
			pass

	def trace_tip_7_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_7_sv.trace('w', callback)
		except:
			pass

	def trace_tip_8_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_8_sv.trace('w', callback)
		except:
			pass

	def trace_tip_9_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_9_sv.trace('w', callback)
		except:
			pass

	def trace_tip_10_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_10_sv.trace('w', callback)
		except:
			pass

	def trace_tip_11_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_11_sv.trace('w', callback)
		except:
			pass

	def trace_tip_12_sv(self, callback: Callable[[tk.Event], None]) -> None:
		try: 
			self.tip_12_sv.trace('w', callback)
		except:
			pass
