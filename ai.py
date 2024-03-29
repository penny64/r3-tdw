from framework import entities, events, numbers, goapy, timers, flags, movement, stats

import ai_squad_logic
import ai_factions
import ai_debugger
import ai_visuals
import ai_squads
import ai_flow
import skeleton
import settings
import brains
import zones
import items
import life

import logging
import time


ONLINE_ENTITIES = []
OFFLINE_ENTITIES = []
MOVE_OFFLINE = []


def boot():
	_entity = entities.create_entity('systems')

	timers.register(_entity, use_system_event='logic')

	#entities.trigger_event(_entity, 'create_timer', time=0, repeat=-1, repeat_callback=_tick_online_entities)
	#entities.trigger_event(_entity, 'create_timer', time=numbers.seconds_as_ticks(3), repeat=-1, repeat_callback=_tick_offline_entities)

def _register(entity, player=False):
	ONLINE_ENTITIES.append(entity['_id'])
	
	entity['ai'] = {'brain': goapy.World(),
	                'brain_offline': goapy.World(),
	                'current_action': 'idle',
	                'last_action': 'idle',
	                'visible_items': {},
	                'visible_life': set(),
	                'visible_targets': [],
	                'targets_to_search': [],
	                'targets': set(),
	                'nearest_target': None,
	                'life_memory': {},
	                'is_player': player,
	                'is_npc': False,
	                'meta': {'is_injured': False,
	                         'is_panicked': False,
	                         'is_squad_combat_ready': False,
	                         'is_squad_overwhelmed': False,
	                         'is_squad_forcing_surrender': False,
	                         'is_squad_mobile_ready': False,
	                         'is_squad_leader': False,
	                         'has_bandage': False,
	                         'has_ammo': False,
	                         'has_weapon': False,
	                         'has_container': False,
	                         'has_firing_position': False,
	                         'has_lost_target': False,
	                         'weapon_loaded': False,
	                         'in_engagement': False,
	                         'is_target_near': False,
	                         'is_target_armed': False,
	                         'in_cover': False,
	                         'in_enemy_los': False,
	                         'in_firing_range': False,
	                         'is_hungry': False,
	                         'has_food': False,
	                         'sees_item_type_weapon': False,
	                         'sees_item_type_container': False,
	                         'sees_item_type_ammo': False,
	                         'has_needs': False},
	                'weights': {'find_bandage': 10,
	                            'find_weapon': 16,
	                            'find_container': 14,
	                            'track': 20}}
	
	entities.create_event(entity, 'logic_offline')
	entities.create_event(entity, 'update_target_memory')
	entities.create_event(entity, 'meta_change')
	entities.create_event(entity, 'set_meta')
	entities.create_event(entity, 'has_needs')
	entities.create_event(entity, 'new_target_spotted')
	entities.create_event(entity, 'broadcast')
	entities.create_event(entity, 'target_lost')
	entities.create_event(entity, 'target_found')
	entities.create_event(entity, 'target_search_failed')
	entities.create_event(entity, 'squad_inform_lost_target')
	entities.create_event(entity, 'squad_inform_found_target')
	entities.create_event(entity, 'squad_inform_failed_search')
	entities.register_event(entity, 'save', save)
	entities.register_event(entity, 'delete', _cleanup)
	entities.register_event(entity, 'set_meta', set_meta)
	entities.register_event(entity, 'update_target_memory', update_target_memory)
	entities.register_event(entity, 'target_lost', ai_squad_logic.member_handle_lost_target)
	entities.register_event(entity, 'target_found', ai_squad_logic.member_handle_found_target)
	entities.register_event(entity, 'target_search_failed', ai_squad_logic.member_handle_failed_target_search)
	entities.register_event(entity, 'squad_inform_lost_target', ai_squad_logic.member_learn_lost_target)
	entities.register_event(entity, 'squad_inform_found_target', ai_squad_logic.member_learn_found_target)
	entities.register_event(entity, 'squad_inform_failed_search', ai_squad_logic.member_learn_failed_target_search)

