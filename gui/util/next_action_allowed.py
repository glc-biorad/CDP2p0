
# Version: Test
from gui.models.state_model import StateModel

# Need to consider the tip use model to see if a pickup or eject is valid based on that data

# Constants
ACTIONS = ['pickup', 'eject', 'aspirate', 'dispense', 'mix']
BANNED_PAIRS = {
	'pickup': ['pickup', 'aspirate', 'dispense', 'mix'],
	'eject': ['aspirate', 'dispense', 'mix'],
}

def next_action_allowed(model: StateModel, new_action: str) -> bool:
	""" Checks the last row in the state model to get the mode
		then compares this to the new action to see if it
		is allowed or not

	Parameters
	----------
	model : StateModel
		The model containing the previous action
	new_action : str
		The new mode (pickup, eject, aspirate, dispense, mix)
	"""
	# Get a list of all previous action mode
	try:
		actions = model.select()
		print(actions)
	except IndexError:
		return True
	# Iterate backwards though the state model
	print(len(actions))
	for i in range(len(actions)-1,-1,-1):
		# Get the mode
		mode = actions[i][3]
		if new_action.lower() == 'pickup':
			# Check if the last tip action was a pickup
			if mode in BANNED_PAIRS['pickup']:
				return False
			# Check if the last tip action was an eject
			elif mode == 'eject':
				return True
			# Everything else is ok
			else:
				continue
		if new_action.lower() == 'aspirate' or new_action.lower() == 'dispense' or new_action.lower() == 'mix':
			# Check if the last tip action was an eject
			if mode == 'eject':
				return False
			# Check if the last tip action was a pickup
			elif mode == 'pickup':
				return True
			# Everything else is ok
			else:
				continue
	return True
