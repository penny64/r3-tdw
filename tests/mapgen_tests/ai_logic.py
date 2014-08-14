from framework import entities, numbers, movement

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