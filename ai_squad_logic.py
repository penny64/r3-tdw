from framework import entities

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