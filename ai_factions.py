from framework import entities, numbers, movement

FACTIONS = {}

import ai_faction_logic
import ai_squad_logic
import ai_squads
import constants
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
	
	_entity.update(_faction)
	
	entities.create_event(_entity, 'add_member')
	entities.register_event(_entity, 'add_member', add_member)
	
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

############
#Operations#
############

def add_member(entity, member_id):
	entities.register_event(entities.get_entity(member_id), 'killed_by', lambda e, target_id, **kwargs: handle_member_killed(entity, member_id, target_id))

def handle_member_killed(entity, member_id, target_id):
	_member = entities.get_entity(member_id)
	_target = entities.get_entity(target_id)
	_target_faction = _target['ai']['faction']
	
	if _target_faction == _member['ai']['faction']:
		logging.info('Friendly fire resulted in death: %s' % _target_faction)
	
	if not _target_faction in entity['enemies']:
		entity['relations'][_target_faction] = 0
		entity['enemies'].append(_target_faction)
		
		logging.info('%s is now hostile to %s: Murder' % (_member['ai']['faction'], _target_faction))

def is_enemy(entity, target_id):
	_target = entities.get_entity(target_id)
	_faction = FACTIONS[entity['ai']['faction']]
	
	return _target['ai']['faction'] in _faction['enemies']
