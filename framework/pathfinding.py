import framework

import multiprocessing
import numbers
import numpy

import time
import sys

PROCESSES = {}
PROCESS_ID = 1
PROCESSING_QUEUE = multiprocessing.Queue()


def setup(width, height, solid_positions):
	_map = numpy.ones((height, width))
	
	for x, y in solid_positions:
		_map[y, x] = -2

	return _map

def astar_mp(start, end, astar_map, weight_map, callback, avoid=[]):
	global PROCESS_ID
	
	def worker(process_id, start, end, astar_map, weight_map, queue, avoid=[]):
		_path = astar(start, end, astar_map, weight_map, avoid=avoid)
		
		queue.put([process_id, _path])

	_p = multiprocessing.Process(target=worker,
	                             args=(PROCESS_ID, start, end, astar_map, weight_map, PROCESSING_QUEUE),
	                             kwargs={'avoid': avoid})
	
	PROCESSES[PROCESS_ID] = [callback, _p]
	PROCESS_ID += 1	
	
	_p.start()	

def wait_for_astar():
	global PROCESSES, PROCESS_ID
	
	if not PROCESSES:
		return False
	
	for i in PROCESSES:
		_id, _p = PROCESSING_QUEUE.get()
		
		PROCESSES[_id][0](_p)

	for p in PROCESSES.values():
		p[1].join()
	
	PROCESSES = {}
	PROCESS_ID = 1
	
	return True

def astar(start, end, astar_map, weight_map, avoid=[]):
	if start == end:
		return []
	
	_height, _width = astar_map.shape

	_path = {'start': tuple(start),
	         'end': tuple(end),
	         'olist': [tuple(start)],
	         'clist': set(),
	         'segments': [],
	         'map': [],
	         'map_size': (_width, _height)}

	_path['fmap'] = numpy.zeros((_height, _width), dtype=numpy.int16)
	_path['gmap'] = weight_map.copy()
	_path['hmap'] = numpy.zeros((_height, _width), dtype=numpy.int16)
	_path['pmap'] = []

	for x in range(_width):
		_path['pmap'].append([0] * _height)

	_path['map'] = astar_map.copy()

	for pos in avoid:
		_path['map'][pos[1], pos[0]] = -2

	_path['hmap'][_path['start'][1], _path['start'][0]] = (abs(_path['start'][0]-_path['end'][0])+abs(_path['start'][1]-_path['end'][1]))*10
	_path['fmap'][_path['start'][1], _path['start'][0]] = _path['hmap'][_path['start'][1],_path['start'][0]]

	return walk_path(_path)

#@profile
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
	_o_scores = {}
	_stime = time.time()

	while len(_olist):
		_olist.remove(node)

		if tuple(node) == path['end']:
			break

		_clist.add(node)
		_lowest = {'pos': None, 'f': 9000}
		_lowest_from_new_set = {'pos': None, 'f': 9000}

		for adj in getadj(path, node, _clist):
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
				
				if _fmap[adj[1],adj[0]] in _o_scores:
					if adj in _o_scores[_fmap[adj[1],adj[0]]]:
						_o_scores[_fmap[adj[1],adj[0]]].remove(adj)
				
				_gmap[adj[1],adj[0]] = _cost
				_fmap[adj[1],adj[0]] = _gmap[adj[1],adj[0]]+_hmap[adj[1],adj[0]]
				_pmap[adj[0]][adj[1]] = node
				
				if _fmap[adj[1],adj[0]] in _o_scores:
					_o_scores[_fmap[adj[1],adj[0]]].add(adj)
				else:
					_o_scores[_fmap[adj[1],adj[0]]] = set([adj])
				
				_olist.add(adj)

		if len(_o_scores):
			_ordered_keys = _o_scores.keys()
			_ordered_keys.sort()
			
			for _min_key in _ordered_keys:
				_list = list(_o_scores[_min_key])
				
				if _list:
					node = _list[0]
					_o_scores[_min_key].remove(node)
					
					if not len(_o_scores[_min_key]):
						del _o_scores[_min_key]
					
					break
	
	#print time.time()-_stime, numbers.distance(path['start'], path['end'])

	return find_path(path)

def getadj(path, pos, cset):
	adj = []

	for _x, _y in [(pos[0]-1, pos[1]-1),
	               (pos[0], pos[1]-1),
	               (pos[0]+1, pos[1]-1),
	               (pos[0]-1, pos[1]),
	               (pos[0]+1, pos[1]),
	               (pos[0]-1, pos[1]+1),
	               (pos[0], pos[1]+1),
	               (pos[0]+1, pos[1]+1)]:

		if path['map'][_y,_x]==-2 or _x<0 or _x>=path['map_size'][0]-1 or _y<0 or _y>=path['map_size'][1]-1:
			continue

		if (_x, _y) in cset:
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

	return astar(start, end, avoid=avoid_positions)
