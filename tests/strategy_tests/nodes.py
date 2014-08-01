from framework import entities, display, movement, numbers, pathfinding, tile

DRAGGING_NODE = None


def register(entity):
	entity['node_path'] = {'nodes': {},
	                       'path': [],
	                       'redraw_path': True}
	
	entities.register_event(entity, 'logic', logic)
	entities.register_event(entity, 'draw', draw_path)

def handle_mouse_pressed(entity, x, y, button):
	global DRAGGING_NODE
	
	if button == 1:
		if DRAGGING_NODE:
			entities.trigger_event(DRAGGING_NODE['node'], 'set_position', x=x, y=y)
			
			DRAGGING_NODE['node']['x'] = x
			DRAGGING_NODE['node']['y'] = y
			DRAGGING_NODE = None
			
			entity['node_path']['redraw_path'] = True
		
		else:
			_hit = False
			
			for node in entity['node_path']['nodes'].values():
				if (x, y) == (node['node']['x'], node['node']['y']):
					DRAGGING_NODE = node
					
					break
				
				if (x, y) in node['node']['path']:
					print 'UH!!!!!!!!!'
					
					_hit = True
				
			if not DRAGGING_NODE and not _hit:
				create_walk_node(entity, x, y)
	
	elif button == 2:
		if DRAGGING_NODE:
			DRAGGING_NODE = None
		
		else:
			for node in entity['node_path']['nodes'].values():
				if (x, y) == (node['node']['x'], node['node']['y']):
					entity['node_path']['path'].remove(node['node']['_id'])
					del entity['node_path']['nodes'][node['node']['_id']]
					
					entities.delete_entity(node['node'])
					entity['node_path']['redraw_path'] = True
					
					break

def _create_node(entity, x, y, passive=True, callback_on_touch=True):
	_node = entities.create_entity(group='nodes')
	_node['x'] = x
	_node['y'] = y
	_node['path'] = []
	_node['owner_id'] = entity['_id']
	
	tile.register(_node, surface='nodes')	
	entities.trigger_event(_node, 'set_position', x=x, y=y)
	
	entity['node_path']['nodes'][_node['_id']] = {'node': _node,
	                                              'passive': passive,
	                                              'callback': None,
	                                              'call_on_touch': callback_on_touch}
	entity['node_path']['path'].append(_node['_id'])
	
	entity['node_path']['redraw_path'] = True
	
	return _node

def create_walk_node(entity, x, y):
	_node = _create_node(entity, x, y, passive=False, callback_on_touch=False)
	
	entities.trigger_event(_node, 'set_char', char='O')
	
	entity['node_path']['nodes'][_node['_id']]['callback'] = lambda: entities.trigger_event(entity, 'move_to_position', x=_node['x'], y=_node['y'])

def logic(entity):
	_last_pos = None
	_stop_here = False
	
	for node_id in entity['node_path']['path'][:]:
		_node = entity['node_path']['nodes'][node_id]
		
		if _stop_here and not (_node['node']['x'], _node['node']['y']) == _last_pos:
			break
		
		_distance = numbers.distance((_node['node']['x'], _node['node']['y']), movement.get_position(entity))
		
		if _node['call_on_touch'] and _distance:
			continue
		elif not _distance:
			entity['node_path']['path'].remove(node_id)
			del entity['node_path']['nodes'][node_id]
			
			entities.delete_entity_via_id(node_id)
		
		_node['callback']()		
		
		if not _node['passive']:
			_stop_here = True
			_last_pos = (_node['node']['x'], _node['node']['y'])

def draw_path(entity):
	#TODO: Not every frame
	_last_x, _last_y = (0, 0)
	
	for node_id in entity['node_path']['path'][:]:
		_node = entity['node_path']['nodes'][node_id]
		
		if not _last_x:
			_last_x, _last_y = movement.get_position(entity)
		
		if (_last_x, _last_y) == (_node['node']['x'], _node['node']['y']):
			continue
		
		if entity['node_path']['redraw_path']:
			_path = pathfinding.astar((_last_x, _last_y), (_node['node']['x'], _node['node']['y']))
			if (_node['node']['x'], _node['node']['y']) in _path:
				_path.remove((_node['node']['x'], _node['node']['y']))
				
			_node['node']['path'] = _path
		
		for pos in _node['node']['path']:
			display.write_char('level', pos[0], pos[1], '.')
			
		_last_x, _last_y = (_node['node']['x'], _node['node']['y'])
	
	entity['node_path']['redraw_path'] = False
