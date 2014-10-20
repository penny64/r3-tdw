from framework import numbers, shapes

import libtcodpy as tcod

import constants
import mapgen
import tiles
import life

import random


def generate(width, height):
	_weight_map, _tile_map, _solids, _node_grid = mapgen.create_map(width, height)
	_zoom = .95
	_noise = tcod.noise_new(3)
	_low_grass = 30
	_fsl = {}
	_building_space = set()
	_walls = set()
	_possible_trees = set()
	
	_river_start_x = random.randint(int(round(width * .35)), int(round(width * .65)))
	_river_start_y = 0#random.randint(int(round(height * .15)), int(round(height * .85)))
	_x = _river_start_x
	_y = _river_start_y
	_px, _py = _river_start_x, _river_start_y
	_river_direction = 270
	_turn_rate = random.randint(-1, 1)
	_river_tiles = set()
	_river_size = random.randint(5, 7)
	
	while 1:
		for i in range(4, 10):
			for __x, __y in shapes.circle(_x, _y, _river_size):
				if __x < 0 or __y < 0 or __x >= width or __y >= height or (__x, __y) in _solids:
					continue
				
				_river_tiles.add((__x, __y))
				_tile = tiles.swamp_water(__x, __y)
				_tile_map[__y][__x] = _tile
				_weight_map[__y][__x] = _tile['w']
			
			_river_direction += _turn_rate
			_xv, _yv = numbers.velocity(_river_direction, 1)
			_px += _xv
			_py += _yv
			_x = int(round(_px))
			_y = int(round(_py))
			
			if _x < 0 or _y < 0 or _x >= width or _y >= height or (_x, _y) in _solids:
				break
		
		if _x < 0 or _y < 0 or _x >= width or _y >= height:
			break
		
		_turn_rate = random.uniform(-2.5, 2.5)
		_river_size = numbers.clip(_river_size + random.randint(-1, 1), 4, 9)
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _river_tiles:
				continue
			
			_tile = tiles.grass(x, y)
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
	
	#tcod.noise_set_type(_noise, tcod.NOISE_WAVELET)
	
	#for y in range(height):
	#	for x in range(width):
	#		_noise_values = [(_zoom * x / (constants.MAP_VIEW_WIDTH)),
	#				         (_zoom * y / (constants.MAP_VIEW_HEIGHT))]
	#		_noise_value = 100 * tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_WAVELET)
	#		
	#		if _low_grass <= _noise_value <= 100:
	#			_tile = tiles.tall_grass(x, y)
	#			
	#			if random.uniform(0, 1) > .5:
	#				_possible_trees.add((x, y))
	#		
	#		elif _noise_value >= _low_grass - 10 and 10 * random.uniform(0, 1) > _low_grass-_noise_value:
	#			_tile = tiles.grass(x, y)
	#		
	#		else:
	#			_tile = tiles.swamp_water(x, y)
	#		
	#		_tile_map[y][x] = _tile
	#		_weight_map[y][x] = _tile['w']
	
	_trees = {}
	_tree_plots = _possible_trees - _solids
	_used_trees = random.sample(_tree_plots, numbers.clip(int(round((width * height) * .002)), 0, len(_tree_plots)))
	
	for x, y in _used_trees:
		_size = random.randint(1, 3)
		
		for _x, _y in shapes.circle(x, y, _size):
			if _x < 0 or _y < 0 or _x >= width or _y >= height or (_x, _y) in _solids:
				break
			
			_tile = tiles.tree(_x, _y)
			_weight_map[_y][_x] = _tile['w']
			_tile_map[_y][_x] = _tile
			_trees[_x, _y] = random.uniform(2, 3.5) * _size
			
			_solids.add((_x, _y))
	
	_plot_pole_x, _plot_pole_y = width/2, height/2
	
	mapgen.build_node_grid(_node_grid, _solids)
	#mapgen.add_plot_pole(_plot_pole_x, _plot_pole_y, 40, _solids)
	
	#_fsl = {'Runners': {'bases': 1, 'squads': 0, 'trader': True, 'type': life.human_runner},
	#        #'Bandits': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit},
	#        'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl, _trees, _building_space - _walls