from framework import entities, display, events, numbers, shapes, tile, workers

import libtcodpy as tcod

import post_processing
import constants
import tiles

import random
import time
import numpy

X = 1
NOISE = None


def add_tile(raw_tile):
	_entity = entities.create_entity(group='tiles')
	
	tile.register(_entity, surface='tiles')
	
	entities.trigger_event(_entity, 'set_char', char=raw_tile['c'])
	entities.trigger_event(_entity, 'set_fore_color', color=raw_tile['c_f'])
	entities.trigger_event(_entity, 'set_back_color', color=raw_tile['c_b'])
	entities.trigger_event(_entity, 'set_position', x=raw_tile['x'], y=raw_tile['y'])
	
	return _entity

def _post_process_water(x, y, clouds, tiles, zoom, clouds_x, clouds_y, size):
	_noise_values = [zoom * x / (size) + clouds_x,
	                 zoom * y / (size) + clouds_y]
	_shade = tcod.noise_get_turbulence(NOISE, _noise_values, tcod.NOISE_SIMPLEX)
	_shade_mod = numbers.clip(abs(_shade), .6, 1)
	
	clouds[y][x] -= _shade_mod

def post_process_water(width, height, tiles):
	global X
	
	_clouds = numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH))
	_clouds += 1.6
	_zoom = 2.0
	_clouds_x = X
	_clouds_y = X*-1
	_size = 100.0
	
	X -= .006
	
	_worker = workers.counter_2d(height, width, 18*(1+((10-constants.SHADOW_QUALITY)/10.0)), lambda x, y: _post_process_water(x, y, _clouds, tiles, _zoom, _clouds_x, _clouds_y, _size))
	
	entities.register_event(_worker, 'finish', lambda e: display.shade_surface_fore('tiles', _clouds))
	entities.register_event(_worker, 'finish', lambda e: display.shade_surface_back('tiles', _clouds))

def swamp(width, height, rings=8):
	global NOISE
	
	NOISE = tcod.noise_new(3)
	
	_tile_map = numpy.zeros((height, width))
	_center_x, _center_y = width/2, height/2
	_map_radius = max([width, height]) / 2
	_number_of_rings = _map_radius / rings
	_handled_positions = set()
	_tiles = []
	
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
				if random.uniform(0, _lod) > .45:
					_tiles.append(add_tile(tiles.swamp_water(x, y)))
				else:
					_tiles.append(add_tile(tiles.grass(x, y)))
				
			else:
				_tiles.append(add_tile(tiles.swamp(x, y)))
	
	#events.register_event('tick', lambda: post_process_water(width, height, _tiles))
	post_processing.run(time=18*(1+((10-constants.SHADOW_QUALITY)/10.0)), repeat=-1, repeat_callback=lambda _: post_process_water(width, height, _tiles))