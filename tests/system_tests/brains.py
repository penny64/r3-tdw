from framework import goapy

import system_ai


def heal():
	_heal_brain = goapy.Planner('is_injured', 'has_bandage')
	_heal_actions = goapy.Action_List()
	
	_heal_actions.add_condition('apply_bandage', has_bandage=True)
	_heal_actions.add_callback('apply_bandage', lambda entity: system_ai.set_meta(entity, 'is_injured', False))
	_heal_actions.add_reaction('apply_bandage', is_injured=False)
	
	_heal_actions.add_condition('find_bandage', has_bandage=False)
	_heal_actions.add_callback('find_bandage', lambda entity: system_ai.set_meta(entity, 'has_bandage', True))
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
	_weapon_search_actions.add_callback('find_weapon', lambda entity: system_ai.set_meta(entity, 'sees_item_type_weapon', True))
	_weapon_search_actions.add_reaction('find_weapon', sees_item_type_weapon=True)
	
	_weapon_search_actions.add_condition('get_weapon', sees_item_type_weapon=True)
	_weapon_search_actions.add_callback('get_weapon', lambda entity: system_ai.set_meta(entity, 'has_weapon', True))
	_weapon_search_actions.add_reaction('get_weapon', has_weapon=True)
	
	return _weapon_search_brain

def panic():
	_brain = goapy.Planner('is_panicked', 'in_engagement', 'is_near')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(is_panicked=False)
	
	_actions.add_condition('panic', is_panicked=True, in_engagement=False)
	_actions.add_callback('panic', lambda entity: system_ai.set_meta(entity, 'is_panicked', False))
	_actions.add_reaction('panic', is_panicked=False)
	
	_actions.add_condition('flee', is_panicked=True, in_engagement=True, is_near=True)
	_actions.add_callback('flee', lambda entity: system_ai.set_meta(entity, 'is_panicked', False))
	_actions.add_callback('flee', lambda entity: system_ai.set_meta(entity, 'is_near', False))
	_actions.add_reaction('flee', is_panicked=False, is_near=False)
	
	return _brain

def reload():
	_brain = goapy.Planner('in_engagement', 'weapon_loaded', 'weapon_armed', 'has_ammo', 'has_weapon')
	_actions = goapy.Action_List()
	
	_brain.set_action_list(_actions)
	_brain.set_goal_state(weapon_loaded=True)
	
	_actions.add_condition('reload', weapon_loaded=False, has_weapon=True, has_ammo=True, in_engagement=False)
	_actions.add_callback('reload', lambda entity: system_ai.set_meta(entity, 'weapon_loaded', True))
	_actions.add_reaction('reload', weapon_loaded=True)
	
	_actions.add_condition('arm',
	                       weapon_loaded=True,
	                       weapon_armed=False,
	                       has_weapon=True)
	_actions.add_callback('arm', lambda entity: system_ai.set_meta(entity, 'weapon_armed', True))
	_actions.add_reaction('arm', weapon_armed=True)
	
	_actions.add_condition('unpack_ammo', has_ammo=False)
	_actions.add_callback('unpack_ammo', lambda entity: system_ai.set_meta(entity, 'has_ammo', True))
	_actions.add_reaction('unpack_ammo', has_ammo=True)
	
	_actions.add_condition('search_for_ammo', has_ammo=False)
	_actions.add_callback('search_for_ammo', lambda entity: system_ai.set_meta(entity, 'has_ammo', True))
	_actions.add_reaction('search_for_ammo', has_ammo=True)	
	
	return _brain

def combat():
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
	_combat_actions.add_callback('track', lambda entity: system_ai.set_meta(entity, 'is_near', True))
	_combat_actions.add_reaction('track', is_near=True)
	
	_combat_actions.add_condition('unpack_ammo', has_ammo=False)
	_combat_actions.add_callback('unpack_ammo', lambda entity: system_ai.set_meta(entity, 'has_ammo', True))
	_combat_actions.add_reaction('unpack_ammo', has_ammo=True)
	
	_combat_actions.add_condition('search_for_ammo', has_ammo=False)
	_combat_actions.add_callback('search_for_ammo', lambda entity: system_ai.set_meta(entity, 'has_ammo', True))
	_combat_actions.add_reaction('search_for_ammo', has_ammo=True)
	
	_combat_actions.add_condition('reload',
                                  has_ammo=True,
                                  weapon_loaded=False,
                                  in_cover=True)
	_combat_actions.add_callback('reload', lambda entity: system_ai.set_meta(entity, 'weapon_loaded', True))
	_combat_actions.add_reaction('reload', weapon_loaded=True)
	
	_combat_actions.add_condition('arm',
                                  weapon_loaded=True,
                                  weapon_armed=False,
	                              has_weapon=True)
	_combat_actions.add_callback('arm', lambda entity: system_ai.set_meta(entity, 'weapon_armed', True))
	_combat_actions.add_reaction('arm', weapon_armed=True)
	
	_combat_actions.add_condition('shoot',
                                  weapon_loaded=True,
                                  weapon_armed=True,
                                  is_near=True)
	_combat_actions.add_callback('shoot', lambda entity: system_ai.set_meta(entity, 'in_engagement', False))
	_combat_actions.add_reaction('shoot', in_engagement=False)
	
	_combat_actions.add_condition('get_cover', in_cover=False)
	_combat_actions.add_callback('get_cover', lambda entity: system_ai.set_meta(entity, 'in_cover', True))
	_combat_actions.add_reaction('get_cover', in_cover=True)
	
	_combat_actions.set_weight('unpack_ammo', 3)
	_combat_actions.set_weight('search_for_ammo', 4)
	_combat_actions.set_weight('track', 20)

	_combat_brain.set_action_list(_combat_actions)
	
	return _combat_brain