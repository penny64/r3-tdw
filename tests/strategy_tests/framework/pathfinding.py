import framework

import numbers
import numpy
import time
import sys


SAVED_MAP = None
REGEN = True


def setup(width, height, solid_positions):
	global SAVED_MAP

	_map = numpy.ones((height, width))
	
	for x, y in solid_positions:
		_map[y, x] = -2

	SAVED_MAP = _map

def astar(start, end, avoid=[]):
	global SAVED_MAP, REGEN

	_height, _width = SAVED_MAP.shape

	_path = {'start': tuple(start),
	         'end': tuple(end),
	         'olist': [tuple(start)],
	         'clist': [],
	         'segments': [],
	         'map': [],
	         'map_size': (_width, _height)}

	_path['fmap'] = numpy.zeros((_height, _width), dtype=numpy.int16)
	_path['gmap'] = numpy.zeros((_height, _width), dtype=numpy.int16)
	_path['hmap'] = numpy.zeros((_height, _width), dtype=numpy.int16)
	_path['pmap'] = []

	for x in range(_width):
		_path['pmap'].append([0] * _height)

	_path['map'] = SAVED_MAP.copy()

	for pos in avoid:
		_path['map'][pos[1], pos[0]] = -2

	_path['hmap'][_path['start'][1], _path['start'][0]] = (abs(_path['start'][0]-_path['end'][0])+abs(_path['start'][1]-_path['end'][1]))*10
	_path['fmap'][_path['start'][1], _path['start'][0]] = _path['hmap'][_path['start'][1],_path['start'][0]]

	return walk_path(_path)

def walk_path(path):
	if path['map'][path['end'][1], path['end'][0]] == -2:
		return False

	node = path['olist'][0]

	_clist = path['clist']
	_olist = set(path['olist'])
	_gmap = path['gmap']
	_hmap = path['hmap']
	_fmap = path['fmap']
	_pmap = path['pmap']
	_stime = time.time()

	while len(_olist):
		_olist.remove(node)

		if tuple(node) == path['end']:
			break

		_clist.append(node)
		_lowest = {'pos': None, 'f': 9000}

		for adj in getadj(path, node):
			if abs(node[0]-adj[0])+abs(node[1]-adj[1]) == 1:
				_cost = _gmap[node[1], node[0]] + 10
			else:
				_cost = _gmap[node[1], node[0]] + 14			
			
			_not_in = 0
			if adj in _olist and _cost < _gmap[adj[1], adj[0]]:
				_olist.remove(adj)
			
			if adj in _clist and _cost < _gmap[adj[1], adj[0]]:
				_clist.remove(adj)
			
			if not adj in _olist and not adj in _clist:
				xDistance = abs(adj[0]-path['end'][0])
				yDistance = abs(adj[1]-path['end'][1])
				
				if xDistance > yDistance:
					_hmap[adj[1],adj[0]] = 14*yDistance + 10*(xDistance-yDistance)
				else:
					_hmap[adj[1],adj[0]] = 14*xDistance + 10*(yDistance-xDistance)
				
				_gmap[adj[1],adj[0]] = _cost
				_fmap[adj[1],adj[0]] = _gmap[adj[1],adj[0]]+_hmap[adj[1],adj[0]]
				_pmap[adj[0]][adj[1]] = node
				
				_olist.add(adj)

		for o in list(_olist):
			if _fmap[o[1],o[0]] < _lowest['f']:
				_lowest['pos'] = o
				_lowest['f'] = _fmap[o[1],o[0]]

		if _lowest['pos']:
			node = _lowest['pos']
	
	print time.time()-_stime

	return find_path(path)

def getadj(path, pos, checkclist=True):
	adj = []

	for r in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
		_x = pos[0]+r[0]
		_y = pos[1]+r[1]

		if _x<0 or _x>=path['map_size'][0]-1 or _y<0 or _y>=path['map_size'][1]-1 or path['map'][_y,_x]==-2:
			continue

		if (_x, _y) in path['clist'] and checkclist:
			continue

		adj.append((_x, _y))

	return adj

def find_path(path):
	if path['map'][path['end'][1], path['end'][0]] == -2:
		return path['start']

	node = path['pmap'][path['end'][0]][path['end'][1]]
	_path = [(path['end'][0], path['end'][1])]
	_broken = False

	while not tuple(node) == tuple(path['start']):
		if not node:
			_broken = True
			break
		else:
			_path.insert(0, node)

		node = path['pmap'][node[0]][node[1]]

	return _path

def create_path(start, end, avoid_positions=[]):
	_start = start
	_end = end

	if not numbers.distance(_start, _end):
		return []

	#print 'start', '%s,%s' % ((int(round(start[0]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE, (int(round(start[1]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE), levels.chunk_is_solid('%s,%s' % ((int(round(start[0]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE, (int(round(start[1]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE))
	#print 'end', '%s,%s' % ((int(round(end[0]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE, (int(round(end[1]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE), levels.chunk_is_solid('%s,%s' % ((int(round(end[0]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE, (int(round(end[1]))/levels.CHUNK_SIZE)*levels.CHUNK_SIZE))

	return astar(start, end, avoid=avoid_positions)