def save(entity, snapshot):
	snapshot['ai'] = entity['ai'].copy()
	
	del snapshot['ai']['brain']
	del snapshot['ai']['brain_offline']
	
	snapshot['ai']['visible_life'] = list(entity['ai']['visible_life'])
	snapshot['ai']['targets'] = list(entity['ai']['targets'])

def load(entity):
	entity['ai']['visible_life'] = set(entity['ai']['visible_life'])
	entity['ai']['targets'] = set(entity['ai']['targets'])

def _cleanup(entity):
	if entity['_id'] in ONLINE_ENTITIES:
		ONLINE_ENTITIES.remove(entity['_id'])
	
	elif entity['_id'] in OFFLINE_ENTITIES:
		OFFLINE_ENTITIES.remove(entity['_id'])
	
	_x, _y = movement.get_position(entity)
	
	if flags.has_flag(entity, 'fire_data'):
		_fire_data = flags.get_flag(entity, 'fire_data')
		_node = entities.get_entity(zones.get_active_node_grid()[_fire_data['node']])
		
		entities.trigger_event(_node, 'set_flag', flag='owner', value=None)
		flags.delete_flag(entity, 'fire_data')
	
	_item_id = items.corpse(_x, _y, entity['tile']['char'], entity['_id'])['_id']
	
	entities.trigger_event(entity, 'handle_corpse', corpse_id=_item_id)

def _register_animal(entity, player=False):
	ONLINE_ENTITIES.append(entity['_id'])
	
	entity['ai'] = {'brain': goapy.World(),
	                'brain_offline': goapy.World(),
	                'current_action': 'idle',
	                'last_action': 'idle',
	                'visible_items': [],
	                'visible_life': set(),
	                'visible_targets': [],
	                'targets': set(),
	                'nearest_target': None,
	                'life_memory': {},
	                'is_player': player,
	                'meta': {'is_injured': False,
	                         'is_panicked': False,
	                         'is_squad_overwhelmed': False,
	                         'is_squad_leader': False,
	                         'is_in_melee_range': False,
	                         'in_engagement': False,
	                         'is_target_near': False,
	                         'is_target_armed': False,
	                         'is_target_lost': False,
	                         'in_cover': False,
	                         'in_enemy_los': False,
	                         'is_hungry': False,
	                         'has_food': False,
	                         'has_needs': False},
	                'weights': {'track': 20}}
	
	entities.create_event(entity, 'logic_offline')
	entities.create_event(entity, 'update_target_memory')
	entities.create_event(entity, 'meta_change')
	entities.create_event(entity, 'set_meta')
	entities.create_event(entity, 'has_needs')
	entities.create_event(entity, 'new_target_spotted')
	entities.create_event(entity, 'broadcast')
	entities.create_event(entity, 'target_lost')
	entities.create_event(entity, 'target_found')
	entities.create_event(entity, 'target_search_failed')
	entities.create_event(entity, 'squad_inform_lost_target')
	entities.create_event(entity, 'squad_inform_found_target')
	entities.create_event(entity, 'squad_inform_failed_search')
	entities.register_event(entity, 'delete', _cleanup)
	entities.register_event(entity, 'set_meta', set_meta)
	entities.register_event(entity, 'update_target_memory', update_target_memory)
	entities.register_event(entity, 'target_lost', ai_squad_logic.member_handle_lost_target)
	entities.register_event(entity, 'target_found', ai_squad_logic.member_handle_found_target)
	entities.register_event(entity, 'target_search_failed', ai_squad_logic.member_handle_failed_target_search)
	entities.register_event(entity, 'squad_inform_lost_target', ai_squad_logic.member_learn_lost_target)
	entities.register_event(entity, 'squad_inform_found_target', ai_squad_logic.member_learn_found_target)
	entities.register_event(entity, 'squad_inform_failed_search', ai_squad_logic.member_learn_failed_target_search)

