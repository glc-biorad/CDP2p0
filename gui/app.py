#!/usr/bin/env python3.8

from controllers.controller import Controller
from models.model import Model
from views.view import View

def main() -> None:
	model = Model()
	view = View(model)
	controller = Controller(model, view)
	controller.setup_bindings()
	controller.run()

if __name__ == '__main__':
	main()
