from framework import display, entities, movement, numbers, flags

import ai_factions
import ai_squads
import ai_flow
import ui_squad_control
import constants
import settings
import camera
import items
import life

import time

PLAYER = None


def boot():
	return

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
	
	#_weapons = items.get_items_in_holder(PLAYER, 'weapon')
	
	#if _weapons:
	#	_weapon = entities.get_entity(_weapons[0])
	#	_ammo = flags.get_flag(_weapon, 'ammo')
	#	_ammo_max = flags.get_flag(_weapon, 'ammo_max')
	#	_weapon_string = '%s (%s/%s)' % (_weapon['stats']['name'], _ammo, _ammo_max)
	#	
	#	display.write_string('ui', _x, constants.MAP_VIEW_HEIGHT, _weapon_string)
	#	
	#	_x += len(_weapon_string)+1

def draw_mission_details():
	for mission_id in PLAYER['missions']['active']:
		_mission = entities.get_entity(mission_id)
		_valid_goals = [g for g in _mission['goals']]
		_y_mod = constants.MAP_VIEW_HEIGHT - len(_valid_goals) - 1
		
		display.write_string('ui', 1, _y_mod - 2, _mission['title'], fore_color=(200, 200, 200), back_color=(10, 10, 10))
		
		for goal_id in _valid_goals:
			_goal = entities.get_entity(goal_id)
			
			entities.trigger_event(_goal, 'get_message', member_id=PLAYER['_id'])
			
			if not _goal['draw']:
				continue
			
			if PLAYER['missions']['active'][mission_id]['goals'][goal_id]['complete']:
				_fore_color = (200, 200, 200)
				_text = '+ %s' % _goal['message']
			else:
				_fore_color = (255, 255, 255)
				_text = '- %s' % _goal['message']
				
			display.write_string('ui', 1, _y_mod, _text, fore_color=_fore_color, back_color=(30, 30, 30))
			
			_y_mod += 1

def draw_turn_bar():
	if not ai_flow.is_flow_active():
		return
	
	_squad = entities.get_entity(ai_flow.get_active_squad())
	_current_action_points = sum([entities.get_entity(m)['stats']['action_points'] for m in _squad['members']])
	_max_action_points = sum([entities.get_entity(m)['stats']['action_points_max'] for m in _squad['members']])
	_mod = _current_action_points / float(_max_action_points)
	_filled_value = int(round(constants.MAP_VIEW_WIDTH * _mod))
	
	if _squad['faction'] == 'Rogues':
		_message = 'Action points: %s' % _current_action_points
		_fore_color = (0, 200, 0)
		_back_color = (0, 50, 0)
	
	elif entities.get_entity(_squad['leader'])['ai']['faction'] in ai_factions.FACTIONS['Rogues']['enemies']:
		_message = 'Enemy'
		_fore_color = (200, 0, 0)
		_back_color = (50, 0, 0)
	
	else:
		_message = 'Friendly'
		_fore_color = (0, 200, 200)
		_back_color = (0, 50, 50)
	
	_n = len(_message)
	_string = _message + ('=' * (_filled_value-_n)) + (' ' * ((constants.MAP_VIEW_WIDTH-_filled_value-1)))
	
	display.write_string('nodes', 0, 0, _string[:constants.MAP_VIEW_WIDTH], fore_color=_fore_color, back_color=_back_color)

def draw_fps():
	display.write_string('ui', 0, 0, '%s fps' % display.get_fps(), fore_color=(255, 255, 255))

def draw_life_memory():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	_draw_life = set()
	_can_see_life = set()
	_last_seen_locations = {}
		
	for squad_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(squad_id)
		
		if not _squad['faction'] == 'Rogues':
			continue
		
		for member_id in _squad['members']:
			_member = entities.get_entity(member_id)
			_can_see_life.update([i for i in _member['ai']['life_memory'] if _member['ai']['life_memory'][i]['can_see'] and i in entities.ENTITIES])
			_draw_life.update(_member['ai']['targets'] - _member['ai']['visible_life'])
			
			for memory_id in _member['ai']['life_memory'].keys():
				if not member_id in _last_seen_locations:
					_last_seen_locations[memory_id] = _member['ai']['life_memory'][memory_id]['last_seen_at']
	
	_draw_life = list(_draw_life)

	for entity_id in _draw_life:
		if entity_id in _can_see_life:
			continue
		
		_entity = entities.get_entity(entity_id)
		_x, _y = _last_seen_locations[entity_id]
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		if time.time() % 1 >= .5:
			_char = _entity['tile']['char']
			_fore_color = _entity['tile']['fore_color']
		else:
			_char = '!'
			_fore_color = (255, 0, 0)
		
		_render_x = numbers.clip(_x - len(_char)/2, 0, _width - len(_char) - 1)
		_render_y = numbers.clip(_y, 0, _height)
		
		#if _x - len(_char)/2 < 0 or _x + len(_char)/2 >= _width:
		#	continue
		
		if _render_y == _y:
			_render_y += 2
		
		display.write_string('ui', _render_x, _render_y, _char, fore_color=_fore_color)

