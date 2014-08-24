from framework import entities, numbers, movement

import logging

FACTIONS = {}


def _create(name, min_squad_size, max_squad_size):
	_faction = {'members': set(),
	            'squads': {},
	            'squad_id': 1,
	            'brains': [],
	            'squad_size_range': (min_squad_size, max_squad_size)}
	
	FACTIONS[name] = _faction

def boot():
	_create('Bandits', 3, 5)
	_create('Runners', 3, 5)
	_create('Rogues', 1, 1)

def register(entity, faction):
	if not faction in FACTIONS:
		raise Exception('Invalid faction: %s' % faction)
	
	entity['ai']['faction'] = faction
	entity['ai']['squad'] = -1
	
	FACTIONS[entity['ai']['faction']]['members'].add(entity['_id'])
	
	assign_to_squad(entity)


############
#Operations#
############

def create_squad(entity):
	_faction = FACTIONS[entity['ai']['faction']]
	_squad = {'members': set(),
	          'leader': entity['_id']}
	_faction['squads'][_faction['squad_id']] = _squad
	
	_faction['squad_id'] += 1
	
	logging.info('Faction \'%s\' created new squad: %s (leader: %s)' % (entity['ai']['faction'],
	                                                                    _faction['squad_id']-1,
	                                                                    entity['stats']['name']))

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
		
		if not _nearest_squad['squad_id'] or _distance_to_leader < _nearest_squad['distance']:
			_nearest_squad['squad_id'] = squad_id
			_nearest_squad['distance'] = _distance_to_leader
	
	if _nearest_squad['squad_id']:
		_faction['squads'][_nearest_squad['squad_id']]['members'].add(entity['_id'])
		
		entity['ai']['squad'] = _nearest_squad['squad_id']
		
		logging.info('Faction \'%s\' added member to squad %s: %s' % (entity['ai']['faction'],
		                                                              entity['ai']['squad'],
		                                                              entity['stats']['name']))
	
	else:
		create_squad(entity)