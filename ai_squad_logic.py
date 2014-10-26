from framework import entities, movement, goapy

import ai_factions
import ai_squads
import brains
import zones
import life

def register_human(entity):
	entity['brain'] = goapy.World()
	entity['brain'].add_planner(brains.squad_capture_camp())
	
	entities.register_event(entity, 'logic', _human_logic)
	
	return entity

def register_wild_dog(entity):
	entity['brain'] = goapy.World()
	entity['brain'].add_planner(brains.squad_capture_camp())
	
	entities.register_event(entity, 'logic', _wild_dog_logic)
	
	return entity

def _handle_goap(entity, brain='brain'):
	for planner in entity[brain].planners:
		_start_state = {}
		
		for key in planner.values.keys():
			_start_state[key] = entity['meta'][key]
			
		for key in planner.action_list.conditions.keys():
			if key in entity['weights']:
				planner.action_list.set_weight(key, entity['weights'][key])
		
		planner.set_start_state(**_start_state)
		
	entity[brain].calculate()
	
	return entity[brain].get_plan(debug=False)


#######
#Logic#
#######

def _human_logic(entity):
	if not entity['leader']:
		return
	
	entity['meta']['has_camp'] = entity['camp_id'] > 0
	
	if entities.get_entity(entity['leader'])['ai']['is_player']:
		return
	
	_goap = _handle_goap(entity)
	
	if not _goap:
		return	
	
	_plan = _goap[0]
	_plan['planner'].trigger_callback(entity, _plan['actions'][0]['name'])

def _wild_dog_logic(entity):
	if not entity['leader']:
		return
	
	entity['meta']['has_camp'] = entity['camp_id'] > 0
	
	if entities.get_entity(entity['leader'])['ai']['is_player']:
		return
	
	_goap = _handle_goap(entity)
	
	if not _goap:
		return	
	
	_plan = _goap[0]
	_plan['planner'].trigger_callback(entity, _plan['actions'][0]['name'])

def leader_handle_lost_target(entity, target_id):
	pass


############
#Operations#
############

#Lost targets

def member_handle_lost_target(entity, target_id):
	for member_id in ai_squads.get_assigned_squad(entity)['members']:
		if member_id == entity['_id']:
			continue
			
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_lost_target', member_id=entity['_id'], target_id=target_id)
	
	entity['ai']['life_memory'][target_id]['is_lost'] = True
	entity['ai']['life_memory'][target_id]['searched_for'] = False

def member_learn_lost_target(entity, member_id, target_id):
	if not target_id in entity['ai']['visible_life']:
		entity['ai']['life_memory'][target_id]['is_lost'] = True
		entity['ai']['life_memory'][target_id]['searched_for'] = False
		
		return
	
	_sender = entities.get_entity(member_id)
	
	entities.trigger_event(_sender, 'update_target_memory',
	                       target_id=target_id,
	                       key='last_seen_at',
	                       value=entity['ai']['life_memory'][target_id]['last_seen_at'][:])


#Found targets

def member_handle_found_target(entity, target_id):
	for member_id in ai_squads.get_assigned_squad(entity)['members']:
		if member_id == entity['_id']:
			continue
			
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_found_target', member_id=entity['_id'], target_id=target_id)

def member_learn_found_target(entity, member_id, target_id):
	if target_id in entity['ai']['visible_life']:
		return
	
	_sender = entities.get_entity(member_id)
	
	entities.trigger_event(entity, 'update_target_memory',
	                       target_id=target_id,
	                       key='last_seen_at',
	                       value=_sender['ai']['life_memory'][target_id]['last_seen_at'][:])


#Make target surrender

def make_target_surrender(entity):
	_last_seen_at = entity['ai']['life_memory'][entity['ai']['nearest_target']]['last_seen_at']
	
	movement.walk_to_position(entity, _last_seen_at[0], _last_seen_at[1], zones.get_active_astar_map(), zones.get_active_weight_map())


#Failed target search

def member_handle_failed_target_search(entity, target_id):
	for member_id in ai_squads.get_assigned_squad(entity)['members']:
		if member_id == entity['_id']:
			continue
			
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_failed_search', member_id=entity['_id'], target_id=target_id)
	
	entity['ai']['life_memory'][target_id]['searched_for'] = True

def member_learn_failed_target_search(entity, member_id, target_id):
	entity['ai']['life_memory'][target_id]['searched_for'] = True
	
	print 'Learned about failed search'


#Regrouping

def leader_order_regroup(entity):
	print 'Leader ordering regroup'


#Raiding

def leader_handle_raid_camp(entity, camp):
	for member_id in ai_squads.get_assigned_squad(entity)['members']:
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_raid', member_id=entity['_id'], camp=camp)

def member_learn_raid(entity, member_id, camp):
	_faction = ai_factions.FACTIONS[camp['owner']['faction']]
	_squad = entities.get_entity(_faction['squads'][camp['owner']['squad']])
	
	if not _squad['leader']:
		return
	
	_camp_leader = entities.get_entity(_squad['leader'])
	
	#TODO: Don't do this
	if not _camp_leader['_id'] in entity['ai']['life_memory']:
		life.create_life_memory(entity, _camp_leader['_id'])
	
	entity['ai']['life_memory'][_camp_leader['_id']].update({'is_lost': True,
	                                                         'searched_for': False,
	                                                         'can_see': False,
	                                                         'last_seen_at': movement.get_position(_camp_leader),
	                                                         'last_seen_velocity': None})
	#entity['ai']['targets'].add(_camp_leader['_id'])


##################
#Squad Operations#
##################

def capture_camp(entity):
	_faction = ai_factions.FACTIONS[entity['faction']]
	_camps = zones.get_active_node_sets()
	
	for camp_id in _camps:
		_camp = _camps[camp_id]
		
		if not _camp['owner']['faction'] in _faction['enemies']:
			continue
		
		entities.trigger_event(entity, 'raid', camp=_camps[camp_id])
		
		entity['task'] = 'raid'
