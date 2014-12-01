from framework import entities, tile, timers, movement, stats, flags, numbers, shapes

import ai_factions
import ai_visuals
import ai_squads
import ai_flow
import ui_director
import ui_dialog
import ui_menu
import constants
import skeleton
import settings
import missions
import effects
import mapgen
import camera
import nodes
import items
import noise
import zones
import life
import ai

import logging
import random


def _create_human(x, y, health, speed, name, vision=50, faction='Rogues', is_player=False, has_ai=False, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	entities.create_event(_entity, 'get_and_store_item')
	entities.create_event(_entity, 'get_and_hold_item')
	entities.create_event(_entity, 'reload')
	entities.create_event(_entity, 'shoot')
	entities.create_event(_entity, 'damage')
	entities.create_event(_entity, 'did_damage')
	entities.create_event(_entity, 'receive_memory')
	entities.create_event(_entity, 'handle_corpse')
	entities.create_event(_entity, 'finish_turn')

	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity, collisions=True)
	timers.register(_entity)
	stats.register(_entity, health, speed, vision, name=name, kind='human')
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)
	missions.register(_entity)
	skeleton.register(_entity)
	skeleton.create_motion(_entity, 'stand')
	skeleton.create_motion(_entity, 'crouch', stat_mod={'speed': 1.55})
	skeleton.create_motion(_entity, 'crawl', stat_mod={'speed': 2.3})
	skeleton.create_limb(_entity, 'head', [], True, 0.1, stat_mod={'vision': .75})
	skeleton.create_limb(_entity, 'chest', ['head'], True, 0.88)
	skeleton.create_limb(_entity, 'torso', ['chest'], True, 0.75)
	skeleton.create_limb(_entity, 'left arm', ['chest'], False, 0.3, can_sever=True, stat_mod={'accuracy': .22})
	skeleton.create_limb(_entity, 'right arm', ['chest'], False, 0.3, can_sever=True, stat_mod={'accuracy': .22})
	skeleton.create_limb(_entity, 'left leg', ['torso'], False, 0.45, can_sever=True, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'right leg', ['torso'], False, 0.45, can_sever=True, stat_mod={'speed': .4})

	if has_ai:
		ai.register_human(_entity)
	
	ai_factions.register(_entity, faction)
	
	_entity['ai']['is_player'] = is_player
	_entity['ai']['is_npc'] = not is_player
	
	if faction == 'Rogues':
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

	entities.register_event(_entity, 'finish_turn', finish_turn)
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
	#entities.register_event(_entity, 'damage',
	#                        lambda e, **kwargs: entities.trigger_event(e,
	#                                                                   'create_noise',
	#                                                                   volume=12,
	#                                                                   text='Ow!',
	#                                                                   owner_can_hear=True,
	#                                                                   show_on_sight=True,
	#                                                                   callback=lambda t, x, y: entities.trigger_event(t,
	#                                                                                                            'update_target_memory',
	#                                                                                                            target_id=_entity['_id'],
	#                                                                                                            key='last_seen_at',
	#                                                                                                            value=[x, y])))
	#entities.register_event(_entity, 'position_changed', lambda e, **kwargs: ai_visuals.add_to_moved_life(e))
	entities.register_event(_entity, 'push', lambda e, **kwargs: movement.sub_move_cost(e))
	                        
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)
	
	_get_and_hold_item(_entity, items.leather_backpack(20, 20)['_id'])

	return _entity

def _create_animal(x, y, health, speed, name, vision=65, faction='Mutants', has_ai=False, char='m', fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='life')
	
	entities.create_event(_entity, 'damage')
	entities.create_event(_entity, 'did_damage')
	entities.create_event(_entity, 'receive_memory')
	entities.create_event(_entity, 'handle_corpse')
	entities.create_event(_entity, 'finish_turn')

	tile.register(_entity, surface='life', char=char, fore_color=fore_color)
	movement.register(_entity, collisions=True)
	timers.register(_entity)
	stats.register(_entity, health, speed, vision, name=name, kind='animal')
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)
	skeleton.register(_entity)
	ai_factions.register(_entity, faction)

	if has_ai:
		ai.register_animal(_entity)
	
	_entity['ai']['is_npc'] = True

	entities.register_event(_entity, 'finish_turn', finish_turn)
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
	#entities.register_event(_entity, 'position_changed', lambda e, **kwargs: ai_visuals.add_to_moved_life(e))
	entities.register_event(_entity, 'push', lambda e, **kwargs: movement.sub_move_cost(e))
	                        
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)

	return _entity

