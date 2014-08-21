from framework import entities, movement, numbers


def register(entity):
	entities.create_event(entity, 'create_noise')
	entities.create_event(entity, 'heard_noise')
	entities.register_event(entity, 'create_noise', create_noise)

	return entity

def create_noise(entity, text, volume, callback=None):
	_x, _y = movement.get_position(entity)
	
	for entity_id in entities.get_entity_group('life'):
		if entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		#TODO: Hearing stat
		_distance = numbers.distance(movement.get_position(entity), movement.get_position(_target))
		_accuracy = 1 - numbers.clip(_distance / float(volume), 0, 1)
		
		entities.trigger_event(_target, 'heard_noise', x=_x, y=_y, text=text, accuracy=_accuracy, callback=callback)