from framework import movement, entities, numbers, shapes

import mapgen
import items


def build_item_list(entity):
	entity['ai']['visible_items'] = {'weapon': [],
	                                 'container': [],
	                                 'ammo': []}
	
	for entity_id in entities.get_entity_group('items'):
		_item = entities.get_entity(entity_id)
		
		if not _item['stats']['type'] in entity['ai']['visible_items']:
			continue
		
		if _item['stats']['owner']:
			continue
		
		_distance = numbers.distance(movement.get_position(entity), movement.get_position(_item))
		
		if _distance >= 100:
			continue
		
		for pos in shapes.line(movement.get_position(entity), movement.get_position(_item)):
			if pos in mapgen.SOLIDS:
				break
		else:
			entity['ai']['visible_items'][_item['stats']['type']].append(entity_id)

def build_life_list(entity):
	entity['ai']['visible_life'] = set()
	entity['ai']['visible_targets'] = []
	_nearest_target = {'target_id': None, 'distance': 0}
	
	for entity_id in entities.get_entity_group('life'):
		if entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		if not entity_id in entity['ai']['life_memory']:
			entity['ai']['life_memory'][entity_id] = {'distance': -1,
				                                      'is_target': False,
				                                      'is_armed': False,
			                                          'can_see': False,
			                                          'last_seen_at': None}
		
		for pos in shapes.line(movement.get_position(entity), movement.get_position(_target)):
			if pos in mapgen.SOLIDS:
				entity['ai']['life_memory'][entity_id]['can_see'] = False
				
				break
		else:
			_is_target = not entity['stats']['faction'] == _target['stats']['faction']
			_profile = {'distance': numbers.distance(movement.get_position(entity), movement.get_position(_target)),
				        'is_target': _is_target,
				        'is_armed': items.get_items_in_holder(_target, 'weapon'),
			            'can_see': True,
			            'last_seen_at': movement.get_position(_target)[:],
			            'last_seen_velocity': None}
			
			entity['ai']['visible_life'].add(entity_id)
			
			if _is_target:
				entity['ai']['targets'].add(entity_id)
				
				_distance = numbers.distance(movement.get_position(entity), movement.get_position_via_id(entity_id))
				
				if not _nearest_target['target_id'] or _distance < _nearest_target['distance']:
					_nearest_target['distance'] = _distance
					_nearest_target['target_id'] = entity_id
			
			if entity['ai']['life_memory'][entity_id]['last_seen_at']:
				_last_seen_at = entity['ai']['life_memory'][entity_id]['last_seen_at'][:]
				_velocity = (_profile['last_seen_at'][0]-_last_seen_at[0], _profile['last_seen_at'][1]-_last_seen_at[1])
				
				_profile['last_seen_velocity'] = _velocity
			else:
				_profile['last_seen_velocity'] = None
				
			entity['ai']['life_memory'][entity_id].update(_profile)
	
	entity['ai']['visible_targets'] = list(entity['ai']['visible_life'] & entity['ai']['targets'])
	entity['ai']['nearest_target'] = _nearest_target['target_id']