def _create_robot(x, y, health, speed, name, vision=30, faction='Rogues', is_player=False, has_ai=True, fore_color=(200, 200, 200)):
	_entity = entities.create_entity(group='life')
	
	entities.create_event(_entity, 'get_and_store_item')
	entities.create_event(_entity, 'get_and_hold_item')
	entities.create_event(_entity, 'reload')
	entities.create_event(_entity, 'shoot')
	entities.create_event(_entity, 'damage')
	entities.create_event(_entity, 'did_damage')
	entities.create_event(_entity, 'receive_memory')
	entities.create_event(_entity, 'handle_corpse')
	entities.create_event(_entity, 'finish_turn')

	tile.register(_entity, surface='life', char='@', fore_color=fore_color)
	movement.register(_entity, collisions=True)
	timers.register(_entity)
	stats.register(_entity, health, speed, vision, name=name, kind='human')
	nodes.register(_entity)
	items.register(_entity)
	flags.register(_entity)
	noise.register(_entity)
	missions.register(_entity)
	skeleton.register(_entity)

	if has_ai:
		ai.register_robot(_entity)
	
	ai_factions.register(_entity, faction)
	
	_entity['ai']['is_player'] = is_player
	_entity['ai']['is_npc'] = not is_player
	
	if is_player:
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

	entities.register_event(_entity, 'finish_turn', finish_turn)
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
	entities.register_event(_entity, 'push', lambda e, **kwargs: movement.sub_move_cost(e))
	                        
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	entities.trigger_event(_entity, 'create_holder', name='weapon', max_weight=10)
	entities.trigger_event(_entity, 'create_holder', name='backpack', max_weight=10)
	
	_get_and_hold_item(_entity, items.leather_backpack(20, 20)['_id'])

	return _entity

def _human(x, y, name, is_player, faction):
	_entity = _create_human(x, y, 100, 10, name, has_ai=True, is_player=is_player, faction=faction)

	#entities.register_event(_entity,
	#			'hold_item',
	#			lambda e, item_id: effects.printer(_entity['tile']['x']-camera.X,
	#								_entity['tile']['y']-camera.Y-5,
	#								'+%s' % entities.get_entity(item_id)['stats']['name'],
	#								fore_color=(0, 255, 0),
	#								speed_mod=0.3,
	#								show_mod=1.0,
	#								moving=False,
	#								center=True))
	#entities.register_event(_entity,
	#			'store_item',
	#			lambda e, item_id: effects.printer(_entity['tile']['x']-camera.X,
	#								_entity['tile']['y']-camera.Y-5,
	#								'+%s' % entities.get_entity(item_id)['stats']['name'],
	#								fore_color=(0, 255, 0),
	#								speed_mod=0.3,
	#								show_mod=1.0,
	#								moving=False,
	#								center=True))
	
	if faction == 'Rogues':
		entities.trigger_event(_entity, 'set_flag', flag='is_player', value=is_player)
		
		if is_player:
			entities.register_event(_entity,
				                    'new_target_spotted',
				                    _handle_new_target)
		
		entities.register_event(_entity,
			                    'broadcast',
			                    lambda e, message: effects.message(message))
		entities.register_event(_entity,
			                    'add_mission',
			                    lambda e, mission_id: effects.message('New mission.'))
		entities.register_event(_entity,
			                    'complete_mission',
			                    lambda e, mission_id: effects.message('Mission complete.'))
		entities.register_event(_entity,
			                    'set_rank',
			                    lambda e, rank: not _entity['stats']['rank'] == rank and effects.message('New Rank: %s' % rank))
		
		entities.register_event(_entity, 'heard_noise', handle_player_heard_noise)
		
		entities.register_event(_entity, 'receive_memory', handle_player_received_memory)
		
		entities.register_event(ai_flow.FLOW, 'start_of_turn', lambda e, squad_id: handle_player_start_of_turn(_entity, squad_id))
		entities.register_event(ai_flow.FLOW, 'end_of_turn', lambda e, squad_id: handle_player_end_of_turn(_entity, squad_id))

	return _entity