def register_human(entity, player=False):
	_register(entity, player=player)
	_ai = entity['ai']
	
	#Healing
	_ai['brain'].add_planner(brains.heal())
	
	#Combat
	_ai['brain'].add_planner(brains.combat())
	
	#Regrouping
	#NOTE: Not sure what I want this functionality to do
	#Maybe once squads have evolved a bit more I will approach
	#it again.
	#_ai['brain'].add_planner(brains.squad_leader_regroup())

	#Panic
	#_ai['brain'].add_planner(brains.panic())

	#Food
	#_ai['brain'].add_planner(brains.food())
	
	#Search
	#_ai['brain'].add_planner(brains.search_for_weapon())
	#_ai['brain'].add_planner(brains.search_for_ammo())
	#_ai['brain'].add_planner(brains.search_for_container())
	_ai['brain'].add_planner(brains.search_for_target())
	
	#Reload
	_ai['brain'].add_planner(brains.reload())
	
	entities.register_event(entity, 'logic', _human_logic)
	entities.register_event(entity, 'logic_offline', _human_logic_offline)

def register_animal(entity, player=False):
	_register_animal(entity, player=player)
	_ai = entity['ai']
	
	#Combat
	_ai['brain'].add_planner(brains.dog_combat())

	#Panic
	_ai['brain'].add_planner(brains.panic())

	#Food
	_ai['brain'].add_planner(brains.food())
	
	#Search
	#TODO: Adopt for mutants
	#_ai['brain'].add_planner(brains.search_for_target())
	
	entities.register_event(entity, 'logic', _animal_logic)
	entities.register_event(entity, 'logic_offline', _animal_logic_offline)

def register_robot(entity, player=False):
	_register(entity, player=player)
	_ai = entity['ai']
	
	#Combat
	_ai['brain'].add_planner(brains.robot_combat())
	
	#Reload
	_ai['brain'].add_planner(brains.reload())
	
	entities.register_event(entity, 'logic', _human_logic)
	entities.register_event(entity, 'logic_offline', _human_logic_offline)


###################
#System Operations#
###################

#DISABLED

def _tick_online_entities(entity):
	global ONLINE_ENTITIES
	
	if not settings.TICK_MODE == 'normal':
		return
	
	for entity_id in ONLINE_ENTITIES:
		if not entity_id in entities.ENTITIES:
			logging.warning('Online entity not found in global entity list.')
			
			continue
		
		entities.trigger_event(entities.get_entity(entity_id), 'logic')

def _tick_offline_entities(entity):
	for entity_id in OFFLINE_ENTITIES:
		entities.trigger_event(entities.get_entity(entity_id), 'logic_offline')


###################
#Entity Operations#
###################

def update_target_memory(entity, target_id, key, value):
	if target_id in entity['ai']['life_memory']:
		entity['ai']['life_memory'][target_id][key] = value
		
		if key == 'last_seen_at' and not target_id in entity['ai']['targets']:
			if ai_factions.is_enemy(entity, target_id):
				entity['ai']['targets'].add(target_id)
				entity['ai']['life_memory'][target_id]['searched_for'] = False

