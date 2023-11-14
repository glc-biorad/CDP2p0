
# Version: Test
# Import BuildProtocolModel for the type
from gui.models.build_protocol_model import BuildProtocolModel

def insert_at_selected_row(action_message: str, selected_row: str, model: BuildProtocolModel) -> None:
	""" Inserts the action message into the selected row

	Parameters
	----------
	action_message : str
		action to be inserted
	selected_row : str
		selected row name
	model : BuildProtocolModel
		Model to be updated
	"""
	# Insert below the selected row or at the end of the action treeview
	if selected_row != None:
		ID = int(selected_row)
		# Store the actions
		actions = model.select()
		# Delete all actions after ID
		for i in range(ID+1, len(actions)):
			model.delete(i)
		# Insert the action
		model.insert(ID, action_message)
		# Insert all actions after ID with an index shifted by 1
		for i in range(ID+1, len(actions)):
			model.insert(i, actions[i][0])
	else:
		ID = len(model.select())
		# Insert action into the action list
		model.insert(ID, action_message)

