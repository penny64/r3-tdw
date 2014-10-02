from framework import entities, tile, timers, movement, stats, flags, numbers, shapes

import ai_factions
import ai_visuals
import ui_dialog
import skeleton
import effects
import mapgen
import camera
import nodes
import items
import noise
import zones
import ai

import logging
import random


def _create_human(x, y, health, speed, name, vision=50, faction='Rogues', has_ai=False, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	entities.create_event(_entity, 'get_and_store_item')
	entities.create_event(_entity, 'get_and_hold_item')
	entities.create_event(_entity, 'reload')
	entities.create_event(_entity, 'shoot')
	entities.create_event(_entity, 'damage')
	entities.create_event(_entity, 'did_damage')

	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity, collisions=True)
	timers.register(_entity)
	stats.register(_entity, health, speed, vision, name=name)
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)
	skeleton.register(_entity)
	skeleton.create_limb(_entity, 'head', [], True, 0.1)
	skeleton.create_limb(_entity, 'chest', ['head'], True, 0.88)
	skeleton.create_limb(_entity, 'torso', ['chest'], True, 0.75)
	skeleton.create_limb(_entity, 'left arm', ['chest'], False, 0.3, can_sever=True, stat_mod={'accuracy': .22})
	skeleton.create_limb(_entity, 'right arm', ['chest'], False, 0.3, can_sever=True, stat_mod={'accuracy': .22})
	skeleton.create_limb(_entity, 'left leg', ['torso'], False, 0.45, can_sever=True, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'right leg', ['torso'], False, 0.45, can_sever=True, stat_mod={'speed': .4})

	if has_ai:
		ai.register_human(_entity)

	entities.register_event(_entity, 'post_tick', ai_visuals.cleanup)
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
	entities.register_event(_entity, 'damage',
	                        lambda e, **kwargs: entities.trigger_event(e,
	                                                                   'create_noise',
	                                                                   volume=12,
	                                                                   text='Ow!',
	                                                                   owner_can_hear=True,
	                                                                   show_on_sight=True,
	                                                                   callback=lambda t, x, y: entities.trigger_event(t,
	                                                                                                            'update_target_memory',
	                                                                                                            target_id=_entity['_id'],
	                                                                                                            key='last_seen_at',
	                                                                                                            value=[x, y])))
	entities.register_event(_entity, 'position_changed', lambda e, **kwargs: ai_visuals.add_to_moved_life(e))
	                        
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)
	
	ai_factions.register(_entity, faction)

	return _entity

def _create_animal(x, y, health, speed, name, vision=65, faction='Mutants', has_ai=False, char='m', fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	entities.create_event(_entity, 'damage')
	entities.create_event(_entity, 'did_damage')	

	tile.register(_entity, surface='life', char=char, fore_color=fore_color)
	movement.register(_entity, collisions=True)
	timers.register(_entity)
	stats.register(_entity, health, speed, vision, name=name)
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)
	skeleton.register(_entity)

	if has_ai:
		ai.register_animal(_entity)

	entities.create_event(_entity, 'get_and_store_item')
	entities.create_event(_entity, 'get_and_hold_item')
	entities.create_event(_entity, 'reload')
	entities.create_event(_entity, 'shoot')
	entities.create_event(_entity, 'damage')
	entities.register_event(_entity, 'post_tick', ai_visuals.cleanup)
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
	                                                                   owner_can_hear=False,
	                                                                   callback=lambda t, x, y: entities.trigger_event(t,
	                                                                                                            'update_target_memory',
	                                                                                                            target_id=_entity['_id'],
	                                                                                                            key='last_seen_at',
	                                                                                                            value=[x, y])))
	entities.register_event(_entity, 'position_changed', lambda e, **kwargs: ai_visuals.add_to_moved_life(e))
	                        
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)
	
	ai_factions.register(_entity, faction)

	return _entity

