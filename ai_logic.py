from framework import entities, numbers, movement, timers, shapes, flags, pathfinding

import ai_squad_director
import ai_factions
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
		movement.walk_to_position(entity, _x, _y, zones.get_active_astar_map(), zones.get_active_weight_map(), smp=True)
	
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
	_squad = entities.get_entity(ai_factions.FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']])
	_cover_position = ai_squad_director.get_cover_position(_squad, entity['_id'])
	
	if not _cover_position:
		return
	
	movement.walk_to_position(entity, _cover_position[0], _cover_position[1], zones.get_active_astar_map(), zones.get_active_weight_map())

def find_firing_position(entity):
	_squad = entities.get_entity(ai_factions.FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']])
	_x, _y = movement.get_position(entity)
	_fire_position = ai_squad_director.get_vantage_point(_squad, entity['_id'])
	
	if not _fire_position:
		return
	
	#if not numbers.distance((_x, _y), _fire_position) and not entity['ai']['visible_targets']:
	#	entity['ai']['meta']['has_lost_target'] = True
	
	movement.walk_to_position(entity, _fire_position[0], _fire_position[1], zones.get_active_astar_map(), zones.get_active_weight_map())

def find_push_position(entity):
	_squad = entities.get_entity(ai_factions.FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']])
	_x, _y = movement.get_position(entity)
	_push_position = ai_squad_director.get_push_position(_squad, entity['_id'])
	
	if not _push_position:
		return
	
	#if not numbers.distance((_x, _y), _push_position) and not entity['ai']['visible_targets']:
	#	entity['ai']['meta']['has_lost_target'] = True
	
	movement.walk_to_position(entity, _push_position[0], _push_position[1], zones.get_active_astar_map(), zones.get_active_weight_map())

def _search_for_target(entity, target_id):
	_nodes = flags.get_flag(entity, 'search_nodes')
	
	if not _nodes:
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
		movement.walk_to_position(entity, _node_x, _node_y, zones.get_active_astar_map(), zones.get_active_weight_map())

def search_for_target(entity):
	_lost_targets = entity['ai']['targets_to_search']
	
	if not _lost_targets:
		print 'Trying to search with no lost targets'
		
		return
	
	_closest_target = {'distance': 0, 'target_id': None}
	
	for target_id in _lost_targets:
		_memory = entity['ai']['life_memory'][target_id]
		_distance = numbers.distance(movement.get_position(entity), _memory['last_seen_at'])
		
		if not _closest_target['target_id'] or _distance < _closest_target['distance']:
			_closest_target['target_id'] = target_id
			_closest_target['distance'] = _distance
	
	_target = entities.get_entity(_closest_target['target_id'])
	_solids = zones.get_active_solids(entity)
	
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
	
	for node_x, node_y in zones.get_active_node_grid():
		_distance = numbers.distance((_tx, _ty), (node_x, node_y))
		
		if _distance >= 30:
			continue
		
		_continue = False
		
		for pos in shapes.line((_tx, _ty), (node_x, node_y)):
			if pos in _solids:
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
	_solids = zones.get_active_solids(entity, ignore_entities=[_target])
	
	for x, y in [(_x-1, _y), (_x+1, _y), (_x, _y-1), (_x, _y+1), (_x-1, _y-1), (_x+1, _y-1), (_x-1, _y+1), (_x+1, _y+1)]:
		if (x, y) in _solids:
			continue
		
		_distance = numbers.distance(movement.get_position(entity), (x, y))
		
		if not _closest_pos['pos'] or _distance < _closest_pos['distance']:
			_closest_pos['distance'] = _distance
			_closest_pos['pos'] = (x, y)
	
	movement.walk_to_position(entity, _closest_pos['pos'][0], _closest_pos['pos'][1], zones.get_active_astar_map(), zones.get_active_weight_map())

def reload_weapon(entity):
	life.reload_weapon(entity)

def shoot_weapon(entity):
	_target = entity['ai']['nearest_target']
	
	entities.trigger_event(entity, 'shoot', target_id=_target)

def melee(entity):
	_target = entity['ai']['nearest_target']