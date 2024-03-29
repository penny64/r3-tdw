#########
#WARNING#
#########

#This file has been marked as MESSY by flags (Luke M.) on 9/16/14
#MESSY files may be hard to read or are trending towards an unmaintainable
#state. This file will be refactored heavily in the future - keep this in
#mind when adding additional code.
#
#10/13/14 - Starting to look a bit better. Most issues are with some of the node path
#interactions.


from framework import entities, display, movement, numbers, pathfinding, tile, controls, stats, timers

import ai_factions
import constants
import ui_cursor
import ui_dialog
import ui_menu
import mapgen
import camera
import zones
import items

import time

DRAGGING_NODE = None
LAST_CLICKED_POS = None
SELECTING_TARGET_CALLBACK = None


def register(entity):
	entity['node_grid'] = {'nodes': {},
	                       'path': [],
	                       'redraw_path': True}
	
	entities.register_event(entity, 'logic', logic)
	entities.register_event(entity, 'draw', draw_path)
	entities.register_event(entity, 'position_changed', _redraw_first_node)

def handle_mouse_movement(entity, x, y, vx, vy):
	if not DRAGGING_NODE:
		return
	
	if (vx, vy) in zones.get_active_solids(entity):
		return
	
	entities.trigger_event(DRAGGING_NODE['node'], 'set_position', x=vx, y=vy)
	entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 255))
	
	DRAGGING_NODE['node']['x'] = vx
	DRAGGING_NODE['node']['y'] = vy
	DRAGGING_NODE['node']['path'] = []
	
	redraw_path(entity)
	entities.trigger_event(entity, 'stop')

def handle_mouse_pressed(entity, x, y, button):
	global DRAGGING_NODE, LAST_CLICKED_POS, SELECTING_TARGET_CALLBACK
	
	if ui_menu.get_active_menu() or ui_menu.DELAY:
		return
	
	if timers.has_timer_with_name(entity, 'passout'):
		return
	
	_x = x+camera.X
	_y = y+camera.Y
	
	if button == 1:
		if DRAGGING_NODE:
			DRAGGING_NODE = None
		
		elif not (_x, _y) in zones.get_active_solids(entity):
			if not DRAGGING_NODE:
				for entity_id in [t for t in entity['ai']['visible_life'] if entity['ai']['life_memory'][t]['can_see']]:
					if entity['_id'] == entity_id:
						continue
					
					_entity = entities.get_entity(entity_id)
					_tx, _ty = movement.get_position(_entity)
					
					if (_x, _y) == (_tx, _ty):
						if SELECTING_TARGET_CALLBACK:
							SELECTING_TARGET_CALLBACK(entity, entity_id)
							SELECTING_TARGET_CALLBACK = None
						else:
							LAST_CLICKED_POS = (_x, _y)
					
							create_life_interact_menu(entity, entity_id)
						
						return
				
				else:
					for entity_id in entities.get_entity_group('contexts'):
						_entity = entities.get_entity(entity_id)
						
						if not _entity['callback']:
							continue
						
						if (_entity['tile']['x'], _entity['tile']['y']) == (_x, _y):
							_entity['callback'](x+2, y-3)
							
							return
					
					else:
						for entity_id in list(entity['ai']['targets'] - entity['ai']['visible_life']):
							_tx, _ty = entity['ai']['life_memory'][entity_id]['last_seen_at']
							
							if (_tx, _ty-2) == (_x, _y):
								ui_dialog.create(x + 2, y - 3, '%s - Last seen <time>' % entities.get_entity(entity_id)['stats']['name'])
								
								return
							
						else:
							for entity_id in entities.get_entity_group('items'):
								_item = entities.get_entity(entity_id)
								
								if _item['stats']['owner']:
									continue
								
								if (_x, _y) == movement.get_position(_item):
									create_item_menu(entity, _item, _x, _y)
									
									return
							
							create_walk_node(entity, _x, _y, clear=True)
							
							return
			
			for node in entity['node_grid']['nodes'].values():
				if (_x, _y) == (node['node']['x'], node['node']['y']):
					DRAGGING_NODE = node
					entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 0))
					
					break
				
				if (_x, _y) in node['node']['path']:
					if not (_x, _y) in node['node']['busy_pos']:
						LAST_CLICKED_POS = (_x, _y)
						
						create_action_menu(entity, LAST_CLICKED_POS[0], LAST_CLICKED_POS[1], on_path=True)
					
					else:
						LAST_CLICKED_POS = None
					
					return
	
	elif button == 2:
		if DRAGGING_NODE:
			entities.trigger_event(DRAGGING_NODE['node'], 'set_fore_color', color=(255, 255, 255))
			
			DRAGGING_NODE = None
		
		else:
			for node in entity['node_grid']['nodes'].values():
				if (_x, _y) == (node['node']['x'], node['node']['y']):
					entity['node_grid']['path'].remove(node['node']['_id'])
					entities.delete_entity(node['node'])
					redraw_path(entity)
					
					del entity['node_grid']['nodes'][node['node']['_id']]
					
					if not entity['node_grid']['nodes']:
						clear_path(entity)
					
					break
			else:
				create_walk_node(entity, _x, _y)

