from framework import entities, numbers, movement, events

from ai_factions import FACTIONS

import ai_squad_director
import ai_squad_logic
import constants

import logging


def boot():
	events.register_event('logic', logic)

def _create_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = entities.create_entity(group='squads')
	_squad.update({'members': set([entity['_id']]),
	               'faction': entity['ai']['faction'],
	               'leader': entity['_id'],
	               'member_info': {},
	               'camp_id': None,
	               'task': None,
	               'brain': None,
	               'position_map': {},
	               'member_position_maps': {},
	               'member_los_maps': {},
	               'coverage_positions': set(),
	               'known_targets': set(),
	               'known_squads': set(),
	               'update_position_maps': False,
	               'position_map_scores': {},
	               'meta': {'is_squad_combat_ready': False,
	                        'is_squad_mobile_ready': False,
	                        'is_squad_overwhelmed': False,
	                        'is_squad_forcing_surrender': False,
	                        'has_camp': False,
	                        'wants_artifacts': False,
	                        'wants_weapons': False},
	               'weights': {}})
	
	entities.create_event(_squad, 'meta_change')
	entities.create_event(_squad, 'raid')
	entities.create_event(_squad, 'update_position_map')
	entities.register_event(_squad, 'raid', handle_raid)
	entities.register_event(_squad, 'logic', ai_squad_director.update_position_maps)
	entities.register_event(_squad, 'update_position_map', ai_squad_director.create_position_map)
	
	_faction['squads'][_faction['squad_id']] = _squad
	entity['ai']['meta']['is_squad_leader'] = True
	
	register_with_squad(entity, _faction['squad_id'])
	
	_faction['squad_id'] += 1
	
	entities.create_event(entity, 'squad_inform_raid')
	entities.register_event(entity, 'meta_change', lambda e, **kwargs: update_squad_member_snapshot(e, target_id=e['_id']))
	entities.register_event(entity, 'meta_change', update_group_status)
	entities.register_event(entity, 'new_squad_member', update_squad_member_snapshot)
	entities.register_event(entity, 'new_squad_member', lambda e, **kwargs: update_group_status(e))
	entities.register_event(entity, 'target_lost', ai_squad_logic.leader_handle_lost_target)
	entities.register_event(entity, 'target_lost', lambda e, **kwargs: update_combat_risk)
	entities.register_event(entity, 'target_found', lambda e, **kwargs: update_combat_risk)
	entities.register_event(entity, 'squad_inform_raid', ai_squad_logic.member_learn_raid)
	
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
	
	return _squad

def create_human_squad(entity):
	_squad = _create_squad(entity)
	
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
		for squad in faction['squads'].values():
			entities.trigger_event(squad, 'logic')

def register_with_squad(entity, squad_id):
	entity['ai']['squad'] = squad_id
	
	_squad = get_assigned_squad(entity)
	
	_squad['member_position_maps'][entity['_id']] = set()
	
	entities.register_event(_squad, 'meta_change', lambda e, **kwargs: entities.trigger_event(entity, 'set_meta', **kwargs))
	entities.register_event(entity, 'position_changed', lambda e, **kwargs: entities.trigger_event(_squad, 'update_position_map', member_id=entity['_id']))

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
		
		register_with_squad(entity, _nearest_squad['squad_id'])
		
		entities.trigger_event(_leader, 'new_squad_member', target_id=entity['_id'])
		entities.trigger_event(entity, 'create_timer',
		                       time=60,
		                       repeat=-1,
		                       repeat_callback=lambda e: update_squad_member_snapshot(_leader, target_id=entity['_id']))
		
		entities.create_event(entity, 'squad_inform_raid')
		entities.register_event(entity, 'squad_inform_raid', ai_squad_logic.member_learn_raid)
		
		logging.info('Faction \'%s\' added member to squad %s: %s' % (entity['ai']['faction'],
		                                                              entity['ai']['squad'],
		                                                              entity['stats']['name']))
	
	else:
		if entity['stats']['kind'] == 'human':
			create_human_squad(entity)
		
		elif entity['stats']['kind'] == 'animal':
			create_wild_dog_squad(entity)

def update_squad_member_snapshot(entity, target_id):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_target = entities.get_entity(target_id)
	
	if 'has_weapon' in _target['ai']['meta']:
		_snapshot = {'armed': _target['ai']['meta']['has_weapon']}
	else:
		_snapshot = {}
	
	_squad['member_info'].update({target_id: _snapshot})

def set_squad_meta(entity, meta, value):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_old_value = _squad['meta'][meta]
	
	if not value == _old_value:
		entities.trigger_event(_squad, 'meta_change', meta=meta, value=value)
		
		_squad['meta'][meta] = value

def update_group_status(entity):
	_squad = FACTIONS[entity['ai']['faction']]['squads'][entity['ai']['squad']]
	_members_combat_ready = 0
	
	if not 'has_weapon' in entity['ai']['meta']:
		return
	
	for member_id in _squad['member_info']:
		_member = entities.get_entity(member_id)
		
		if _member['ai']['meta']['has_needs'] and not _member['ai']['meta']['weapon_loaded']:
			continue
		
		_members_combat_ready += _squad['member_info'][member_id]['armed']
	
	set_squad_meta(entity, 'is_squad_combat_ready', _members_combat_ready / float(len(_squad['member_info'].keys())) >= .5)
	set_squad_meta(entity, 'is_squad_mobile_ready', _members_combat_ready / float(len(_squad['member_info'].keys())) >= .65)

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

def handle_raid(entity, camp):
	_leader = entities.get_entity(entity['leader'])
	
	ai_squad_logic.leader_handle_raid_camp(_leader, camp)
