import items
import tiles

import numpy


def neighbors_in_set(x, y, check_set, diag=False):
	_return_set = set()
	_mods = [(0, -1), (1, 0), (0, 1), (-1, 0)]
	
	if diag:
		_mods.extend([(-1, 1), (1, 1), (-1, -1), (1, -1)])
	
	for x1, y1 in _mods:
		_neighbor_x, _neighbor_y = x + x1, y + y1
		
		if (_neighbor_x, _neighbor_y) in check_set:
			_return_set.add((_neighbor_x, _neighbor_y))
	
	return _return_set

def neighbors_in_all_sets(x, y, check_sets, diag=False):
	_return_set = set()
	_mods = [(0, -1), (1, 0), (0, 1), (-1, 0)]
	
	if diag:
		_mods.extend([(-1, 1), (1, 1), (-1, -1), (1, -1)])
	
	for x1, y1 in _mods:
		_neighbor_x, _neighbor_y = x + x1, y + y1
		_not_in_set = True
		
		for check_set in check_sets:
			if not (_neighbor_x, _neighbor_y) in check_set:
				_not_in_set = False
				
				break
		
		if _not_in_set:
			_return_set.add((_neighbor_x, _neighbor_y))
	
	return _return_set

def neighbors_in_any_sets(x, y, check_sets, diag=False):
	_return_set = set()
	_mods = [(0, -1), (1, 0), (0, 1), (-1, 0)]
	
	if diag:
		_mods.extend([(-1, 1), (1, 1), (-1, -1), (1, -1)])
	
	for x1, y1 in _mods:
		_neighbor_x, _neighbor_y = x + x1, y + y1
		
		for check_set in check_sets:
			if (_neighbor_x, _neighbor_y) in check_set:
				_return_set.add((_neighbor_x, _neighbor_y))
				
				break
	
	return _return_set

def spawn_items(room_list, bitmask_map, bitmask_door_map, floor_list, solids, room_size, divisor, offsets, tile_map, weight_map):
	_item_positions = set()
	_placed_map = numpy.zeros((room_size, room_size))
	_room_spawns = {}
	_floors = set()
	_solids = set()
	
	for x, y, room_name in floor_list:
		_r_x, _r_y = (x - offsets[0]) / divisor, (y - offsets[1]) / divisor
		_room = room_list[room_name]
		_room_x, _room_y = (x / room_size) * room_size, (y / room_size) * room_size
		
		if not room_name in _room_spawns:
			_room_spawns[room_name] = {}
		
		if not (_r_x, _r_y) in _room_spawns[room_name]:
			_room_spawns[room_name][_r_x, _r_y] = {'against_wall': set(),
			                                       'away_from_wall': set(),
			                                       'floor': set()}
			
		
		_spawn_list = _room_spawns[room_name][_r_x, _r_y]
		_hit_solid = False
		
		for x1, y1 in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
			_neighbor_x, _neighbor_y = x + x1, y + y1
			
			if _neighbor_x < _room_x or _neighbor_x >= _room_x + room_size or _neighbor_y < _room_y or _neighbor_y >= _room_y + room_size:
				continue
			
			if (_neighbor_x, _neighbor_y) in solids:
				_spawn_list['against_wall'].add((x, y))
				_hit_solid = True
		
		if not _hit_solid:
			_spawn_list['away_from_wall'].add((x, y))
		
		_spawn_list['floor'].add((x, y))
	
	for room_name in _room_spawns:
		_rooms = _room_spawns[room_name]
		
		for r_x, r_y in _rooms:
			_wall_bitmask = bitmask_map[r_y, r_x]
			_spawns = _rooms[r_x, r_y]
			
			if room_name == 'Bunks':
				print 'Spawn here:', _wall_bitmask
				
				if _wall_bitmask in [105]:
					for x, y in _spawns['against_wall']:
						if not y % 4:
							_solids.add((x, y))
							
							for x1, y1 in list(neighbors_in_any_sets(x, y, [_spawns['against_wall'], _spawns['away_from_wall']])):
								if (x1, y1) in _item_positions:
									continue
								
								_solids.add((x1, y1))
				
				elif _wall_bitmask in [110]:
					for x, y in _spawns['against_wall']:
						if not x % 4:
							_solids.add((x, y))
							
							for x1, y1 in list(neighbors_in_any_sets(x, y, [_spawns['against_wall'], _spawns['away_from_wall']])):
								if (x1, y1) in _item_positions:
									continue
								
								_solids.add((x1, y1))
			
			_floor_tiles = _spawns['floor'] - _solids
			
			for x, y in list(_floor_tiles):
				_tile = room_list[room_name]['tile'](x, y)
				tile_map[y][x] = _tile
				weight_map[y][x] = _tile['w']
			
			for x, y in list(_solids):
				_tile = tiles.wooden_fence(x, y)
				tile_map[y][x] = _tile
				weight_map[y][x] = _tile['w']
			
			_floors.update(_floor_tiles)
	
	return _floors, _solids
