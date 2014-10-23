from framework import goapy

import ai_squad_logic
import ai_logic
import ai

import logging


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
	_weapon_search_brain = goapy.Planner('has_weapon', 'sees_item_type_weapon', 'is_panicked')
	_weapon_search_actions = goapy.Action_List()

	_weapon_search_brain.set_action_list(_weapon_search_actions)
	_weapon_search_brain.set_goal_state(has_weapon=True)

	_weapon_search_actions.add_condition('find_weapon', has_weapon=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	_weapon_search_actions.add_reaction('find_weapon', sees_item_type_weapon=True)
	
	_weapon_search_actions.add_condition('get_weapon', sees_item_type_weapon=True, is_panicked=False)
	_weapon_search_actions.add_callback('get_weapon', lambda entity: ai_logic.get_weapon(entity))
	_weapon_search_actions.add_reaction('get_weapon', has_weapon=True)
	
	return _weapon_search_brain

def search_for_ammo():
	_brain = goapy.Planner('has_container', 'has_weapon', 'has_ammo', 'weapon_loaded', 'sees_item_type_ammo', 'is_panicked')
	_actions = goapy.Action_List()

	_brain.set_action_list(_actions)
	_brain.set_goal_state(has_ammo=True)

	_actions.add_condition('find_ammo', has_weapon=True, has_ammo=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	_actions.add_reaction('find_ammo', sees_item_type_ammo=True)
	
	_actions.add_condition('get_ammo', sees_item_type_ammo=True, has_container=True, weapon_loaded=False, has_ammo=False, is_panicked=False)
	_actions.add_callback('get_ammo', lambda entity: ai_logic.get_ammo(entity))
	_actions.add_reaction('get_ammo', has_ammo=True)
	
	return _brain

def search_for_container():
	_brain = goapy.Planner('has_container', 'sees_item_type_container', 'in_engagement')
	_actions = goapy.Action_List()

	_brain.set_action_list(_actions)
	_brain.set_goal_state(has_container=True)

	#_actions.add_condition('find_container', has_container=False, in_engagement=False)
	#_weapon_search_actions.add_callback('find_weapon', lambda entity: ai_logic.find_weapon(entity))
	#_actions.add_reaction('find_container', sees_item_type_container=True)
	
	_actions.add_condition('get_container', sees_item_type_container=True, in_engagement=False)
	_actions.add_callback('get_container', lambda entity: ai_logic.get_container(entity))
	_actions.add_reaction('get_container', has_container=True)
	
	return _brain

def search_for_target():
	_brain = goapy.Planner('weapon_loaded',
	                       'is_target_lost',
	                       'is_squad_mobile_ready')
	
	_brain.set_goal_state(is_target_lost=False)

	_actions = goapy.Action_List()
	_actions.add_condition('search',
	                       is_target_lost=True,
	                       weapon_loaded=True,
	                       is_squad_mobile_ready=True)
	_actions.add_callback('search', ai_logic.search_for_target)
	_actions.add_reaction('search', is_target_lost=False)
	
	_brain.set_action_list(_actions)
		
	return _brain

def panic():
	_brain = goapy.Planner('is_panicked', 'in_engagement', 'is_target_near')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(is_panicked=False)
	
	_actions.add_condition('flee', is_panicked=True, in_engagement=True)
	_actions.add_callback('flee', lambda entity: ai_logic.find_cover(entity))
	_actions.add_reaction('flee', is_panicked=False)
	
	return _brain

def reload():
	_brain = goapy.Planner('in_enemy_los', 'weapon_loaded', 'has_ammo', 'has_weapon')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(weapon_loaded=True)
	
	_actions.add_condition('cover', in_enemy_los=True)
	_actions.add_callback('cover', ai_logic.find_cover)
	_actions.add_reaction('cover', in_enemy_los=False)
	
	_actions.add_condition('reload', weapon_loaded=False, has_weapon=True, has_ammo=True, in_enemy_los=False)
	_actions.add_callback('reload', lambda entity: ai_logic.reload_weapon(entity))
	_actions.add_reaction('reload', weapon_loaded=True)
	
	return _brain

def squad_leader_regroup():
	_brain = goapy.Planner('is_squad_mobile_ready', 'in_engagement', 'is_target_lost', 'is_squad_leader')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(is_squad_mobile_ready=True)
	
	_actions.add_condition('regroup', is_squad_mobile_ready=False, in_engagement=False, is_target_lost=False)
	_actions.add_callback('regroup', ai_squad_logic.leader_order_regroup)
	_actions.add_reaction('regroup', is_squad_mobile_ready=True)
	
	return _brain

def squad_capture_camp():
	_brain = goapy.Planner('has_camp')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(has_camp=True)
	
	_actions.add_condition('capture', has_camp=False)
	_actions.add_callback('capture', ai_squad_logic.capture_camp)
	_actions.add_reaction('capture', has_camp=True)
	
	return _brain

def combat():
	_combat_brain = goapy.Planner('has_ammo',
                                  'has_weapon',
                                  'weapon_loaded',
                                  'in_engagement',
                                  'in_enemy_los',
                                  'is_target_near',
	                              'is_target_lost',
	                              'is_squad_combat_ready',
	                              'is_squad_overwhelmed',
	                              'is_squad_forcing_surrender',
	                              'is_squad_mobile_ready',
	                              'is_target_armed',
	                              'has_firing_position',
	                              'is_panicked')
	_combat_brain.set_goal_state(in_engagement=False)

	_combat_actions = goapy.Action_List()
	
	_combat_actions.add_condition('position',
	                              weapon_loaded=True,
	                              has_firing_position=True,
	                              is_target_near=False)
	_combat_actions.add_callback('position', ai_logic.find_firing_position)
	_combat_actions.add_reaction('position', is_target_near=True, in_enemy_los=True)
	
	_combat_actions.add_condition('camp',
	                              weapon_loaded=True,
	                              has_firing_position=False)
	_combat_actions.add_callback('camp', ai_logic.find_cover)
	_combat_actions.add_reaction('camp', has_firing_position=True)
	
	_combat_actions.add_condition('shoot',
                                  weapon_loaded=True,
                                  in_enemy_los=True,
	                              is_target_near=True,
	                              is_target_lost=False,
	                              is_squad_combat_ready=True,
	                              is_squad_overwhelmed=False,
	                              is_squad_forcing_surrender=False,
	                              has_firing_position=True,
	                              is_panicked=False)
	_combat_actions.add_callback('shoot', ai_logic.shoot_weapon)
	_combat_actions.add_reaction('shoot', in_engagement=False)
	
	#TODO: This doesn't work because is_target_near was repurposed as more of a "in shooting range" value
	#_combat_actions.add_condition('panic_shoot',
	#                              weapon_loaded=True,
	#                              in_enemy_los=True,
	#                              is_target_lost=False,
	#                              is_squad_overwhelmed=False,
	#                              is_squad_forcing_surrender=False,
	#                              has_firing_position=False,
	#                              is_target_near=True)
	#_combat_actions.add_callback('panic_shoot', ai_logic.shoot_weapon)
	#_combat_actions.add_reaction('panic_shoot', in_engagement=False)
	
	#_combat_actions.set_weight('track', 20)
	#_combat_actions.set_weight('make_surrender', 10)

	_combat_brain.set_action_list(_combat_actions)
	
	return _combat_brain

def dog_combat():
	_combat_brain = goapy.Planner('in_engagement',
                                  'in_enemy_los',
                                  'is_target_near',
	                              'is_target_lost',
	                              'is_squad_overwhelmed',
	                              'is_in_melee_range')
	_combat_brain.set_goal_state(in_engagement=False)

	_combat_actions = goapy.Action_List()
	
	_combat_actions.add_condition('search',
		                          is_target_lost=True)
	_combat_actions.add_callback('search', ai_logic.search_for_target)
	_combat_actions.add_reaction('search', in_enemy_los=True, is_target_lost=False)
	
	_combat_actions.add_condition('position',
	                              is_target_lost=False,
                                  is_in_melee_range=False)
	_combat_actions.add_callback('position', ai_logic.find_melee_position)
	_combat_actions.add_reaction('position', is_in_melee_range=True)
	
	_combat_actions.add_condition('bite',
	                              is_squad_overwhelmed=False,
	                              is_in_melee_range=True)
	_combat_actions.add_callback('bite', ai_logic.melee)
	_combat_actions.add_reaction('bite', in_engagement=False)
	
	#_combat_actions.set_weight('track', 20)

	_combat_brain.set_action_list(_combat_actions)
	
	return _combat_brain