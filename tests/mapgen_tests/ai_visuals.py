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
	entity['ai']['visible_life'] = {'targets': {}}
	
	for entity_id in entities.get_entity_group('life'):
		if entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		for pos in shapes.line(movement.get_position(entity), movement.get_position(_target)):
			if pos in mapgen.SOLIDS:
				break
		else:
			_is_target = not entity['stats']['faction'] == _target['stats']['faction']
			_profile = {'distance': numbers.distance(movement.get_position(entity), movement.get_position(_target)),
				        'is_target': _is_target,
				        'is_armed': items.get_items_in_holder(_target, 'weapon')}
			
			if _is_target:
				entity['ai']['visible_life']['targets'][entity_id] = _profile
