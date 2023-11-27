#!/usr/bin/env python3.8

import pythonnet
from pythonnet import load

try:
	load("coreclr")
except:
	print("Cannot load coreclr into gui")

from api.util.controller import Controller as ComPortController

from gui.controllers.controller import Controller
from gui.models.model import Model
from gui.views.view import View

import multiprocessing

def main() -> None:
	unit = 'D'
	meerstetter_com_port = 'COM7'
	meerstetter_com_port_controller = ComPortController(meerstetter_com_port, 57600, dont_use_fast_api=True, timeout=1)
	print(f"Unit: {unit}")
	model = Model(unit=unit)
	view = View(model)
	controller = Controller(model, view, meerstetter_com_port_controller)
	controller.setup_bindings()
	controller.run()

if __name__ == '__main__':
	# Allow exe not to have issues with multiprocessing package
	multiprocessing.freeze_support()
	main()