def turret(x, y, name, faction):
	_entity = _create_robot(x, y, 100, 0, 'Turret', faction=faction)
	
	skeleton.create_motion(_entity, 'stand')
	skeleton.create_limb(_entity, 'optic', [], False, 0.1, stat_mod={'vision': .25, 'accuracy': .22})
	skeleton.create_limb(_entity, 'mount', ['optic'], True, 0.88)
	
	_get_and_hold_item(_entity, items.chaingun()['_id'])
	
	return _entity

def sniper(x, y, name, faction, is_player=False):
	_entity = _human(x, y, name, is_player, faction)
	
	_entity['stats']['class'] = 'Sniper'
	_entity['stats']['rank'] = 'Novice'
	_entity['stats']['smgs'] = random.randint(15, 20)
	_entity['stats']['pistols'] = random.randint(17, 22)
	_entity['stats']['rifles'] = random.randint(28, 32)
	
	_get_and_hold_item(_entity, items.shortrifle()['_id'])
	
	return _entity

def engineer(x, y, name, faction, is_player=False):
	_entity = _human(x, y, name, is_player, faction)
	
	_entity['stats']['class'] = 'Engineer'
	_entity['stats']['rank'] = 'Novice'
	_entity['stats']['smgs'] = random.randint(25, 30)
	_entity['stats']['pistols'] = random.randint(20, 25)
	_entity['stats']['rifles'] = random.randint(12, 16)
	
	_get_and_hold_item(_entity, items.glock(0, 0, ammo=17)['_id'])
	
	return _entity

#def human_terrorist(x, y, name):
#	_entity = _create_human(x, y, 100, 10, name, faction='Terrorists', fore_color=(200, 140, 190), has_ai=True)
#	
#	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])
#	
#	return _entity

#def human_runner(x, y, name):
#	_entity = _create_human(x, y, 100, 10, name, faction='Terrorists', fore_color=(200, 140, 190), has_ai=True)
#	
#	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])
#	
#	return _entity

#def human_bandit(x, y, name):
#	_entity = _create_human(x, y, 100, 10, name, faction='Militia', fore_color=(140, 140, 190), has_ai=True)
#	
#	_get_and_hold_item(_entity, items.glock(20, 20, ammo=17)['_id'])
#	
#	return _entity