def human(x, y, name):
	_entity = _create_human(x, y, 100, 10, name, has_ai=True)
	
	entities.trigger_event(_entity, 'set_flag', flag='is_player', value=True)

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
	entities.register_event(_entity,
				'did_damage',
				lambda e, target_id, damage: effects.printer(entities.get_entity(target_id)['tile']['x'],
									entities.get_entity(target_id)['tile']['y']-1,
									'%s' % damage,
									fore_color=(200, 0, 0),
									speed_mod=0.3,
									show_mod=1.0,
									moving=True,
									center=True))
	entities.register_event(_entity,
				'log_kill',
				lambda e, target_id: effects.printer(entities.get_entity(target_id)['tile']['x'],
									entities.get_entity(target_id)['tile']['y']-1,
									'KILL',
									fore_color=(255, 0, 0),
									speed_mod=0.3,
									show_mod=1.0,
									moving=True,
									center=True))
	entities.register_event(_entity,
				'broadcast',
				lambda e, message: effects.message(message))
	
	entities.register_event(_entity,
				'set_rank',
				lambda e, rank: not _entity['stats']['rank'] == rank and effects.message('New Rank: %s' % rank))
	
	entities.register_event(_entity, 'heard_noise', handle_player_heard_noise)
	
	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])

	return _entity

def human_runner(x, y, name):
	_entity = _create_human(x, y, 100, 10, name, faction='Runners', fore_color=(200, 140, 190), has_ai=True)
	
	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])
	
	return _entity

def human_bandit(x, y, name):
	_entity = _create_human(x, y, 100, 10, name, faction='Bandits', fore_color=(140, 140, 190), has_ai=True)
	
	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])
	
	return _entity

def wild_dog(x, y, name):
	_entity = _create_animal(x, y, 100, 4, 'Wild Dog', faction='Wild Dogs', char='d', fore_color=(200, 0, 0), has_ai=True)
	
	skeleton.create_limb(_entity, 'head', [], True, 0.1, health=25, stat_mod={'vision': .75})
	skeleton.create_limb(_entity, 'torso', ['head'], True, 0.88, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'front left leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'front right leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'back left leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'back right leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	
	return _entity


############
#Operations#
############

def handle_heard_noise(entity, x, y, text, direction, accuracy, show_on_sight, callback, context_callback):
	if accuracy <= .75 and accuracy < random.uniform(0, 1):
		return
	
	callback(entity, x, y)

def handle_player_heard_noise(entity, x, y, text, direction, accuracy, show_on_sight, callback, context_callback):
	_entity = effects.show_noise(entity, x, y, accuracy, direction, text, show_on_sight, callback)
	
	if not _entity:
		return
	
	if not context_callback:
		return
	
	_x, _y = flags.get_flag(_entity, 'text_orig_pos')
	
	entities.register_event(_entity, 'delete', lambda e: noise.create_context(_x, _y, text, context_callback))

def can_see_position(entity, position):
	_solids = zones.get_active_solids(entity)
	
	if numbers.distance(movement.get_position(entity), position) > stats.get_vision(entity):
		return False
	
	for pos in shapes.line(movement.get_position(entity), position):
		if pos in _solids:
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
	
	if not target_id in entities.ENTITIES:
		logging.warning('Target deleted during shooting.')
		
		return
	
	_tx, _ty = movement.get_position(entities.get_entity(target_id))
	_direction = numbers.direction_to((_x, _y), (_tx, _ty))
	effects.muzzle_flash(_x, _y, _direction)

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
	                                                                value=[x, y]),
	                       context_callback=lambda x, y: ui_dialog.create(x, y, 'Gunshot (Unknown)', title='Noise'))

	entities.trigger_event(entity, 'get_accuracy')
	_accuracy = stats.get_accuracy(entity, weapon_id)

	effects.light(_x, _y, random.randint(2, 5))
	items.bullet(entity, _x, _y, _tx, _ty, 1, _accuracy)

def shoot_weapon(entity, target_id):
	if timers.has_timer_with_name(entity, 'Shoot'):
		return

	_weapon = items.get_items_in_holder(entity, 'weapon')[0]
	_ammo = flags.get_flag(entities.get_entity(_weapon), 'ammo')

	if not _ammo:
		return

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=10,
	                       repeat=3,
		                   name='Shoot',
		                   repeat_callback=lambda _: _shoot_weapon(entity, _weapon, target_id))