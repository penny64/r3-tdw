from framework import entities, tile, timers, movement, stats, flags, numbers, shapes

import ai_factions
import effects
import mapgen
import camera
import nodes
import items
import noise
import ai

import random


def _create(x, y, health, speed, name, faction='Rogues', has_ai=False, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')

	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity)
	timers.register(_entity)
	stats.register(_entity, health, speed, name=name)
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)

	if has_ai:
		ai.register_human(_entity)
	
	ai_factions.register(_entity, faction)

	entities.create_event(_entity, 'get_and_store_item')
	entities.create_event(_entity, 'get_and_hold_item')
	entities.create_event(_entity, 'reload')
	entities.create_event(_entity, 'shoot')
	entities.register_event(_entity, 'get_and_store_item', get_and_store_item)
	entities.register_event(_entity, 'get_and_hold_item', get_and_hold_item)
	entities.register_event(_entity, 'reload', reload_weapon)
	entities.register_event(_entity, 'shoot', shoot_weapon)
	entities.register_event(_entity, 'heard_noise', handle_heard_noise)
	entities.register_event(_entity, 'position_changed',
	                        lambda e, **kwargs: entities.trigger_event(e,
	                                                                   'create_noise',
	                                                                   volume=25,
	                                                                   text='?',
	                                                                   callback=lambda t, x, y: entities.trigger_event(t,
	                                                                                                            'update_target_memory',
	                                                                                                            target_id=_entity['_id'],
	                                                                                                            key='last_seen_at',
	                                                                                                            value=[x, y])))

	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)

	return _entity

def human(x, y, name):
	_entity = _create(x, y, 100, 20, name, has_ai=True)

	entities.register_event(_entity,
				'hold_item',
				lambda e, item_id: effects.printer(_entity['tile']['x']-camera.X,
									_entity['tile']['y']-camera.Y-5,
									'+%s' % entities.get_entity(item_id)['stats']['name'],
									fore_color=(0, 255, 0),
									speed_mod=0.3,
									show_mod=1.0,
									moving=False,
									center=True))
	entities.register_event(_entity,
				'store_item',
				lambda e, item_id: effects.printer(_entity['tile']['x']-camera.X,
									_entity['tile']['y']-camera.Y-5,
									'+%s' % entities.get_entity(item_id)['stats']['name'],
									fore_color=(0, 255, 0),
									speed_mod=0.3,
									show_mod=1.0,
									moving=False,
									center=True))
	
	entities.register_event(_entity, 'heard_noise', effects.show_noise)

	return _entity

def human_runner(x, y, name):
	return _create(x, y, 100, 20, name, faction='Runners', fore_color=(200, 140, 190), has_ai=True)

def human_bandit(x, y, name):
	return _create(x, y, 100, 20, name, faction='Bandits', fore_color=(140, 140, 190), has_ai=True)

############
#Operations#
############

def handle_heard_noise(entity, x, y, text, direction, accuracy, callback):
	if accuracy <= .75 and accuracy < random.uniform(0, 1):
		return
	
	callback(entity, x, y)

def can_see_position(entity, position):
	for pos in shapes.line(movement.get_position(entity), position):
		if pos in mapgen.SOLIDS:
			return False
	
	return True

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
	_item = entities.get_entity(item_id)
	
	if timers.has_timer_with_name(entity, 'Getting %s' % _item['stats']['name'], fuzzy=True):
		return

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=30,
		                   name='Getting %s' % _item['stats']['name'],
		                   exit_callback=lambda _: _get_and_store_item(entity, item_id))

def _get_and_hold_item(entity, item_id):
	entities.trigger_event(entity, 'hold_item', item_id=item_id)

def get_and_hold_item(entity, item_id):
	_item = entities.get_entity(item_id)
	
	if timers.has_timer_with_name(entity, 'Getting %s' % _item['stats']['name'], fuzzy=True):
		return

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=30,
		                   name='Getting %s' % _item['stats']['name'],
		                   exit_callback=lambda _: _get_and_hold_item(entity, item_id))

def _reload_weapon(entity, weapon_id, ammo_id):
	_weapon = entities.get_entity(weapon_id)
	_ammo = entities.get_entity(ammo_id)
	_weapon_ammo = flags.get_flag(_weapon, 'ammo')
	_weapon_ammo_max = flags.get_flag(_weapon, 'ammo_max')
	_ammo_count = flags.get_flag(_ammo, 'ammo')

	if _weapon_ammo == _weapon_ammo_max:
		return

	_need_ammo = numbers.clip(_weapon_ammo_max - _weapon_ammo, 1, _ammo_count)
	_ammo_count -= _need_ammo

	entities.trigger_event(_weapon, 'set_flag', flag='ammo', value=_weapon_ammo + _need_ammo)

	if _ammo_count:
		entities.trigger_event(_ammo, 'set_flag', flag='ammo', value=_ammo_count)
	else:
		entities.delete_entity(_ammo)

def reload_weapon(entity):
	if timers.has_timer_with_name(entity, 'Reloading'):
		return

	_weapon = items.get_items_in_holder(entity, 'weapon')[0]
	_ammo = items.get_items_matching(entity, {'type': 'ammo'})[0]

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=30,
		                   name='Reloading',
		                   exit_callback=lambda _: _reload_weapon(entity, _weapon, _ammo))

def _shoot_weapon(entity, weapon_id, target_id):
	_weapon = entities.get_entity(weapon_id)
	_x, _y = movement.get_position(entities.get_entity(_weapon['stats']['owner']))
	_tx, _ty = movement.get_position(entities.get_entity(target_id))

	entities.trigger_event(_weapon, 'flag_sub', flag='ammo', value=1)
	entities.trigger_event(entity,
	                       'create_noise',
	                       volume=80,
	                       direction=numbers.direction_to((_x, _y), (_tx, _ty)),
	                       text='BAM',
	                       callback=lambda t, x, y: entities.trigger_event(t,
	                                                                'update_target_memory',
	                                                                target_id=entity['_id'],
	                                                                key='last_seen_at',
	                                                                value=[x, y]))	

	items.bullet(_x, _y, _tx, _ty, 1)

def shoot_weapon(entity, target_id):
	if timers.has_timer_with_name(entity, 'Shoot'):
		return

	_weapon = items.get_items_in_holder(entity, 'weapon')[0]
	_ammo = flags.get_flag(entities.get_entity(_weapon), 'ammo')

	if not _ammo:
		return

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=60,
		                   name='Shoot',
		                   enter_callback=lambda _: _shoot_weapon(entity, _weapon, target_id))