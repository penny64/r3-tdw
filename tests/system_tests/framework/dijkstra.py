import numbers
import entities

import numpy


def create(width, height, target_positions, collision_positions, detail=30):
	_map = numpy.zeros((height, width))
	_solid_positions = set()
	_target_positions = set(target_positions)

	for x, y in collision_positions:
		if (x, y) in _target_positions:
			continue

		_solid_positions.add((x, y))

	_map += detail
	_starting_lowest = detail

	for x, y in target_positions:
		_map[y][x] = 0

	_open_positions = []

	for y in range(height):
		for x in range(width):				
			if (x, y) in target_positions or (x, y) in _solid_positions:
				continue

			_open_positions.append((x, y))

	while 1:
		_changed = False
		_orig_map = _map.copy()

		for x, y in _open_positions:
			_lowest_score = _starting_lowest

			for x_mod, y_mod in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
				_x = x + x_mod
				_y = y + y_mod

				if _x < 0 or _x >= width or _y < 0 or _y >= height:
					continue

				if (_x, _y) in _solid_positions:
					continue

				_dist = 1
				_neighbor_diff = _orig_map[y, x]-_orig_map[_y, _x]

				if _neighbor_diff >= 2 and _orig_map[_y, _x] < _lowest_score:
					_lowest_score = _orig_map[_y, _x]

			if _lowest_score < _starting_lowest:
				_map[y, x] = _lowest_score + 1
				_changed = True

		if not _changed:
			break

	return _map
	#with open('test.txt', 'w') as _f:
	#	for y in range(height):
	#		_line = ''

	#		for x in range(width):
	#			_line += str(numbers.clip(int(round(_map[y][x])), 0, 9))

	#		_line += '\n'

	#		_f.write(_line)
