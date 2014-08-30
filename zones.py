from framework import pathfinding, display, shapes

import libtcodpy as tcod

import post_processing
import ai_factions
import constants
import camera
import life
import maps

import logging
import random

ZONES = {}
ACTIVE_ZONE = None


def create(name, width, height, node_grid, node_sets, weight_map, tile_map, solids, faction_spawn_list):
	ZONES[name] = {'name': name,
	               'width': width,
	               'height': height,
	               'node_grid': node_grid,
	               'node_sets': node_sets,
	               'weight_map': weight_map,
	               'tile_map': tile_map,
	               'solids': solids,
	               'faction_spawn_list': faction_spawn_list}
	
	logging.info('Created zone: %s' % name)
	
	return name

def activate(zone_id):
	global ACTIVE_ZONE
	
	ACTIVE_ZONE = zone_id
	
	_zone = ZONES[zone_id]
	_noise = tcod.noise_new(3)
	
	logging.info('Bringing zone \'%s\' online...' % _zone['name'])
	
	pathfinding.setup(_zone['width'], _zone['height'], _zone['solids'], _zone['weight_map'])
	display.create_surface('tiles', width=_zone['width'], height=_zone['height'])
	maps.render_map(_zone['tile_map'], _zone['width'], _zone['height'])
	
	post_processing.generate_shadow_map(_zone['width'], _zone['height'], _zone['solids'])
	post_processing.run(time=8,
                        repeat=-1,
                        repeat_callback=lambda _: post_processing.post_process_clouds(constants.MAP_VIEW_WIDTH,
                                                                                      constants.MAP_VIEW_HEIGHT,
                                                                                      8,
                                                                                      _noise))	
	
	camera.set_limits(0, 0, _zone['width']-constants.MAP_VIEW_WIDTH, _zone['height']-constants.MAP_VIEW_HEIGHT)	
	
	logging.info('Zone \'%s\' is online' % _zone['name'])

def is_zone_active():
	return not ACTIVE_ZONE == None

def get_active_node_grid():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['node_grid']

def get_active_solids():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['solids']

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
							_squad = ai_factions.get_assigned_squad(_e)
							_squad['camp_id'] = node_set_id
							_node_set['owner'] = _e['ai']['squad']
		
		else:
			for b in range(_spawn_profile['squads']):
				_spawn_pos = []
				_center_x, _center_y = (150, 120)
						
				for x, y in shapes.circle(_center_x, _center_y, 5):
					if (x, y) in _zone['solids']:
						continue
					
					_spawn_pos.append((x, y))
				
				_min_squad_size, _max_squad_size = ai_factions.FACTIONS[faction_name]['squad_size_range']
				
				for i in range(random.randint(_min_squad_size, _max_squad_size)):
					_x, _y = _spawn_pos.pop(random.randint(0, len(_spawn_pos)-1))
					_e = _spawn_profile['type'](_x, _y, 'Test NPC %s' % str(i+1))
