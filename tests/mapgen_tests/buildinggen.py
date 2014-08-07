import numpy

import random

ROOM_TYPES = {'living_room': {'plots': 4, 'avoid_rooms': []},
              'kitchen': {'plots': 3, 'avoid_rooms': []},
              'bathroom': {'plots': 1, 'avoid_rooms': ['kitchen']}}


def _generate(width, height, facing, room_types, allow_tunnels=False):
	_plot_map = numpy.zeros((height, width))
	_unclaimed_plots = []
	_claimed_plots = {}
	_claimed_plot_types = {}
	_entrance_room_placed = False
	
	for y in range(height):
		for x in range(width):
			_unclaimed_plots.append((x, y))
	
	if facing == 'north':
		_entrance_x = random.randint(0, width-1)
		_entrance_y = 0
	
	elif facing == 'south':
		_entrance_x = random.randint(0, width-1)
		_entrance_y = height-1
	
	elif facing == 'east':
		_entrance_x = width-1
		_entrance_y = random.randint(0, height-1)
	
	elif facing == 'west':
		_entrance_x = 0
		_entrance_y = random.randint(0, height-1)
	
	while room_types:
		room_type = room_types.pop(0)
		
		_plots_needed = ROOM_TYPES[room_type]['plots'] - 1
		_temp_unclaimed_plots = _unclaimed_plots[:]
		
		if _entrance_x > -1:
			_x_plot = _entrance_x
			_y_plot = _entrance_y
			_entrance_x = -1
			_entrance_y = -1
		else:
			while 1:
				if not _temp_unclaimed_plots:
					return -1
				
				_x_plot, _y_plot = _temp_unclaimed_plots.pop(random.randint(0, len(_temp_unclaimed_plots)-1))
				_continue = False
				_found_good_room = False
				
				if not _entrance_room_placed:
					break
				
				for nn_x, nn_y in [(_x_plot+1, _y_plot), (_x_plot-1, _y_plot), (_x_plot, _y_plot+1), (_x_plot, _y_plot-1)]:
					if (nn_x, nn_y) in _claimed_plots:
						if _claimed_plots[(nn_x, nn_y)] in ROOM_TYPES[room_type]['avoid_rooms']:
							_continue = True
							
							break
						else:
							_found_good_room = True
				
				if not _found_good_room and not allow_tunnels:
					continue
				
				if not _continue:
					break
		
		_claimed_plots[(_x_plot, _y_plot)] = room_type
		
		if room_type in _claimed_plot_types:
			_claimed_plot_types[room_type].append((_x_plot, _y_plot))
		else:
			_claimed_plot_types[room_type] = [(_x_plot, _y_plot)]
		
		_check_positions = [(_x_plot+1, _y_plot), (_x_plot-1, _y_plot), (_x_plot, _y_plot+1), (_x_plot, _y_plot-1)]
		_placed_this_iteration = [(_x_plot, _y_plot)]
		
		while _plots_needed > 0:
			if not len(_check_positions):
				room_types.insert(0, room_type)
				
				for x, y in _placed_this_iteration:
					del _claimed_plots[(x, y)]
					
					_claimed_plot_types[room_type].remove((x, y))
					_unclaimed_plots.append((x, y))
				
				return -1
				break
			
			n_x, n_y = _check_positions.pop(random.randint(0, len(_check_positions)-1))
			
			#Check for OOB or claimed plot
			if n_x < 0 or n_x >= width or n_y < 0 or n_y >= height or (n_x, n_y) in _claimed_plots:
				continue
			
			#Check for neighbors of neighbors
			_found_bad_room = False
			_found_good_room = False
			
			for nn_x, nn_y in [(_x_plot+1, _y_plot), (_x_plot-1, _y_plot), (_x_plot, _y_plot+1), (_x_plot, _y_plot-1)]:
				if (nn_x, nn_y) in _claimed_plots:
					if _claimed_plots[(nn_x, nn_y)] in ROOM_TYPES[room_type]['avoid_rooms']:
						_found_bad_room = True
						
						break
					else:
						_found_good_room = True

			print _found_bad_room, _found_good_room
			
			if _entrance_room_placed:
				if _found_bad_room or (not _found_good_room and not allow_tunnels):
					continue
			
			_placed_this_iteration.append((n_x, n_y))
			_claimed_plots[(n_x, n_y)] = room_type
			_claimed_plot_types[room_type].append((n_x, n_y))
			_unclaimed_plots.remove((n_x, n_y))
			_plots_needed -= 1
			_x_plot = n_x
			_y_plot = n_y
			
			if not _plots_needed:
				print room_type
		
		_entrance_room_placed = True
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _claimed_plots:
				print _claimed_plots[(x, y)][0],
			else:
				print '.',
		
		print
	
	return 1

def generate(width, height, facing, room_types, allow_tunnels=False):
	while 1:
		if not _generate(width, height, facing, room_types, allow_tunnels=allow_tunnels) == -1:
			break

if __name__ == '__main__':
	generate(6, 6, 'north', ['living_room', 'kitchen', 'bathroom'])