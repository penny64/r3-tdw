from framework import entities, numbers, movement

import ai_squad_logic
import constants
import mapgen

import logging

FACTIONS = {}


def _create(name, min_squad_size, max_squad_size, enemy_factions):
	_faction = {'members': set(),
	            'squads': {},
	            'squad_id': 1,
	            'brains': [],
	            'squad_size_range': (min_squad_size, max_squad_size),
	            'enemies': enemy_factions}
	
	FACTIONS[name] = _faction

def boot():
	_create('Bandits', 3, 5, ['Runners', 'Rogues'])
	_create('Runners', 3, 5, ['Bandits'])
	_create('Rogues', 1, 1, ['Bandits'])

def register(entity, faction):
	if not faction in FACTIONS:
		raise Exception('Invalid faction: %s' % faction)
	
	entities.create_event(entity, 'new_squad_member')
	
	entity['ai']['faction'] = faction
	entity['ai']['squad'] = -1
	
	FACTIONS[entity['ai']['faction']]['members'].add(entity['_id'])
	
	assign_to_squad(entity)


############
#Operations#
############

def create_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = {'members': set([entity['_id']]),
	          'leader': entity['_id'],
	          'member_info': {},
	          'camp_id': None,
	          'meta': {'is_squad_combat_ready': False,
	                   'is_squad_overwhelmed': False,
	                   'is_squad_forcing_surrender': False}}
	_faction['squads'][_faction['squad_id']] = _squad
	entity['ai']['squad'] = _faction['squad_id']
	entity['ai']['meta']['is_squad_leader'] = True
	_faction['squad_id'] += 1
	
	entities.register_event(entity, 'meta_change', lambda e, **kwargs: update_squad_member_snapshot(e, target_id=e['_id']))
	entities.register_event(entity, 'meta_change', update_group_status)
	entities.register_event(entity, 'new_squad_member', update_squad_member_snapshot)
	entities.register_event(entity, 'new_squad_member', lambda e, **kwargs: update_group_status(e))
	entities.register_event(entity, 'target_lost', ai_squad_logic.leader_handle_lost_target)
	entities.register_event(entity, 'target_lost', lambda e, **kwargs: update_combat_risk)
	entities.register_event(entity, 'target_found', lambda e, **kwargs: update_combat_risk)
	
	entities.trigger_event(entity, 'create_timer',
	                       time=60,
	                       repeat=-1,
	                       repeat_callback=update_group_status)
	
	entities.trigger_event(entity, 'create_timer',
	                       time=60,
	                       repeat=-1,
	                       repeat_callback=update_combat_risk)
	
	logging.info('Faction \'%s\' created new squad: %s (leader: %s)' % (entity['ai']['faction'],
	                                                                    _faction['squad_id']-1,
	                                                                    entity['stats']['name']))

def get_assigned_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = entity['ai']['squad']
	
	if _squad == -1:
		raise Exception('Entity is not in a squad.')
	
	return _faction['squads'][_squad]

def assign_to_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_nearest_squad = {'squad_id': None, 'distance': 0}
	
	#Check for fitting squads (by squad leader)
	
	for squad_id in _faction['squads']:
		_squad = _faction['squads'][squad_id]
		
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
		_faction['squads'][_nearest_squad['squad_id']]['members'].add(entity['_id'])
		_leader = entities.get_entity(_squad['leader'])
		
		entity['ai']['squad'] = _nearest_squad['squad_id']
		
		entities.trigger_event(_leader, 'new_squad_member', target_id=entity['_id'])
		entities.trigger_event(entity, 'create_timer',
		                       time=60,
		                       repeat=-1,
		                       repeat_callback=lambda e: update_squad_member_snapshot(_leader, target_id=entity['_id']))
		
		logging.info('Faction \'%s\' added member to squad %s: %s' % (entity['ai']['faction'],
		                                                              entity['ai']['squad'],
		                                                              entity['stats']['name']))
	
	else:
		create_squad(entity)

def update_squad_member_snapshot(entity, target_id):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_target = entities.get_entity(target_id)
	_snapshot = {'armed': _target['ai']['meta']['has_weapon']}
	
	_squad['member_info'].update({target_id: _snapshot})

def update_group_status(entity):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_members_combat_ready = 0
	
	for member_id in _squad['member_info']:
		_member = entities.get_entity(member_id)
		
		if _member['ai']['meta']['has_needs']:
			continue
		
		_members_combat_ready += _squad['member_info'][member_id]['armed']
	
	_squad['meta']['is_squad_combat_ready'] = _members_combat_ready / float(len(_squad['member_info'].keys())) >= .5
	_squad['meta']['is_squad_mobile_ready'] = _members_combat_ready / float(len(_squad['member_info'].keys())) >= .75

def update_combat_risk(entity):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_squad_member_count = len(_squad['member_info'].keys())
	_target_count = len(entity['ai']['targets'])
	_armed_target_count = len([e for e in entity['ai']['targets'] if entity['ai']['life_memory'][e]['is_armed']])
	
	if not _armed_target_count and _target_count:
		#_squad['meta']['is_squad_forcing_surrender'] = True
		_squad['meta']['is_squad_overwhelmed'] = False
	else:
		_squad['meta']['is_squad_overwhelmed'] = _armed_target_count > _squad_member_count

def apply_squad_meta(entity):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	
	entity['ai']['meta'].update(_squad['meta'])
