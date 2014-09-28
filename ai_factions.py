from framework import entities, numbers, movement, flags

FACTIONS = {}

import ai_faction_logic
import ai_squad_logic
import ai_squads
import ui_dialog
import constants
import effects
import mapgen

import logging


def boot():
	create_human_faction('Bandits', (2, 3), (4, 6), ['Runners', 'Rogues', 'Wild Dogs'])
	create_human_faction('Runners', (3, 5), (2, 3), ['Bandits', 'Wild Dogs'])
	create_human_faction('Rogues', (1, 1), (1, 1), ['Bandits', 'Wild Dogs'])
	create_dog_faction('Wild Dogs', (2, 4), (0, 0), ['Bandits', 'Runners', 'Rogues'])

def _create(name, squad_size_range, base_size_range, enemy_factions):
	_entity = entities.create_entity(group='factions')
	_faction = {'members': set(),
	            'squads': {},
	            'squad_id': 1,
	            'faction_memory': {},
	            'brains': [],
	            'meta': {},
	            'squad_size_range': squad_size_range,
	            'base_size_range': base_size_range,
	            'enemies': enemy_factions,
	            'relations': {}}
	
	for faction_name in FACTIONS:
		_other_faction = FACTIONS[faction_name]
		
		if name in _other_faction['enemies']:
			_other_score = 0
		else:
			_other_score = 25
		
		if faction_name in enemy_factions:
			_score = 0
		else:
			_score = 25
		
		_other_faction['relations'][name] = _other_score
		_faction['relations'][faction_name] = _score
		_faction['faction_memory'][faction_name] = {'squads': {}}
		_other_faction['faction_memory'][name] = {'squads': {}}
	
	_entity.update(_faction)
	
	entities.create_event(_entity, 'add_member')
	entities.create_event(_entity, 'faction_raid_incoming')
	entities.create_event(_entity, 'broadcast')
	entities.register_event(_entity, 'add_member', add_member)
	entities.register_event(_entity, 'broadcast', handle_broadcast)
	entities.register_event(_entity, 'faction_raid_incoming', handle_raid_incoming)
	
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

def register(entity, faction):
	if not faction in FACTIONS:
		raise Exception('Invalid faction: %s' % faction)
	
	entities.create_event(entity, 'new_squad_member')
	
	#TODO: Move this to ai_squads at some point
	entities.register_event(entity, 'delete', cleanup)
	
	entity['ai']['faction'] = faction
	entity['ai']['squad'] = -1
	
	FACTIONS[entity['ai']['faction']]['members'].add(entity['_id'])
	
	entities.trigger_event(FACTIONS[entity['ai']['faction']], 'add_member', member_id=entity['_id'] )
	
	ai_squads.assign_to_squad(entity)

def logic():
	for faction in FACTIONS.values():
		entities.trigger_event(faction, 'logic')

def cleanup(entity):
	_squad = ai_squads.get_assigned_squad(entity)
	
	if _squad['leader'] == entity['_id']:
		logging.warning('Leader of squad died. Handle this.')
		
		_squad['leader'] = None
	
	_squad['members'].remove(entity['_id'])
	del _squad['member_info'][entity['_id']]

def _faction_is_enemy(entity, target_id):
	return entities.get_entity(target_id)['ai']['faction'] in entity['enemies']

def is_enemy(entity, target_id):
	_target = entities.get_entity(target_id)
	_faction = FACTIONS[entity['ai']['faction']]
	
	return _target['ai']['faction'] in _faction['enemies']

############
#Operations#
############

def add_member(entity, member_id):
	entities.register_event(entities.get_entity(member_id),
	                        'killed_by',
	                        lambda e, target_id, **kwargs: handle_member_killed(entity, member_id, target_id))
	entities.register_event(entities.get_entity(member_id),
	                        'new_target_spotted',
	                        lambda e, target_id: handle_new_target(entity, target_id))

def broadcast_to_friends(entity, message):
	for faction_name in FACTIONS:
		if faction_name in entity['enemies']:
			continue
		
		entities.trigger_event(FACTIONS[faction_name], 'broadcast', message=message)

def handle_broadcast(entity, message):
	for member_id in entity['members']:
		_member = entities.get_entity(member_id)
		
		entities.trigger_event(_member, 'broadcast', message=message)

def handle_member_killed(entity, member_id, target_id):
	_member = entities.get_entity(member_id)
	_target = entities.get_entity(target_id)
	_target_faction = _target['ai']['faction']
	
	if _target_faction == _member['ai']['faction']:
		logging.info('Friendly fire resulted in death: %s' % _target_faction)
		
		return
	
	if not _target_faction in entity['enemies']:
		entity['relations'][_target_faction] = 0
		entity['enemies'].append(_target_faction)
		
		logging.info('%s is now hostile to %s: Murder' % (_member['ai']['faction'], _target_faction))
		
		if flags.has_flag(_target, 'is_player') and flags.get_flag(_target, 'is_player'):
			effects.message('%s now see you as hostile.' % _member['ai']['faction'])

def handle_new_target(entity, target_id):
	if not _faction_is_enemy(entity, target_id):
		return
	
	_target = entities.get_entity(target_id)
	_target_faction = _target['ai']['faction']
	_target_squad = FACTIONS[_target_faction]['squads'][_target['ai']['squad']]
	
	if _target['ai']['squad'] in entity['faction_memory'][_target_faction]['squads']:
		_squad_memory = entity['faction_memory'][_target_faction]['squads'][_target['ai']['squad']]
		
		if not target_id in _squad_memory['members']:
			_squad_memory['members'].append(target_id)
		
		_squad_memory['task'] = _target_squad['task']
	
	else:
		entity['faction_memory'][_target_faction]['squads'][_target['ai']['squad']] = {'members': [target_id],
		                                                                               'last_task': '',
		                                                                               'task': _target_squad['task']}
		_squad_memory = entity['faction_memory'][_target_faction]['squads'][_target['ai']['squad']]
	
	if not _squad_memory['task'] == _squad_memory['last_task']:
		if _squad_memory['task'] == 'raid':
			entities.trigger_event(entity, 'faction_raid_incoming', target_faction=_target_faction, target_squad=_target['ai']['squad'])
		
		_squad_memory['last_task'] = _target_squad['task']
		

def handle_raid_incoming(entity, target_faction, target_squad):
	_target_faction = FACTIONS[target_faction]
	_target_squad = _target_faction['squads'][target_squad]
	
	broadcast_to_friends(entity, '<CAMP_ID> is being raided by %s' % target_faction)
