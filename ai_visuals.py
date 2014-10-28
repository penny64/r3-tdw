from framework import movement, entities, numbers, shapes, stats

import ai_factions
import mapgen
import zones
import items
import life

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
	                                 'bullet': [],
	                                 'corpse': []}
	
	_active_solids = zones.get_active_solids(entity)
	
	for entity_id in entities.get_entity_group('items'):
		_item = entities.get_entity(entity_id)
		
		if not _item['stats']['type'] in entity['ai']['visible_items']:
			continue
		
		if _item['stats']['owner']:
			continue
		
		_distance = numbers.distance(movement.get_position(entity), movement.get_position(_item))
		
		if _distance >= stats.get_vision(entity):
			continue
		
		for pos in shapes.line(movement.get_position(entity), movement.get_position(_item)):
			if pos in _active_solids:
				break
		else:
			entity['ai']['visible_items'][_item['stats']['type']].append(entity_id)
			
			entities.trigger_event(_item, 'seen', target_id=entity['_id'])

def build_life_list(entity):
	entity['ai']['visible_targets'] = []
	_nearest_target = {'target_id': None, 'distance': 0}
	_solids = zones.get_active_solids(entity)
	_visible_life = set()
	_vision = stats.get_vision(entity)
	_visible_by_friendlies = [entities.get_entity(e)['ai']['visible_targets'] for e in entity['ai']['life_memory'] if not entity['ai']['life_memory'][e]['is_target'] and e in entities.ENTITIES]
	
	#Warning: Makes AI super smart
	_visible_by_friendlies = [item for sublist in _visible_by_friendlies for item in sublist]
	
	for entity_id in entities.get_entity_group('life'):
		if entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		if not entity_id in entity['ai']['life_memory']:
			life.create_life_memory(entity, entity_id)
		
		if not ai_factions.is_enemy(entity, entity_id):
			_visible = True
		
		else:
			if numbers.distance(movement.get_position(entity), movement.get_position(_target)) > _vision:
				if entity['ai']['life_memory'][entity_id]['can_see'] and ai_factions.is_enemy(entity, _target['_id']):
					entities.trigger_event(entity, 'target_lost', target_id=entity_id)
				
				if entity_id in _visible_by_friendlies:
					entity['ai']['life_memory'][entity_id]['in_los'] = False
					entity['ai']['life_memory'][entity_id]['can_see'] = True
					
					_visible = True
				else:
					entity['ai']['life_memory'][entity_id]['can_see'] = False
					entity['ai']['life_memory'][entity_id]['in_los'] = False
					
					if entity_id in entity['ai']['visible_life']:
						entity['ai']['visible_life'].remove(entity_id)
					
					_visible = False
				
			else:
				for pos in shapes.line(movement.get_position(entity), movement.get_position(_target)):
					if pos in _solids:
						if entity['ai']['life_memory'][entity_id]['can_see'] and ai_factions.is_enemy(entity, _target['_id']):
							entities.trigger_event(entity, 'target_lost', target_id=entity_id)
						
						if entity_id in _visible_by_friendlies:
							entity['ai']['life_memory'][entity_id]['in_los'] = False
							entity['ai']['life_memory'][entity_id]['can_see'] = True
							
							_visible = True
						
						else:
							entity['ai']['life_memory'][entity_id]['can_see'] = False
							entity['ai']['life_memory'][entity_id]['in_los'] = False
							
							if entity_id in entity['ai']['visible_life']:
								entity['ai']['visible_life'].remove(entity_id)
							
							_visible = False
						
						break
				else:
					entity['ai']['life_memory'][entity_id]['in_los'] = True
					_visible = True
		
		if not _visible and entity['ai']['life_memory'][entity_id]['seen_time'] > 0:
			_visible = True
			
			entity['ai']['life_memory'][entity_id]['in_los'] = False
			entity['ai']['life_memory'][entity_id]['can_see'] = True
			
			entity['ai']['life_memory'][entity_id]['seen_time'] -= 1
			
			if entity_id in entity['ai']['visible_life']:
				entity['ai']['visible_life'].remove(entity_id)
		
		elif not _visible and entity_id in entity['ai']['visible_life']:
			entity['ai']['visible_life'].remove(entity_id)
		
		if _visible:
			_previous_last_seen_at = entity['ai']['life_memory'][entity_id]['last_seen_at']
			_target_position = movement.get_position(_target)[:]
			
			entity['ai']['life_memory'][entity_id]['is_lost'] = False
			
			if entity['ai']['life_memory'][entity_id]['in_los']:
				if entity['ai']['life_memory'][entity_id]['seen_time'] < 30:
					entity['ai']['life_memory'][entity_id]['seen_time'] += 1
			
			else:
				entity['ai']['life_memory'][entity_id]['seen_time'] -= 1
				
				if entity['ai']['life_memory'][entity_id]['seen_time'] < 0 and entity_id in entity['ai']['visible_life']:
					entity['ai']['visible_life'].remove(entity_id)
					entity['ai']['life_memory'][entity_id]['in_los'] = False
			
			if movement.get_position(_target) == _previous_last_seen_at:
				_new_last_seen_at = _previous_last_seen_at
			
			else:
				_new_last_seen_at = _target_position
			
			_is_target = ai_factions.is_enemy(entity, _target['_id'])
			_profile = {'distance': numbers.distance(movement.get_position(entity), movement.get_position(_target)),
				        'is_target': _is_target,
				        'is_armed': items.get_items_in_holder(_target, 'weapon'),
			            'is_lost': False,
			            'can_see': True,
			            'last_seen_at': _new_last_seen_at,
			            'last_seen_velocity': None}
			
			if not entity_id in entity['ai']['visible_life']:
				entities.trigger_event(entity, 'new_target_spotted', target_id=entity_id)
			
			if entity['ai']['life_memory'][entity_id]['in_los']:
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
	
	for t in entity['ai']['life_memory']:
		if not 'is_lost' in entity['ai']['life_memory'][t]:
			print entity['ai']['life_memory'][t]
	
	entity['ai']['visible_targets'] = list(entity['ai']['visible_life'] & entity['ai']['targets'])
	entity['ai']['targets_to_search'] = [t for t in entity['ai']['life_memory'].keys() if entity['ai']['life_memory'][t]['is_lost'] and not entity['ai']['life_memory'][t]['searched_for'] and t in entities.ENTITIES]
	
	if _nearest_target['target_id']:
		if not entity['ai']['nearest_target'] == _nearest_target['target_id']:
			entity['ai']['meta']['has_firing_position'] = True
		
		entity['ai']['nearest_target'] = _nearest_target['target_id']
	
	elif entity['ai']['targets']:
		for target_id in list(entity['ai']['targets']):
			_target = entity['ai']['life_memory'][target_id]
			
			if not target_id in entities.ENTITIES or _target['is_lost']:
				entity['ai']['targets'].remove(target_id)
				
				continue
			
			_distance = numbers.distance(movement.get_position(entity), _target['last_seen_at'])
			
			if not _nearest_target['target_id'] or _distance < _nearest_target['distance']:
				_nearest_target['target_id'] = target_id
				_nearest_target['distance'] = _distance
		
		if not entity['ai']['nearest_target'] == _nearest_target['target_id']:
			entity['ai']['meta']['has_firing_position'] = True
		
		entity['ai']['nearest_target'] = _nearest_target['target_id']

def cleanup(entity):
	for entity_id in entity['ai']['life_memory'].keys():
		if not entity_id in entities.ENTITIES:
			entity['ai']['life_memory'][entity_id]['can_see'] = False
	
	for target_id in list(entity['ai']['targets']):
		if not target_id in entities.ENTITIES:
			entity['ai']['targets'].remove(target_id)
	
	for entity_id in list(entity['ai']['visible_life']):
		if not entity_id in entities.ENTITIES:
			entity['ai']['visible_life'].remove(entity_id)
