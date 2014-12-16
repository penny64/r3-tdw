import logging
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
                      'allow_only_if_required_by_neighbor': False,
                      'whitelist_required': False,
                      'entry_room': True}}

_kitchen = {'name': 'kitchen',
            'size': 3,
            'rules': {'banned_rooms': [],
                      'required_rooms': [],
                      'allow_only_if_required_by_neighbor': False,
                      'whitelist_required': False,
                      'entry_room': False}}

_pantry = {'name': 'pantry',
           'size': 2,
           'rules': {'banned_rooms': [],
                     'required_rooms': ['kitchen'],
                     'allow_only_if_required_by_neighbor': False,
                     'whitelist_required': True,
                     'entry_room': False}}

_bathroom = {'name': 'bathroom',
             'size': 1,
             'rules': {'banned_rooms': [],
                       'required_rooms': ['hall'],
                       'allow_only_if_required_by_neighbor': False,
                       'whitelist_required': True,
                       'entry_room': False}}

_hall = {'name': 'hall',
             'size': 3,
             'rules': {'banned_rooms': [],
                       'required_rooms': [],
                       'allow_only_if_required_by_neighbor': False,
                       'whitelist_required': False,
                       'entry_room': False}}

_bunks = {'name': 'Bunks',
             'size': 3,
             'rules': {'banned_rooms': [],
                       'required_rooms': ['hall'],
                       'allow_only_if_required_by_neighbor': False,
                       'whitelist_required': True,
                       'entry_room': False}}

ROOMS = {_landing['name']: _landing,
         _kitchen['name']: _kitchen,
         _pantry['name']: _pantry,
         _bathroom['name']: _bathroom,
         _hall['name']: _hall,
         _bunks['name']: _bunks,}


