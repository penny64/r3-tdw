from framework import entities, display, events, numbers, shapes, tile, workers, flags

import libtcodpy as tcod

import buildinggen
import constants
import missions
import tiles
import life

import random
import time
import numpy

UNCLAIMED_NODES = set()
NODE_SETS = {}
NODE_SET_ID = 1


def _create_node(node_grid, x, y):
	_entity = entities.create_entity()
	
	flags.register(_entity)
	tile.register(_entity, surface='node_grid', fore_color=(255, 0, 255))
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'set_flag', flag='owner', value=None)
	entities.register_event(_entity, 'flag_changed', handle_node_flag_change)
	
	node_grid[(x, y)] = _entity['_id']
	UNCLAIMED_NODES.add((x, y))

def handle_node_flag_change(entity, flag, value, last_value):
	if flag == 'owner':
		if value:
			entity['tile']['char'] = 'O'
			entity['tile']['fore_color'] = (255, 0, 0)
			
		else:
			entity['tile']['char'] = 'X'
			entity['tile']['fore_color'] = (255, 0, 255)

def _reset():
	global UNCLAIMED_NODES
	global NODE_SETS
	global NODE_SET_ID
	
	UNCLAIMED_NODES = set()
	NODE_SETS = {}
	NODE_SET_ID = 1

def build_node_grid(node_grid, solids):
	global UNCLAIMED_NODES

	_ignore_positions = set()

	for x, y in solids:
		for _sy in range(y-5, y+6, 2):
			for _sx in range(x-5, x+6, 2):
				if (_sx, _sy) in _ignore_positions:
					continue

				if (_sx, _sy) in solids:
					continue

				_create_node(node_grid, _sx, _sy)

				for _x, _y in [(_sx-1, _sy-1), (_sx, _sy-1), (_sx+1, _sy-1), (_sx-1, _sy), (_sx, _sy), (_sx-1, _sy+1), (_sx, _sy+1), (_sx+1, _sy+1)]:
					_ignore_positions.add((_x, _y))

def add_plot_pole(x, y, radius, solids, cell_split=3.0, debug=False):
	global NODE_SET_ID

	_node_set = set()
	_min_x = 999999999
	_max_x = 0
	_min_y = 999999999
	_max_y = 0

	for node_pos in list(UNCLAIMED_NODES):
		if numbers.distance((x, y), node_pos) > radius:
			continue
		
		if node_pos[0] < _min_x:
			_min_x = node_pos[0]
		
		if node_pos[0] > _max_x:
			_max_x = node_pos[0]
		
		if node_pos[1] < _min_y:
			_min_y = node_pos[1]
		
		if node_pos[1] > _max_y:
			_max_y = node_pos[1]

		_node_set.add(node_pos)
	
	_map = numpy.ones(((_max_y-_min_y)+1, (_max_x-_min_x)+1))
	
	for _x, _y in solids:
		if _x >= _max_x or _x <= _min_x or _y >= _max_y or _y <= _min_y:
			continue
		
		_map[int(round((_y-_min_y))), int(round((_x-_min_x)))] = -2

	NODE_SETS[NODE_SET_ID] = {'owner': None,
	                          'nodes': _node_set,
	                          'center': (x, y),
	                          'astar_map': _map,
	                          'min_x': _min_x,
	                          'min_y': _min_y,
	                          'cell_split': float(cell_split),
	                          'weight_map': numpy.ones(((_max_y-_min_y)+1, (_max_x-_min_x)+1), dtype=numpy.int16)}
	NODE_SET_ID += 1
	
	if debug:
		for y in range(_max_y-_min_y):
			for x in range(_max_x-_min_x):
				_val = int(round(_map[y, x]))
				
				if _val == -2:
					print '#',
				elif _val == 1:
					print '.',
			
			print

	return NODE_SET_ID-1

def create_map(width, height):
	_reset()
	
	_weight_map = numpy.ones((height, width), dtype=numpy.int16)
	_tile_map = []
	_node_grid = {}
	_solids = set()
	
	for y in range(height):
		_x = []

		for x in range(width):
			_x.append(None)

		_tile_map.append(_x)
	
	return _weight_map, _tile_map, _solids, _node_grid
