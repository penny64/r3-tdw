from framework import entities, events, numbers, goapy, timers

import logging


ONLINE_ENTITIES = []
OFFLINE_ENTITIES = []
MOVE_OFFLINE = []


def boot():
	_entity = entities.create_entity('systems')

	timers.register(_entity)

	entities.trigger_event(_entity, 'create_timer', time=0, repeat=-1, repeat_callback=_tick_online_entities)
	entities.trigger_event(_entity, 'create_timer', time=numbers.seconds_as_ticks(3), repeat=-1, repeat_callback=_tick_offline_entities)

def _register(entity):
	ONLINE_ENTITIES.append(entity['_id'])
	
	entity['ai'] = {'brain': goapy.World(),
	                'brain_offline': goapy.World(),
	                'meta': {'is_injured': True,
	                         'has_bandage': False,
	                         'has_ammo': False,
	                         'has_weapon': False,
	                         'weapon_loaded': False,
	                         'weapon_armed': False,
	                         'in_engagement': False,
	                         'is_near': False,
	                         'in_cover': False,
	                         'in_enemy_los': False,
	                         'is_hungry': False,
	                         'has_food': False,
	                         'sees_item_type_weapon': False},
	                'weights': {'find_bandage': 4,
	                            'find_weapon': 6}}
	
	entities.create_event(entity, 'logic')
	entities.create_event(entity, 'logic_offline')

def register_animal(entity):
	_register(entity)
	_ai = entity['ai']
	
	entities.register_event(entity, 'logic', _animal_logic)
	entities.register_event(entity, 'logic_offline', _animal_logic_offline)

def register_human(entity):
	_register(entity)
	_ai = entity['ai']
	
	#Healing
	_heal_brain = goapy.Planner('is_injured', 'has_bandage')
	_heal_actions = goapy.Action_List()
	
	_heal_actions.add_condition('apply_bandage', has_bandage=True)
	_heal_actions.add_reaction('apply_bandage', is_injured=False)
	_heal_actions.add_condition('find_bandage', has_bandage=False)
	_heal_actions.add_reaction('find_bandage', has_bandage=True)
	
	_heal_brain.set_action_list(_heal_actions)
	_heal_brain.set_goal_state(is_injured=False)
	
	_ai['brain'].add_planner(_heal_brain)
	
	#Combat
	_combat_brain = goapy.Planner('has_ammo',
                                  'has_weapon',
                                  'weapon_armed',
                                  'weapon_loaded',
                                  'in_engagement',
                                  'in_cover',
                                  'in_enemy_los',
                                  'is_near')
	_combat_brain.set_goal_state(in_engagement=False)

	_combat_actions = goapy.Action_List()
	_combat_actions.add_condition('track',
                                  is_near=False,
                                  weapon_armed=True)
	_combat_actions.add_reaction('track', is_near=True)
	_combat_actions.add_condition('unpack_ammo', has_ammo=False)
	_combat_actions.add_reaction('unpack_ammo', has_ammo=True)
	_combat_actions.add_condition('search_for_ammo', has_ammo=False)
	_combat_actions.add_reaction('search_for_ammo', has_ammo=True)
	_combat_actions.add_condition('reload',
                                  has_ammo=True,
                                  weapon_loaded=False,
                                  in_cover=True)
	_combat_actions.add_reaction('reload', weapon_loaded=True)
	_combat_actions.add_condition('arm',
                                  weapon_loaded=True,
                                  weapon_armed=False)
	_combat_actions.add_reaction('arm', weapon_armed=True)
	_combat_actions.add_condition('shoot',
                                  weapon_loaded=True,
                                  weapon_armed=True,
                                  is_near=True)
	_combat_actions.add_reaction('shoot', in_engagement=False)
	_combat_actions.add_condition('get_cover', in_cover=False)
	_combat_actions.add_reaction('get_cover', in_cover=True)
	_combat_actions.set_weight('unpack_ammo', 3)
	_combat_actions.set_weight('search_for_ammo', 4)
	_combat_actions.set_weight('track', 20)

	_combat_brain.set_action_list(_combat_actions)
	
	_ai['brain'].add_planner(_combat_brain)	

	#Food
	_food_brain = goapy.Planner('is_hungry',
                                'has_food')
	_food_actions = goapy.Action_List()

	_food_brain.set_action_list(_food_actions)
	_food_brain.set_goal_state(is_hungry=False)

	_food_actions.add_condition('find_food', has_food=False)
	_food_actions.add_reaction('find_food', has_food=True)
	_food_actions.add_condition('eat_food', has_food=True)
	_food_actions.add_reaction('eat_food', is_hungry=False)
	_food_actions.set_weight('find_food', 20)
	_food_actions.set_weight('eat_food', 10)
	
	_ai['brain'].add_planner(_food_brain)
	
	#Search
	_weapon_seach_brain = goapy.Planner('has_weapon', 'sees_item_type_weapon')
	_weapon_search_actions = goapy.Action_List()

	_weapon_seach_brain.set_action_list(_weapon_search_actions)
	_weapon_seach_brain.set_goal_state(has_weapon=True)

	_weapon_search_actions.add_condition('find_weapon', has_weapon=False)
	_weapon_search_actions.add_reaction('find_weapon', sees_item_type_weapon=True)
	_weapon_search_actions.add_condition('get_weapon', sees_item_type_weapon=True)
	_weapon_search_actions.add_reaction('get_weapon', has_weapon=True)
	
	_ai['brain'].add_planner(_weapon_seach_brain)
	
	entities.register_event(entity, 'logic', _human_logic)
	entities.register_event(entity, 'logic_offline', _human_logic_offline)

###################
#System Operations#
###################

def _tick_online_entities(entity):
	global ONLINE_ENTITIES
	
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
	entity['ai'][brain].get_plan(debug=True)

def _animal_logic(entity):
	_plan = _handle_goap(entity)

def _human_logic(entity):
	entity['ai']['meta']['is_injured']
	
	_plan = _handle_goap(entity)

def _animal_logic_offline(entity):
	_plan = _handle_goap(entity, brain='brain_offline')

def _human_logic_offline(entity):
	entity['ai']['meta']['is_injured']
	
	_plan = _handle_goap(entity, brain='brain_offline')