from framework import numbers, shapes

import libtcodpy as tcod

import constants
import sculpted
import roomgen
import mapgen
import tiles
import life

import logging
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
	_room_size = 17
	_door_width = 1
	_place_x, _place_y = 5, 10
	_floor = set()
	_lights = []
	_spawns = {'defending': set(),
	           'attacking': set()}
	#_room_bitmask_maps = {}
	
	_min_door_pos = (_room_size / 2) - _door_width
	_max_door_pos = (_room_size / 2) + _door_width
	
	for y in range(_blueprint['height']):
		for x in range(_blueprint['width']):
			_o_bitmask = _blueprint['bitmask_map'][y, x]
			_bitmask = _blueprint['bitmask_map'][y, x]
			_door_bitmask = _blueprint['bitmask_door_map'][y, x]
			
			if not _bitmask:
				continue
			
			if _bitmask < 100:
				_bitmask += 100
			
			else:
				_room_name = _blueprint['room_lookup'][_blueprint['room_map'][y, x]]
				_wall_offset = 0 #Don't even think about touching this...
				_wall_padding = range(_blueprint['rooms'][_room_name]['wall_padding'] + 1)
				_wall_padding_actual = range(_wall_offset, _blueprint['rooms'][_room_name]['wall_padding'] + 1)
				_wall_padding_2_actual = [(_room_size-1) - i for i in range(_wall_offset, _blueprint['rooms'][_room_name]['wall_padding'] + 1)]
				_wall_padding_2 = [(_room_size-1) - i for i in range(_blueprint['rooms'][_room_name]['wall_padding'] + 1)]
				_wall_padding_3 = range(_blueprint['rooms'][_room_name]['doorway_padding'] + 1)
				_wall_padding_3_actual = range(_wall_offset, _blueprint['rooms'][_room_name]['doorway_padding'] + 1)
				_wall_padding_4 = [(_room_size-1) - i for i in range(_blueprint['rooms'][_room_name]['doorway_padding'] + 1)]
				_wall_padding_4_actual = [(_room_size-1) - i for i in range(_wall_offset, _blueprint['rooms'][_room_name]['doorway_padding'] + 1)]
				_wall_bitmask = 0
				
				logging.debug('Building: %s' % _room_name)
				
				if _o_bitmask > 100 and _o_bitmask < 200:
					_wall_bitmask = _o_bitmask
			
			for y1 in range(_room_size):
				for x1 in range(_room_size):
					_placed = False
					_p_x, _p_y = (x * _room_size) + x1, (y * _room_size) + y1
					
					if _o_bitmask > 100 and _o_bitmask < 200:
						if y1 in _wall_padding and not _bitmask in [101, 103, 105, 107, 109, 111, 113, 115]:
							if y1 in _wall_padding_actual:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
							
							_placed = True
						
						elif y1 in _wall_padding_2 and not _bitmask in [104, 105, 106, 107, 112, 113, 114, 115]:
							if y1 in _wall_padding_2_actual:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
							
							_placed = True
						
						if x1 in _wall_padding_2 and not _bitmask in [102, 103, 106, 107, 110, 111, 114, 115]:
							if x1 in _wall_padding_2_actual:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
							
							_placed = True
						
						elif x1 in _wall_padding and not _bitmask in [108, 109, 110, 111, 112, 113, 114, 115]:
							if x1 in _wall_padding_actual:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
							
							_placed = True
					
					else:
						if y1 == 0 and _bitmask in [101, 103, 105, 107, 109, 111, 113, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif y1 == _room_size - 1 and _bitmask in [104, 105, 106, 107, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						if x1 == _room_size - 1 and _bitmask in [102, 103, 106, 107, 110, 111, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
						
						elif x1 == 0 and _bitmask in [108, 109, 110, 111, 112, 113, 114, 115]:
							_solids.add((_place_x + _p_x, _place_y + _p_y))
							_placed = True
			
					if not _placed and _o_bitmask > 100 and not _door_bitmask:
						_floor.add((_place_x + _p_x, _place_y + _p_y, _room_name))
					
					elif _door_bitmask:
						_doorway_placed = False
						
						if y1 in _wall_padding_3 and _door_bitmask in [101, 103, 105, 107, 109, 111, 113, 115]:
							if x1 < _min_door_pos or x1 > _max_door_pos:
								#if x1 in _wall_padding_3_actual:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
								_doorway_placed = True
							
							elif (_place_x + _p_x, _place_y + _p_y) in _solids:
								_solids.remove((_place_x + _p_x, _place_y + _p_y))
						
						elif y1 in _wall_padding_4 and _door_bitmask in [104, 105, 106, 107, 112, 113, 114, 115]:
							if x1 < _min_door_pos or x1 > _max_door_pos:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
								_doorway_placed = True
							
							elif (_place_x + _p_x, _place_y + _p_y) in _solids:
								_solids.remove((_place_x + _p_x, _place_y + _p_y))
						
						if x1 in _wall_padding_4 and _door_bitmask in [102, 103, 106, 107, 110, 111, 114, 115]:
							if y1 < _min_door_pos or y1 > _max_door_pos:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
								_doorway_placed = True
							
							elif (_place_x + _p_x, _place_y + _p_y) in _solids:
								_solids.remove((_place_x + _p_x, _place_y + _p_y))
						
						elif x1 in _wall_padding_3 and _door_bitmask in [108, 109, 110, 111, 112, 113, 114, 115]:
							if y1 < _min_door_pos or y1 > _max_door_pos:
								_solids.add((_place_x + _p_x, _place_y + _p_y))
								_doorway_placed = True
							
							elif (_place_x + _p_x, _place_y + _p_y) in _solids:
								_solids.remove((_place_x + _p_x, _place_y + _p_y))
						
						if not _doorway_placed and not _placed:
							_floor.add((_place_x + _p_x, _place_y + _p_y, _room_name))
	
	_lookup = {(0, -1): 1,
	           (1, 0): 2,
	           (0, 1): 4,
	           (-1, 0): 8}		
	
	_new_floors, _new_solids, _windows, _new_lights, _new_spawns = roomgen.spawn_items(_blueprint['rooms'], _blueprint['bitmask_map'], _blueprint['bitmask_door_map'], _floor, _solids, _room_size, _room_size, (_place_x, _place_y), _tile_map, _weight_map)
	_floor_new = set()
	
	for x, y, room_name in _floor.copy():
		_floor_new.add((x, y))
	
	_spawns['defending'].update(_new_spawns)
	_spawns['attacking'].add((70, 5))
	_floor = _floor_new
	_floor.update(_new_floors)
	_solids.update(_new_solids)
	_remove_solids = set()
	_solids = _solids - _windows
	_lights.extend(_new_lights)
	
	for x, y in _solids:
		#_count = 0
		_delete = True
		
		for x1, y1 in [(0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
			_x = x + x1
			_y = y + y1
			
			if (_x, _y) in _floor:
				_delete = False
				#_count += 1
		
		if _delete:
			_remove_solids.add((x, y))
			_ground_tiles.add((x, y))
	
	_solids = _solids - _remove_solids

	for x in range(width):
		for y in range(height):
			if (x, y) in _solids:
				continue
			
			_ground_tiles.add((x, y))

	#This generates the outside walls	
	for pos in _solids:
		_tile = tiles.wooden_fence(pos[0], pos[1])
		_tile_map[pos[1]][pos[0]] = _tile
		_weight_map[pos[1]][pos[0]] = _tile['w']
	
	_ground_tiles = _ground_tiles - _windows
	
	for x, y in _ground_tiles - _floor:
		_tile = tiles.grass(x, y)
		_tile_map[y][x] = _tile
		_weight_map[y][x] = _tile['w']
	
	mapgen.build_node_grid(_node_grid, _solids)
	_floor.update(_windows)
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, {}, _trees, _floor, _lights, _spawns