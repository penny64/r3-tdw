from framework import entities, display, events, numbers, shapes, tile, workers, flags

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

def swamp(width, height, rings=8):
	_weight_map, _tile_map, _solids = create_map(width, height)
	
	_c_x, _c_y = width/2, height/2
	_bushes = set()
	_fences = set()

	for y in range(height):
		for x in range(width):
			if (1 < x < width-2 and y in [2, 3]) or (1 < x < width-2 and y in [height-3, height-4]) or (x in [2, 3] and 1 < y < height-2) or (x in [width-3, width-4] and 1 < y < height-2):
				_weight_map[y][x] = _tile['w']
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

						_weight_map[_y][_x] = _tile['w']
						_tile_map[_y][_x] = _tile
						_bushes.add((_x, _y))

					continue

				if random.uniform(random.uniform(.1, .2), 1) < _dist / float(max([height, width])):
					_tile = tiles.grass(x, y)

				else:
					_tile = tiles.swamp(x, y)

				_weight_map[y][x] = _tile['w']
				_tile_map[y][x] = _tile

			else:
				_weight_map[y][x] = _tile['w']
				_tile = tiles.swamp(x, y)
				_tile_map[y][x] = _tile

	_s_x, _s_y = (110, 110)
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
	        'Wild Dogs': {'bases': 0, 'squads': 1, 'type': life.wild_dog}}
	
	return width, height, NODE_GRID.copy(), NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl