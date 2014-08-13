from framework import movement, entities, numbers, shapes

import mapgen


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