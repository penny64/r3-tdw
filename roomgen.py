from framework import entities

import effects
import items
import tiles

import random
import numpy


def get_corner_points(spawns):
	return [(spawns['min_x'] + 1, spawns['min_y'] + 1),
	        (spawns['min_x'] + spawns['width'] - 2, spawns['min_y'] + 1),
	        (spawns['min_x'] + 1, spawns['min_y'] + spawns['height'] - 2),
	        (spawns['max_x'] - 2, spawns['max_y'] - 2)]

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
	_windows = set()
	_lights = []
	_spawn_positions = set()
	
	for x, y, room_name in floor_list:
		_r_x, _r_y = (x - offsets[0]) / divisor, (y - offsets[1]) / divisor
		_room = room_list[room_name]
		_room_x, _room_y = (x / room_size) * room_size, (y / room_size) * room_size
		
		if not room_name in _room_spawns:
			_room_spawns[room_name] = {}
		
		if not (_r_x, _r_y) in _room_spawns[room_name]:
			_room_spawns[room_name][_r_x, _r_y] = {'against_wall': set(),
			                                       'away_from_wall': set(),
			                                       'floor': set(),
			                                       'direction': None,
			                                       'width': 0,
			                                       'height': 0,
			                                       'min_x': 9999,
			                                       'max_x': 0,
			                                       'min_y': 9999,
			                                       'max_y': 0}
			
		
		_spawn_list = _room_spawns[room_name][_r_x, _r_y]
		_hit_solid = False
		
		if x < _spawn_list['min_x']:
			_spawn_list['min_x'] = x
		
		if x > _spawn_list['max_x']:
			_spawn_list['max_x'] = x
		
		if y < _spawn_list['min_y']:
			_spawn_list['min_y'] = y
		
		if y > _spawn_list['max_y']:
			_spawn_list['max_y'] = y
		
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
		#_min_x = 9999
		#_max_x = 0
		#_min_y = 9999
		#_max_y = 0
		
		for r_x, r_y in _rooms:
			_spawns = _rooms[r_x, r_y]
			_spawns['width'] = _spawns['max_x'] - _spawns['min_x']
			_spawns['height'] = _spawns['max_y'] - _spawns['min_y']
			
			if _spawns['width'] > _spawns['height']:
				_spawns['direction'] = 'horizontal'
			
			else:
				_spawns['direction'] = 'vertical'
			
			#if _spawns['min_x'] < _min_x:
			#	_min_x = _spawns['min_x']
			
			#if _spawns['min_y'] < _min_y:
			#	_min_y = _spawns['min_y']
			
			#if _spawns['max_x'] > _max_x:
			#	_max_x = _spawns['max_x']
			
			#if _spawns['max_y'] > _max_y:
			#	_max_y = _spawns['max_y']
		
		#_width_of_all_rooms = _max_x - _min_x
		#height_of_all_rooms = _max_y - _min_y
	
	for room_name in _room_spawns:
		_rooms = _room_spawns[room_name]
		
		for r_x, r_y in _rooms:
			_wall_bitmask = bitmask_map[r_y, r_x]
			_door_bitmask = bitmask_door_map[r_y, r_x]
			_spawns = _rooms[r_x, r_y]
			_new_floor = set()
			
			if room_name == 'bunks':
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
			
			elif room_name == 'landing':
				_carpet = set()
				
				for x, y in _spawns['floor']:
					_xx = x - _spawns['min_x']
					_yy = y - _spawns['min_y']
					
					if _xx == _spawns['width'] / 2 and _yy == _spawns['height'] / 2:
						_lights.append((x, y, 16, 1.5, 1.5, 1.5))
					
					if _spawns['width'] * .15 < _xx < _spawns['width'] * .85 and _spawns['height'] * .15 < _yy < _spawns['height'] * .85:
						if _xx < _spawns['width'] * .3 or _xx > _spawns['width'] * .7 or _yy < _spawns['height'] * .3 or _yy > _spawns['height'] * .7:
							if random.uniform(0, 1) > .5:
								_tile = tiles.carpet_light_blue(x, y)
								_carpet.add((x, y))
							
							else:
								_tile = tiles.carpet_blue(x, y)
								_carpet.add((x, y))
						
						else:
							_tile = tiles.carpet_burgandy_specs(x, y)
							_carpet.add((x, y))
					
					elif _spawns['width'] * .10 < _xx < _spawns['width'] * .90 and _spawns['height'] * .10 < _yy < _spawns['height'] * .90:
						_tile = tiles.carpet_burgandy(x, y)
						_carpet.add((x, y))
					
					else:
						_tile = tiles.carpet_brown(x, y)
					
					tile_map[y][x] = _tile
					weight_map[y][x] = _tile['w']
					
					_new_floor.add((x, y))
				
				#Placing tables
				_placed_tables = set()
				
				for x, y in _spawns['against_wall']:
					if neighbors_in_set(x, y, [_carpet]):
						continue
					
					if random.uniform(0, 1) > .87:
						if neighbors_in_set(x, y, _placed_tables):
							continue
						
						_neighbors = neighbors_in_set(x, y, _spawns['against_wall'])
						
						if len(_neighbors) >= 2:
							_neighbors.add((x, y))
							_placed_tables.add(tuple(_neighbors))
				
				_windows_placed = 0
				
				for table in _placed_tables:
					_temp_windows = set()
					
					for x, y in table:
						_tile = tiles.countertop(x, y)
						tile_map[y][x] = _tile
						weight_map[y][x] = _tile['w']
						
						_wood_blocks = set()
						_new_floor.add((x, y))
						
						for x1, y1 in neighbors_in_set(x, y, _spawns['floor'], diag=True) - neighbors_in_set(x, y, table, diag=True):
							_tile = tiles.wood_block(x1, y1)
							tile_map[y1][x1] = _tile
							weight_map[y1][x1] = _tile['w']
							
							_new_floor.add((x1, y1))
							_wood_blocks.add((x1, y1))
						
						if _windows_placed > 2:
							continue
						
						for x1, y1 in neighbors_in_set(x, y, solids, diag=True):
							_temp_windows.add((x1, y1))
					
					_windows_placed += 1
					
					for x, y in _temp_windows:
						pass
						#if neighbors_in_set(x, y, solids) - neighbors_in_set(x, y, _temp_windows):
						#	break
					else:
						for x, y in _temp_windows:
							_tile = tiles.water(x, y)
							tile_map[y][x] = _tile
							weight_map[y][x] = _tile['w']
						
						_windows.update(_temp_windows)
			
			elif room_name == 'hall':
				#for x, y in _spawns['floor']:
				if _door_bitmask:
					_xx = _spawns['min_x'] + int(round((_spawns['width'] * .5))) - 1
					_yy = _spawns['min_y'] + int(round((_spawns['height'] * .5))) - 1
					
					for x1, y1 in [(0, 0), (1, 0), (0, 1), (1, 1)]:
						_solids.add((_xx + x1, _yy + y1))
				
				else:
					for x, y in [(_spawns['min_x'] + 2, _spawns['min_y'] + 2),
					             (_spawns['min_x'] + 2, _spawns['min_y'] + _spawns['height'] - 3)]:
						for x1, y1 in [(0, 0), (1, 0), (0, 1), (1, 1)]:
							_solids.add((x + x1, y + y1))
			
			elif room_name == 'lab':
				#_x_split = 0
				#_y_split = 0
				
				#print _spawns['direction'], r_x, r_y
				#if _spawns['direction'] == 'horizontal':
				#	_start_x_dist_split = 6
				#	_start_y_dist_split = 4
				
				#else:
				#	_start_x_dist_split = 4
				#	_start_y_dist_split = 5
				
				#for dist_split in range(_start_x_dist_split, 9):
				#	if not _spawns['width'] % (dist_split):
				#		_x_split = dist_split
				#		
				#		break
				
				
				#for dist_split in range(_start_y_dist_split, 9):
				#	if not _spawns['height'] % (dist_split):
				#		_y_split = dist_split
				#		
				#		break
				
				for x, y in get_corner_points(_spawns):
					for m_x, m_y in [(0, 0), (1, 0), (0, 1), (1, 1)]:
						_x = x + m_x
						_y = y + m_y
						
						_tile = tiles.carpet_burgandy(_x, _y)
						tile_map[_y][_x] = _tile
						weight_map[_y][_x] = _tile['w']
						_new_floor.add((_x, _y))
			
			_floor_tiles = _spawns['floor'] - _solids
			_floor_tiles = _floor_tiles - _new_floor
			
			for x, y in list(_floor_tiles):
				_tile = room_list[room_name]['tile'](x, y)
				tile_map[y][x] = _tile
				weight_map[y][x] = _tile['w']
				_spawn_positions.add((x, y))
			
			for x, y in list(_solids):
				_tile = tiles.wooden_fence(x, y)
				tile_map[y][x] = _tile
				weight_map[y][x] = _tile['w']
			
			_floors.update(_floor_tiles)
	
	return _floors, _solids, _windows, _lights, _spawn_positions
