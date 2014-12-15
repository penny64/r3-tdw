import random
import numpy

#For bitmasking
LOOKUP = {(0, -1): 1,
          (1, 0): 2,
          (0, 1): 4,
          (-1, 0): 8}


_landing = {'name': 'landing',
            'size': 1,
            'rules': {'banned_rooms': ['bathroom'],
                      'required_rooms': [],
                      'allow_only_required': False,
                      'entry_room': True}}

_kitchen = {'name': 'kitchen',
            'size': 2,
            'rules': {'banned_rooms': [],
                      'required_rooms': ['pantry'],
                      'allow_only_required': False,
                      'entry_room': False}}

_pantry = {'name': 'pantry',
           'size': 1,
           'rules': {'banned_rooms': [],
                     'required_rooms': [],
                     'allow_only_required': True,
                     'entry_room': False}}

_bathroom = {'name': 'bathroom',
             'size': 1,
             'rules': {'banned_rooms': [],
                       'required_rooms': [],
                       'allow_only_required': False,
                       'entry_room': False}}

ROOMS = {_landing['name']: _landing,
         _kitchen['name']: _kitchen,
         _bathroom['name']: _bathroom,
         _pantry['name']: _pantry}


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
	
	#TODO: CERTAIN ROOMS (PANTRY, ETC) SHOULDN'T CONNECT TO ANYTHING
		
	_bitmask_map = numpy.zeros((_total_room_size, _total_room_size))
	_room_id_map = numpy.zeros((_total_room_size, _total_room_size))
	_width, _height = _total_room_size, _total_room_size
	
	#Pick an entry point - can be keyword arg at some point
	_current_room_name = random.choice(_potential_start_rooms)
	_placer_x, _placer_y = random.randint(0, _width-1), 0
	_potential_next_positions = set([(_placer_x, _placer_y)])
	_placed_rooms = {}
	
	while _room_pool:
		print 'starting with', _current_room_name, len(_potential_next_positions)
		_room_rules = room_list[_current_room_name]['rules']
		_room_id = _room_reverse_lookup[_current_room_name]
		_rejected_potential_potential_next_positions = set()
		_saved_potential_next_positions_no_removal = set()
		
		while 1:
			#if not _potential_next_positions:
			if len(_room_pool) > 1:
				_temp_room_pool = _room_pool[:]
				_temp_room_pool.remove(_current_room_name)
				
				print 'Failed', _current_room_name,
				
				_current_room_name = random.choice(_temp_room_pool)
				
				print 'moving on to', _current_room_name
			
			_room_rules = room_list[_current_room_name]['rules']
			_room_id = _room_reverse_lookup[_current_room_name]
			_potential_next_positions = set()
			
			for placed_room_name in _placed_rooms:
				_placed_room_at_x, _placed_room_at_y = _placed_rooms[placed_room_name]
				
				for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
					_neighbor_x = _placed_room_at_x + x_mod
					_neighbor_y = _placed_room_at_y + y_mod
					
					if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
						continue
					
					_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
					
					if not _neighbor_id:
						_potential_next_positions.add((_neighbor_x, _neighbor_y))
			
		_placer_x, _placer_y = random.choice(list(_potential_next_positions))
		_fail_bad_neighbor = False
		_potential_potential_next_positions = set()
		
		if (_placer_x, _placer_x) in _rejected_potential_potential_next_positions:
			_potential_next_positions.remove((_placer_x, _placer_y))
			print 'early continue'
			
			continue
			
			#Required/banned neighbor check
			for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
				_neighbor_x = _placer_x + x_mod
				_neighbor_y = _placer_y + y_mod
				
				if (_neighbor_x, _neighbor_y) in _rejected_potential_potential_next_positions:
					print 'rej'
					continue
				
				if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
					continue
				
				_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
				
				if not _neighbor_id:
					continue
				
				_neighbor_room_name = _room_lookup[_neighbor_id]
				_neighbor_room_rules = room_list[_neighbor_room_name]['rules']
				
				if _neighbor_room_name in _room_rules['banned_rooms'] or _current_room_name in _neighbor_room_rules['banned_rooms']:
					_fail_bad_neighbor = True
					print '\tNeighbor is banned/banned by neighbor:', _neighbor_room_name
					
					break
				
				if _neighbor_room_rules['allow_only_required'] and not _current_room_name in _neighbor_room_rules['required_rooms']:
					_fail_bad_neighbor = True
					
					print '\t(1) Neighbor banned us: Not in required list:', _neighbor_room_name
					
					break
				
				#if _room_rules['allow_only_required'] and not _neighbor_room_name in _room_rules['required_rooms']:
				#	_fail_bad_neighbor = True
				#	
				#	print '\t(2) Neighbor banned %s: Not in required list:' % _current_room_name, _neighbor_room_name
				#	
				#	break
			
			if not _fail_bad_neighbor:
				_rejected_potential_potential_next_positions.add((_placer_x, _placer_y))
				_potential_next_positions.remove((_placer_x, _placer_y))
				
				break
			
			else:
				_potential_next_positions.remove((_placer_x, _placer_y))
				continue
			
			if not _potential_potential_next_positions:
				raise Exception('No positions available.')
		
		_potential_next_positions.update(_potential_potential_next_positions)
		_room_id_map[_placer_y, _placer_x] = _room_id
		_placed_rooms[_current_room_name] = _placer_x, _placer_y
		_room_pool.remove(_current_room_name)
		
		print 'placed', _current_room_name, _room_id
		
		#for y in range(_height):
		#	for x in range(_width):
		#		print _room_id_map[y, x],
		#	
		#	print
		
		if not _room_pool:
			break
		
		#TODO: If we have required rooms to place, put those in next
		if _room_rules['required_rooms']:
			_potential_next_positions = set()
			_required_rooms_left_to_place = list(set(_room_rules['required_rooms']) - set(_placed_rooms.keys()))
			_current_room_name = random.choice(_required_rooms_left_to_place)
			print 'New required room', _current_room_name
			
			for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
				_neighbor_x = _placer_x + x_mod
				_neighbor_y = _placer_y + y_mod
				
				if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
					continue
				
				_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
				
				if not _neighbor_id:
					_potential_next_positions.add((_neighbor_x, _neighbor_y))
			
			print _potential_next_positions
			
			continue
		
		_rooms_okay_to_choose_in_pool = []
		
		for next_room_name in _room_pool:
			_r = room_list[next_room_name]
			
			if not _r['rules']['required_rooms'] or len(set(_r['rules']['required_rooms']) & set(_placed_rooms.keys())) == len(_r['rules']['required_rooms']):
				_rooms_okay_to_choose_in_pool.append(next_room_name)
			
		_current_room_name = random.choice(_rooms_okay_to_choose_in_pool)
	
	print
	
	for y in range(_height):
		for x in range(_width):
			print _room_id_map[y, x],
		
		print

if __name__ == '__main__':
	create_blueprint(ROOMS)
