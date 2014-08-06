from framework import entities, tile, timers, movement, stats

import nodes


def _create(x, y, health, speed, name):
	_entity = entities.create_entity(group='life')
	
	tile.register(_entity, surface='life', char='@')
	movement.register(_entity)
	timers.register(_entity)
	stats.register(_entity, health, speed, name=name)
	nodes.register(_entity)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity


def human(x, y, name):
	return _create(x, y, 100, 10, name)


############
#Operations#
############

def get_status_string(entity):
	if entity['movement']['path']['positions']:
		return 'Moving'
	
	return 'Idle'