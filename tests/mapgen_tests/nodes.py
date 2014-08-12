from framework import entities, display, movement, numbers, pathfinding, tile, controls, stats

import constants
import ui_cursor
import ui_menu
import mapgen
import camera

import time

DRAGGING_NODE = None
LAST_CLICKED_POS = None


def register(entity):
	entity['node_path'] = {'nodes': {},
	                       'path': [],
	                       'redraw_path': True}
	
	entities.register_event(entity, 'logic', logic)
	entities.register_event(entity, 'draw', draw_path)
	entities.register_event(entity, 'position_changed', _redraw_first_node)

def handle_keyboard_input(entity):
	if LAST_CLICKED_POS:
		if controls.get_input_char_pressed('f'):
			create_action_node(entity,
			                   LAST_CLICKED_POS[0],
			                   LAST_CLICKED_POS[1],
			                   40,
			                   lambda: entities.trigger_event(entity, 'shoot'), icon='+')
			
			redraw_path(entity)

def handle_mouse_movement(entity, x, y, vx, vy):
	if not DRAGGING_NODE:
		return
	
	if (vx, vy) in mapgen.SOLIDS:
		return
	
	entities.trigger_event(DRAGGING_NODE['node'], 'set_position', x=vx, y=vy)
	entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 255))
	
	DRAGGING_NODE['node']['x'] = vx
	DRAGGING_NODE['node']['y'] = vy	
	DRAGGING_NODE['node']['path'] = []
	
	redraw_path(entity)

def handle_mouse_pressed(entity, x, y, button):
	global DRAGGING_NODE, LAST_CLICKED_POS
	
	if ui_menu.get_active_menu():
		return
	
	_x = x+camera.X
	_y = y+camera.Y
	
	if button == 1:
		if DRAGGING_NODE:
			DRAGGING_NODE = None
		
		elif not (_x, _y) in mapgen.SOLIDS:
			for entity_id in entities.get_entity_group('items'):
				_item = entities.get_entity(entity_id)
				
				if _item['stats']['owner']:
					continue
				
				if (_x, _y) == movement.get_position(_item):
					create_item_menu(entity, _item, _x, _y)
					return
			
			for node in entity['node_path']['nodes'].values():
				if (_x, _y) == (node['node']['x'], node['node']['y']):
					DRAGGING_NODE = node
					entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 0))
					
					break
				
				if (_x, _y) in node['node']['path']:
					if not (_x, _y) in node['node']['busy_pos']:
						LAST_CLICKED_POS = (_x, _y)
						
						create_action_menu(entity, LAST_CLICKED_POS[0], LAST_CLICKED_POS[1])
					
					else:
						LAST_CLICKED_POS = None
					
					return
			
			if not DRAGGING_NODE:
				for entity_id in entities.get_entity_group('life'):
					_target = entities.get_entity(entity_id)
					
					if movement.get_position(_target) == (_x, _y):
						LAST_CLICKED_POS = (_x, _y)
						create_action_menu(entity, LAST_CLICKED_POS[0], LAST_CLICKED_POS[1])
						
						return
				
				create_walk_node(entity, _x, _y)
			
	
	elif button == 2:
		if DRAGGING_NODE:
			entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 255))
			
			DRAGGING_NODE = None
		
		else:
			for node in entity['node_path']['nodes'].values():
				if (_x, _y) == (node['node']['x'], node['node']['y']):
					entity['node_path']['path'].remove(node['node']['_id'])
					entities.delete_entity(node['node'])
					redraw_path(entity)
					
					del entity['node_path']['nodes'][node['node']['_id']]
					
					break

def _create_node(entity, x, y, draw_path=False, passive=True, action_time=0, name='Node', callback_on_touch=True):
	global LAST_CLICKED_POS
	
	_path_index = -1
	
	if LAST_CLICKED_POS:
		_node_positions = [(p['node']['x'], p['node']['y']) for p in entity['node_path']['nodes'].values() if not p['node']['name'] == 'Walk']
		
		for node_id in entity['node_path']['path'][:]:
			_last_node = entity['node_path']['nodes'][node_id]
			
			if LAST_CLICKED_POS in _last_node['node']['path']:
				_move_cost = 0
				
				for pos in _last_node['node']['path'][_last_node['node']['path'].index(LAST_CLICKED_POS):]:
					_move_cost += stats.get_speed(entity)
					
					if _move_cost < action_time and pos in _node_positions:
						return
				
				_path_index = entity['node_path']['path'].index(node_id)
				entity['node_path']['nodes'][entity['node_path']['path'][_path_index]]['node']['action_time'] = action_time
				
				break
		
		LAST_CLICKED_POS = None	
	
	_node = entities.create_entity(group='nodes')
	_node['x'] = x
	_node['y'] = y
	_node['name'] = name
	_node['draw_path'] = draw_path
	_node['path'] = []
	_node['owner_id'] = entity['_id']
	_node['action_time'] = action_time
	_node['busy_pos'] = []
	
	tile.register(_node, surface='nodes')	
	entities.trigger_event(_node, 'set_position', x=x, y=y)
		
	if _path_index == -1:
		_path_index = len(entity['node_path']['path'])
	
	entity['node_path']['nodes'][_node['_id']] = {'node': _node,
	                                              'passive': passive,
	                                              'callback': None,
	                                              'call_on_touch': callback_on_touch}
	entity['node_path']['path'].insert(_path_index, _node['_id'])
	
	return _node

