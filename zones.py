from framework import pathfinding, display

import constants
import camera
import maps

import logging

ZONES = {}


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
	
	return name

def activate(zone_id):
	_zone = ZONES[zone_id]
	
	logging.info('Bringing zone \'%s\' online...' % _zone['name'])
	
	pathfinding.setup(_zone['width'], _zone['height'], _zone['solids'], _zone['weight_map'])
	display.create_surface('tiles', width=_zone['width'], height=_zone['height'])
	maps.render_map(_zone['tile_map'], _zone['width'], _zone['height'])
	
	camera.set_limits(0, 0, _zone['width']-constants.MAP_VIEW_WIDTH, _zone['height']-constants.MAP_VIEW_HEIGHT)	
	
	logging.info('Zone \'%s\' is online' % _zone['name'])