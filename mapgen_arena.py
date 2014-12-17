from framework import numbers, shapes

import libtcodpy as tcod

import constants
import sculpted
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
	_blueprint = sculpted.create_blueprint(sculpted.ROOMS)
	_room_size = 11
	_place_x, _place_y = 0, 15
	_floor = set()
	
	for y in range(_blueprint['height']):
		for x in range(_blueprint['width']):
			_o_bitmask = _blueprint['bitmask_map'][y, x]
			_bitmask = _blueprint['bitmask_map'][y, x]
			
			if not _bitmask:
				continue
			
			if _bitmask < 100:
				_bitmask += 100
			
			for y1 in range(_room_size):
				for x1 in range(_room_size):
					_placed = False
					_p_x, _p_y = (x * _room_size) + x1, (y * _room_size) + y1
					
					if _o_bitmask > 100:
						if y1 == 0 and not _bitmask in [101, 103, 105, 107, 109, 111, 113, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif y1 == _room_size-1 and not _bitmask in [104, 105, 106, 117, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						if x1 == _room_size-1 and not _bitmask in [102, 103, 106, 107, 110, 111, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif x1 == 0 and not _bitmask in [108, 109, 110, 111, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
					
					else:
						if y1 == 0 and _bitmask in [101, 103, 105, 107, 109, 111, 113, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif y1 == _room_size-1 and _bitmask in [104, 105, 106, 117, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						if x1 == _room_size-1 and _bitmask in [102, 103, 106, 107, 110, 111, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif x1 == 0 and _bitmask in [108, 109, 110, 111, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
			
					if not _placed and _o_bitmask > 100:
						_floor.add((_place_x + _p_x, _place_y + _p_y))
	
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
	
	for x, y in _floor:
		_tile = tiles.concrete_striped(x, y)
		_tile_map[y][x] = _tile
		_weight_map[y][x] = _tile['w']
	
	mapgen.build_node_grid(_node_grid, _solids)
	
	#_fsl = {'Terrorists': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_runner, 'spawn_pos': (15, 50)},
	#        'Militia': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit, 'spawn_pos': (90, 50)}}
	#        'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, {}, _trees, _floor