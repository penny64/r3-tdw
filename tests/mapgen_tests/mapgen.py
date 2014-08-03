from framework import entities, numbers, shapes, tile

import constants
import tiles

import random
import numpy


def add_tile(raw_tile):
	_entity = entities.create_entity(group='tiles')
	
	tile.register(_entity, surface='tiles')
	
	entities.trigger_event(_entity, 'set_char', char=raw_tile['c'])
	entities.trigger_event(_entity, 'set_fore_color', color=raw_tile['c_f'])
	entities.trigger_event(_entity, 'set_back_color', color=raw_tile['c_b'])
	entities.trigger_event(_entity, 'set_position', x=raw_tile['x'], y=raw_tile['y'])
	
	return _entity

def swamp(width, height, rings=8):
	_tile_map = numpy.zeros((height, width))
	_center_x, _center_y = width/2, height/2
	_map_radius = max([width, height]) / 2
	_number_of_rings = _map_radius / rings
	_handled_positions = set()
	_circs = []
	
	for i in range(_number_of_rings):
		_lod = numbers.clip((i / float(rings)) * 2, 0, .9)
		_circ_radius = (_map_radius * ((i / float(rings)) * 2)) * 3.0
		_n_circ_set = set(shapes.circle(_center_x, _center_y, int(round(_circ_radius))))
		_n_circ = list(_n_circ_set - _handled_positions)
		_handled_positions.update(_n_circ)
		
		for x, y in _n_circ:
			if x < 0 or y < 0 or x >= width or y >= height:
				continue
			
			if random.uniform(.26, 1) < _lod:
				if random.uniform(0, _lod) > .65:
					add_tile(tiles.water(x, y))
				else:
					add_tile(tiles.grass(x, y))
				
			else:
				add_tile(tiles.swamp(x, y))
			
