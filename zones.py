from framework import pathfinding, display, shapes, movement, entities, events, numbers

import libtcodpy as tcod

import post_processing
import ai_factions
import ai_squads
import constants
import missions
import effects
import mapgen
import camera
import life
import maps

import logging
import random
import sys

ZONES = {}
ACTIVE_ZONE = None


def create(name, width, height, node_grid, node_sets, weight_map, tile_map, solids, faction_spawn_list, trees, inside):
	ZONES[name] = {'name': name,
	               'width': width,
	               'height': height,
	               'node_grid': node_grid,
	               'node_sets': node_sets,
	               'weight_map': weight_map,
	               'tile_map': tile_map,
	               'solids': solids,
	               'faction_spawn_list': faction_spawn_list,
	               'astar_map': None,
	               'trees': trees,
	               'inside': inside,
	               'los_map': None,
	               'shaders': []}
	
	logging.info('Created zone: %s' % name)
	
	return name

def activate(zone_id):
	global ACTIVE_ZONE
	
	ACTIVE_ZONE = zone_id
	
	_zone = ZONES[zone_id]
	_noise = tcod.noise_new(2)
	
	logging.info('Bringing zone \'%s\' online...' % _zone['name'])
	
	_zone['astar_map'] = pathfinding.setup(_zone['width'], _zone['height'], _zone['solids'])
	_zone['los_map'] = mapgen.generate_los_map(_zone['width'], _zone['height'], _zone['solids'])
	
	display.create_surface('tiles', width=_zone['width'], height=_zone['height'])
	
	maps.render_map(_zone['tile_map'], _zone['width'], _zone['height'])
	
	post_processing.start()
	
	events.register_event('logic', post_processing.tick_sun)
	
	_zone['shaders'].append(post_processing.generate_shadow_map(_zone['width'], _zone['height'], _zone['solids'], _zone['trees']))
	post_processing.generate_light_map(_zone['width'], _zone['height'], _zone['solids'], _zone['trees'])
	
	_noise = tcod.noise_new(3)
	_zoom = 2.0
	_shader = display.create_shader(_zone['width'], _zone['height'])
	
	for y in range(0, _zone['height']):
		for x in range(0, _zone['width']):
			_noise_values = [(_zoom * x / _zone['width']),
					         (_zoom * y / _zone['height'])]
			_height = .35 + numbers.clip(tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_SIMPLEX), .35, 1)
			
			_shader[0][y, x] = 1.3 * _height
			_shader[1][y, x] = 1.3 * _height
			_shader[2][y, x] = 1.1 * _height
	
	_zone['shaders'].append(_shader)
	#if not '--no-fx' in sys.argv:
	#	post_processing.run(time=8,
	#		                repeat=-1,
	#		                repeat_callback=lambda _: post_processing.post_process_clouds(constants.MAP_VIEW_WIDTH,
	#		                                                                              constants.MAP_VIEW_HEIGHT,
	#		                                                                              8,
	#		                                                                              _noise,
	#		                                                                              _zone['inside']))
	#	post_processing.run(time=0,
	#		                repeat=-1,
	#		                repeat_callback=lambda _: post_processing.post_process_lights())
	#post_processing.run(time=0,
	#                    repeat=-1,
	#                    repeat_callback=lambda _: post_processing.sunlight())
	
	camera.set_limits(0, 0, _zone['width']-constants.MAP_VIEW_WIDTH, _zone['height']-constants.MAP_VIEW_HEIGHT)
	
	logging.info('Zone \'%s\' is online' % _zone['name'])

def deactivate(zone_id):
	events.unregister_event('logic', post_processing.tick_sun)

def is_zone_active():
	return not ACTIVE_ZONE == None

def get_active_node_grid():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['node_grid']

def get_active_solids(entity, ignore_entities=[], ignore_calling_entity=False, no_life=False):
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	_solids = ZONES[ACTIVE_ZONE]['solids'].copy()
	
	if not no_life:
		if not ignore_calling_entity:
			ignore_entities.append(entity['_id'])
		
		_solids.update([movement.get_position_via_id(p) for p in entities.get_entity_group('life') if not p in ignore_entities])
	
	return _solids

def get_active_life_positions(entity):
	return [movement.get_position_via_id(p) for p in entities.get_entity_group('life') if not p == entity['_id']]

def get_active_astar_map():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['astar_map']

def get_active_weight_map():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['weight_map']

def get_active_node_sets():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['node_sets']