def wild_dog(x, y, name):
	_entity = _create_animal(x, y, 100, 4, 'Wild Dog', faction='Wild Dogs', char='d', fore_color=(200, 0, 0), has_ai=True)
	
	skeleton.create_motion(_entity, 'stand')
	skeleton.create_limb(_entity, 'head', [], True, 0.1, health=25, stat_mod={'vision': .75})
	skeleton.create_limb(_entity, 'torso', ['head'], True, 0.88, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'front left leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'front right leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'back left leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	skeleton.create_limb(_entity, 'back right leg', ['torso'], False, 0.4, health=45, stat_mod={'speed': .4})
	
	return _entity

def _handle_cut_tail(entity, target_id):
	_target = entities.get_entity(target_id)
	_tail = items.mutated_wild_dog_tail(0, 0, entity['_id'])
	
	entities.trigger_event(_target, 'store_item', item_id=_tail['_id'])

def _handle_mutated_wild_dog_corpse(entity, corpse_id):
	_corpse = entities.get_entity(corpse_id)
	
	entities.register_event(_corpse, 'get_interactions', lambda e, menu, target_id: ui_menu.add_selectable(menu,
	                                                                                            'Cut off tail',
	                                                                                            lambda: _handle_cut_tail(e, target_id)))

def mutated_wild_dog(x, y, name):
	_entity = wild_dog(x, y, name)
	
	entities.trigger_event(_entity, 'set_char', char='D')
	entities.register_event(_entity, 'handle_corpse', _handle_mutated_wild_dog_corpse)
	
	return _entity

############
#Operations#
############

def finish_turn(entity):
	entity['stats']['action_points'] = 0

def create_life_memory(entity, target_id):
	if target_id in entity['ai']['life_memory']:
		logging.warn('Trying to overwrite life memory.')
		
		return
		
	entity['ai']['life_memory'][target_id] = {'distance': -1,
	                                          'is_target': False,
	                                          'is_armed': False,
	                                          'is_lost': False,
	                                          'in_los': False,
	                                          'searched_for': False,
	                                          'can_see': False,
	                                          'last_seen_at': None,
	                                          'last_seen_velocity': None,
	                                          'is_dead': False,
	                                          'seen_time': 0,
	                                          'mission_related': False}

def _handle_new_target(entity, target_id):
	if ai_factions.is_enemy(entity, target_id) and not len(entity['ai']['targets'] & entity['ai']['visible_life']):
		_can_see = target_id in [e for e in entity['ai']['life_memory'] if entity['ai']['life_memory'][e]['in_los']]
		
		#if _can_see:
		#	settings.set_tick_mode('strategy')
		
		if entity['ai']['life_memory'][target_id]['seen_time'] == 1:
			ui_director.focus_on_entity(entity, target_id, show_line=_can_see, pause=_can_see)

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

def handle_player_received_memory(entity, memory, message, member_id):
	_member = entities.get_entity(member_id)
	
	ui_dialog.create(5, 5, message, title='Dialog with %s' % _member['stats']['name'])
	
	_m = ui_menu.create(5, 15, title='Respond')
	
	for life_id in memory:
		if not life_id in entity['ai']['life_memory']:
			life.create_life_memory(entity, life_id)
		
		entity['ai']['life_memory'][life_id].update(memory[life_id])
	
	ui_menu.add_selectable(_m, 'Bribe', lambda: 1==1 and ui_dialog.delete(ui_dialog.ACTIVE_DIALOG))
	ui_menu.add_selectable(_m, 'Leave', lambda: 1==1 and ui_dialog.delete(ui_dialog.ACTIVE_DIALOG))

def handle_player_start_of_turn(entity, squad_id):
	if ai_squads.get_assigned_squad(entity)['_id'] == squad_id:
		settings.set_tick_mode('strategy')
		
		print 'Start of turn'
		
		return False
	
	_squad = entities.get_entity(squad_id)
	
	if not ai_factions.is_enemy(entity, _squad['leader']):
		if _squad['meta']['is_squad_combat_ready']:
			_message = random.choice(['Locked and loaded.',
			                          'Nuke \'em!',
			                          'No mercy, boys...'])
		
		elif _squad['meta']['is_squad_overwhelmed']:
			_message = random.choice(['We\'re outnumbered!',
			                          'Fall back!'])
			
		else:
			return
		
		effects.message(_message, time=70)

def handle_player_end_of_turn(entity, squad_id):
	if ai_squads.get_assigned_squad(entity)['_id'] == squad_id:
		settings.set_tick_mode('normal')
		
		print 'End of turn'
		
		return False

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

	entity['stats']['action_points'] -= stats.get_shoot_cost(entity, weapon_id)

	entities.trigger_event(entity, 'get_accuracy')
	_accuracy = stats.get_accuracy(entity, weapon_id)
	_damage = flags.get_flag(_weapon, 'damage')

	effects.light(_x, _y, random.randint(3, 5), r=1.5, g=1.5, b=0)
	items.bullet(entity, _x, _y, _tx, _ty, 1, _accuracy, _damage)

def shoot_weapon(entity, target_id):
	if timers.has_timer_with_name(entity, 'shoot'):
		return

	_weapon = items.get_items_in_holder(entity, 'weapon')[0]
	_ammo = flags.get_flag(entities.get_entity(_weapon), 'ammo')
	_rounds_per_shot = flags.get_flag(entities.get_entity(_weapon), 'rounds_per_shot')
	_pause_time = 30

	if not _ammo:
		return

	entities.trigger_event(entity,
		                   'create_timer',
		                   time=_pause_time,
	                       repeat=_rounds_per_shot,
		                   name='shoot',
	                       enter_callback=lambda _: entities.trigger_event(entity, 'animate', animation=['\\', '|', '/', '-'], delay=_pause_time/4),
		                   repeat_callback=lambda _: _shoot_weapon(entity, _weapon, target_id))