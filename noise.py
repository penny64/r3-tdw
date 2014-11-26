from framework import entities, movement, numbers, tile, timers


def register(entity):
	entities.create_event(entity, 'create_noise')
	entities.create_event(entity, 'heard_noise')
	entities.register_event(entity, 'create_noise', create_noise)

	return entity

def create_noise(entity, text, volume, owner_can_hear=False, show_on_sight=False, direction=-1000, callback=None, context_callback=None):
	_x, _y = movement.get_position(entity)
	
	for entity_id in entities.get_entity_group('life'):
		if not owner_can_hear and entity['_id'] == entity_id:
			continue
		
		_target = entities.get_entity(entity_id)
		
		if entity['ai']['faction'] == _target['ai']['faction']:
			continue
		
		#TODO: Hearing stat
		_distance = numbers.distance(movement.get_position(entity), movement.get_position(_target))
		_accuracy = 1 - numbers.clip(_distance / float(volume), 0, 1)
		
		entities.trigger_event(_target,
		                       'heard_noise',
		                       x=_x,
		                       y=_y,
		                       text=text,
		                       direction=direction,
		                       show_on_sight=show_on_sight,
		                       accuracy=_accuracy,
		                       callback=callback,
		                       context_callback=context_callback)

def create_context(x, y, text, callback):
	_entity = entities.create_entity(group='contexts')
	_entity['text'] = text
	_entity['callback'] = callback
	
	tile.register(_entity, surface='effects', char='!', fore_color=(0, 200, 0))
	timers.register(_entity, use_system_event='logic')
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'animate', animation=['!', ' '], repeat=-1)
	entities.trigger_event(_entity, 'create_timer', time=120, exit_callback=entities.delete_entity)
	
	return _entity