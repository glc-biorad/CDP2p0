import sqlite3

import tkinter as tk

class ImageModel:
	def __init__(self):
		self.connection = sqlite3.connect('cdp2p0_gui.db')
		self.cursor = self.connection.cursor()
		self.cursor.execute("create table if not exists image (title text)")
		self.filter_sv = tk.StringVar()
		self.filter_sv.set(' ')
		self.led_sv = tk.StringVar()
		self.led_sv.set('Off')
		self.dx_sv = tk.StringVar()
		self.dx_sv.set('500')
		self.dy_sv = tk.StringVar()
		self.dy_sv.set('500')
		self.dz_sv = tk.StringVar()
		self.dz_sv.set('500')
