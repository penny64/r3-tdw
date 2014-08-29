from framework import pathfinding, display, shapes

import libtcodpy as tcod

import post_processing
import constants
import mapgen
import camera
import life
import maps

import logging
import random

ZONES = {}
ACTIVE_ZONE = None


def create(name, width, height, node_grid, node_sets, weight_map, tile_map, solids):
	ZONES[name] = {'name': name,
	               'width': width,
	               'height': height,
	               'node_grid': node_grid,
	               'node_sets': node_sets,
	               'weight_map': weight_map,
	               'tile_map': tile_map,
	               'solids': solids}
	
	logging.info('Created zone: %s' % name)
	
	mapgen.reset()
	
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

def get_active_node_grid():
	if not ACTIVE_ZONE:
		raise Exception('No zone is active.')
	
	return ZONES[ACTIVE_ZONE]['node_grid']

def populate_life(zone_id):
	_zone = ZONES[zone_id]
	
	for node_set_id in _zone['node_sets']:
		_node_set = _zone['node_sets'][node_set_id]
		_set_center_x, _set_center_y = _node_set['center']
		_spawn_pos = []
		
		print _node_set['center']
		
		for x, y in shapes.circle(_set_center_x, _set_center_y, 5):
			if (x, y) in _zone['solids']:
				continue
			
			_spawn_pos.append((x, y))
		
		for i in range(2):
			_x, _y = _spawn_pos.pop(random.randint(0, len(_spawn_pos)-1))
			life.human_runner(_x, _y, 'Test NPC %s' % str(i+1))