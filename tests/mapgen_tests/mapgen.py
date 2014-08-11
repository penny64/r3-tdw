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
	
	_s_x, _s_y = (110, 110)
	_room_size = 11
	_building, _rooms = buildinggen.generate(6, 6, 'north', ['foyer', 'living_room', 'kitchen', 'bathroom'])
	
	for room in _rooms:
		for plot_x, plot_y in room['plots']:
			_room = _building[(plot_x, plot_y)]
			_build_walls = ['north', 'south', 'east', 'west']
			
			for n_plot_x, n_plot_y in [(plot_x-1, plot_y), (plot_x+1, plot_y), (plot_x, plot_y-1), (plot_x, plot_y+1)]:
				if (n_plot_x, n_plot_y) in room['plots']:
					if n_plot_x - plot_x == -1 or (n_plot_x, n_plot_y) == room['parent_plot']:
						if 'west' in _build_walls:
							_build_walls.remove('west')
					
					elif n_plot_x - plot_x == 1 or (n_plot_x, n_plot_y) == room['parent_plot']:
						if 'east' in _build_walls:
							_build_walls.remove('east')
					
					if n_plot_y - plot_y == -1 or (n_plot_x, n_plot_y) == room['parent_plot']:
						if 'north' in _build_walls:
							_build_walls.remove('north')
					
					elif n_plot_y - plot_y == 1 or (n_plot_x, n_plot_y) == room['parent_plot']:
						if 'south' in _build_walls:
							_build_walls.remove('south')
			
			_x, _y = (_s_x + (plot_x*_room_size)), (_s_y + (plot_y*_room_size))
			
			for y in range(_y, _y+_room_size):
				for x in range(_x, _x+_room_size):
					if ((x-_x == 0 and 'west' in _build_walls) or (y-_y == 0 and 'north' in _build_walls) or (x-_x == _room_size-1 and 'east' in _build_walls) or (y-_y == _room_size-1 and 'south' in _build_walls)):
						WEIGHT_MAP[y][x] = _tile['w']
						_tile_map[y][x] = tiles.wooden_fence(x, y)
						
						SOLIDS.append((x, y))
			
			_last_plot_x, _last_plot_y = plot_x, plot_y
	
	for room in _rooms:
		for plot_x, plot_y in room['plots']:
			_x, _y = (_s_x + (plot_x*_room_size)), (_s_y + (plot_y*_room_size))
			
			for n_plot_x, n_plot_y in [(plot_x-1, plot_y), (plot_x+1, plot_y), (plot_x, plot_y-1), (plot_x, plot_y+1)]:
				if not (n_plot_x, n_plot_y) == room['parent_plot']:
					continue
				
				_x_diff = plot_x - n_plot_x
				_y_diff = plot_y - n_plot_y
				
				if _x_diff == 1:
					for y in range(_y+2, _y+_room_size-2):
						_tile_map[y][_x] = tiles.swamp(_x, y)
						
						if (_x, y) in SOLIDS:
							SOLIDS.remove((_x, y))
						
						_tile_map[y][_x-1] = tiles.swamp(_x-1, y)
						
						if (_x-1, y) in SOLIDS:
							SOLIDS.remove((_x-1, y))
				
				elif _x_diff == -1:
					for y in range(_y+2, _y+_room_size-2):
						_tile_map[y][_x+_room_size] = tiles.swamp(_x+_room_size, y)
						
						if (_x+_room_size, y) in SOLIDS:
							SOLIDS.remove((_x+_room_size, y))
						
						_tile_map[y][_x+_room_size-1] = tiles.swamp(_x+_room_size-1, y)
						
						if (_x+_room_size-1, y) in SOLIDS:
							SOLIDS.remove((_x+_room_size-1, y))
				
				if _y_diff == 1:
					for x in range(_x+2, _x+_room_size-2):
						_tile_map[_y][x] = tiles.swamp(x, _y)
						
						if (x, _y) in SOLIDS:
							SOLIDS.remove((x, _y))
						
						_tile_map[_y-1][x] = tiles.swamp(x, _y-1)
						
						if (x, _y-1) in SOLIDS:
							SOLIDS.remove((x, _y-1))
				
				elif _y_diff == -1:
					for x in range(_x+2, _x+_room_size-2):
						_tile_map[_y+_room_size][x] = tiles.swamp(x, _y+_room_size)
						
						if (x, _y+_room_size) in SOLIDS:
							SOLIDS.remove((x, _y+_room_size))
						
						_tile_map[_y+_room_size-1][x] = tiles.swamp(x, _y+_room_size-1)
						
						if (x, _y+_room_size-1) in SOLIDS:
							SOLIDS.remove((x, _y+_room_size-1))
					
	
	TILE_MAP = _tile_map
	
	post_processing.generate_shadow_map(width, height, SOLIDS)
	
	post_processing.run(time=_passes,
	                    repeat=-1,
	                    repeat_callback=lambda _: post_processing.post_process_clouds(constants.MAP_VIEW_WIDTH,
	                                                                                 constants.MAP_VIEW_HEIGHT,
	                                                                                 _passes,
	                                                                                 _noise))