def _create_node(entity, x, y, draw_path=False, passive=True, action_time=0, name='Node', callback_on_touch=True):
	global LAST_CLICKED_POS
	
	_path_index = -1
	
	if LAST_CLICKED_POS:
		_node_positions = [(p['node']['x'], p['node']['y']) for p in entity['node_grid']['nodes'].values() if not p['node']['name'] == chr(31)]
		
		for node_id in entity['node_grid']['path'][:]:
			_last_node = entity['node_grid']['nodes'][node_id]
			
			if LAST_CLICKED_POS in _last_node['node']['path']:
				_move_cost = 0
				
				for pos in _last_node['node']['path'][_last_node['node']['path'].index(LAST_CLICKED_POS):]:
					_move_cost += movement.get_move_cost(entity)
					
					if _move_cost < action_time and pos in _node_positions:
						return
				
				_path_index = entity['node_grid']['path'].index(node_id)
				entity['node_grid']['nodes'][entity['node_grid']['path'][_path_index]]['node']['action_time'] = action_time
				
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
		_path_index = len(entity['node_grid']['path'])
	
	entity['node_grid']['nodes'][_node['_id']] = {'node': _node,
	                                              'passive': passive,
	                                              'callback': None,
	                                              'call_on_touch': callback_on_touch}
	entity['node_grid']['path'].insert(_path_index, _node['_id'])
	
	return _node

def create_walk_node(entity, x, y, clear=False):
	_walk_speed = chr(31)
	
	if clear:
		clear_path(entity)
		redraw_path(entity)
	
	_node = _create_node(entity, x, y, draw_path=True, passive=False, name=_walk_speed, callback_on_touch=False)
	
	entities.trigger_event(_node, 'set_char', char='O')
	
	entity['node_grid']['nodes'][_node['_id']]['callback'] = lambda: entities.trigger_event(entity,
	                                                                                        'move_to_position',
	                                                                                        x=_node['x'],
	                                                                                        y=_node['y'],
	                                                                                        astar_map=zones.get_active_astar_map(),
	                                                                                        weight_map=zones.get_active_weight_map())

def create_action_node(entity, x, y, time, callback, on_path=False, icon='X', name='Action'):
	#_will_move = on_path
	
	#if not no_move:
	#	for node_id in entity['node_grid']['path']:
	#		_node = entity['node_grid']['nodes'][node_id]['node']
	#		
	#		if not (_node['x'], _node['y']) == (x, y):
	#			continue
	#		
	#		if _node['name'] == chr(31):
	#			_will_move = True
		
	#if not _will_move:
	#	create_walk_node(entity, x, y)
	
	_node = _create_node(entity, x, y, passive=False, action_time=time, callback_on_touch=True, name=name)
	
	if not _node:
		return
	
	entities.trigger_event(_node, 'set_char', char=icon)
	
	entity['node_grid']['nodes'][_node['_id']]['callback'] = callback

