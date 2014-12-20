import items

import numpy


def spawn_items(room_list, floor_list, solids, room_size):
	_item_positions = set()
	_placed_map = numpy.zeros((room_size, room_size))
	_against_wall = set()
	
	for x, y, room_name in floor_list:
		_room = room_list[room_name]
		_room_x, _room_y = (x / room_size) * room_size, (y / room_size) * room_size
		
		for x1, y1 in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
			_neighbor_x, _neighbor_y = x + x1, y + y1
			
			if _neighbor_x < _room_x or _neighbor_x >= _room_x + room_size or _neighbor_y < _room_y or _neighbor_y >= _room_y + room_size:
				continue
			
			if (_neighbor_x, _neighbor_y) in solids:
				_against_wall.add((x, y))
	
	for x, y in _against_wall:
		items.ammo_9x19mm(x, y)
		_item_positions.add((x, y))
	
	
	return _item_positions
