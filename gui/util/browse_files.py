
# Version: Test
import tkinter as tk

def browse_files(mode: str, title: str , initial_filename: str, initial_dir: str = './'):
	"""Opens a file browser window
	"""
	# Make sure mode is valid
	assert mode in ['w', 'r']
	# Handle the mode
	if mode == 'w':
		file = tk.filedialog.asksaveasfile(initialfile=initial_filename, initialdir=initial_dir, title=title)
	else:
		file = tk.filedialog.askopenfile(initialfile=initial_filename, initialdir=initial_dir, title=title)
	return file
