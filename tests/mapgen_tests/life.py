from framework import entities, tile, timers, movement, stats

import items
import ai

import nodes


def _create(x, y, health, speed, name, faction='Neutral', has_ai=False, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity)
	timers.register(_entity)
	stats.register(_entity, health, speed, name=name, faction=faction)
	nodes.register(_entity)
	items.register(_entity)
	
	if has_ai:
		ai.register_human(_entity)
	
	entities.create_event(_entity, 'get_and_store_item')
	entities.register_event(_entity, 'get_and_store_item', get_and_store_item)
	entities.create_event(_entity, 'get_and_hold_item')
	entities.register_event(_entity, 'get_and_hold_item', get_and_hold_item)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	
	return _entity

def human(x, y, name):
	return _create(x, y, 100, 10, name, has_ai=True)

def human_runner(x, y, name):
	return _create(x, y, 100, 10, name, faction='Runners', fore_color=(200, 140, 190), has_ai=True)


############
#Operations#
############

def get_status_string(entity):
	_timer = timers.get_nearest_timer(entity)
	
	if _timer and _timer['name']:
		return _timer['name']
	
	if entity['movement']['path']['positions']:
		return 'Moving'
	
	return 'Idle'

def _get_and_store_item(entity, item_id):
	entities.trigger_event(entity, 'store_item', item_id=item_id)

def get_and_store_item(entity, item_id):
	if timers.has_timer_with_name(entity, 'get_and_store_item'):
		return
	
	_item = entities.get_entity(item_id)
	
	entities.trigger_event(entity,
	                       'create_timer',
	                       time=30,
	                       name='Getting %s' % _item['stats']['name'],
	                       exit_callback=lambda _: _get_and_store_item(entity, item_id))

def _get_and_hold_item(entity, item_id):
	entities.trigger_event(entity, 'hold_item', item_id=item_id)

def get_and_hold_item(entity, item_id):
	if timers.has_timer_with_name(entity, 'get_and_hold_item'):
		return
	
	_item = entities.get_entity(item_id)
	
	entities.trigger_event(entity,
	                       'create_timer',
	                       time=30,
	                       name='Getting %s' % _item['stats']['name'],
	                       exit_callback=lambda _: _get_and_hold_item(entity, item_id))
