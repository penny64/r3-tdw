from framework import movement, entities, numbers, shapes

import mapgen
import zones
import items

LIFE_MOVED = set()


def add_to_moved_life(entity):
	LIFE_MOVED.add(entity['_id'])

def reset_moved_entities():
	global LIFE_MOVED
	
	LIFE_MOVED = set()

def build_item_list(entity):
	entity['ai']['visible_items'] = {'weapon': [],
	                                 'container': [],
	                                 'ammo': [],
	                                 'bullet': []}
	
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
			if pos in zones.get_active_solids():
				break
		else:
			entity['ai']['visible_items'][_item['stats']['type']].append(entity_id)

def build_life_list(entity):
	entity['ai']['visible_targets'] = []
	_nearest_target = {'target_id': None, 'distance': 0}
	
	_visible_life = set()
	
	for entity_id in entities.get_entity_group('life'):
		if entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		if not entity_id in entity['ai']['life_memory']:
			entity['ai']['life_memory'][entity_id] = {'distance': -1,
				                                      'is_target': False,
				                                      'is_armed': False,
			                                          'can_see': False,
			                                          'last_seen_at': None,
			                                          'last_seen_velocity': None}
		
		for pos in shapes.line(movement.get_position(entity), movement.get_position(_target)):
			if pos in zones.get_active_solids():
				if entity['ai']['life_memory'][entity_id]['can_see'] and not entity['ai']['faction'] == _target['ai']['faction']:
					entities.trigger_event(entity, 'target_lost', target_id=entity_id)
				
				entity['ai']['life_memory'][entity_id]['can_see'] = False
				
				if entity_id in entity['ai']['visible_life']:
					entity['ai']['visible_life'].remove(entity_id)
				
				break
		else:
			_is_target = not entity['ai']['faction'] == _target['ai']['faction']
			_profile = {'distance': numbers.distance(movement.get_position(entity), movement.get_position(_target)),
				        'is_target': _is_target,
				        'is_armed': items.get_items_in_holder(_target, 'weapon'),
			            'can_see': True,
			            'last_seen_at': movement.get_position(_target)[:],
			            'last_seen_velocity': None}
			
			#_visible_life.add(entity_id)
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
			
			if not entity['ai']['life_memory'][entity_id]['can_see'] and _is_target:
				_could_not_see_target_before = True
			else:
				_could_not_see_target_before = False
			
			entity['ai']['life_memory'][entity_id].update(_profile)
			
			if _could_not_see_target_before:
				entities.trigger_event(entity, 'target_found', target_id=entity_id)
	
	#entity['ai']['visible_life'].update(_visible_life)
	entity['ai']['visible_targets'] = list(entity['ai']['visible_life'] & entity['ai']['targets'])
	
	if _nearest_target['target_id']:
		entity['ai']['nearest_target'] = _nearest_target['target_id']
	elif entity['ai']['targets']:
		for target_id in list(entity['ai']['targets']):
			_target = entity['ai']['life_memory'][target_id]
			_distance = numbers.distance(movement.get_position(entity), _target['last_seen_at'])
			
			if not _nearest_target['target_id'] or _distance < _nearest_target['distance']:
				_nearest_target['target_id'] = target_id
				_nearest_target['distance'] = _distance
		
		entity['ai']['nearest_target'] = _nearest_target['target_id']
