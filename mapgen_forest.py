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
	_low_grass = 25
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
	_river_size = random.randint(7, 10)
	_ground_tiles = set()
	_possible_camps = set()
	
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
		_river_size = numbers.clip(_river_size + random.randint(-1, 1), 7, 10)
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _river_tiles:
				continue
			
			_tile = tiles.grass(x, y)
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
			
			_ground_tiles.add((x, y))
	
	tcod.noise_set_type(_noise, tcod.NOISE_WAVELET)
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _river_tiles:
				continue
			
			_noise_values = [(_zoom * x / (constants.MAP_VIEW_WIDTH)),
					         (_zoom * y / (constants.MAP_VIEW_HEIGHT))]
			_noise_value = 100 * tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_WAVELET)
			
			if _low_grass <= _noise_value <= 100:
				_tile = tiles.tall_grass(x, y)
				
				if _noise_value >= 40:
					if not x < width * .15 and not x > width * .85 and not y < height * .15 and not y > height * .85:
						_possible_camps.add((x, y))
				
				if random.uniform(0, 1) > .5:
					_possible_trees.add((x, y))
			
			elif _noise_value >= _low_grass - 10 and 10 * random.uniform(0, 1) > _low_grass-_noise_value:
				_tile = tiles.grass(x, y)
			
			else:
				_tile = tiles.rock(x, y)
				_solids.add((x, y))
			
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
	
	_trees = {}
	_tree_plots = _possible_trees - _solids - _river_tiles
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
	
	_ground_tiles = _ground_tiles - _solids
	_plot_pole_x, _plot_pole_y = width/2, height/2
	_bushes = random.sample(_ground_tiles, numbers.clip(int(round((width * height) * .0003)), 0, len(_ground_tiles)))
	_camps = set()
	
	while len(_possible_camps):
		_camp_1 = random.choice(list(_possible_camps))
		_possible_camps.remove(_camp_1)
		_camps.add(_camp_1)
		
		for camp_2 in _possible_camps.copy():
			_dist = numbers.distance(_camp_1, camp_2)
			
			if _dist <= 250:
				_possible_camps.remove(camp_2)
	
	for x, y in _bushes:
		_walker_x = x
		_walker_y = y
		_last_dir = -2, -2
		
		for i in range(random.randint(10, 15)):
			_tile = tiles.tree(_walker_x, _walker_y)
			_weight_map[_walker_y][_walker_x] = _tile['w']
			_tile_map[_walker_y][_walker_x] =_tile
			
			_dir = random.randint(-1, 1), random.randint(-1, 1)
			_n_x = _walker_x + _dir[0]
			_n_y = _walker_y + _dir[1]

			if _n_x < 0 or _n_y < 0 or _n_x >= width or _n_y >= height or (_n_x, _n_y) in _solids:
				break
			
			_last_dir = _dir[0] * -1, _dir[0] * -1
			_walker_x = _n_x
			_walker_y = _n_y
	
	_camp_info = {}
	
	for c_x, c_y in _camps:
		_building_walls = random.sample(['north', 'south', 'east', 'west'], random.randint(2, 3))
		_broken_walls = random.sample(_building_walls, numbers.clip(random.randint(0, 3), 0, len(_building_walls)))
		_camp = {'center': (c_x, c_y)}
		_camp_ground = []
		
		for y in range(-10, 10+1):
			for x in range(-10, 10+1):
				_x = x + c_x
				_y = y + c_y
				
				if (_x, _y) in _solids or (_x, _y) in _river_tiles:
					continue
				
				if (x == -10 and 'west' in _building_walls) or (y == -10 and 'north' in _building_walls) or (x == 10 and 'east' in _building_walls) or (y == 10 and 'south' in _building_walls):
					if x == -10 and 'west' in _building_walls and 'west' in _broken_walls and random.uniform(0, 1) > .75:
						continue
					
					if x == 10 and 'east' in _building_walls and 'east' in _broken_walls and random.uniform(0, 1) > .75:
						continue
					
					if y == -10 and 'north' in _building_walls and 'north' in _broken_walls and random.uniform(0, 1) > .75:
						continue
					
					if y == 10 and 'south' in _building_walls and 'south' in _broken_walls and random.uniform(0, 1) > .75:
						continue
					
					_tile = tiles.wooden_fence(_x, _y)
					_weight_map[_y][_x] = _tile['w']
					_tile_map[_y][_x] = _tile
					_solids.add((_x, _y))
				
				elif (x > -10 and x <= 10) and (y > -10 and y <= 10):
					_camp_ground.append((_x, _y))
		
		_camp['ground'] = _camp_ground[:]
		_camp_info[c_x, c_y] = _camp
	
	mapgen.build_node_grid(_node_grid, _solids)
	
	for c_x, c_y in _camps:
		mapgen.add_plot_pole(c_x, c_y, 40, _solids)
	
	_fsl = {'Runners': {'bases': 1, 'squads': 0, 'trader': False, 'type': life.human_runner}}
	#        #'Bandits': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit},
	#        'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl, _trees, _building_space - _walls