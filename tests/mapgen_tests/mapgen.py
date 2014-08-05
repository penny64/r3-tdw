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
TILE_MAP = []
LEVEL_WIDTH = 0
LEVEL_HEIGHT = 0


def add_tile(raw_tile):
	_entity = entities.create_entity(group='tiles')
	
	tile.register(_entity, surface='tiles')
	
	entities.trigger_event(_entity, 'set_char', char=raw_tile['c'])
	entities.trigger_event(_entity, 'set_fore_color', color=raw_tile['c_f'])
	entities.trigger_event(_entity, 'set_back_color', color=raw_tile['c_b'])
	entities.trigger_event(_entity, 'set_position', x=raw_tile['x'], y=raw_tile['y'])
	
	return _entity

def _post_process_water(x, y, clouds, zoom, clouds_x, clouds_y, size):
	_noise_values = [(zoom * x / (size)) + clouds_x,
	                 (zoom * y / (size)) + clouds_y]
	_shade = tcod.noise_get_turbulence(NOISE, _noise_values, tcod.NOISE_SIMPLEX)
	_shade_mod = numbers.clip(abs(_shade), .6, 1)
	
	clouds[y][x] -= _shade_mod

def post_process_water(width, height, passes):
	global X
	
	_clouds = numpy.zeros((height, width))
	_clouds += 1.6
	_zoom = 2.0
	_clouds_x = (display.get_surface('tiles')['start_x']*.015)+X
	_clouds_y = (display.get_surface('tiles')['start_y']*.015)+(X * -.5)
	_size = 100.0
	
	X -= .003
	
	_worker = workers.counter_2d(width,
	                             height,
	                             passes,
	                             lambda x, y: _post_process_water(x, y, _clouds, _zoom, _clouds_x, _clouds_y, _size))
	
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_fore('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT))
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_back('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT))

def swamp(width, height, rings=8):
	global NOISE
	global TILE_MAP
	global LEVEL_WIDTH
	global LEVEL_HEIGHT
	
	NOISE = tcod.noise_new(3)
	LEVEL_WIDTH = width
	LEVEL_HEIGHT = height
	
	_tile_map = []
	for y in range(height):
		_x = []
		
		for x in range(width):
			_x.append(None)
		
		_tile_map.append(_x)
	
	_c_x, _c_y = width/2, height/2
	_passes = 18
	_bushes = set()
	_fences = set()
	
	for y in range(LEVEL_HEIGHT):
		for x in range(LEVEL_WIDTH):
			if (1 < x < width-2 and y in [2, 3]) or (1 < x < width-2 and y in [height-3, height-4]) or (x in [2, 3] and 1 < y < height-2) or (x in [width-3, width-4] and 1 < y < height-2):
				_tile_map[y][x] = tiles.wooden_fence(x, y)
				_fences.add((x, y))
				
				continue
				
			if (x, y) in _bushes or (x, y) in _fences:
				continue
			
			_dist = numbers.float_distance((x, y), (_c_x, _c_y))
			_mod = (_dist / float(max([height, width]))) * 1.3
			
			if _dist >= 40:
				if random.uniform(random.uniform(.15, .45), 1) < _dist / float(max([height, width])):
					for _x, _y in shapes.circle(x, y, random.randint(5, 9)):
						if _x < 0 or _y < 0 or _x >= width or _y >= height or (_x, _y) in _fences:
							continue
						
						if random.uniform(0, _mod) < .3:
							if random.uniform(0, 1) < .2:
								_tile = tiles.swamp(_x, _y)
							else:
								_tile = tiles.grass(_x, _y)
						else:
							_tile = tiles.swamp_water(_x, _y)
						
						_tile_map[_y][_x] = _tile
						_bushes.add((_x, _y))
					
					continue
					
				if random.uniform(random.uniform(.1, .2), 1) < _dist / float(max([height, width])):
					_tile = tiles.grass(x, y)
					
				else:
					_tile = tiles.swamp(x, y)
				
				_tile_map[y][x] = _tile
			
			else:
				_tile = tiles.swamp(x, y)
				_tile_map[y][x] = _tile
	
	#for pos in _bushes:
	#	
	
	TILE_MAP = _tile_map
	
	post_processing.run(time=_passes,
	                    repeat=-1,
	                    repeat_callback=lambda _: post_process_water(constants.MAP_VIEW_WIDTH,
	                                                                 constants.MAP_VIEW_HEIGHT,
	                                                                 _passes))