def logic(entity):
	_last_pos = None
	_stop_here = False
	
	for node_id in entity['node_grid']['path'][:]:
		_node = entity['node_grid']['nodes'][node_id]
		
		if not (_node['node']['x'], _node['node']['y']) == movement.get_position(entity):
			if _stop_here and not (_node['node']['x'], _node['node']['y']) == _last_pos:
				break
		
		_distance = numbers.distance((_node['node']['x'], _node['node']['y']), movement.get_position(entity))
		
		if _node['call_on_touch'] and _distance:
			continue
		
		elif not _distance:
			entity['node_grid']['path'].remove(node_id)
			del entity['node_grid']['nodes'][node_id]
			
			entities.delete_entity_via_id(node_id)
		
		_node['callback']()		
		
		if not _node['passive']:
			_stop_here = True
			_last_pos = (_node['node']['x'], _node['node']['y'])

def _redraw_first_node(entity, **kargs):
	_x, _y = movement.get_position(entity)
	
	for node_id in entity['node_grid']['path']:
		_node = entity['node_grid']['nodes'][node_id]['node']
		
		if (_x, _y) in _node['path']:
			if _node['draw_path']:
				_node['path'] = _node['path'][_node['path'].index((_x, _y)):]
				
				break

def create_action_menu(entity, x, y, on_path=False):
	_menu = ui_menu.create(ui_cursor.CURSOR['tile']['x']+2, ui_cursor.CURSOR['tile']['y']-1, title='Context')
	
	if items.get_items_in_holder(entity, 'weapon'):
		ui_menu.add_selectable(_menu, 'Shoot', lambda: select_target(x, y, on_path))
	
	ui_menu.add_selectable(_menu, 'Reload', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'reload'),
	                                                                   name='Reload',
	                                                                   on_path=on_path))
	ui_menu.add_selectable(_menu, 'Crouch', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'set_motion', motion='crouch'),
	                                                                   name='Crouch',
	                                                                   on_path=on_path))
	ui_menu.add_selectable(_menu, 'Crawl', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'set_motion', motion='crawl'),
	                                                                   name='Prone',
	                                                                   on_path=on_path))
	ui_menu.add_selectable(_menu, 'Stand', lambda: create_action_node(entity,
	                                                                   x,
	                                                                   y,
	                                                                   30,
	                                                                   lambda: entities.trigger_event(entity, 'set_motion', motion='stand'),
	                                                                   name='Stand',
	                                                                   on_path=on_path))

def create_mission_menu(entity, target_id):
	_menu = ui_menu.create(LAST_CLICKED_POS[0]-camera.X+2, LAST_CLICKED_POS[1]-camera.Y-4, title='Inquire')
	
	for mission_id in entity['missions']['active']:
		_mission = entities.get_entity(mission_id)
		
		ui_menu.add_title(_menu, _mission['title'])
		entities.trigger_event(_mission, 'get_details', menu=_menu, member_id=entity['_id'], target_id=target_id)

def create_talk_menu(entity, target_id):
	_menu = ui_menu.create(LAST_CLICKED_POS[0]-camera.X+2, LAST_CLICKED_POS[1]-camera.Y-4, title='Talk')
	_target = entities.get_entity(target_id)
	
	for mission_id in _target['missions']['inactive']:
		_mission = entities.get_entity(mission_id)
		
		ui_menu.add_selectable(_menu, _mission['title'], lambda: show_mission_details(entity, _mission))

def show_mission_details(entity, mission):
	entities.trigger_event(mission, 'get_briefing')
	
	_menu = ui_menu.create((constants.MAP_VIEW_WIDTH/2) - 10, (constants.MAP_VIEW_HEIGHT/2) - 10, title='Mission')
	
	ui_menu.add_selectable(_menu, 'Accept', lambda: accept_mission(entity, mission['_id']))
	ui_menu.add_selectable(_menu, 'Decline', lambda: ui_dialog.delete(ui_dialog.ACTIVE_DIALOG))

def accept_mission(entity, mission_id):
	entities.trigger_event(entity, 'add_mission', mission_id=mission_id)
	
	ui_dialog.delete(ui_dialog.ACTIVE_DIALOG)

