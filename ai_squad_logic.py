from framework import entities, movement

import ai_factions


def leader_handle_lost_target(entity, target_id):
	pass


#Lost targets

def member_handle_lost_target(entity, target_id):
	for member_id in ai_factions.get_assigned_squad(entity)['members']:
		if member_id == entity['_id']:
			continue
			
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_lost_target', member_id=entity['_id'], target_id=target_id)

def member_learn_lost_target(entity, member_id, target_id):
	if not target_id in entity['ai']['visible_life']:
		return
	
	_sender = entities.get_entity(member_id)
	
	entities.trigger_event(_sender, 'update_target_memory',
	                       target_id=target_id,
	                       key='last_seen_at',
	                       value=entity['ai']['life_memory'][target_id]['last_seen_at'][:])


#Found targets

def member_handle_found_target(entity, target_id):
	for member_id in ai_factions.get_assigned_squad(entity)['members']:
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
	
	movement.walk_to_position(entity, _last_seen_at[0], _last_seen_at[1])


#Failed target search

def member_handle_failed_target_search(entity, target_id):
	for member_id in ai_factions.get_assigned_squad(entity)['members']:
		if member_id == entity['_id']:
			continue
			
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_failed_search', member_id=entity['_id'], target_id=target_id)

def member_learn_failed_target_search(entity, member_id, target_id):
	print 'Learned about failed search'


#Regrouping

def leader_order_regroup(entity):
	print 'Leader ordering regroup'


#Raiding

def leader_handle_raid_camp(entity, camp):
	for member_id in ai_factions.get_assigned_squad(entity)['members']:
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'squad_inform_raid', member_id=entity['_id'], camp=camp)

def member_learn_raid(entity, member_id, camp):
	_camp_leader = entities.get_entity(ai_factions.FACTIONS[camp['owner']['faction']]['squads'][camp['owner']['squad']]['leader'])
	
	#TODO: Don't do this
	entity['ai']['life_memory'][_camp_leader['_id']] = {'distance': -1,
	                                                    'is_target': True,
	                                                    'is_armed': False,
	                                                    'can_see': False,
	                                                    'last_seen_at': movement.get_position(_camp_leader),
	                                                    'last_seen_velocity': None}
	entity['ai']['targets'].add(_camp_leader['_id'])
