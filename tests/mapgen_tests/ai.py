from framework import entities, events, numbers, goapy, timers, flags

import ai_visuals
import settings
import brains

import logging


ONLINE_ENTITIES = []
OFFLINE_ENTITIES = []
MOVE_OFFLINE = []


def boot():
	_entity = entities.create_entity('systems')

	timers.register(_entity, use_system_event='logic')

	entities.trigger_event(_entity, 'create_timer', time=0, repeat=-1, repeat_callback=_tick_online_entities)
	entities.trigger_event(_entity, 'create_timer', time=numbers.seconds_as_ticks(3), repeat=-1, repeat_callback=_tick_offline_entities)

def _register(entity, player=False):
	ONLINE_ENTITIES.append(entity['_id'])
	
	entity['ai'] = {'brain': goapy.World(),
	                'brain_offline': goapy.World(),
	                'last_action': 'idle',
	                'visible_items': [],
	                'is_player': player,
	                'meta': {'is_injured': False,
	                         'is_panicked': False,
	                         'has_bandage': False,
	                         'has_ammo': False,
	                         'has_weapon': False,
	                         'weapon_loaded': False,
	                         'weapon_armed': False,
	                         'in_engagement': False,
	                         'is_target_near': False,
	                         'in_cover': False,
	                         'in_enemy_los': False,
	                         'is_hungry': False,
	                         'has_food': False,
	                         'sees_item_type_weapon': False},
	                'weights': {'find_bandage': 10,
	                            'find_weapon': 16}}
	
	entities.create_event(entity, 'logic')
	entities.create_event(entity, 'logic_offline')

def register_animal(entity):
	_register(entity)
	_ai = entity['ai']
	
	entities.register_event(entity, 'logic', _animal_logic)
	entities.register_event(entity, 'logic_offline', _animal_logic_offline)

def register_human(entity, player=False):
	_register(entity, player=player)
	_ai = entity['ai']
	
	#Healing
	_ai['brain'].add_planner(brains.heal())
	
	#Combat
	_ai['brain'].add_planner(brains.combat())

	#Panic
	_ai['brain'].add_planner(brains.panic())

	#Food
	_ai['brain'].add_planner(brains.food())
	
	#Search
	_ai['brain'].add_planner(brains.search_for_weapon())
	
	#Reload
	_ai['brain'].add_planner(brains.reload())
	
	entities.register_event(entity, 'logic', _human_logic)
	entities.register_event(entity, 'logic_offline', _human_logic_offline)


###################
#System Operations#
###################

def _tick_online_entities(entity):
	global ONLINE_ENTITIES
	
	if not settings.TICK_MODE == 'normal':
		return
	
	for entity_id in ONLINE_ENTITIES:
		if not entity_id in entities.ENTITIES:
			logging.warning('Online entity not found in global entity list: Moving to offline queue.')
			
			continue
		
		entities.trigger_event(entities.get_entity(entity_id), 'logic')

def _tick_offline_entities(entity):
	for entity_id in OFFLINE_ENTITIES:
		entities.trigger_event(entities.get_entity(entity_id), 'logic_offline')


###################
#Entity Operations#
###################

def set_meta(entity, key, value):
	if not key in entity['ai']['meta']:
		raise Exception('Trying to set invalid brain meta: %s' % key)
	
	entity['ai']['meta'][key] = value

def set_meta_weight(entity, key, value):
	entity['ai']['weights'][key] = value

def _handle_goap(entity, brain='brain'):
	for planner in entity['ai'][brain].planners:
		_start_state = {}
		
		for key in planner.values.keys():
			_start_state[key] = entity['ai']['meta'][key]
			
		for key in planner.action_list.conditions.keys():
			if key in entity['ai']['weights']:
				planner.action_list.set_weight(key, entity['ai']['weights'][key])
		
		planner.set_start_state(**_start_state)
		
	entity['ai'][brain].calculate()
	
	return entity['ai'][brain].get_plan(debug=False)

def _animal_logic(entity):
	_plan = _handle_goap(entity)

def _human_logic(entity):
	ai_visuals.build_item_list(entity)
	
	if len(entity['ai']['visible_items']['gun']) > 0:
		entity['ai']['meta']['sees_item_type_weapon'] = True
	
	if entity['ai']['is_player']:
		return
	
	_goap = _handle_goap(entity)
	
	if not _goap:
		return	
	
	_plan = _goap[0]
	_plan['planner'].trigger_callback(entity, _plan['actions'][0]['name'])

	if not entity['ai']['last_action'] == _plan['actions'][0]['name']:
		print '%s: %s -> %s' % (entity['_id'], entity['ai']['last_action'], _plan['actions'][0]['name'])
		
		entity['ai']['last_action'] = _plan['actions'][0]['name']

def _animal_logic_offline(entity):
	_plan = _handle_goap(entity, brain='brain_offline')

def _human_logic_offline(entity):
	_plan = _handle_goap(entity, brain='brain_offline')
