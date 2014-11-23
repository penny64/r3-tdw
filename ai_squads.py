from framework import entities, numbers, movement, events, timers, tile

from ai_factions import FACTIONS

import ai_squad_director
import ai_squad_logic
import ai_flow
import constants
import settings
import zones

import logging


def boot():
	events.register_event('logic', logic)

def _create_squad(faction_name, x, y):
	_faction = FACTIONS[faction_name]
	_squad = entities.create_entity(group='squads')
	_squad.update({'members': set(),
	               'faction': faction_name,
	               'leader': None,
	               'member_info': {},
	               'camp_id': None,
	               'squad_id': _faction['squad_id'],
	               'task': None,
	               'brain': None,
	               'position_map': {},
	               'member_position_maps': {},
	               'member_los_maps': {},
	               'coverage_positions': set(),
	               'known_targets': set(),
	               'known_squads': set(),
	               'position_map_scores': {},
	               'meta': {'is_squad_combat_ready': False,
	                        'is_squad_mobile_ready': False,
	                        'is_squad_overwhelmed': False,
	                        'is_squad_forcing_surrender': False,
	                        'has_camp': False,
	                        'wants_artifacts': False,
	                        'wants_weapons': False},
	               'weights': {}})
	
	timers.register(_squad, use_entity_event='logic')
	movement.register(_squad, x, y)
	
	entities.create_event(_squad, 'meta_change')
	entities.create_event(_squad, 'raid')
	entities.create_event(_squad, 'update_position_map')
	entities.create_event(_squad, 'new_squad_member')
	entities.register_event(_squad, 'raid', handle_raid)
	entities.register_event(_squad, 'update_position_map', ai_squad_director.create_position_map)
	
	_faction['squads'][_faction['squad_id']] = _squad['_id']
	#entity['ai']['meta']['is_squad_leader'] = True
	
	#register_with_squad(entity, _faction['squad_id'])
	
	_faction['squad_id'] += 1
	
	entities.register_event(_squad, 'new_squad_member', update_squad_member_snapshot)
	entities.register_event(_squad, 'new_squad_member', lambda e, **kwargs: update_group_status(e))
	entities.register_event(ai_flow.FLOW, 'start_of_turn', lambda e, squad_id: handle_start_of_turn(_squad, squad_id))
	
	logging.info('Faction \'%s\' created new squad.' % faction_name)
	
	return _squad

def create_human_squad(faction_name, x, y):
	_squad = _create_squad(faction_name, x, y)
	
	ai_squad_logic.register_human(_squad)
	
	return _squad

def create_wild_dog_squad(entity):
	_squad = _create_squad(entity)
	
	ai_squad_logic.register_wild_dog(_squad)
	
	return _squad

def logic():
	#for faction in FACTIONS.values():
	#	for squad in faction['squads'].values():
	#		entities.trigger_event(squad, 'create')
	
	for faction in FACTIONS.values():
		for squad_id in faction['squads'].values():
			_squad = entities.get_entity(squad_id)
			
			entities.trigger_event(_squad, 'logic')

def register_with_squad(entity, squad_id):
	entity['ai']['squad'] = squad_id
	
	_squad = get_assigned_squad(entity)
	
	_squad['members'].add(entity['_id'])
	_squad['member_position_maps'][entity['_id']] = set()
	
	if not _squad['leader']:
		_squad['leader'] = entity['_id']
	
	entity['ai']['meta']['is_squad_leader'] = _squad['leader'] == entity['_id']
	
	entities.create_event(entity, 'squad_inform_raid')
	entities.register_event(_squad, 'meta_change', lambda e, **kwargs: entities.trigger_event(entity, 'set_meta', **kwargs))
	#entities.register_event(entity, 'position_changed', lambda e, **kwargs: _squad['_id'] in entities.ENTITIES and entities.trigger_event(_squad, 'update_position_map', member_id=entity['_id']))
	entities.register_event(entity, 'meta_change', lambda e, **kwargs: update_squad_member_snapshot(_squad, target_id=e['_id']))
	entities.register_event(entity, 'meta_change', lambda e, **kwargs: update_group_status(_squad)) #TODO: Needs to be moved to a general area. Are squad members registering this?
	entities.register_event(entity, 'target_lost', ai_squad_logic.leader_handle_lost_target)
	entities.register_event(entity, 'target_lost', lambda e, **kwargs: update_combat_risk)
	entities.register_event(entity, 'target_found', lambda e, **kwargs: update_combat_risk)
	entities.register_event(entity, 'squad_inform_raid', ai_squad_logic.member_learn_raid)
	entities.register_event(entity,
	                        'killed_by',
	                        lambda e, target_id, **kwargs: remove_member(_squad, entity['_id']))
	
	entities.trigger_event(_squad, 'new_squad_member', target_id=entity['_id'])

