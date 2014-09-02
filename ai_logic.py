from framework import entities, numbers, movement, timers, shapes, flags

import ai_debugger
import mapgen
import zones
import life
import ai

import time


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
	_target = entities.get_entity(entity['ai']['nearest_target'])
	_x, _y = movement.get_position(entity)
	_tx, _ty = movement.get_position(_target)
	_closest_node = {'node': None, 'distance': 0}
	
	if flags.has_flag(entity, 'cover_data'):
		_cover_data = flags.get_flag(entity, 'cover_data')
		
		if _target['_id'] == _cover_data['target']:
			if not life.can_see_position(_target, _cover_data['node']):
				movement.walk_to_position(entity, _cover_data['node'][0], _cover_data['node'][1])
				
				return
			
			flags.delete_flag(entity, 'cover_data')
	
	for node_x, node_y in zones.get_active_node_grid():
		_distance = numbers.distance((_x, _y), (node_x, node_y))
		
		#TODO: Replace with sight distance
		if _distance >= 30:
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
	
	entities.trigger_event(entity, 'set_flag', flag='cover_data', value={'target': _target['_id'], 'node': _closest_node['node'][:]})
	
	movement.walk_to_position(entity, _closest_node['node'][0], _closest_node['node'][1])

def find_firing_position(entity):
	_target = entities.get_entity(entity['ai']['nearest_target'])
	_x, _y = movement.get_position(entity)
	_tx, _ty = entity['ai']['life_memory'][_target['_id']]['last_seen_at']
	_closest_node = {'node': None, 'distance': 0}
	_can_see = entity['ai']['life_memory'][_target['_id']]['can_see']
	
	_t = time.time()
	
	if _can_see:
		_max_distance = 16
	else:
		_max_distance = 16
	
	if flags.has_flag(entity, 'fire_data'):
		_fire_data = flags.get_flag(entity, 'fire_data')
		
		if _target['_id'] == _fire_data['target']:
			_distance = numbers.distance((_tx, _ty), _fire_data['node'])
					
			#TODO: Replace with sight distance
			if _distance < _max_distance:
				_invalid = False
				
				for pos in shapes.line((_tx, _ty), _fire_data['node']):
					if pos in zones.get_active_solids(_target, ignore_entities=[entity['_id']]):
						_invalid = True
						break
				
				if not _invalid:
					movement.walk_to_position(entity, _fire_data['node'][0], _fire_data['node'][1])
					
					return
				
				_node = entities.get_entity(zones.get_active_node_grid()[_fire_data['node']])
				entities.trigger_event(_node, 'set_flag', flag='owner', value=None)
				
				flags.delete_flag(entity, 'fire_data')
	
	for node_x, node_y in zones.get_active_node_grid():
		_distance = numbers.distance((_tx, _ty), (node_x, node_y))
		
		#TODO: Replace with sight distance
		if _distance >= _max_distance:
			continue
		
		if _closest_node['node'] and _distance >= _closest_node['distance']:
			continue
		
		_node = entities.get_entity(zones.get_active_node_grid()[(node_x, node_y)])
		
		if _node['flags']['owner']['value']:
			print 'Ignore'
			continue
		
		_continue = False
		
		for pos in shapes.line((_tx, _ty), (node_x, node_y)):
			if pos in zones.get_active_solids(_target, ignore_entities=[entity['_id']]):
				_continue = True
				
				break
		
		if _continue:
			continue
		
		if not _closest_node['node'] or _distance < _closest_node['distance']:
			_closest_node['node'] = (node_x, node_y)
			_closest_node['distance'] = _distance
	
	if not _closest_node['node']:
		entity['ai']['meta']['has_firing_position'] = False
		
		return
	
	_node = entities.get_entity(zones.get_active_node_grid()[_closest_node['node']])
	
	entities.trigger_event(entity, 'set_flag', flag='fire_data', value={'target': _target['_id'], 'node': _closest_node['node'][:]})
	entities.trigger_event(_node, 'set_flag', flag='owner', value=entity['_id'])
	
	movement.walk_to_position(entity, _closest_node['node'][0], _closest_node['node'][1])

def _search_for_target(entity, target_id):
	_nodes = flags.get_flag(entity, 'search_nodes')
	
	if not _nodes:
		entity['ai']['targets'].remove(target_id)
		flags.delete_flag(entity, 'search_nodes')
		
		entities.trigger_event(entity, 'target_search_failed', target_id=target_id)
		
		return
	
	_node_list = _nodes.keys()
	_node_list.sort()	
	_node_x, _node_y = _nodes[_node_list[0]][0]
	_distance = numbers.distance(movement.get_position(entity), (_node_x, _node_y))
	
	if _distance <= 15 and life.can_see_position(entity, (_node_x, _node_y)):
		_nodes[_node_list[0]].remove((_node_x, _node_y))
		
		if not _nodes[_node_list[0]]:
			del _nodes[_node_list[0]]
	else:
		movement.walk_to_position(entity, _node_x, _node_y)

def search_for_target(entity):
	_target = entities.get_entity(entity['ai']['nearest_target'])
	
	if flags.has_flag(entity, 'search_nodes'):
		_search_for_target(entity, _target['_id'])
		
		return
	
	_x, _y = movement.get_position(entity)
	_tx, _ty = entity['ai']['life_memory'][_target['_id']]['last_seen_at']
	_nodes_to_search = {}
	
	if entity['ai']['life_memory'][_target['_id']]['last_seen_velocity']:
		_vx, _vy = entity['ai']['life_memory'][_target['_id']]['last_seen_velocity']
		_tx + _vx*6
		_ty + _vy*6
	
	entities.trigger_event(entity, 'set_flag', flag='search_nodes', value=_nodes_to_search)
	
	_t = time.time()
	
	for node_x, node_y in zones.get_active_node_grid():
		_distance = numbers.distance((_tx, _ty), (node_x, node_y))
		
		if _distance >= 30:
			continue
		
		_continue = False
		
		for pos in shapes.line((_tx, _ty), (node_x, node_y)):
			if pos in zones.get_active_solids(entity):
				_continue = True
				
				break
		
		if _continue:
			continue
		
		if _distance in _nodes_to_search:
			if not (node_x, node_y) in _nodes_to_search[_distance]:
				_nodes_to_search[_distance].append((node_x, node_y))
		else:
			_nodes_to_search[_distance] = [(node_x, node_y)]

def find_melee_position(entity):
	_target = entity['ai']['nearest_target']
	_x, _y = entity['ai']['life_memory'][_target]['last_seen_at']
	_closest_pos = {'pos': None, 'distance': 0}
	
	for x, y in [(_x-1, _y), (_x+1, _y), (_x, _y-1), (_x, _y+1), (_x-1, _y-1), (_x+1, _y-1), (_x-1, _y+1), (_x+1, _y+1)]:
		_distance = numbers.distance(movement.get_position(entity), (x, y))
		
		if not _closest_pos['pos'] or _distance < _closest_pos['distance']:
			_closest_pos['distance'] = _distance
			_closest_pos['pos'] = (x, y)
	
	movement.walk_to_position(entity, _closest_pos['pos'][0], _closest_pos['pos'][1])

def reload_weapon(entity):
	life.reload_weapon(entity)

def shoot_weapon(entity):
	_target = entity['ai']['nearest_target']
	
	entities.trigger_event(entity, 'shoot', target_id=_target)

def melee(entity):
	_target = entity['ai']['nearest_target']