def create_walk_node(entity, x, y):
	_walk_speed = 'Walk'
	
	_node = _create_node(entity, x, y, draw_path=True, passive=False, name=_walk_speed, callback_on_touch=False)
	
	entities.trigger_event(_node, 'set_char', char='O')
	
	entity['node_path']['nodes'][_node['_id']]['callback'] = lambda: entities.trigger_event(entity,
	                                                                                        'move_to_position',
	                                                                                        x=_node['x'],
	                                                                                        y=_node['y'])

def create_action_node(entity, x, y, time, callback, icon='X', name='Action'):
	_will_move = False
	
	for node_id in entity['node_path']['path']:
		_node = entity['node_path']['nodes'][node_id]['node']
		
		if not (_node['x'], _node['y']) == (x, y):
			continue
		
		if _node['name'] == 'Walk':
			_will_move = True
	
	if not _will_move:
		create_walk_node(entity, x, y)
	
	_node = _create_node(entity, x, y, passive=False, action_time=time, callback_on_touch=True, name=name)
	
	if not _node:
		return
	
	entities.trigger_event(_node, 'set_char', char=icon)
	
	entity['node_path']['nodes'][_node['_id']]['callback'] = callback

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

def _redraw_first_node(entity, **kargs):
	_x, _y = movement.get_position(entity)
	
	for node_id in entity['node_path']['path']:
		_node = entity['node_path']['nodes'][node_id]['node']
		
		if (_x, _y) in _node['path']:
			if _node['draw_path']:
				_node['path'] = _node['path'][_node['path'].index((_x, _y)):]
				
				break

def create_action_menu(entity, x, y):
	_menu = ui_menu.create(ui_cursor.CURSOR['tile']['x']+2, ui_cursor.CURSOR['tile']['y']-1, title='Context')
	ui_menu.add_selectable(_menu, 'Reload', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'reload'),
	                                                                   name='Reload'))
	ui_menu.add_selectable(_menu, 'Crouch', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'crouch'),
	                                                                   name='Crouch'))

def create_item_menu(entity, item, x, y):
	_menu = ui_menu.create(ui_cursor.CURSOR['tile']['x']+2, ui_cursor.CURSOR['tile']['y']-1, title='Context')
	ui_menu.add_selectable(_menu, 'Pick Up', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'pick_up_item', item_id=item['_id']),
	                                                                   name='Pick up %s' % item['stats']['name']))

def redraw_path(entity):
	for node in entity['node_path']['nodes'].values():
		node['node']['path'] = []

def draw_path(entity, x_mod=0, y_mod=0):
	_last_x, _last_y = (0, 0)
	_node_ids = entity['node_path']['path'][:]
	_action_time_max = 0
	_surface_width = display.get_surface('nodes')['width']
	_surface_height = display.get_surface('nodes')['height']
	
	for node_id in _node_ids:
		_node = entity['node_path']['nodes'][node_id]
		
		if not _last_x:
			_last_x, _last_y = movement.get_position(entity)
		
		if (_last_x, _last_y) == (_node['node']['x'], _node['node']['y']):
			continue
		
		_node['node']['busy_pos'] = []
		
		if _node['node']['draw_path'] and not _node['node']['path']:
			_path = pathfinding.astar((_last_x, _last_y), (_node['node']['x'], _node['node']['y']))
			
			if (_node['node']['x'], _node['node']['y']) in _path:
				_path.remove((_node['node']['x'], _node['node']['y']))
			
			_node['node']['path'] = _path
		
		_move_cost = 0
		for pos in _node['node']['path']:
			for node_id in _node_ids:
				_check_node = entity['node_path']['nodes'][node_id]['node']
				
				if not _check_node['action_time']:
					continue
				
				if (_check_node['x'], _check_node['y']) == pos:
					_action_time_max = _check_node['action_time']
			
			if _action_time_max and _move_cost <= _action_time_max:
				_color_mod = int(round(200*numbers.clip(_move_cost/float(_action_time_max), .75, 1)))
				_color = (_color_mod, 0, 0)
				
				_node['node']['busy_pos'].append(pos)
			
			else:
				_color = (200, 200, 200)
			
			if _action_time_max:
				_move_cost += stats.get_speed(entity)
				
				if _move_cost >= _action_time_max:
					_action_time_max = 0
					_move_cost = 0
			
			if pos[0]-x_mod < 0 or pos[1]-y_mod < 0 or pos[0]-x_mod >= _surface_width or pos[1]-y_mod >= _surface_height:
				continue
			
			display.write_char('nodes', pos[0]-x_mod, pos[1]-y_mod, chr(177), fore_color=_color)
		
		if _node['node']['draw_path']:
			_last_x, _last_y = (_node['node']['x'], _node['node']['y'])
