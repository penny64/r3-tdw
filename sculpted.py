import random
import numpy

#For bitmasking
LOOKUP = {(0, -1): 1,
          (1, 0): 2,
          (0, 1): 4,
          (-1, 0): 8}


_landing = {'name': 'landing',
            'size': 1,
            'rules': {'banned_neighbors': ['bathroom'],
                      'entry_room': True}}

_kitchen = {'name': 'kitchen',
            'size': 2,
            'rules': {'banned_neighbors': [],
                      'entry_room': False}}

_bathroom = {'name': 'bathroom',
             'size': 1,
             'rules': {'banned_neighbors': ['landing'],
                       'entry_room': False}}

ROOMS = {_landing['name']: _landing,
         _kitchen['name']: _kitchen,
         _bathroom['name']: _bathroom}


def create_blueprint(room_list):
	_total_room_size = 0
	_bitmask_map = None
	_room_id_map = None
	_potential_start_rooms = []
	_room_pool = []
	_room_lookup = {}
	_room_reverse_lookup = {}
	_room_id_counter = 1
	
	for room_name in room_list:
		_room = room_list[room_name]
		_total_room_size += _room['size']
		_room_pool.append(room_name)
		_room_lookup[_room_id_counter] = room_name
		_room_reverse_lookup[room_name] = _room_id_counter
		_room_id_counter += 1
		
		if _room['rules']['entry_room']:
			_potential_start_rooms.append(room_name)
	
	if not _potential_start_rooms:
		raise Exception('No defined start rooms.')
		
	_bitmask_map = numpy.zeros((_total_room_size, _total_room_size))
	_room_id_map = numpy.zeros((_total_room_size, _total_room_size))
	_width, _height = _total_room_size, _total_room_size
	
	#Pick an entry point - can be keyword arg at some point
	_current_room_name = random.choice(_potential_start_rooms)
	_placer_x, _placer_y = random.randint(0, _width-1), 0
	_potential_next_positions = set([(_placer_x, _placer_y)])
	
	while _room_pool:
		_room_pool.remove(_current_room_name)
		_room_rules = room_list[_current_room_name]['rules']
		_room_id = _room_reverse_lookup[_current_room_name]
		
		while 1:
			_placer_x, _placer_y = random.choice(list(_potential_next_positions))
			_fail_bad_neighbor = False
			_potential_potential_next_positions = set()
			
			#Required/banned neighbor check
			for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
				_neighbor_x = _placer_x + x_mod
				_neighbor_y = _placer_y + y_mod
				
				if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
					continue
				
				_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
				
				if not _neighbor_id:
					_potential_potential_next_positions.add((_neighbor_x, _neighbor_y))
					
					continue
				
				_neighbor_room_name = _room_lookup[_neighbor_id]
				
				if _neighbor_room_name in _room_rules['banned_neighbors']:
					_fail_bad_neighbor = True
					
					break
			
			if not _fail_bad_neighbor:
				_potential_next_positions.remove((_placer_x, _placer_y))
				
				break
			
			elif not _potential_next_positions:
				raise Exception('No positions available.')
		
		#if not _potential_next_positions and _room_pool:
		#	raise Exception('No next position available - not fatal.')
		
		_potential_next_positions.update(_potential_potential_next_positions)
		
		print 'Placing %s (%i) at' % (_current_room_name, _room_id), _placer_x, _placer_y
		
		_room_id_map[_placer_y, _placer_x] = _room_id
		
		if not _room_pool:
			break
		
		#TODO: If we have required rooms to place, put those in next
		_current_room_name = random.choice(_room_pool)
	
	for y in range(_height):
		for x in range(_width):
			print _room_id_map[y, x],
		
		print

if __name__ == '__main__':
	create_blueprint(ROOMS)