def get_active_size():
	if not ACTIVE_ZONE:
			raise Exception('No zone is active.')	
	
	return ZONES[ACTIVE_ZONE]['width'], ZONES[ACTIVE_ZONE]['height']

def get_active_los_map():
	if not ACTIVE_ZONE:
			raise Exception('No zone is active.')	
	
	return ZONES[ACTIVE_ZONE]['los_map']

def populate_life(zone_id):
	_zone = ZONES[zone_id]
	
	for faction_name in _zone['faction_spawn_list']:
		_spawn_profile = _zone['faction_spawn_list'][faction_name]
		
		if _spawn_profile['bases']:
			for b in range(_spawn_profile['bases']):
				for node_set_id in _zone['node_sets']:
					_node_set = _zone['node_sets'][node_set_id]
					_set_center_x, _set_center_y = _node_set['center']
					_spawn_pos = []
					
					for x, y in shapes.circle(_set_center_x, _set_center_y, 5):
						if (x, y) in _zone['solids']:
							continue
						
						_spawn_pos.append((x, y))
					
					_min_squad_size, _max_squad_size = ai_factions.FACTIONS[faction_name]['base_size_range']
					
					for i in range(random.randint(_min_squad_size, _max_squad_size)):
						_x, _y = _spawn_pos.pop(random.randint(0, len(_spawn_pos)-1))
						_e = _spawn_profile['type'](_x, _y, 'Test NPC %s' % str(i+1))
						
						if _e['ai']['meta']['is_squad_leader']:
							_squad = ai_squads.get_assigned_squad(_e)
							_squad['camp_id'] = node_set_id
							_node_set['owner'] = {'faction': faction_name,
							                      'squad': _e['ai']['squad']}
			
					if _spawn_profile['trader']:
						_x, _y = _spawn_pos.pop(random.randint(0, len(_spawn_pos)-1))
						_e = _spawn_profile['type'](_x, _y, 'Trader')
						
		
		else:
			for b in range(_spawn_profile['squads']):
				_spawn_pos = []
				
				if 'spawn_pos' in _spawn_profile:
					_center_x, _center_y = _spawn_profile['spawn_pos']
				
				else:
					_center_x, _center_y = random.sample([_zone['width'] - 50, _zone['height'] - 50, 50, 50], 2)
						
				for x, y in shapes.circle(_center_x, _center_y, 5):
					if (x, y) in _zone['solids']:
						continue
					
					_spawn_pos.append((x, y))
				
				_min_squad_size, _max_squad_size = ai_factions.FACTIONS[faction_name]['squad_size_range']
				
				for i in range(random.randint(_min_squad_size, _max_squad_size)):
					_x, _y = _spawn_pos.pop(random.randint(0, len(_spawn_pos)-1))
					_e = _spawn_profile['type'](_x, _y, 'Test NPC %s' % str(i+1))

def path_node_set(node_set, start, end, weights=None, path=False, entity=None, avoid=[]):
	if not weights == None:
		_weights = weights
	else:
		_weights = node_set['weight_map']
		
	_n_avoid = []
	
	for p in avoid:
		_p_x, _p_y = p[0]-node_set['min_x'], p[1]-node_set['min_y']
		
		if _p_x < node_set['min_x'] or _p_y < node_set['min_y'] or _p_x >= node_set['max_x'] or _p_y >= node_set['max_y']:
			continue
		
		_n_avoid.append((_p_x, _p_y))
	
	_start = (int(round((start[0]-node_set['min_x']))), int(round((start[1]-node_set['min_y']))))
	_end = (int(round((end[0]-node_set['min_x']))), int(round((end[1]-node_set['min_y']))))
	_node_set_path = pathfinding.astar(_start, _end, node_set['astar_map'], _weights, avoid=_n_avoid)

	if not _node_set_path:
		return []
	
	if path:
		_actual_path = []
		_astar_map = get_active_astar_map()
		_weight_map = get_active_weight_map()
		_x, _y = movement.get_position(entity)
		
		for pos in _node_set_path:
			_actual_path.append((node_set['min_x']+pos[0], node_set['min_y']+pos[1]))
		
		print (_x, _y), _actual_path[0], (_x, _y) in avoid, _actual_path[0] in avoid
		print _astar_map[_actual_path[0][1], _actual_path[0][0]]
		_n_path = pathfinding.astar((_x, _y), _actual_path[0], _astar_map, _weight_map, avoid=avoid)
		_n_path.extend(_actual_path)
	
		return _n_path
	
	return _node_set_path
