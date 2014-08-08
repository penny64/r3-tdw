from framework import entities, display, events, numbers, shapes, tile, workers

import libtcodpy as tcod

import post_processing
import buildinggen
import constants
import tiles

import random
import time
import numpy

TILE_MAP = []
WEIGHT_MAP = None
LEVEL_WIDTH = 0
LEVEL_HEIGHT = 0
SOLIDS = []


def swamp(width, height, rings=8):
	global TILE_MAP
	global LEVEL_WIDTH
	global LEVEL_HEIGHT
	global WEIGHT_MAP
	global SOLIDS
	
	WEIGHT_MAP = numpy.ones((height, width), dtype=numpy.int16)
	
	_noise = tcod.noise_new(3)
	LEVEL_WIDTH = width
	LEVEL_HEIGHT = height
	
	_tile_map = []
	for y in range(height):
		_x = []
		
		for x in range(width):
			_x.append(None)
		
		_tile_map.append(_x)
	
	_c_x, _c_y = width/2, height/2
	_passes = 8
	_bushes = set()
	_fences = set()
	
	for y in range(LEVEL_HEIGHT):
		for x in range(LEVEL_WIDTH):
			if (1 < x < width-2 and y in [2, 3]) or (1 < x < width-2 and y in [height-3, height-4]) or (x in [2, 3] and 1 < y < height-2) or (x in [width-3, width-4] and 1 < y < height-2):
				WEIGHT_MAP[y][x] = _tile['w']
				_tile_map[y][x] = tiles.wooden_fence(x, y)
				_fences.add((x, y))
				
				continue
				
			if (x, y) in _bushes or (x, y) in _fences:
				continue
			
			_dist = numbers.float_distance((x, y), (_c_x, _c_y))
			_mod = (_dist / float(max([height, width]))) * 1.3
			
			if _dist >= 30:
				if random.uniform(random.uniform(.15, .45), 1) < _dist / float(max([height, width])):
					for _x, _y in shapes.circle(x, y, random.randint(7, 10)):
						if _x < 0 or _y < 0 or _x >= width or _y >= height or (_x, _y) in _fences:
							continue
						
						if random.uniform(0, _mod) < .3:
							_tile = tiles.grass(_x, _y)
						else:
							_tile = tiles.swamp_water(_x, _y)
						
						WEIGHT_MAP[_y][_x] = _tile['w']
						_tile_map[_y][_x] = _tile
						_bushes.add((_x, _y))
					
					continue
					
				if random.uniform(random.uniform(.1, .2), 1) < _dist / float(max([height, width])):
					_tile = tiles.grass(x, y)
					
				else:
					_tile = tiles.swamp(x, y)
				
				WEIGHT_MAP[y][x] = _tile['w']
				_tile_map[y][x] = _tile
			
			else:
				WEIGHT_MAP[y][x] = _tile['w']
				_tile = tiles.swamp(x, y)
				_tile_map[y][x] = _tile
	
	_s_x, _s_y = (23, 23)
	for plot_x, plot_y in buildinggen.generate(6, 6, 'north', ['foyer', 'living_room', 'kitchen', 'bathroom']):
		_x, _y = (_s_x+plot_x)*7, (_s_y+plot_y)*7
		
		for y in range(_y, _y+7):
			for x in range(_x, _x+7):
				WEIGHT_MAP[y][x] = _tile['w']
				_tile_map[y][x] = tiles.wooden_fence(x, y)
				SOLIDS.append((x, y))
				
	
	TILE_MAP = _tile_map
	
	post_processing.generate_shadow_map(width, height, SOLIDS)
	
	post_processing.run(time=_passes,
	                    repeat=-1,
	                    repeat_callback=lambda _: post_processing.post_process_clouds(constants.MAP_VIEW_WIDTH,
	                                                                                 constants.MAP_VIEW_HEIGHT,
	                                                                                 _passes,
	                                                                                 _noise))
