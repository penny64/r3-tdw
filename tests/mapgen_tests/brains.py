from framework import goapy

import ai_logic
import ai


def heal():
	_heal_brain = goapy.Planner('is_injured', 'has_bandage')
	_heal_actions = goapy.Action_List()
	
	_heal_actions.add_condition('apply_bandage', has_bandage=True)
	#_heal_actions.add_callback('apply_bandage', lambda entity: ai.set_meta(entity, 'is_injured', False))
	_heal_actions.add_reaction('apply_bandage', is_injured=False)
	
	_heal_actions.add_condition('find_bandage', has_bandage=False)
	#_heal_actions.add_callback('find_bandage', lambda entity: ai.set_meta(entity, 'has_bandage', True))
	_heal_actions.add_reaction('find_bandage', has_bandage=True)
	
	_heal_brain.set_action_list(_heal_actions)
	_heal_brain.set_goal_state(is_injured=False)
	
	return _heal_brain

def food():
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
	
	return _food_brain

def search_for_weapon():
	_weapon_search_brain = goapy.Planner('has_weapon', 'sees_item_type_weapon')
	_weapon_search_actions = goapy.Action_List()

	_weapon_search_brain.set_action_list(_weapon_search_actions)
	_weapon_search_brain.set_goal_state(has_weapon=True)

	_weapon_search_actions.add_condition('find_weapon', has_weapon=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	_weapon_search_actions.add_reaction('find_weapon', sees_item_type_weapon=True)
	
	_weapon_search_actions.add_condition('get_weapon', sees_item_type_weapon=True)
	_weapon_search_actions.add_callback('get_weapon', lambda entity: ai_logic.get_weapon(entity))
	_weapon_search_actions.add_reaction('get_weapon', has_weapon=True)
	
	return _weapon_search_brain

def search_for_ammo():
	_brain = goapy.Planner('has_container', 'has_weapon', 'has_ammo', 'weapon_loaded', 'sees_item_type_ammo')
	_actions = goapy.Action_List()

	_brain.set_action_list(_actions)
	_brain.set_goal_state(has_ammo=True)

	_actions.add_condition('find_ammo', has_weapon=True, has_ammo=False, weapon_loaded=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	_actions.add_reaction('find_ammo', sees_item_type_ammo=True)
	
	_actions.add_condition('get_ammo', sees_item_type_ammo=True, has_container=True)
	_actions.add_callback('get_ammo', lambda entity: ai_logic.get_ammo(entity))
	_actions.add_reaction('get_ammo', has_ammo=True)
	
	return _brain

def search_for_container():
	_brain = goapy.Planner('has_container', 'sees_item_type_container')
	_actions = goapy.Action_List()

	_brain.set_action_list(_actions)
	_brain.set_goal_state(has_container=True)

	_actions.add_condition('find_container', has_container=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	_actions.add_reaction('find_container', sees_item_type_container=True)
	
	_actions.add_condition('get_container', sees_item_type_container=True)
	_actions.add_callback('get_container', lambda entity: ai_logic.get_container(entity))
	_actions.add_reaction('get_container', has_container=True)
	
	return _brain

def panic():
	_brain = goapy.Planner('is_panicked', 'in_engagement', 'is_target_near')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(is_panicked=False)
	
	_actions.add_condition('panic', is_panicked=True, in_engagement=False)
	#_actions.add_callback('panic', lambda entity: ai.set_meta(entity, 'is_panicked', False))
	_actions.add_reaction('panic', is_panicked=False)
	
	_actions.add_condition('flee', is_panicked=True, in_engagement=True, is_target_near=True)
	_actions.add_callback('flee', lambda entity: ai_logic.find_cover(entity))
	_actions.add_reaction('flee', is_panicked=False, is_target_near=False)
	
	return _brain

def reload():
	_brain = goapy.Planner('in_engagement', 'weapon_loaded', 'has_ammo', 'has_weapon')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(weapon_loaded=True)
	
	_actions.add_condition('reload', weapon_loaded=False, has_weapon=True, has_ammo=True)
	_actions.add_callback('reload', lambda entity: ai_logic.reload_weapon(entity))
	_actions.add_reaction('reload', weapon_loaded=True)
	
	_actions.add_condition('unpack_ammo', has_ammo=False)
	#_actions.add_callback('unpack_ammo', lambda entity: ai.set_meta(entity, 'has_ammo', True))
	_actions.add_reaction('unpack_ammo', has_ammo=True)
	
	_actions.add_condition('search_for_ammo', has_ammo=False)
	#_actions.add_callback('search_for_ammo', lambda entity: ai.set_meta(entity, 'has_ammo', True))
	_actions.add_reaction('search_for_ammo', has_ammo=True)	
	
	return _brain

def combat():
	_combat_brain = goapy.Planner('has_ammo',
                                  'has_weapon',
                                  'weapon_loaded',
                                  'in_engagement',
                                  'in_enemy_los',
                                  'is_target_near')
	_combat_brain.set_goal_state(in_engagement=False)

	_combat_actions = goapy.Action_List()
	_combat_actions.add_condition('track',
                                  in_enemy_los=False,
                                  weapon_loaded=True)
	_combat_actions.add_callback('track', ai_logic.find_firing_position)
	_combat_actions.add_reaction('track', in_enemy_los=True)
	
	_combat_actions.add_condition('shoot',
                                  weapon_loaded=True,
                                  in_enemy_los=True)
	_combat_actions.add_callback('shoot', ai_logic.shoot_weapon)
	_combat_actions.add_reaction('shoot', in_engagement=False)
	
	_combat_actions.set_weight('track', 20)

	_combat_brain.set_action_list(_combat_actions)
	
	return _combat_brain