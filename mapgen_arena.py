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
	_river_direction = 270
	_turn_rate = random.randint(-1, 1)
	_river_tiles = set()
	_river_size = random.randint(7, 10)
	_ground_tiles = set()
	_possible_camps = set()
	_trees = {}
	_num_walls = 10
	
	for i in range(_num_walls):
		_x = random.randint(int(round(width * .15)), int(round(width * .85)))
		_y = random.randint(int(round(height * .15)), int(round(height * .85)))
		
		for pos in shapes.circle(_x, _y, random.randint(7, 10)):
			#_tile = tiles.wooden_fence(pos[0], pos[1])
			#_tile_map[pos[1]][pos[0]] = _tile
			#_weight_map[pos[1]][pos[0]] = _tile['w']
			_solids.add((pos[0], pos[1]))
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _solids:
				continue
			
			#_tile = tiles.grass(x, y)
			#_tile_map[y][x] = _tile
			#_weight_map[y][x] = _tile['w']
			_ground_tiles.add((x, y))
	
	_lookup = {(0, -1): 1,
	           (1, 0): 2,
	           (0, 1): 4,
	           (-1, 0): 8}
	_tile_type = {}
	
	for x, y in _ground_tiles.copy():
		_count = 0
				
		for x1, y1 in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
			_x = x + x1
			_y = y + y1
			
			if (_x, _y) in _solids:
				_count += 1
		
		if _count >= 4:
			_solids.add((x, y))
			
			if (x, y) in list(_ground_tiles):
				_ground_tiles.remove((x, y))		
	
	for x, y in _solids:#_ground_tiles.copy():
		_count = 0
		
		for x1, y1 in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
			_x = x + x1
			_y = y + y1
			
			if (_x, _y) in _solids:
				_count += _lookup[x1, y1]
		
		_tile_type[x, y] = _count
	
	for pos in _solids:
		_type = _tile_type[pos]
		_tile = tiles.wooden_fence(pos[0], pos[1])
		
		if _type in [11, 14]: # left - right
			_tile['c'] = chr(196)
			_tile['c_f'] = (200, 200, 200)
		
		elif _type == 6: # top left
			_tile['c'] = chr(218)
			_tile['c_f'] = (200, 200, 200)
		
		elif _type in [7, 13]: # top - bottom
			_tile['c'] = chr(179)
			_tile['c_f'] = (200, 200, 200)
		
		elif _type == 12: # top right
			_tile['c'] = chr(187)
			_tile['c_f'] = (200, 200, 200)
		
		elif _type == 3: # bottom left
			_tile['c'] = chr(192)
			_tile['c_f'] = (200, 200, 200)
		
		elif _type == 9: # bottom right
			_tile['c'] = chr(188)
			_tile['c_f'] = (200, 200, 200)
		
		_tile_map[pos[1]][pos[0]] = _tile
		_weight_map[pos[1]][pos[0]] = _tile['w']
	
	for x, y in _ground_tiles:
		_tile = tiles.grass(x, y)
		_tile_map[y][x] = _tile
		_weight_map[y][x] = _tile['w']
	
	mapgen.build_node_grid(_node_grid, _solids)
	
	#_fsl = {'Terrorists': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_runner, 'spawn_pos': (15, 50)},
	#        'Militia': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit, 'spawn_pos': (90, 50)}}
	#        'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, {}, _trees, _building_space - _walls