def create_item_menu(entity, item, x, y, on_path=False):
	_menu = ui_menu.create(ui_cursor.CURSOR['tile']['x']+2, ui_cursor.CURSOR['tile']['y']-1, title='Context')
	
	if items.get_list_of_free_holders(entity, item['_id']) and item['stats']['equip_to']:
		ui_menu.add_selectable(_menu, 'Equip', lambda: create_action_node(entity,
		                                                                  x,
		                                                                  y,
		                                                                  30,
		                                                                  lambda: entities.trigger_event(entity, 'get_and_hold_item', item_id=item['_id']),
		                                                                  name='Equip %s' % item['stats']['name'],
		                                                                  on_path=on_path))
	
	if items.get_list_of_free_containers(entity, item['_id']):
		ui_menu.add_selectable(_menu, 'Store', lambda: create_action_node(entity,
		                                                                  x,
		                                                                  y,
		                                                                  30,
		                                                                  lambda: entities.trigger_event(entity, 'get_and_store_item', item_id=item['_id']),
		                                                                  name='Store %s' % item['stats']['name'],
		                                                                  on_path=on_path))
	
	entities.trigger_event(item, 'get_interactions', menu=_menu, target_id=entity['_id'])

def select_target(x, y, on_path):
	global SELECTING_TARGET_CALLBACK
	
	SELECTING_TARGET_CALLBACK = lambda entity, target: create_action_node(entity,
	                                                                      x,
	                                                                      y,
	                                                                      5,
	                                                                      lambda: entities.trigger_event(entity, 'shoot', target_id=target),
	                                                                      name='Shoot',
	                                                                      on_path=on_path)

def has_node_path(entity):
	return len(entity['node_grid']['path']) > 0

def clear_path(entity):
	for node_id in entity['node_grid']['path']:
		_last_node = entity['node_grid']['nodes'][node_id]
		
		entities.delete_entity(_last_node['node'])
	
	entities.trigger_event(entity, 'stop')
	entity['node_grid']['path'] = []
	entity['node_grid']['nodes'] = {}

def redraw_path(entity):
	for node in entity['node_grid']['nodes'].values():
		node['node']['path'] = []

def draw_path(entity, x_mod=0, y_mod=0):
	_last_x, _last_y = (0, 0)
	_node_ids = entity['node_grid']['path'][:]
	_action_time_max = 0
	_surface_width = display.get_surface('nodes')['width']
	_surface_height = display.get_surface('nodes')['height']
	
	for node_id in _node_ids:
		_node = entity['node_grid']['nodes'][node_id]
		
		if not _last_x:
			_last_x, _last_y = movement.get_position(entity)
		
		if (_last_x, _last_y) == (_node['node']['x'], _node['node']['y']):
			continue
		
		_node['node']['busy_pos'] = []
		
		if _node['node']['draw_path'] and not _node['node']['path']:
			_path = pathfinding.astar((_last_x, _last_y), (_node['node']['x'], _node['node']['y']), zones.get_active_astar_map(), zones.get_active_weight_map())
			
			if (_node['node']['x'], _node['node']['y']) in _path:
				_path.remove((_node['node']['x'], _node['node']['y']))
			
			_node['node']['path'] = _path
		
		_move_cost = 0
		for pos in _node['node']['path']:
			for node_id in _node_ids:
				_check_node = entity['node_grid']['nodes'][node_id]['node']
				
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
				_move_cost += movement.get_move_cost(entity)
				
				if _move_cost >= _action_time_max:
					_action_time_max = 0
					_move_cost = 0
			
			if pos[0]-x_mod < 0 or pos[1]-y_mod < 0 or pos[0]-x_mod >= _surface_width or pos[1]-y_mod >= _surface_height:
				continue
			
			display.write_char('nodes', pos[0]-x_mod, pos[1]-y_mod, chr(177), fore_color=_color)
		
		if _node['node']['draw_path']:
			_last_x, _last_y = (_node['node']['x'], _node['node']['y'])
