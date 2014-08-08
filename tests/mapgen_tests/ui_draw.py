from framework import display, entities, movement, numbers

import constants
import camera
import life

PLAYER = None


def boot(entity):
	global PLAYER
	
	PLAYER = entity


def draw_status_bar(planning=False, executing=False, execute_speed=''):
	_x = 0
	
	if planning:
		display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, 'PLANNING')
		
		_x += len('PLANNING')+1
	
	if executing:
		display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, 'EXECUTING')
		
		_x += len('EXECUTING')+1
	
	if execute_speed:
		display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, execute_speed)
		
		_x += len(execute_speed)+1

def draw_fps():
	display.write_string('ui', 0, 0, '%s fps' % display.get_fps(), fore_color=(255, 255, 255))

def draw_life_labels():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	for entity_id in entities.get_entity_group('life'):
		_entity = entities.get_entity(entity_id)
		_x, _y = movement.get_position(_entity)
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		_label = life.get_status_string(_entity)
		_render_x = numbers.clip(_x - len(_label)/2, 0, _width - len(_label))
		_render_y = numbers.clip(_y - 2, 0, _height)
		
		if _render_y == _y:
			_render_y += 2
		
		display.write_string('ui', _render_x, _render_y, _label)

def draw_node_path(entity):
	for node in entity['node_path']['nodes'].values():
		_node = node['node']
		
		_x, _y = _node['x'], _node['y']
		_camera_x, _camera_y = camera.X, camera.Y
		_width = display.get_surface('life')['width']
		_height = display.get_surface('life')['height']
		
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		_label = 'node'
		_render_x = numbers.clip(_x - len(_label)/2, 0, _width - len(_label))
		_render_y = numbers.clip(_y - 2, 0, _height)
		
		if _render_y == _y:
			_render_y += 2
		
		display.write_string('ui', _render_x, _render_y, _label)