def set_meta(entity, meta, value):
	if not meta in entity['ai']['meta']:
		raise Exception('Trying to set invalid brain meta: %s' % meta)
	
	entity['ai']['meta'][meta] = value

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
	if timers.has_timer_with_name(entity, 'passout'):
		return	
	
	ai_visuals.build_item_list(entity)
	ai_visuals.build_life_list(entity)
	
	_old_meta = entity['ai']['meta'].copy()
	
	entity['ai']['meta']['in_engagement'] = len(entity['ai']['targets']) > 0
	entity['ai']['meta']['in_enemy_los'] = len([t for t in entity['ai']['targets'] if entity['ai']['life_memory'][t]['in_los']]) > 0
	
	if not entity['ai']['meta'] == _old_meta:
		entities.trigger_event(entity, 'meta_change')
	
	if entity['ai']['meta']['in_engagement']:
		_target = entity['ai']['nearest_target']
		_target_distance = numbers.distance(movement.get_position_via_id(_target), movement.get_position(entity))
		
		entity['ai']['meta']['is_target_near'] = _target_distance <= 25
		
		if not entity['ai']['meta']['in_enemy_los'] and life.can_see_position(entity, entity['ai']['life_memory'][_target]['last_seen_at']):
			entity['ai']['meta']['has_lost_target'] = entity['ai']['meta']['is_target_near']
		
		elif entity['ai']['meta']['in_enemy_los']:
			if flags.has_flag(entity, 'search_nodes'):
				flags.delete_flag(entity, 'search_nodes')
			
			entity['ai']['meta']['is_in_melee_range'] = _target_distance == 1
				
	else:
		entity['ai']['meta']['is_target_near'] = False
	
	entity['ai']['meta']['is_target_armed'] = len([t for t in entity['ai']['targets'] if entity['ai']['life_memory'][t]['is_armed']]) > 0
	#entity['ai']['meta']['is_panicked'] = skeleton.has_critical_injury(entity)
	entity['ai']['meta']['is_injured'] = skeleton.has_critical_injury(entity)
	entity['ai']['meta']['is_panicked'] = entity['ai']['meta']['is_injured']
	
	if entity['ai']['is_player']:
		return
	
	_goap = _handle_goap(entity)
	
	if not _goap:
		entity['ai']['current_action'] = 'idle'
		
		return	
	
	_plan = _goap[0]
	_plan['planner'].trigger_callback(entity, _plan['actions'][0]['name'])
	#print time.time() - _t

	if not entity['ai']['last_action'] == _plan['actions'][0]['name']:
		logging.debug('%s: %s -> %s' % (entity['_id'], entity['ai']['last_action'], _plan['actions'][0]['name']))
		
		entity['ai']['last_action'] = _plan['actions'][0]['name']
	
	entity['ai']['current_action'] = _plan['actions'][0]['name']

