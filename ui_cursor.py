from framework import movement, entities, events, tile, controls, flags

import ui_dialog
import ui_menu
import constants
import camera

CURSOR = None


def boot():
	global CURSOR
	
	CURSOR = entities.create_entity(group='systems')
	tile.register(CURSOR, surface='ui')
	
	events.register_event('camera', logic)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('input', handle_keyboard_input)
	events.register_event('draw', lambda *args: entities.trigger_event(CURSOR, 'draw'))

def handle_mouse_movement(x, y, **kwargs):
	entities.trigger_event(CURSOR, 'set_position', x=x, y=y)

def handle_mouse_pressed(x, y, button):
	_x = x + camera.X
	_y = y + camera.Y
	
	if button == 1:
		for entity_id in entities.get_entity_group('contexts'):
			_entity = entities.get_entity(entity_id)
			
			if not _entity['callback']:
				continue
			
			if (_entity['tile']['x'], _entity['tile']['y']) == (_x, _y):
				_entity['callback'](x+2, y-3)
				
				break

def handle_keyboard_input():
	if controls.get_input_char('w'):
		camera.set_pos(camera.X, camera.Y - 2)
	elif controls.get_input_char('s'):
		camera.set_pos(camera.X, camera.Y + 2)
	
	if controls.get_input_char('a'):
		camera.set_pos(camera.X - 2, camera.Y)
	elif controls.get_input_char('d'):
		camera.set_pos(camera.X + 2, camera.Y)

def logic():
	if not ui_dialog.ACTIVE_DIALOG or ui_menu.ACTIVE_MENU:
		if CURSOR['tile']['x'] > constants.MAP_VIEW_WIDTH - 5:
			camera.set_pos(camera.X + 3, camera.Y)
		
		elif CURSOR['tile']['x'] <= 5:
			camera.set_pos(camera.X - 3, camera.Y)
		
		if CURSOR['tile']['y'] > constants.MAP_VIEW_HEIGHT - 5:
			camera.set_pos(camera.X, camera.Y + 3)
		
		elif CURSOR['tile']['y'] <= 5:
			camera.set_pos(camera.X, camera.Y - 3)	

def get_screen_position():
	return CURSOR['tile']['x'], CURSOR['tile']['y']

def get_map_position():
	return CURSOR['tile']['x']+camera.X, CURSOR['tile']['y']+camera.Y
