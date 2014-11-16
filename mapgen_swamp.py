from framework import numbers

import libtcodpy as tcod

import constants
import mapgen
import tiles
import life

import random


def generate(width, height):
	_weight_map, _tile_map, _solids, _node_grid = mapgen.create_map(width, height)
	
	_c_x, _c_y = width/2, height/2
	_zoom = 1.2
	_noise = tcod.noise_new(3)
	_possible_trees = set()
	
	for y in range(height):
		for x in range(width):
			_c_dist = numbers.float_distance((x, y), (_c_x, _c_y)) / float(max([width, height]))
			_noise_values = [(_zoom * x / (constants.MAP_VIEW_WIDTH)),
					         (_zoom * y / (constants.MAP_VIEW_HEIGHT))]
			_noise_value = numbers.clip(tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_SIMPLEX) - .7, .5-_c_dist, 1)
			
			if _noise_value > .3:
				_tile = tiles.grass(x, y)
				_possible_trees.add((x, y))
				
			elif _noise_value > .2:
				if random.uniform(.2, .3) + (_noise_value-.2) > .3:
					if _c_dist < .35:
						_tile = tiles.grass(x, y)
						_possible_trees.add((x, y))
					else:
						_tile = tiles.grass(x, y)
						_possible_trees.add((x, y))
				else:
					#TODO: Slowly dither in swamp water
					if _c_dist < .35:
						_tile = tiles.swamp_water(x, y)
					else:
						_tile = tiles.swamp_water(x, y)
			
			elif _noise_value >= 0:
				_r_val = random.uniform(0, .2) + (_noise_value)
				
				if _r_val > .2:
					_tile = tiles.swamp_water(x, y)
				else:
					if random.uniform(0, .2) + (_noise_value) > .2:
						_tile = tiles.swamp_water(x, y)
					else:
						_tile = tiles.tall_grass(x, y)
			
			elif _noise_value < 0:
				_tile = tiles.tall_grass(x, y)
				_possible_trees.add((x, y))
			
			else:
				_tile = tiles.swamp(x, y)
				
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
	
	#############
	#Trader camp#
	#############
	
	_s_x, _s_y = ((width/2)-20, (height/2)-20)
	_building_space = set()
	_walls = set()
	
	#Building
	_width, _height = random.choice([(20, 20), (12, 20), (20, 12)])
	_random_dir = random.randint(0, 3)
	
	if _random_dir == 1:
		_door_x = _width / 2
		_door_y = 0
	
	elif _random_dir == 2:
		_door_x = _width / 2
		_door_y = _height
	
	elif _random_dir == 3:
		_door_x = 0
		_door_y = _height / 2
	
	else:
		_door_x = _width
		_door_y = _height / 2
	
	if _width > _height:
		if _random_dir in [1, 3]:
			_mod = .75
		else:
			_mod = .25
		
		_trade_room_x = int(round(_width * _mod))
		_trade_room_y = -1
		_trade_window_x = _trade_room_x
		_trade_window_y = _height / 2
	else:
		if _random_dir == 1:
			_mod = .75
		else:
			_mod = .25
		
		_trade_room_x = -1
		_trade_room_y = int(round(_height * _mod))
		_trade_window_x = _width / 2
		_trade_window_y = _trade_room_y
	
	for y in range(_height+1):
		_y = _s_y+y
		
		for x in range(_width+1):
			_x = _s_x+x
			
			if (x, y) == (_door_x, _door_y):
				_tile = tiles.concrete(_x, _y)
			
			elif x == 0 or y == 0 or x == _width or y == _height:
				_tile = tiles.wooden_fence(_x, _y)
				_solids.add((_x, _y))
				_walls.add((_x, _y))
			
			else:
				if x == _trade_window_x and y == _trade_window_y:
					_tile = tiles.trade_window(_x, _y)
					
				elif x == _trade_room_x or y == _trade_room_y:
					_tile = tiles.wooden_fence(_x, _y)
					_solids.add((_x, _y))
					_walls.add((_x, _y))
				
				else:
					_tile = tiles.wood_floor(_x, _y)
			
			_weight_map[_y][_x] = _tile['w']
			_tile_map[_y][_x] = _tile
			_building_space.add((_x, _y))
	
	#Wall
	_width, _height = _width * 4, _height * 4
	_ground_space = set()
	
	for y in range(_height + 1):
		_y = _s_y + y
		_yy = _y - int(round(_height * .4))
		
		for x in range(_width + 1):
			_x = _s_x + x
			_xx = _x - int(round(_width * .4))
			
			if random.uniform(0, 1) >= .75:
				continue
			
			if x == 0 or y == 0 or x == _width or y == _height:
				_tile = tiles.wooden_fence(_xx, _yy)
			else:
				if (_xx, _yy) in _building_space:
					continue
				
				_ground_space.add((_xx, _yy))
				
				continue
			
			_weight_map[_yy][_xx] = _tile['w']
			_tile_map[_yy][_xx] = _tile
			_solids.add((_xx, _yy))
	
	#Ground: Inside wall - outside building
	_ground_seeds = random.sample(list(_ground_space - _building_space), 50)
	
	for x, y in _ground_seeds:
		_walker_x = x
		_walker_y = y
		_last_dir = -2, -2
		
		for i in range(random.randint(80, 90)):
			_tile = tiles.concrete_striped(_walker_x, _walker_y)
			_weight_map[_walker_y][_walker_x] = _tile['w']
			_tile_map[_walker_y][_walker_x] =_tile
			
			_dir = random.randint(-1, 1), random.randint(-1, 1)
			_n_x = _walker_x + _dir[0]
			_n_y = _walker_y + _dir[1]
			
			while (_n_x, _n_y) in _building_space or (_n_x, _n_y) in _solids or _last_dir == _dir:
				_dir = random.randint(-1, 1), random.randint(-1, 1)
				_n_x = _walker_x + _dir[0]
				_n_y = _walker_y + _dir[1]
			
			_last_dir = _dir[0] * -1, _dir[0] * -1
			_walker_x = _n_x
			_walker_y = _n_y
	
	#Bushes around outside wall
	
	#Campfires

	"""for room in _rooms:
		_build_doors = []

		for plot_x, plot_y in room['plots']:
			_room = _building[(plot_x, plot_y)]
			_build_walls = ['north', 'south', 'east', 'west']

			for n_plot_x, n_plot_y in [(plot_x-1, plot_y), (plot_x+1, plot_y), (plot_x, plot_y-1), (plot_x, plot_y+1)]:
				if ((n_plot_x, n_plot_y) == _room['door_plot']) or (not _build_doors and not (n_plot_x, n_plot_y) in room['plots'] and (n_plot_x, n_plot_y) in _building):
					if n_plot_x - plot_x == -1:
						_build_doors.append('west')

						if 'west' in _build_walls:
							_build_walls.remove('west')

					elif n_plot_x - plot_x == 1:
						_build_doors.append('east')

						if 'east' in _build_walls:
							_build_walls.remove('east')

					if n_plot_y - plot_y == -1:
						_build_doors.append('north')

						if 'north' in _build_walls:
							_build_walls.remove('north')

					elif n_plot_y - plot_y == 1:
						_build_doors.append('south')

						if 'south' in _build_walls:
							_build_walls.remove('south')

				if (n_plot_x, n_plot_y) in _building:
					if n_plot_x - plot_x == -1 and not _building[(n_plot_x, n_plot_y)]['type'] in buildinggen.ROOM_TYPES[room['type']]['avoid_rooms']:
						if 'west' in _build_walls:
							_build_walls.remove('west')

					elif n_plot_x - plot_x == 1 and not _building[(n_plot_x, n_plot_y)]['type'] in buildinggen.ROOM_TYPES[room['type']]['avoid_rooms']:
						if 'east' in _build_walls:
							_build_walls.remove('east')

					if n_plot_y - plot_y == -1 and not _building[(n_plot_x, n_plot_y)]['type'] in buildinggen.ROOM_TYPES[room['type']]['avoid_rooms']:
						if 'north' in _build_walls:
							_build_walls.remove('north')

					elif n_plot_y - plot_y == 1 and not _building[(n_plot_x, n_plot_y)]['type'] in buildinggen.ROOM_TYPES[room['type']]['avoid_rooms']:
						if 'south' in _build_walls:
							_build_walls.remove('south')

			_x, _y = (_s_x + (plot_x*_room_size)), (_s_y + (plot_y*_room_size))

			for y in range(_y, _y+_room_size):
				for x in range(_x, _x+_room_size):
					if ((x-_x == 0 and 'west' in _build_walls) or (y-_y == 0 and 'north' in _build_walls) or (x-_x == _room_size-1 and 'east' in _build_walls) or (y-_y == _room_size-1 and 'south' in _build_walls)):
						_weight_map[y][x] = _tile['w']
						_tile_map[y][x] = tiles.wooden_fence(x, y)
						_solids.add((x, y))

					else:
						_tile_map[y][x] = buildinggen.ROOM_TYPES[room['type']]['tiles'](x, y)
						_building_space.add((x, y))

			for y in range(_y, _y+_room_size):
				for x in range(_x-1, _x+_room_size+1):
					if (x-_x in [-1, 0] and 'west' in _build_doors and (y-_y<=2 or y-_y>=_room_size-3)) or (x-_x in [_room_size, _room_size+1] and 'east' in _build_doors and (y-_y<=2 or y-_y>=_room_size-3)):
						_weight_map[y][x] = _tile['w']
						_tile_map[y][x] = tiles.wooden_fence(x, y)

						_solids.add((x, y))

			for y in range(_y-1, _y+_room_size+1):
				for x in range(_x, _x+_room_size):
					if (y-_y in [-1, 0] and 'north' in _build_doors and (x-_x<=2 or x-_x>=_room_size-3)) or (y-_y in [_room_size, _room_size+1] and 'south' in _build_doors and (x-_x<=2 or x-_x>=_room_size-3)):
						_weight_map[y][x] = _tile['w']
						_tile_map[y][x] = tiles.wooden_fence(x, y)
						_solids.add((x, y))

			_last_plot_x, _last_plot_y = plot_x, plot_y

	#TODO: Make this into a function?
	_min_x, _max_x = (width, 0)
	_min_y, _max_y = (height, 0)

	for x, y in _building:
		_x, _y = (_s_x + (x*_room_size)), (_s_y + (y*_room_size))

		if _x > _max_x:
			_max_x = _x

		if _x < _min_x:
			_min_x = _x

		if _y > _max_y:
			_max_y = _y

		if _y < _min_y:
			_min_y = _y"""

	_plot_pole_x, _plot_pole_y = _s_x, _s_y
	_tree_plots = _possible_trees - _solids
	_tree_plots = list(_tree_plots - _building_space)
	_trees = {}
	_used_trees = random.sample(_tree_plots, numbers.clip(int(round((width * height) * .001)), 0, len(_tree_plots)))
	_bush_plots = set(_tree_plots) - set(_used_trees)
	_used_bush = random.sample(_bush_plots, numbers.clip(int(round((width * height) * .003)), 0, len(_bush_plots)))
	_swamp_plots = set(_tree_plots) - set(_used_bush)
	_used_swamp = random.sample(_swamp_plots, numbers.clip(int(round((width * height) * .003)), 0, len(_swamp_plots)))
	
	for x, y in _used_trees:
		_size = random.randint(7, 12)
		_trees[x, y] = _size
		
		for w in range(random.randint(1, 2)):
			_walker_x = x
			_walker_y = y
			_walker_direction = random.randint(0, 359)
			
			for i in range(random.randint(_size/4, _size/2)):
				_actual_x, _actual_y = int(round(_walker_x)), int(round(_walker_y))
				
				if _actual_x < 0 or _actual_y < 0 or _actual_x >= width or _actual_y >= height or (_actual_x, _actual_y) in _solids:
					break
				
				_center_mod = numbers.float_distance((_actual_x, _actual_y), (x, y)) / float(_size)
				_tile = tiles.tree(_actual_x, _actual_y)
				_weight_map[_actual_y][_actual_x] = _tile['w']
				_tile_map[_actual_y][_actual_x] = _tile
				
				if random.randint(0, 3):
					_trees[_actual_x, _actual_y] = random.randint(1, _size)
				
				_solids.add((_actual_x, _actual_y))
				_walker_direction += random.randint(-45, 45)
				_n_x, _n_y = numbers.velocity(_walker_direction, 1)
				
				_walker_x += _n_x
				_walker_y += _n_y
	
	for x, y in _used_bush:
		_center_mod = numbers.float_distance((x, y), (_plot_pole_x, _plot_pole_y)) / 60.0
		_walker_x = x
		_walker_y = y
		
		for i in range(int(round(random.randint(44, 55) * _center_mod))):
			_tile = tiles.swamp_water(_walker_x, _walker_y)
			_weight_map[_walker_y][_walker_x] = _tile['w']
			_tile_map[_walker_y][_walker_x] =_tile
			
			_walker_x += random.randint(-1, 1)
			_walker_y += random.randint(-1, 1)
			
			if _walker_x < 0 or _walker_y < 0 or _walker_x >= width or _walker_y >= height or (_walker_x, _walker_y) in _solids:
				break
	
	for x, y in _used_swamp:
		_center_mod = numbers.float_distance((x, y), (_plot_pole_x, _plot_pole_y)) / 120.0
		_walker_x = x
		_walker_y = y
		
		for i in range(int(round(random.randint(44, 55) * (1-_center_mod)))):
			_tile = tiles.swamp(_walker_x, _walker_y)
			_weight_map[_walker_y][_walker_x] = _tile['w']
			_tile_map[_walker_y][_walker_x] =_tile
			
			_walker_x += random.randint(-1, 1)
			_walker_y += random.randint(-1, 1)
			
			if _walker_x < 0 or _walker_y < 0 or _walker_x >= width or _walker_y >= height or (_walker_x, _walker_y) in _solids:
				break

	mapgen.build_node_grid(_node_grid, _solids)
	mapgen.add_plot_pole(_plot_pole_x, _plot_pole_y, 40, _solids)
	
	_fsl = {'Terrorists': {'bases': 1, 'squads': 0, 'trader': True, 'type': life.human_runner},
	        'Militia': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit}}
	#'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl, _trees, _building_space - _walls