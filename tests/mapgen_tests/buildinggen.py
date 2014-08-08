import numpy

import random

ROOM_TYPES = {'living_room': {'plots': 4, 'avoid_rooms': []},
              'kitchen': {'plots': 3, 'avoid_rooms': ['bathroom']},
              'bathroom': {'plots': 1, 'avoid_rooms': ['kitchen']},
              'foyer': {'plots': 2, 'avoid_rooms': ['bathroom']}}


def _generate(width, height, facing, room_types, allow_tunnels=False):
	_plot_map = numpy.zeros((height, width))
	_unclaimed_plots = []
	_claimed_plots = {}
	_claimed_plot_types = {}
	
	for y in range(height):
		for x in range(width):
			_unclaimed_plots.append((x, y))
	
	if facing == 'north':
		_plot_x = random.randint(0, width-1)
		_plot_y = 0
	
	elif facing == 'south':
		_plot_x = random.randint(0, width-1)
		_plot_y = height-1
	
	elif facing == 'east':
		_plot_x = width-1
		_plot_y = random.randint(0, height-1)
	
	elif facing == 'west':
		_plot_x = 0
		_plot_y = random.randint(0, height-1)
	
	_generate_new = False
	
	for room_type in room_types:
		if _generate_new:
			_possible_next_plots = []
			
			for _x, _y in _claimed_plots.keys():
				for n_x, n_y in [(_x+1, _y), (_x-1, _y), (_x, _y+1), (_x, _y-1)]:
					if n_x < 0 or n_x >= _plot_map.shape[1] or n_y < 0 or n_y >= _plot_map.shape[0]:
						continue
					
					if (n_x, n_y) in _claimed_plots and _claimed_plots[(n_x, n_y)] in ROOM_TYPES[room_type]['avoid_rooms']:
						continue
					
					_break = False
					
					for nn_x, nn_y in [(n_x+1, n_y), (n_x-1, n_y), (n_x, n_y+1), (n_x, n_y-1)]:
						if (nn_x, nn_y) in _claimed_plots and _claimed_plots[(nn_x, nn_y)] in ROOM_TYPES[room_type]['avoid_rooms']:
							_break = True
							
							break
					
					if _break:
						continue
					
					_possible_next_plots.append((n_x, n_y))
			
			_plot_x, _plot_y = random.choice(_possible_next_plots)
		
		_room = ROOM_TYPES[room_type]
		_plot_map[_plot_y][_plot_x] = 1
		_claimed_plots[(_plot_x, _plot_y)] = room_type
		_plots_for_this_room = [(_plot_x, _plot_y)]
		
		if _room['plots'] == 1:
			continue
		
		for _ in range(_room['plots']):
			_available_next_plot_spaces = {}
			
			for _x, _y in _plots_for_this_room:
				for n_x, n_y in [(_x+1, _y), (_x-1, _y), (_x, _y+1), (_x, _y-1)]:
					if n_x < 0 or n_x >= _plot_map.shape[1] or n_y < 0 or n_y >= _plot_map.shape[0]:
						continue
					
					if _plot_map[n_y][n_x]:
						continue
					
					if (n_x, n_y) in _claimed_plots:# and _claimed_plots[(n_x, n_y)] in ROOM_TYPES[room_type]['avoid_rooms']:
						continue
					
					_number_of_plots_around = available_plots_around(n_x, n_y, _plot_map, room_type, _claimed_plots, ROOM_TYPES[room_type]['avoid_rooms'])
					
					if _number_of_plots_around < _room['plots']-1:
						continue
					
					if _number_of_plots_around in _available_next_plot_spaces:
						_available_next_plot_spaces[_number_of_plots_around].append((n_x, n_y))
					else:
						_available_next_plot_spaces[_number_of_plots_around] = [(n_x, n_y)]
			
			if not _available_next_plot_spaces:
				return -1
			
			_plot_x, _plot_y = random.choice(_available_next_plot_spaces[max(_available_next_plot_spaces.keys())])
			_claimed_plots[(_plot_x, _plot_y)] = room_type
			_plot_map[_plot_y][_plot_x] = 1
			_plots_for_this_room.append((_plot_x, _plot_y))
		
		_generate_new = True
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _claimed_plots:
				print _claimed_plots[(x, y)][0],
			else:
				print '.',
		
		print
	
	return _claimed_plots

def available_plots_around(x, y, plot_map, room_name, claimed_plots, avoid_rooms):
	_plots = 1
	_check_next = [(x, y)]
	_temp_plot_map = plot_map.copy()
	
	while _check_next:
		_x, _y = _check_next.pop(0)
		_break = False
		
		for n_x, n_y in [(_x+1, _y), (_x-1, _y), (_x, _y+1), (_x, _y-1)]:
			if n_x < 0 or n_x >= plot_map.shape[1] or n_y < 0 or n_y >= plot_map.shape[0]:
				continue
			
			if (n_x, n_y) in claimed_plots and claimed_plots[(n_x, n_y)] in ROOM_TYPES[room_name]['avoid_rooms']:
				_break = True
				print 'ooooooooo'
				break
			
			if not _temp_plot_map[n_y][n_x]:
				_check_next.append((n_x, n_y))

		if _break:
			continue
		
		if not _temp_plot_map[_y][_x]:
			_temp_plot_map[_y][_x] = 1
			_plots += 1
	
	return _plots

def generate(width, height, facing, room_types, allow_tunnels=False):
	while 1:
		_building = _generate(width, height, facing, room_types, allow_tunnels=allow_tunnels)
		
		if not _building == -1:
			return _building

if __name__ == '__main__':
	generate(6, 6, 'north', ['foyer', 'living_room', 'kitchen', 'bathroom'])