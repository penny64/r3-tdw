from framework import display, entities, movement, numbers, flags

import constants
import camera
import items
import life

PLAYER = None


def boot(entity):
	global PLAYER
	
	PLAYER = entity


def draw_status_bar(planning=False, executing=False, execute_speed='', selecting=False):
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
	
	if selecting:
		display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, 'SELECTING TARGET')
		
		_x += len('SELECTING TARGET')+1
	
	_weapons = items.get_items_in_holder(PLAYER, 'weapon')
	
	if _weapons:
		_weapon = entities.get_entity(_weapons[0])
		_ammo = flags.get_flag(_weapon, 'ammo')
		_ammo_max = flags.get_flag(_weapon, 'ammo_max')
		_weapon_string = '%s (%s/%s)' % (_weapon['stats']['name'], _ammo, _ammo_max)
		
		display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, _weapon_string)
		
		_x += len(_weapon_string)+1

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

def draw_item_labels():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	for entity_id in entities.get_entity_group('items'):
		_entity = entities.get_entity(entity_id)
		
		if _entity['stats']['owner']:
			continue
		
		_x, _y = movement.get_position(_entity)
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		_label = _entity['stats']['name']
		_render_x = numbers.clip(_x - len(_label)/2, 0, _width - len(_label))
		_render_y = numbers.clip(_y + 2, 0, _height)
		
		if _render_y == _y:
			_render_y -= 1
		
		display.write_string('ui', _render_x, _render_y, _label)

def draw_node_path(entity):
	_labels = {}
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	for node in entity['node_path']['nodes'].values():
		_node = node['node']
		
		_x, _y = _node['x'], _node['y']
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		_label = _node['name']
		
		if (_x, _y) in _labels:
			_labels[(_x, _y)] += ' -> '+_label
		else:
			_labels[(_x, _y)] = _label
	
	for x, y in _labels:
		_label = _labels[(x, y)]
		_render_x = numbers.clip(x - len(_label)/2, 0, _width - len(_label))
		_render_y = numbers.clip(y - 1, 0, _height)
		
		if _render_y == y:
			_render_y += 2
		
		display.write_string('ui', _render_x, _render_y, _label)