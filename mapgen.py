from framework import entities, display, events, numbers, shapes, tile, workers, flags

import libtcodpy as tcod

import buildinggen
import constants
import tiles
import life

import random
import time
import numpy

NODE_GRID = {}
UNCLAIMED_NODES = set()
NODE_SETS = {}
NODE_SET_ID = 1


def _create_node(x, y):
	_entity = entities.create_entity()
	
	flags.register(_entity)
	tile.register(_entity, surface='node_grid', fore_color=(255, 0, 255))
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'set_flag', flag='owner', value=None)
	entities.register_event(_entity, 'flag_changed', handle_node_flag_change)
	
	NODE_GRID[(x, y)] = _entity['_id']
	UNCLAIMED_NODES.add((x, y))

def handle_node_flag_change(entity, flag, value, last_value):
	if flag == 'owner':
		if value:
			entity['tile']['char'] = 'O'
			entity['tile']['fore_color'] = (255, 0, 0)
			
		else:
			entity['tile']['char'] = 'X'
			entity['tile']['fore_color'] = (255, 0, 255)

def _reset():
	global NODE_GRID
	global UNCLAIMED_NODES
	global NODE_SETS
	global NODE_SET_ID
	
	UNCLAIMED_NODES = set()
	NODE_GRID = {}
	NODE_SETS = {}
	NODE_SET_ID = 1

def build_node_grid(solids):
	global UNCLAIMED_NODES

	_ignore_positions = set()

	for x, y in solids:
		for _sy in range(y-5, y+6, 2):
			for _sx in range(x-5, x+6, 2):
				if (_sx, _sy) in _ignore_positions:
					continue

				if (_sx, _sy) in solids:
					continue

				_create_node(_sx, _sy)

				for _x, _y in [(_sx-1, _sy-1), (_sx, _sy-1), (_sx+1, _sy-1), (_sx-1, _sy), (_sx, _sy), (_sx-1, _sy+1), (_sx, _sy+1), (_sx+1, _sy+1)]:
					_ignore_positions.add((_x, _y))

def add_plot_pole(x, y, radius, solids, cell_split=3.0, debug=False):
	global NODE_SET_ID

	_node_set = set()
	_min_x = 999999999
	_max_x = 0
	_min_y = 999999999
	_max_y = 0

	for node_pos in list(UNCLAIMED_NODES):
		if numbers.distance((x, y), node_pos) > radius:
			continue
		
		if node_pos[0] < _min_x:
			_min_x = node_pos[0]
		
		if node_pos[0] > _max_x:
			_max_x = node_pos[0]
		
		if node_pos[1] < _min_y:
			_min_y = node_pos[1]
		
		if node_pos[1] > _max_y:
			_max_y = node_pos[1]

		_node_set.add(node_pos)
	
	_map = numpy.ones(((_max_y-_min_y)+1, (_max_x-_min_x)+1))
	
	for _x, _y in solids:
		if _x >= _max_x or _x <= _min_x or _y >= _max_y or _y <= _min_y:
			continue
		
		_map[int(round((_y-_min_y))), int(round((_x-_min_x)))] = -2

	NODE_SETS[NODE_SET_ID] = {'owner': None,
	                          'nodes': _node_set,
	                          'center': (x, y),
	                          'astar_map': _map,
	                          'min_x': _min_x,
	                          'min_y': _min_y,
	                          'cell_split': float(cell_split),
	                          'weight_map': numpy.ones(((_max_y-_min_y)+1, (_max_x-_min_x)+1), dtype=numpy.int16)}
	NODE_SET_ID += 1
	
	if debug:
		for y in range(_max_y-_min_y):
			for x in range(_max_x-_min_x):
				_val = int(round(_map[y, x]))
				
				if _val == -2:
					print '#',
				elif _val == 1:
					print '.',
			
			print

	return NODE_SET_ID-1

def create_map(width, height):
	_reset()
	
	_weight_map = numpy.ones((height, width), dtype=numpy.int16)
	_tile_map = []
	_solids = set()
	
	for y in range(height):
		_x = []

		for x in range(width):
			_x.append(None)

		_tile_map.append(_x)
	
	return _weight_map, _tile_map, _solids

def swamp(width, height):
	_weight_map, _tile_map, _solids = create_map(width, height)
	
	_c_x, _c_y = width/2, height/2
	_zoom = 1.2
	_noise = tcod.noise_new(3)
	_possible_trees = set()
	_built_on = set()
	
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
	
	_s_x, _s_y = ((width/2)-20, (height/2)-20)
	_room_size = 11
	_direction = random.choice(['east'])
	_width, _height = random.choice([(6, 6), (3, 6), (6, 3)])
	_building, _rooms = buildinggen.generate(_width, _height, _direction, ['trader_room'])

	for room in _rooms:
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
						_built_on.add((x, y))

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
			_min_y = _y

	_plot_pole_x, _plot_pole_y = int(round(numbers.clip(_min_x, _max_x, 0.05))), int(round(numbers.clip(_min_y, _max_y, 0.5)))
	_tree_plots = _possible_trees - _solids
	_tree_plots = list(_tree_plots - _built_on)
	_trees = {}
	_used_trees = random.sample(_tree_plots, numbers.clip(int(round((width * height) * .001)), 0, len(_tree_plots)))
	_bush_plots = set(_tree_plots) - set(_used_trees)
	_used_bush = random.sample(_bush_plots, numbers.clip(int(round((width * height) * .003)), 0, len(_bush_plots)))
	_swamp_plots = set(_tree_plots) - set(_used_bush)
	_used_swamp = random.sample(_swamp_plots, numbers.clip(int(round((width * height) * .003)), 0, len(_swamp_plots)))
	
	for x, y in _used_trees:
		_size = random.randint(7, 12)
		_trees[x, y] = _size
		
		for w in range(random.randint(2, 4)):
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

	build_node_grid(_solids)
	add_plot_pole(_plot_pole_x, _plot_pole_y, 40, _solids)
	
	_fsl = {'Runners': {'bases': 1, 'squads': 0, 'type': life.human_runner},
	        'Bandits': {'bases': 0, 'squads': 1, 'type': life.human_bandit}}
	
	return width, height, NODE_GRID.copy(), NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl, _trees, _built_on