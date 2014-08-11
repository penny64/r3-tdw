from framework import entities, tile, timers, movement, stats

import ai

import nodes


def _create(x, y, health, speed, name, faction='Neutral', has_ai=False, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity)
	timers.register(_entity)
	stats.register(_entity, health, speed, name=name, faction=faction)
	nodes.register(_entity)
	
	if has_ai:
		ai.register_human(_entity)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity

def human(x, y, name):
	return _create(x, y, 100, 10, name)

def human_runner(x, y, name):
	return _create(x, y, 100, 10, name, faction='Runners', fore_color=(200, 140, 190), has_ai=True)


############
#Operations#
############

def get_status_string(entity):
	if entity['movement']['path']['positions']:
		return 'Moving'
	
	return 'Idle'

def _pick_up_item(entity, item_id):
	_item = entities.get_entity(item_id)
	
	_item['stats']['owner'] = entity['_id']

def pick_up_item(entity, item_id):
	if timers.has_timer_with_name(entity, 'pick_up_item'):
		return
	
	_item = entities.get_entity(item_id)
	
	entities.trigger_event(entity, 'create_timer', time=30, exit_callback=lambda _: _pick_up_item(entity, item_id))