def draw_long_range_life():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	if settings.OBSERVER_MODE:
		_draw_life = entities.get_entity_group('life')
	else:
		_draw_life = set()
		_draw_life_targets = set()
		
		for squad_id in entities.get_entity_group('squads'):
			_squad = entities.get_entity(squad_id)
			
			if not _squad['faction'] == 'Rogues':
				continue
			
			for member_id in _squad['members']:
				_member = entities.get_entity(member_id)
				_draw_life.add(member_id)
				_draw_life.update([i for i in _member['ai']['life_memory'] if _member['ai']['life_memory'][i]['can_see'] and i in entities.ENTITIES])
				_draw_life_targets.update([i for i in _member['ai']['life_memory'] if _member['ai']['life_memory'][i]['can_see'] and _member['ai']['life_memory'][i]['is_target'] and i in entities.ENTITIES])
		
		_draw_life = list(_draw_life)
	
	for entity_id in _draw_life:
		_entity = entities.get_entity(entity_id)
		_x, _y = movement.get_position(_entity)
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			_x = numbers.clip(_x, 0, _width-1)
			_y = numbers.clip(_y, 0, _height-1)
		else:
			continue
		
		if time.time() % 1 >= .5:
			_char = 'X'
		else:
			_char = 'O'
		
		if entity_id in _draw_life_targets:
			_fore_color = (255, 0, 0)
			_back_color = (100, 0, 0)
		else:
			_fore_color = (255, 255, 255)
			_back_color = (100, 100, 100)
		
		display.write_string('ui', _x, _y, _char, fore_color=_fore_color, back_color=_back_color)

def draw_life_labels():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	if settings.OBSERVER_MODE:
		_draw_life = entities.get_entity_group('life')
	else:
		_draw_life = [i for i in PLAYER['ai']['life_memory'] if PLAYER['ai']['life_memory'][i]['can_see']]
		
		if PLAYER['_id'] in entities.ENTITIES:
			_draw_life.append(PLAYER['_id'])
	
	for entity_id in _draw_life:
		_entity = entities.get_entity(entity_id)
		_x, _y = movement.get_position(_entity)
		_x -= _camera_x
		_y -= _camera_y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		_back_color = None
		
		if settings.OBSERVER_MODE:
			_label = _entity['ai']['current_action']
		else:
			_label = life.get_status_string(_entity)
			
			if not PLAYER['_id'] == entity_id and PLAYER['ai']['life_memory'][entity_id]['mission_related'] and time.time() % 1 >= .5:
				_back_color = (200, 0, 0)
		
		_render_x = numbers.clip(_x - len(_label)/2, 0, _width - len(_label))
		_render_y = numbers.clip(_y - 2, 0, _height)
		
		if _render_y == _y:
			_render_y += 2
		
		display.write_string('ui', _render_x, _render_y, _label, back_color=_back_color)

def draw_item_labels():
	_camera_x, _camera_y = camera.X, camera.Y
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	
	if settings.OBSERVER_MODE:
		_draw_items = entities.get_entity_group('items')
	else:
		_draw_items = [item for _items in PLAYER['ai']['visible_items'].values() for item in _items]
	
	for entity_id in _draw_items:
		if not entity_id in entities.ENTITIES:
			continue
		
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

def draw_walk_path():
	_walk_path = ui_squad_control.WALK_PATH
	
	if not _walk_path:
		return
	
	_width = display.get_surface('life')['width']
	_height = display.get_surface('life')['height']
	_entity = ui_squad_control.get_selected_squad_member()
	_action_points = _entity['stats']['action_points']
	
	for x, y in _walk_path:
		_x = x - camera.X
		_y = y - camera.Y
		
		if _x < 0 or _y < 0 or _x >= _width or _y >= _height:
			continue
		
		if _action_points < 0:
			_fore_color = (200, 0, 0)
			_char = chr(176)
		
		else:
			_fore_color = (200, 200, 200)
			_char = chr(177)
		
		display.write_char('nodes', _x, _y, _char, fore_color=_fore_color)
		_action_points -= constants.IDLE_COST
		_action_points -= movement.get_move_cost(_entity)
