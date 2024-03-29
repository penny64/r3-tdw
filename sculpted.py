import tiles

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
            'wall_padding': 0,
            'doorway_padding': 0,
            'tile': tiles.carpet_brown,
            'rules': {'banned_rooms': ['bathroom'],
                      'required_rooms': [],
                      'allow_only_if_required_by_neighbor': False,
                      'whitelist_required': False,
                      'entry_room': True,
                      'max_doors_to_same_room': 1}}

_kitchen = {'name': 'kitchen',
            'size': 2,
            'wall_padding': 1,
            'doorway_padding': 0,
            'tile': tiles.tile_checkered,
            'rules': {'banned_rooms': [],
                      'required_rooms': [],
                      'allow_only_if_required_by_neighbor': False,
                      'whitelist_required': False,
                      'entry_room': False,
                      'max_doors_to_same_room': 2}}

_pantry = {'name': 'pantry',
           'size': 1,
           'wall_padding': 2,
           'doorway_padding': 0,
           'tile': tiles.wood_floor,
           'rules': {'banned_rooms': [],
                     'required_rooms': ['kitchen'],
                     'allow_only_if_required_by_neighbor': False,
                     'whitelist_required': True,
                     'entry_room': False,
                     'max_doors_to_same_room': 1}}

_closet = {'name': 'closet',
           'size': 1,
           'wall_padding': 4,
           'doorway_padding': 0,
           'tile': tiles.wood_floor,
           'rules': {'banned_rooms': [],
                     'required_rooms': ['kitchen'],
                     'allow_only_if_required_by_neighbor': False,
                     'whitelist_required': True,
                     'entry_room': False,
                     'max_doors_to_same_room': 1}}

_bathroom = {'name': 'bathroom',
             'size': 1,
             'wall_padding': 3,
             'doorway_padding': 0,
             'tile': tiles.concrete_striped,
             'rules': {'banned_rooms': [],
                       'required_rooms': ['hall'],
                       'allow_only_if_required_by_neighbor': False,
                       'whitelist_required': True,
                       'entry_room': False,
                       'max_doors_to_same_room': 1}}

_hall = {'name': 'hall',
         'size': 3,
         'wall_padding': 4,
         'doorway_padding': 0,
         'tile': tiles.carpet_brown,
         'rules': {'banned_rooms': [],
                   'required_rooms': [],
                   'allow_only_if_required_by_neighbor': True,
                   'whitelist_required': False,
                   'entry_room': False,
                   'max_doors_to_same_room': 1}}

_bunks = {'name': 'bunks',
          'size': 2,
          'wall_padding': 2,
          'doorway_padding': 0,
          'tile': tiles.concrete_striped,
          'rules': {'banned_rooms': [],
                    'required_rooms': ['hall'],
                    'allow_only_if_required_by_neighbor': False,
                    'whitelist_required': True,
                    'entry_room': False,
                    'max_doors_to_same_room': 1}}

_lab = {'name': 'lab',
        'size': 2,
        'wall_padding': 3,
        'doorway_padding': 0,
        'tile': tiles.tile_checkered,
        'rules': {'banned_rooms': [],
                  'required_rooms': ['hall'],
                  'allow_only_if_required_by_neighbor': False,
                  'whitelist_required': True,
                  'entry_room': False,
                  'max_doors_to_same_room': 1}}

_range = {'name': 'range',
          'size': 1,
          'wall_padding': 0,
          'doorway_padding': 0,
          'tile': tiles.carpet_burgandy,
          'rules': {'banned_rooms': [],
                    'required_rooms': ['hall'],
                    'allow_only_if_required_by_neighbor': False,
                    'whitelist_required': False,
                    'entry_room': False,
                    'max_doors_to_same_room': 1}}

_ammo_room = {'name': 'ammo_room',
              'size': 1,
              'wall_padding': 5,
              'doorway_padding': 0,
              'tile': tiles.swamp,
              'rules': {'banned_rooms': [],
                        'required_rooms': ['range'],
                        'allow_only_if_required_by_neighbor': False,
                        'whitelist_required': True,
                        'entry_room': False,
                        'max_doors_to_same_room': 1}}

_lab_closet = {'name': 'lab_closet',
               'size': 1,
               'wall_padding': 3,
               'doorway_padding': 0,
               'tile': tiles.swamp,
               'rules': {'banned_rooms': [],
                         'required_rooms': ['lab'],
                         'allow_only_if_required_by_neighbor': False,
                         'whitelist_required': False,
                         'entry_room': False,
                         'max_doors_to_same_room': 1}}

