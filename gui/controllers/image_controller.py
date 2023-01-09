import tkinter as tk

class ImageController:
	"""
	System for passing data from the Image View to the Image Model
	"""
	def __init__(self, model, view) -> None:
		self.model = model
		self.view = view
	
	def get_filter_sv(self, id: int) -> tk.StringVar:
		return self.model.filter_sv

	def get_led_sv(self, id: int) -> tk.StringVar:
		return self.model.led_sv

	def get_dx_sv(self, id: int) -> tk.StringVar:
		return self.model.dx_sv

	def get_dy_sv(self, id: int) -> tk.StringVar:
		return self.model.dy_sv

	def get_dz_sv(self, id: int) -> tk.StringVar:
		return self.model.dz_sv
