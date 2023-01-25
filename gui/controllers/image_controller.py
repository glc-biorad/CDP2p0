import threading
import tkinter as tk

# Import utility
import time
from api.util.utils import delay

# Import the Reader API
try:
	from api.reader.reader import Reader
except Exception as e:
	print(e)
	print("Couldn't import the Reader API to the ImageController")

class ImageController:
	"""
	System for passing data from the Image View to the Image Model
	"""
	def __init__(self, model, view) -> None:
		self.model = model
		self.view = view
		self.db_name = self.model.db_name
		self.unit = self.db_name[-4]

		# Initialize the Reader
		try:
			self.reader =Reader()
		except Exception as e:
			print(e)
			print("Couldn't initialize the Reader into the ImageController")
			self.reader = None

	def setup_bindings(self) -> None:
		""" Setup the bindings between the view and the controller """
		self.view.trace_led_sv(self.callback_led)
		self.view.trace_led_intensity_iv(self.callback_led_intensity)
		self.view.trace_filter_sv(self.callback_filter)
		self.view.bind_brightfield(self.brightfield)
	
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

	def callback_led(self, *args) -> None:
		""" Callback for a change in the led selection on the view """
		# Get the selected LED
		led = self.view.led_sv.get()
		# Get the LED intensity based on the led selected
		led_intensity = int(0.5 * 100)
		# Check if the user is trying to turn off the LED
		if led == 'Off':
			# Reset the LED slider for intensity and disable it
			self.view.led_intensity_iv.set(0)
			self.view.slider_led_intensity.configure(state='disabled')
			return None
		else:
			self.view.slider_led_intensity.configure(state='normal')
			self.view.led_intensity_iv.set(led_intensity)

	def callback_led_intensity(self, *args) -> None:
		""" Callback for when the LED intensity changes """
		# Get the selected LED
		led = self.view.led_sv.get()
		# Get LED intensity set
		led_intensity = self.view.led_intensity_iv.get() * 10
		# Turn off all LEDs
		for channel in [1,2,3,4,5,6]:
			self.reader.turn_off_led(channel)
		# Check if the user is trying to turn off the LED
		if led == 'Off':
			# Reset the LED slider for intensity and disable it
			self.view.led_intensity_iv.set(0)
			self.view.slider_led_intensity.configure(state='disabled')
			return None
		# Get the channel for this led
		channel = 1
		# Turn on the selected LED 
		channels = {
			'ATTO590': 1,
			'FAM': 2,
			'CY5.5': 3,
			'ALEXA405': 4,
			'CY5': 5,
			'HEX': 6,
		}
		channel = channels[led]
		self.reader.turn_on_led(channel, led_intensity)

	def callback_filter(self, *args) -> None:
		""" Callback for the filter option changing """
		# Get the filter option selected
		filter = self.view.filter_sv.get()
		# Get the filter location based on the filer (need this in the model)
		filter_locations = {
			'Home': 0,
			'ATTO590': -21000,
			'FAM': -37000,
			'CY5.5': -4000,
			'ALEXA405': -47000,
			'CY5': -13000,
			'HEX': -30000,
		}
		filter_location = filter_locations[filter]
		# Determine if blocking is necessary (unit A and B have different hardware requiring blocking since motion and led functionality cannot be simultaneous)
		if self.unit in ['A', 'B']:
			block = True
		else:
			block = False
		# Move the filter wheel
		thread = threading.Thread(target=self.thread_filter_wheel, args=(filter_location, block,))
		thread.start()
	def thread_filter_wheel(self, filter_location: int, block: bool) -> None:
		""" Thread for moving the filter wheel """
		# Move the filter wheel
		self.reader.set_filter_wheel_location(filter_location, block)
		if filter_location == 0:
			self.reader.get_fast_api_interface().reader.axis.home('reader', 4)

	def brightfield(self, event=None) -> None:
		""" Deals with when the Brightfield button is clicked """
		# Get the current intensity and LED selections
		led_intensity = self.view.led_intensity_iv.get()
		led = self.view.led_sv.get()
		if led_intensity != 0:
			# Set LED to off
			self.view.led_sv.set('Off')
			return None
		# Turn off all leds
		for channel in [1,2,3,4,5,6]:
			self.reader.turn_off_led(channel)
		# Rotate the filter wheel to FAM and turn on the HEX LED
		thread = threading.Thread(target=self.thread_brightfield)
		thread.start()
	def thread_brightfield(self):
		""" Thread function for dealing with brightfield """
		# Get the filter option selected
		filter = 'FAM'
		# Get the filter location based on the filer (need this in the model)
		filter_locations = {
			'Home': 0,
			'ATTO590': -21000,
			'FAM': -37000,
			'CY5.5': -4000,
			'ALEXA405': -47000,
			'CY5': -13000,
			'HEX': -30000,
		}
		filter_location = filter_locations[filter]
		# Determine if blocking is necessary (unit A and B have different hardware requiring blocking since motion and led functionality cannot be simultaneous)
		if self.unit in ['A', 'B']:
			block = True
		else:
			block = False
		self.reader.set_filter_wheel_location(filter_location, block)
		self.view.filter_sv.set(filter)
		#delay(1, 'seconds')
		time.sleep(0.2)
		# Turn on the HEX LED
		self.view.led_sv.set('HEX')
