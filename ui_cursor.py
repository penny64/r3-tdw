from framework import movement, entities, events, tile

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
	events.register_event('draw', lambda *args: entities.trigger_event(CURSOR, 'draw'))

def handle_mouse_movement(x, y, **kwargs):
	entities.trigger_event(CURSOR, 'set_position', x=x, y=y)

def handle_mouse_pressed(x, y, button):
	pass

def logic():
	if CURSOR['tile']['x'] > constants.MAP_VIEW_WIDTH - 5:
		camera.set_pos(camera.X + (CURSOR['tile']['x'] - (constants.MAP_VIEW_WIDTH - 5)), camera.Y)
	
	elif CURSOR['tile']['x'] <= 5:
		camera.set_pos(camera.X + (CURSOR['tile']['x'] - 5), camera.Y)
	
	if CURSOR['tile']['y'] > constants.MAP_VIEW_HEIGHT - 5:
		camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - (constants.MAP_VIEW_HEIGHT - 5)))
	
	elif CURSOR['tile']['y'] <= 5:
		camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - 5))	

def get_screen_position():
	return CURSOR['tile']['x'], CURSOR['tile']['y']

def get_map_position():
	return CURSOR['tile']['x']+camera.X, CURSOR['tile']['y']+camera.Y