def _human_logic(entity):
	_t = time.time()
	ai_visuals.build_item_list(entity)
	ai_visuals.build_life_list(entity)
	
	if ai_flow.is_flow_active() and not ai_flow.can_act(entity):
		return
	
	if timers.has_timer_with_name(entity, 'passout'):
		return
	
	#if not ai_squads.is_active(ai_squads.get_assigned_squad(entity)) or entity['stats']['action_points'] <= 0:
	#	return
	
	_old_meta = entity['ai']['meta'].copy()
	
	entity['ai']['meta']['sees_item_type_weapon'] = len(entity['ai']['visible_items']['weapon']) > 0
	entity['ai']['meta']['sees_item_type_ammo'] = len(entity['ai']['visible_items']['ammo']) > 0
	entity['ai']['meta']['sees_item_type_container'] = len(entity['ai']['visible_items']['container']) > 0
	entity['ai']['meta']['has_weapon'] = len(items.get_items_in_holder(entity, 'weapon')) > 0
	entity['ai']['meta']['has_ammo'] = len(items.get_items_matching(entity, {'type': 'ammo'})) > 0
	entity['ai']['meta']['has_container'] = len(items.get_items_matching(entity, {'type': 'container'})) > 0
	entity['ai']['meta']['weapon_loaded'] = len([w for w in items.get_items_in_holder(entity, 'weapon') if entities.get_entity(w)['flags']['ammo']['value'] > 0]) > 0
	entity['ai']['meta']['in_engagement'] = len([t for t in entity['ai']['targets'] if not entity['ai']['life_memory'][t]['is_lost']]) > 0
	entity['ai']['meta']['has_lost_target'] = len(entity['ai']['targets_to_search']) > 0
	entity['ai']['meta']['in_enemy_los'] = len([t for t in entity['ai']['targets'] if entity['ai']['life_memory'][t]['in_los']]) > 0
	entity['ai']['meta']['has_needs'] = not entity['ai']['meta']['has_weapon'] or not entity['ai']['meta']['has_container'] or not entity['ai']['meta']['weapon_loaded']
	entity['ai']['meta']['is_injured'] = skeleton.has_critical_injury(entity)
	
	if not entity['ai']['meta'] == _old_meta:
		entities.trigger_event(entity, 'meta_change')
	
	if entity['ai']['meta']['in_engagement']:
		_target = entity['ai']['nearest_target']
		_target_distance = numbers.distance(movement.get_position_via_id(_target), movement.get_position(entity))
		_engage_distance = stats.get_vision(entity) * .75
		_weapon = entities.get_entity(items.get_items_in_holder(entity, 'weapon')[0])
		_engage_distance =  numbers.clip(_engage_distance - (flags.get_flag(_weapon, 'accuracy') * 3), 1, stats.get_vision(entity))
		_min_engage_distance = 3
		
		if _weapon['stats']['kind'] == 'explosive':
			_engage_distance /= 2
			_min_engage_distance = 8
		
		entities.trigger_event(entity, 'set_flag', flag='engage_distance', value=_engage_distance)
		entities.trigger_event(entity, 'set_flag', flag='min_engage_distance', value=_min_engage_distance)
		
		#NOTE: Mirror change in ai_logic!
		entity['ai']['meta']['in_firing_range'] = _target_distance <= _engage_distance and _target_distance >= _min_engage_distance
		
		if entity['ai']['meta']['in_enemy_los']:
			if flags.has_flag(entity, 'search_nodes'):
				flags.delete_flag(entity, 'search_nodes')
			
			entity['ai']['meta']['is_in_melee_range'] = _target_distance == 1
				
	else:
		entity['ai']['meta']['is_target_near'] = False
		entity['ai']['meta']['in_firing_range'] = False
	
	entity['ai']['meta']['is_target_armed'] = len([t for t in entity['ai']['targets'] if entity['ai']['life_memory'][t]['is_armed']]) > 0
	entity['ai']['meta']['is_panicked'] = (not entity['ai']['meta']['weapon_loaded'] and entity['ai']['meta']['is_target_armed'])
	
	if entity['ai']['is_player']:
		return
	
	#TODO: Experimental!
	#if entity['ai']['meta'] == _old_meta:
		#print 'Something changed...'
		
		#return
	
	if timers.has_timer_with_name(entity, 'shoot') or entity['movement']['path']['positions'] or timers.has_timer_with_name(entity, 'move'):
		#print 'Clearing existing action...'
		return
	
	_goap = _handle_goap(entity)
	
	if not _goap:
		entity['ai']['current_action'] = 'idle'
		
		entities.trigger_event(entity, 'finish_turn')
		entities.trigger_event(entity, 'stop')
		
		#print
		#print entity['stats']['name'], 'no possible action'
		#print
		
		#for meta_name in entity['ai']['meta']:
		#	print meta_name, '\t', entity['ai']['meta'][meta_name]
		
		return	
	
	_plan = _goap[0]
	
	if not entity['ai']['last_action'] == _plan['actions'][0]['name']:
		if entity['_id'] in ai_debugger.WATCHING:
			logging.info('%s: %s -> %s' % (entity['_id'], entity['ai']['last_action'], _plan['actions'][0]['name']))
		
		#TODO: Only do this if the action requires movement changes
		entities.trigger_event(entity, 'stop')
		
		entity['ai']['last_action'] = _plan['actions'][0]['name']
	
	#print entity['stats']['name'], _plan['actions'][0]['name']
	
	_plan['planner'].trigger_callback(entity, _plan['actions'][0]['name'])
	
	#print time.time() - _t
	
	entity['ai']['current_action'] = _plan['actions'][0]['name']

def _animal_logic_offline(entity):
	_plan = _handle_goap(entity, brain='brain_offline')

def _human_logic_offline(entity):
	_plan = _handle_goap(entity, brain='brain_offline')
