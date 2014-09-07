from framework import entities, numbers, movement

import ai_faction_logic
import ai_squad_logic
import constants
import mapgen

import logging

FACTIONS = {}


def _create(name, squad_size_range, base_size_range, enemy_factions):
	_entity = entities.create_entity(group='factions')
	_faction = {'members': set(),
	            'squads': {},
	            'squad_id': 1,
	            'brains': [],
	            'meta': {},
	            'squad_size_range': squad_size_range,
	            'base_size_range': base_size_range,
	            'enemies': enemy_factions}
	
	_entity.update(_faction)
	
	FACTIONS[name] = _entity
	
	return _entity

def create_human_faction(name, squad_size_range, base_size_range, enemy_factions):
	_faction = _create(name, squad_size_range, base_size_range, enemy_factions)
	_faction['meta'] = {'wants_territory': False}
	
	return _faction

def create_dog_faction(name, squad_size_range, base_size_range, enemy_factions):
	_faction = _create(name, squad_size_range, base_size_range, enemy_factions)
	_faction['meta'] = {'wants_territory': False}
	
	ai_faction_logic.register_animal(_faction)
	
	return _faction

def boot():
	create_human_faction('Bandits', (3, 5), (4, 6), ['Runners', 'Rogues', 'Wild Dogs'])
	create_human_faction('Runners', (3, 5), (2, 3), ['Bandits', 'Wild Dogs'])
	create_human_faction('Rogues', (1, 1), (1, 1), ['Bandits', 'Wild Dogs'])
	create_dog_faction('Wild Dogs', (2, 4), (0, 0), ['Bandits', 'Runners', 'Rogues'])

def register(entity, faction):
	if not faction in FACTIONS:
		raise Exception('Invalid faction: %s' % faction)
	
	entities.create_event(entity, 'new_squad_member')
	entities.register_event(entity, 'delete', cleanup)
	
	entity['ai']['faction'] = faction
	entity['ai']['squad'] = -1
	
	FACTIONS[entity['ai']['faction']]['members'].add(entity['_id'])
	
	assign_to_squad(entity)

def logic():
	for faction in FACTIONS.values():
		entities.trigger_event(faction, 'logic')

def cleanup(entity):
	_squad = get_assigned_squad(entity)
	
	_squad['members'].remove(entity['_id'])
	del _squad['member_info'][entity['_id']]

############
#Operations#
############

def is_enemy(entity, target_id):
	_target = entities.get_entity(target_id)
	_faction = FACTIONS[entity['ai']['faction']]
	
	return _target['ai']['faction'] in _faction['enemies']

def register_with_squad(entity, squad_id):
	entity['ai']['squad'] = squad_id
	
	_squad = get_assigned_squad(entity)
	
	entities.register_event(_squad, 'meta_change', lambda e, **kwargs: entities.trigger_event(entity, 'set_meta', **kwargs))

def create_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = entities.create_entity(group='squads')
	_squad.update({'members': set([entity['_id']]),
	               'leader': entity['_id'],
	               'member_info': {},
	               'camp_id': None,
	               'task': None,
	               'brains': [],
	               'meta': {'is_squad_combat_ready': False,
	                        'is_squad_mobile_ready': False,
	                        'is_squad_overwhelmed': False,
	                        'is_squad_forcing_surrender': False,
	                        'wants_artifacts': False,
	                        'wants_weapons': False}})
	
	entities.create_event(_squad, 'meta_change')
	entities.create_event(_squad, 'raid')
	entities.register_event(_squad, 'raid', handle_raid)
	
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
		create_squad(entity)

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