def _create_blueprint(room_list):
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
	_room_id_map = numpy.zeros((_total_room_size, _total_room_size), dtype=numpy.int32)
	_width, _height = _total_room_size, _total_room_size
	
	#Pick an entry point - can be keyword arg at some point
	_current_room_name = random.choice(_potential_start_rooms)
	_placer_x, _placer_y = random.randint(3, _width-4), 0
	_potential_next_positions = set([(_placer_x, _placer_y)])
	_placed_rooms = {}
	_room_pool_priority = set()
	
	while _room_pool:
		_room_rules = room_list[_current_room_name]['rules']
		_room_size = room_list[_current_room_name]['size']
		_room_id = _room_reverse_lookup[_current_room_name]
		_rejected_potential_potential_next_positions = set()
		
		while 1:
			#NOTE: _potential_next_positions will almost always be empty
			if not _potential_next_positions:
				if len(_room_pool) > 1:
					_temp_room_pool = _room_pool[:]
					
					#if _current_room_name in _temp_room_pool:
					_temp_room_pool.remove(_current_room_name)
					
					_last_room_name = _current_room_name
					_current_room_name = random.choice(_temp_room_pool)
					
					logging.debug('Failed to place \'%s\', moving to \'%s\'' % (_last_room_name, _current_room_name))
				
				_room_rules = room_list[_current_room_name]['rules']
				_room_size = room_list[_current_room_name]['size']
				_room_id = _room_reverse_lookup[_current_room_name]
				
				for placed_room_name in _placed_rooms:
					for _placed_room_at_x, _placed_room_at_y in _placed_rooms[placed_room_name]:
						for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
							_neighbor_x = _placed_room_at_x + x_mod
							_neighbor_y = _placed_room_at_y + y_mod
							
							if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
								continue
							
							_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
							
							if not _neighbor_id:
								_potential_next_positions.add((_neighbor_x, _neighbor_y))
							
							#TODO: can probably fix split room bug
							#if _room_size 
			
			logging.debug('Placement start: %s (%i potential location(s) left)' % (_current_room_name, len(_potential_next_positions)))
			
			_placer_x, _placer_y = random.choice(list(_potential_next_positions))
			_potential_potential_next_positions = set()
			_failures = 0
			_fail = False
			
			while _room_size:
				_fail_bad_neighbor = False
				_failures += 1
				
				if _failures >= 12:
					_fail = True
					break
				
				#Required/banned neighbor check
				for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
					_neighbor_x = _placer_x + x_mod
					_neighbor_y = _placer_y + y_mod
					
					if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
						continue
					
					_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
					
					if not _neighbor_id:
						continue
					
					_neighbor_room_name = _room_lookup[_neighbor_id]
					_neighbor_room_rules = room_list[_neighbor_room_name]['rules']
					
					if not _current_room_name == _neighbor_room_name:
						if _neighbor_room_name in _room_rules['banned_rooms'] or _current_room_name in _neighbor_room_rules['banned_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor is banned/banned by neighbor: %s' % _neighbor_room_name)
							
							continue
						
						if _neighbor_room_rules['allow_only_if_required_by_neighbor'] and not _current_room_name in _neighbor_room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor banned us: Not in required list: %s' % _neighbor_room_name)
							
							continue
						
						if _room_rules['whitelist_required'] and not _neighbor_room_name in _room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor is banned: Only allowing required links: %s' % _neighbor_room_name)
							
							continue
						
						if _neighbor_room_rules['whitelist_required'] and not _current_room_name in _neighbor_room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor banned us: Not in required list: %s' % _neighbor_room_name)
							
							continue
				
				if not _fail_bad_neighbor:
					if (_placer_x, _placer_y) in _potential_next_positions:
						_potential_next_positions.remove((_placer_x, _placer_y))
					
					if _room_id_map[_placer_y, _placer_x]:
						raise Exception('How in the actual fuck?')
					
					_room_id_map[_placer_y, _placer_x] = _room_id
					
					logging.debug('\tPutting down 1 room at %i, %i' % (_placer_x, _placer_y))
					
					for y in range(_height):
						for x in range(_width):
							_id = _room_id_map[y, x]
							
							if not _id:
								print '.',
								
								continue
							
							print _room_lookup[_id][0],
						
						print
					
					print
					
					if _current_room_name in _placed_rooms:
						_placed_rooms[_current_room_name].append((_placer_x, _placer_y))
					
					else:
						_placed_rooms[_current_room_name] = [(_placer_x, _placer_y)]
					
					_room_size -= 1
					
					if not _room_size:
						break
					
					_potential_potential_next_positions = set()
					
					for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
						_neighbor_x = _placer_x + x_mod
						_neighbor_y = _placer_y + y_mod
						
						if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
							continue
						
						_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
						
						if not _neighbor_id:
							_potential_potential_next_positions.add((_neighbor_x, _neighbor_y))
					
					_placer_x, _placer_y = random.choice(list(_potential_potential_next_positions))
					print 'taking off pp list'
					
					continue
				
				else:
					_placer_x, _placer_y = random.choice(list(_potential_next_positions))
					print 'taking off Next pos'
				
				
			
			break
		
		if _fail:
			return False
		
		_room_pool.remove(_current_room_name)
		_potential_next_positions = set()
		
		logging.debug('\tPlaced room: %s (ID=%i) at %s' % (_current_room_name, _room_id, _placed_rooms[_current_room_name]))
		
		if not _room_pool:
			break
		
		#Next room selection
		if _room_rules['required_rooms']:
			_required_rooms_left_to_place = list(set(_room_rules['required_rooms']) - set(_placed_rooms.keys()))
			_last_room_name = _current_room_name
			
			if _required_rooms_left_to_place:
				_room_pool_priority.update(_required_rooms_left_to_place)
				
				logging.debug('\'%s\' has required rooms left to place: %s' % (_last_room_name, _required_rooms_left_to_place))
		
		if _room_pool_priority:
			_current_room_name = random.choice(list(_room_pool_priority))
			_room_pool_priority.remove(_current_room_name)
			
			logger.debug('\tChoosing room in priority pool: %s' % _current_room_name)
			
			continue
		
		_rooms_okay_to_choose_in_pool = []
		
		for next_room_name in _room_pool:
			_r = room_list[next_room_name]
			
			if not _r['rules']['required_rooms'] or len(set(_r['rules']['required_rooms']) & set(_placed_rooms.keys())) == len(_r['rules']['required_rooms']):
				_rooms_okay_to_choose_in_pool.append(next_room_name)
		
		_current_room_name = random.choice(_rooms_okay_to_choose_in_pool)
	
	print
	
	logging.debug('Writing bitmask map')
	
	for y in range(_height):
		for x in range(_width):
			_room_id = _room_id_map[y, x]
			_neighbor_count = 0
			
			if _room_id:
				_neighbor_count += 100
			
			for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
				_neighbor_x = x + x_mod
				_neighbor_y = y + y_mod
				
				if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
					continue
			
				_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
			
				if _room_id:
					_current_room_name = _room_lookup[_room_id]
					_room_rules = room_list[_current_room_name]['rules']
					
					if _neighbor_id:
						_neighbor_room_name = _room_lookup[_neighbor_id]
						_neighbor_room_rules = room_list[_neighbor_room_name]['rules']
						
						if not _current_room_name == _neighbor_room_name:
							if _room_rules['whitelist_required'] and not _neighbor_room_name in _room_rules['required_rooms']:
								continue
							
							if _neighbor_room_rules['whitelist_required'] and not _current_room_name in _neighbor_room_rules['required_rooms']:
								continue
						
						_neighbor_count += LOOKUP[x_mod, y_mod]
				
				elif not _room_id and _neighbor_id:
					_neighbor_count += LOOKUP[x_mod, y_mod]
			
			_bitmask_map[y, x] = _neighbor_count
	
	for y in range(_height):
		for x in range(_width):
			_id = _room_id_map[y, x]
			
			if not _id:
				print '.',
				
				continue
			
			print _room_lookup[_id][0],
		
		print
	
	_blueprint = {'bitmask_map': _bitmask_map,
	              'room_map': _room_id_map,
	              'rooms': room_list,
	              'room_lookup': _room_lookup,
	              'width': _width,
	              'height': _height}
	
	return _blueprint

def create_blueprint(room_list):
	while 1:
		_blueprint = _create_blueprint(room_list)
		
		if _blueprint:
			break
	
	return _blueprint

if __name__ == '__main__':
	print create_blueprint(ROOMS)