def remove_member(squad, member_id):
	pass
	#TODO: This is done elsewhere
	#if member_id in squad['members']:
	#	squad['members'].remove(member_id)
	
	#if not squad['members']:
	#	entities.delete_entity(squad)

def get_assigned_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = entity['ai']['squad']
	
	if _squad == -1:
		raise Exception('Entity is not in a squad.')
	
	return entities.get_entity(_faction['squads'][_squad])

'''def assign_to_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_nearest_squad = {'squad_id': None, 'distance': 0}
	
	#Check for fitting squads (by squad leader)
	
	for squad_id in _faction['squads']:
		_squad = entities.get_entity(_faction['squads'][squad_id])
		
		if len(_squad['members']) >= _faction['squad_size_range'][1]:
			continue
		
		_distance_to_leader = numbers.distance(movement.get_position(entity),
											   movement.get_position_via_id(_squad['leader']))
		
		if _distance_to_leader >= constants.MAX_SQUAD_LEADER_DISTANCE:
			continue
		
		if not _nearest_squad['squad_id'] or _distance_to_leader < _nearest_squad['distance']:
			_nearest_squad['squad_id'] = squad_id
			_nearest_squad['distance'] = _distance_to_leader
	
	if _nearest_squad['squad_id']:
		_squad = entities.get_entity(_faction['squads'][_nearest_squad['squad_id']])
		_squad['members'].add(entity['_id'])
		_leader = entities.get_entity(_squad['leader'])
		
		register_with_squad(entity, _nearest_squad['squad_id'])
		
		entities.create_event(entity, 'squad_inform_raid')
		entities.register_event(entity, 'squad_inform_raid', ai_squad_logic.member_learn_raid)
		
		logging.info('Faction \'%s\' added member to squad %s: %s' % (entity['ai']['faction'],
		                                                              entity['ai']['squad'],
		                                                              entity['stats']['name']))
	
	else:
		if entity['stats']['kind'] == 'human':
			create_human_squad(entity)
		
		elif entity['stats']['kind'] == 'animal':
			create_wild_dog_squad(entity)'''

def update_squad_member_snapshot(entity, target_id):
	_target = entities.get_entity(target_id)
	
	if 'has_weapon' in _target['ai']['meta']:
		_snapshot = {'armed': _target['ai']['meta']['has_weapon']}
	else:
		_snapshot = {}
	
	entity['member_info'].update({target_id: _snapshot})

def set_squad_meta(entity, meta, value):
	_old_value = entity['meta'][meta]
	
	if not value == _old_value:
		entities.trigger_event(entity, 'meta_change', meta=meta, value=value)
		
		entity['meta'][meta] = value

def update_group_status(entity):
	_members_combat_ready = 0
	
	for member_id in entity['member_info']:
		_member = entities.get_entity(member_id)
		
		if _member['ai']['meta']['has_needs'] and not _member['ai']['meta']['weapon_loaded']:
			continue
		
		if _member['ai']['meta']['is_injured'] or _member['ai']['meta']['is_panicked']:
			continue
		
		if timers.has_timer_with_name(_member, 'passout'):
			continue
		
		_members_combat_ready += entity['member_info'][member_id]['armed']
	
	set_squad_meta(entity, 'is_squad_combat_ready', _members_combat_ready / float(len(entity['member_info'].keys())) >= .65)
	set_squad_meta(entity, 'is_squad_mobile_ready', _members_combat_ready / float(len(entity['member_info'].keys())) >= .65)

def update_combat_risk(entity):
	_squad_member_count = len(entity['member_info'].keys())
	_squad_enemies = set()
	_squad_armed_enemies = set()
	
	for member_id in entity['member_info']:
		_member = entities.get_entity(member_id)
		
		_squad_enemies.update(_member['ai']['targets'])
		_squad_armed_enemies.update([e for e in _member['ai']['targets'] if _member['ai']['life_memory'][e]['is_armed']])
	
	_target_count = len(_squad_enemies)
	_armed_target_count = len(_squad_armed_enemies)
	
	#TODO: Is this right? Who all is registered to see this change (everyone, 90% sure)
	if not _armed_target_count and _target_count:
		set_squad_meta(entity, 'is_squad_overwhelmed', False)
	
	else:
		set_squad_meta(entity, 'is_squad_overwhelmed', _armed_target_count > _squad_member_count)

def handle_start_of_turn(entity, squad_id):
	update_combat_risk(entity)
	update_group_status(entity)
	entities.trigger_event(entity, 'update_position_map')
	
	if entity['faction'] == 'Rogues':
		settings.set_tick_mode('strategy')
	
	else:
		settings.set_tick_mode('normal')

def handle_raid(entity, camp_id):
	entity['movement']['override_speed'] = 60 * 5
	
	movement.walk_to_position(entity, camp_id[0], camp_id[1], zones.get_active_astar_map(), zones.get_active_weight_map())
	
	#_leader = entities.get_entity(entity['leader'])
	
	#ai_squad_logic.leader_handle_raid_camp(_leader, camp)
