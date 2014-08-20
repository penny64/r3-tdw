from framework import entities, numbers, movement, timers, shapes, flags

import mapgen
import life
import ai


def get_nearest_entity_in_list(entity, entity_list):
	_nearest_entity = {'entity': None, 'distance': 0}
	
	for entity_id in entity_list:
		_entity = entities.get_entity(entity_id)
		_distance = numbers.distance(movement.get_position(entity), movement.get_position(_entity))
		
		if not _nearest_entity['entity'] or _distance < _nearest_entity['distance']:
			_nearest_entity['entity'] = _entity
			_nearest_entity['distance'] = _distance
	
	return _nearest_entity['entity']


#########
#Actions#
#########

def _get_item(entity, item_id, hold=False, weight=None):
	_item = entities.get_entity(item_id)
	_x, _y = movement.get_position(_item)
	_distance = numbers.distance(movement.get_position(entity), (_x, _y))
	
	if weight:
		ai.set_meta_weight(entity, weight, 10*numbers.clip(_distance/30.0, 0, 1))
	
	if _distance:
		movement.walk_to_position(entity, _x, _y)
	
	else:
		if hold:
			life.get_and_hold_item(entity, item_id)
		else:
			life.get_and_store_item(entity, item_id)

#TODO: Combine these

def get_weapon(entity):
	_nearest_weapon = get_nearest_entity_in_list(entity, entity['ai']['visible_items']['weapon'])
	
	if not _nearest_weapon:
		return
	
	_get_item(entity, _nearest_weapon['_id'], hold=True, weight='find_weapon')

def get_ammo(entity):
	_nearest_weapon = get_nearest_entity_in_list(entity, entity['ai']['visible_items']['ammo'])
	
	if not _nearest_weapon:
		return
	
	_get_item(entity, _nearest_weapon['_id'], weight='find_ammo')

def get_container(entity):
	_nearest_weapon = get_nearest_entity_in_list(entity, entity['ai']['visible_items']['container'])
	
	if not _nearest_weapon:
		return
	
	_get_item(entity, _nearest_weapon['_id'], weight='find_container', hold=True)

def find_cover(entity):
	#TODO: Sort when building visible AI list
	_target = entities.get_entity(entity['ai']['visible_life']['targets'][0])
	_x, _y = movement.get_position(entity)
	_tx, _ty = movement.get_position(_target)
	_closest_node = {'node': None, 'distance': 0}
	
	for node_x, node_y in mapgen.NODE_GRID:
		_distance = numbers.distance((_x, _y), (node_x, node_y))
		
		#TODO: Replace with sight distance
		if _distance >= 40:
			continue
		
		if _closest_node['node'] and _distance >= _closest_node['distance']:
			continue
		
		if life.can_see_position(_target, (node_x, node_y)):
			continue
		
		if not _closest_node['node'] or _distance < _closest_node['distance']:
			_closest_node['node'] = (node_x, node_y)
			_closest_node['distance'] = _distance
	
	if not _closest_node['node']:
		print 'No cover.'
		
		return
	
	movement.walk_to_position(entity, _closest_node['node'][0], _closest_node['node'][1])

def find_firing_position(entity):
	#TODO: Sort when building visible AI list
	_target = entities.get_entity(entity['ai']['visible_life']['targets'][0])
	_x, _y = movement.get_position(entity)
	_tx, _ty = entity['ai']['life_memory'][_target['_id']]['last_seen_at']
	_closest_node = {'node': None, 'distance': 0}
	_can_see = entity['ai']['life_memory'][_target['_id']]['can_see']
	
	if _can_see:
		_max_distance = 25
	else:
		_max_distance = 10
	
	for node_x, node_y in mapgen.NODE_GRID:
		_distance = numbers.distance((_tx, _ty), (node_x, node_y))
		
		#TODO: Replace with sight distance
		if _distance >= _max_distance:
			continue
		
		if _closest_node['node'] and _distance >= _closest_node['distance']:
			continue
		
		_continue = False
		
		for pos in shapes.line((_tx, _ty), (node_x, node_y)):
			if pos in mapgen.SOLIDS:
				_continue = True
				
				break
		
		if _continue:
			continue
		
		if not _closest_node['node'] or _distance < _closest_node['distance']:
			_closest_node['node'] = (node_x, node_y)
			_closest_node['distance'] = _distance
	
	if not _closest_node['node']:
		print 'No cover.'
		
		return
	
	movement.walk_to_position(entity, _closest_node['node'][0], _closest_node['node'][1])

def _search_for_target(entity):
	_nodes = flags.get_flag(entity, 'search_nodes')
	_node_list = _nodes.keys()
	_node_list.sort()	
	_node_x, _node_y = _nodes[_node_list[0]][0]
	_distance = numbers.distance(movement.get_position(entity), (_node_x, _node_y))
	
	if _distance <= 2:
		_nodes[_node_list[0]].remove((_node_x, _node_y))
		
		if not _nodes[_node_list[0]]:
			print 'Cleared node', _node_x, _node_y
			del _nodes[_node_list[0]]
	else:
		movement.walk_to_position(entity, _node_x, _node_y)

def search_for_target(entity):
	if flags.has_flag(entity, 'search_nodes'):
		_search_for_target(entity)
		return
	
	_target = entities.get_entity(entity['ai']['visible_life']['targets'][0])
	_x, _y = movement.get_position(entity)
	_tx, _ty = entity['ai']['life_memory'][_target['_id']]['last_seen_at']
	_closest_node = {'node': None, 'distance': 0}
	_nodes_to_search = {}
	
	entities.trigger_event(entity, 'set_flag', flag='search_nodes', value=_nodes_to_search)
	
	for node_x, node_y in mapgen.NODE_GRID:
		_distance = numbers.distance((_tx, _ty), (node_x, node_y))
		
		if _distance >= 30:
			continue
		
		if _closest_node['node'] and _distance >= _closest_node['distance']:
			continue
		
		_continue = False
		
		if _distance in _nodes_to_search:
			_nodes_to_search[_distance].append((node_x, node_y))
		else:
			_nodes_to_search[_distance] = [(node_x, node_y)]

def reload_weapon(entity):
	life.reload_weapon(entity)

def shoot_weapon(entity):
	_target = entity['ai']['visible_life']['targets'][0]
	
	entities.trigger_event(entity, 'shoot', target_id=_target)
