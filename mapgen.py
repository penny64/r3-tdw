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
		for _sy in range(y-5, y+6):
			for _sx in range(x-5, x+6):
				if (_sx, _sy) in _ignore_positions:
					continue

				if not _sx % 3 and not _sy % 3:
					if (_sx, _sy) in solids:
						continue

					_create_node(_sx, _sy)

				_ignore_positions.add((_sx, _sy))

def add_plot_pole(x, y, radius):
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
	
	_map = numpy.zeros((_max_y-_min_y, _max_x-_min_x))
	_map -= 2
	
	for _x, _y in list(_node_set):
		_map[int(round((_y-_min_y)/3.0)), int(round((_x-_min_x)/3.0))] = 1

	NODE_SETS[NODE_SET_ID] = {'owner': None,
	                          'nodes': _node_set,
	                          'center': (x, y),
	                          'astar_map': _map,
	                          'min_x': _min_x,
	                          'min_y': _min_y,
	                          'weight_map': numpy.ones((_max_y-_min_y, _max_x-_min_x), dtype=numpy.int16)}
	NODE_SET_ID += 1

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
	
	for y in range(height):
		for x in range(width):
			_c_dist = numbers.float_distance((x, y), (_c_x, _c_y)) / float(max([width, height]))
			_noise_values = [(_zoom * x / (constants.MAP_VIEW_WIDTH)),
					         (_zoom * y / (constants.MAP_VIEW_HEIGHT))]
			_noise_value = numbers.clip(tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_SIMPLEX) - .7, .5-_c_dist, 1)
			
			if _noise_value > .3:
				_tile = tiles.grass(x, y)
				
			elif _noise_value > .2:
				if random.uniform(.2, .3) + (_noise_value-.2) > .3:
					if _c_dist < .35:
						_tile = tiles.grass(x, y)
					else:
						_tile = tiles.grass(x, y)
				else:
					#TODO: Slowly dither in swamp water
					if _c_dist < .35:
						_tile = tiles.swamp(x, y)
					else:
						_tile = tiles.swamp(x, y)
			
			elif _noise_value >= 0:
				_r_val = random.uniform(0, .2) + (_noise_value)
				
				if _r_val > .2:
					_tile = tiles.swamp(x, y)
				else:
					if random.uniform(0, .2) + (_noise_value) > .2:
						_tile = tiles.swamp_water(x, y)
					else:
						_tile = tiles.tall_grass(x, y)
			
			elif _noise_value < 0:
				_tile = tiles.tall_grass(x, y)
			
			else:
				_tile = tiles.swamp(x, y)
				
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
	
	_s_x, _s_y = ((width/2)-20, (height/2)-20)
	_room_size = 11
	_direction = random.choice(['east'])
	_width, _height = random.choice([(6, 6), (3, 6), (6, 3)])
	_building, _rooms = buildinggen.generate(_width, _height, _direction, ['living_room'])

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

	_plot_pole_x, _plot_pole_y = int(round(numbers.clip(_min_x, _max_x, 0.5))), int(round(numbers.clip(_min_y, _max_y, 0.5)))

	build_node_grid(_solids)
	add_plot_pole(_plot_pole_x, _plot_pole_y, 40)
	
	_fsl = {'Runners': {'bases': 1, 'squads': 0, 'type': life.human_runner},
	        'Bandits': {'bases': 0, 'squads': 1, 'type': life.human_bandit}}
	
	return width, height, NODE_GRID.copy(), NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl