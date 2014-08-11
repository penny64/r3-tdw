from framework import entities, movement, tile


def _create(x, y, name, char, item_type):
	_entity = entities.create_entity(group='items')
	
	_entity['stats'] = {'name': name, 'type': item_type, 'owner': None}
	
	movement.register(_entity)
	tile.register(_entity, surface='items', char=char)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity


#######
#Items#
#######

def glock(x, y):
	return _create(x, y, 'Glock', 'P', 'gun')