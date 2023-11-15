#!/usr/bin/env python3.8

import pythonnet
from pythonnet import load
from api.util.server import Server

try:
	load("coreclr")
except:
	print("Cannot load coreclr into gui")

import multiprocessing

def main() -> None:
	server = Server()
	server.run()

if __name__ == '__main__':
	# Allow exe not to have issues with multiprocessing package
	multiprocessing.freeze_support()
	main()
