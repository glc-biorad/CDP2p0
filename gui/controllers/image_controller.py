import threading
import tkinter as tk

# Import utility
import time
from turtle import bgcolor
from api.util.utils import delay

# Import the Reader API
try:
	from api.reader.reader import Reader
except Exception as e:
	print(e)
	print("Couldn't import the Reader API to the ImageController")

# Constants
LIVE_VIEW_OFF_COLOR = '#2FA572'
LIVE_VIEW_ON_COLOR = 'black'
IMAGER_VIEW_SCALED_WIDTH = 803
IMAGER_VIEW_SCALED_HEIGHT = 803

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
		self.view.bind_live_view(self.live_view)
	
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

	def live_view(self, event=None) -> None: 
		""" Deals with the Live View button being clicked """
		button_color = self.view.buttons["Live View"].cget('fg_color')
		if button_color == LIVE_VIEW_ON_COLOR:
			self.view.led_sv.set('Off')
			self.view.led_intensity_iv.set(0)
			self.view.buttons["Live View"].configure(fg_color=LIVE_VIEW_OFF_COLOR)
		else:
			self.view.buttons["Live View"].configure(fg_color=LIVE_VIEW_ON_COLOR)
			thread = threading.Thread(target=self.thread_live_view)
			thread.start()
	def thread_live_view(self, *args) -> None:
		""" Thread function for live view """
		from PIL import Image, ImageTk
		try:
			self.reader = Reader()
			# Get the camera
			camcontroller = self.reader.camcontroller
			camera = camcontroller.camera
			# Snap continuously
			camcontroller.snap_continuous_prep()
			#camcontroller.snap_single()
			camcontroller.setExposureTimeMicroseconds(2000)
			while self.view.buttons["Live View"].cget('fg_color') == LIVE_VIEW_ON_COLOR:
				# Get the image from the Camera
				image = camera.GetNextImage(1000)
				# Convert the image to a numpy array
				array = image.GetNDArray()
				# Convert to 8-bit 
				array = array / (2**16-1)
				array *= 255
				# Transpose the image so it is oriented correctly
				array = array.transpose((0,1))
				# Create an image from the array
				_image = Image.fromarray(array)
				# Set the size of the image
				width, height = _image.size
				_image = _image.resize((IMAGER_VIEW_SCALED_WIDTH,IMAGER_VIEW_SCALED_HEIGHT))
				# Store the image to avoid garbage collection
				self.img = ImageTk.PhotoImage(image=_image)
				image.Release()
				self.view.textbox_imager_view.create_image(0,0, anchor=tk.CENTER, image=self.img)
				time.sleep(0.001)
			camera.EndAcquisition()
		except Exception as e:
			print(e)
			tk.messagebox.showwarning(title="Reader Connection Issue", message="Reader could not be initialized")
			self.reader = None