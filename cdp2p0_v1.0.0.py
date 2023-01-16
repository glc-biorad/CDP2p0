#!/usr/bin/env python3.8

import pythonnet
from pythonnet import load

try:
	load("coreclr")
except:
	print("Cannot load coreclr into gui")

from gui.controllers.controller import Controller
from gui.models.model import Model
from gui.views.view import View

def main() -> None:
	unit = 'C'
	print(f"Unit: {unit}")
	model = Model(unit=unit)
	view = View(model)
	controller = Controller(model, view)
	controller.setup_bindings()
	controller.run()

if __name__ == '__main__':
	main()