ROOMS = {_landing['name']: _landing,
         _kitchen['name']: _kitchen,
         _pantry['name']: _pantry,
         _bathroom['name']: _bathroom,
         _hall['name']: _hall,
         _range['name']: _range,
         _ammo_room['name']: _ammo_room,
         _bunks['name']: _bunks,
         _closet['name']: _closet,
         _lab['name']: _lab,
         _lab_closet['name']: _lab_closet}


def _create_blueprint(room_list):
	_total_room_size = 0
	_bitmask_map = None
	_bitmask_door_map = None
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
	_bitmask_door_map = numpy.zeros((_total_room_size, _total_room_size))
	_room_id_map = numpy.zeros((_total_room_size, _total_room_size), dtype=numpy.int32)
	_width, _height = int(round(_total_room_size * .5)), int(round(_total_room_size * .5))
	
	#Pick an entry point - can be keyword arg at some point
	_current_room_name = random.choice(_potential_start_rooms)
	_placer_x, _placer_y = _width / 2, 0
	_potential_next_positions = set([(_placer_x, _placer_y)])
	_placed_rooms = {}
	_room_pool_priority = set()
	_try_new_positions_first = False
	
	while _room_pool:
		_room_rules = room_list[_current_room_name]['rules']
		_room_size = room_list[_current_room_name]['size']
		_room_id = _room_reverse_lookup[_current_room_name]
		_rejected_potential_potential_next_positions = set()
		
		while 1:
			#NOTE: _potential_next_positions will almost always be empty
			if not _potential_next_positions:
				if len(_room_pool) > 1:
					if _try_new_positions_first:
						_try_new_positions_first = False
					
					else:
						_temp_room_pool = _room_pool[:]
						
						_temp_room_pool.remove(_current_room_name)
						
						_last_room_name = _current_room_name
						_current_room_name = random.choice(_temp_room_pool)
						
						logging.debug('Failed to place \'%s\', moving to \'%s\'' % (_last_room_name, _current_room_name))
				
				_room_rules = room_list[_current_room_name]['rules']
				_room_size = room_list[_current_room_name]['size']
				_room_id = _room_reverse_lookup[_current_room_name]
				
				if _room_rules['required_rooms'] and len(set(_room_rules['required_rooms']) & set(_placed_rooms.keys())) == len(_room_rules['required_rooms']):
					_placed_rooms_to_check = _room_rules['required_rooms']
				
				else:
					_placed_rooms_to_check = _placed_rooms
				
				for placed_room_name in _placed_rooms_to_check:
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
			
			if not _potential_next_positions:
				logging.warning('No potential next positions. If this is happening a lot, check your room list.')
				
				return False
			
			_placer_x, _placer_y = random.choice(list(_potential_next_positions))
			_potential_potential_next_positions = set()
			_failures = 0
			_placed_at_least_one_room = False
			
			while _room_size:
				_fail_bad_neighbor = False
				_had_one_good_neighbor = False
				_failures += 1
				
				if _failures >= 12:
					logging.warning('Failed too many times when placing room. If this is happening a lot, check your room list.')
					
					return False
				
				#Required/banned neighbor check
				for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
					_neighbor_x = _placer_x + x_mod
					_neighbor_y = _placer_y + y_mod
					
					if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
						continue
					
					_neighbor_id = _room_id_map[_neighbor_y, _neighbor_x]
					
					if not _neighbor_id:
						if _room_size == 1 or _placed_at_least_one_room:
							_had_one_good_neighbor = True
						
						continue
					
					_neighbor_room_name = _room_lookup[_neighbor_id]
					_neighbor_room_rules = room_list[_neighbor_room_name]['rules']
					
					if not _current_room_name == _neighbor_room_name:
						if _neighbor_room_name in _room_rules['banned_rooms'] or _current_room_name in _neighbor_room_rules['banned_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor is banned/banned by neighbor: %s' % _neighbor_room_name)
							
							continue
						
						elif _neighbor_room_rules['allow_only_if_required_by_neighbor'] and not _neighbor_room_name in _room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor banned us: Not in required list: %s (is only allowed if required by this room)' % _neighbor_room_name)
							
							continue
						
						elif _room_rules['whitelist_required'] and not _neighbor_room_name in _room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor is banned: Only allowing required links: %s' % _neighbor_room_name)
							
							continue
						
						elif _neighbor_room_rules['whitelist_required'] and not _current_room_name in _neighbor_room_rules['required_rooms']:
							_fail_bad_neighbor = True
							
							logging.debug('\tNeighbor banned us: Not in required list: %s' % _neighbor_room_name)
							
							continue
						
						else:
							_had_one_good_neighbor = True
							
							break
					
					else:
						_had_one_good_neighbor = True
						
						break
				
				if _had_one_good_neighbor:
					if (_placer_x, _placer_y) in _potential_next_positions:
						_potential_next_positions.remove((_placer_x, _placer_y))
					
					if _room_id_map[_placer_y, _placer_x]:
						raise Exception('How in the actual fuck?')
					
					_room_id_map[_placer_y, _placer_x] = _room_id
					_failures = 0
					_try_new_positions_first = True
					_placed_at_least_one_room = True
					
					logging.debug('\tPutting down 1 room at %i, %i' % (_placer_x, _placer_y))
					
					#for y in range(_height):
					#	for x in range(_width):
					#		_id = _room_id_map[y, x]
					#		
					#		if not _id:
					#			print '.',
					#			
					#			continue
					#		
					#		print _room_lookup[_id][0],
					#	
					#	print
					#
					#print
					
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
					
					if not _potential_potential_next_positions:
						logging.warning('No next position to place room: %s' % _current_room_name)
						
						return False
					
					_placer_x, _placer_y = random.choice(list(_potential_potential_next_positions))
					
					continue
				
				else:
					_placer_x, _placer_y = random.choice(list(_potential_next_positions))
			
			break
		
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
			
			logging.debug('\tChoosing room in priority pool: %s' % _current_room_name)
			
			continue
		
		_rooms_okay_to_choose_in_pool = []
		
		for next_room_name in _room_pool:
			_r = room_list[next_room_name]
			
			if not _r['rules']['required_rooms'] or len(set(_r['rules']['required_rooms']) & set(_placed_rooms.keys())) == len(_r['rules']['required_rooms']):
				_rooms_okay_to_choose_in_pool.append(next_room_name)
		
		_current_room_name = random.choice(_rooms_okay_to_choose_in_pool)
		
		logging.debug('Next room: %s' % _current_room_name)
		_try_new_positions_first = True
	
	#print
	
	logging.debug('Writing bitmask map')
	_doors_map = {}
	
	for y in range(_height):
		for x in range(_width):
			_room_id = _room_id_map[y, x]
			_neighbor_count = 0
			_door_count = 0
			_has_door_to = [] #set()
			_room_name = None
			
			if _room_id:
				_neighbor_count += 100
				_room_name = _room_lookup[_room_id]
				_room_rules = room_list[_room_name]['rules']
			
			for x_mod, y_mod in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
				_neighbor_x = x + x_mod
				_neighbor_y = y + y_mod
				
				#Outside door
				if _neighbor_x < 0 or _neighbor_x > _width-1 or _neighbor_y < 0 or _neighbor_y > _height-1:
					if _room_id and _room_rules['entry_room'] and _neighbor_y < 0:
						_door_count += LOOKUP[x_mod, y_mod]
					
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
							
							if _has_door_to.count(_neighbor_room_name) < _room_rules['max_doors_to_same_room']:
								if _neighbor_room_name in _doors_map and _room_name in _doors_map[_neighbor_room_name] and not (x, y) in _doors_map[_neighbor_room_name][_room_name]:
									continue
								
								_door_count += LOOKUP[x_mod, y_mod]
								_has_door_to.append(_neighbor_room_name)
								
								if _room_name in _doors_map:
									if _neighbor_room_name in _doors_map[_room_name]:
										_doors_map[_room_name][_neighbor_room_name].append((_neighbor_x, _neighbor_y))
									else:
										_doors_map[_room_name][_neighbor_room_name] = [(_neighbor_x, _neighbor_y)]
								
								else:
									_doors_map[_room_name] = {_neighbor_room_name: [(_neighbor_x, _neighbor_y)]}
							
							else:
								continue
						
						_neighbor_count += LOOKUP[x_mod, y_mod]
				
				elif not _room_id and _neighbor_id:
					_neighbor_count += LOOKUP[x_mod, y_mod]
			
			_bitmask_map[y, x] = _neighbor_count
			
			if _door_count:
				_bitmask_door_map[y, x] = _door_count + 100
	
	for y in range(_height):
		for x in range(_width):
			_id = _room_id_map[y, x]
			
			if not _id:
				print '.',
				
				continue
			
			print _room_lookup[_id][0],
		
		print
	
	_blueprint = {'bitmask_map': _bitmask_map,
	              'bitmask_door_map': _bitmask_door_map,
	              'room_map': _room_id_map,
	              'rooms': room_list,
	              'room_lookup': _room_lookup,
	              'room_reverse_lookup': _room_reverse_lookup,
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