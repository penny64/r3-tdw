from framework import entities

import ai_squads

import settings


FIGHTING_SQUADS = set()
FLOW = None


def boot():
	global FLOW
	
	_entity = entities.create_entity()
	
	entities.create_event(_entity, 'start_of_turn')
	entities.create_event(_entity, 'end_of_turn')
	
	FLOW = _entity

def is_flow_active():
	return len(settings.TURN_QUEUE) > 0

def get_active_squad():
	return settings.TURN_QUEUE[0]

def can_act(entity):
	_squad = ai_squads.get_assigned_squad(entity)['_id']
	
	if _squad in settings.TURN_QUEUE:
		return _squad == get_active_squad() and entity['stats']['action_points'] > 0
	
	return True

def register_combat(entity, target_id):
	_target = entities.get_entity(target_id)
	_squad_1 = ai_squads.get_assigned_squad(entity)['_id']
	_squad_2 = ai_squads.get_assigned_squad(_target)['_id']

	FIGHTING_SQUADS.add(_squad_1)
	FIGHTING_SQUADS.add(_squad_2)
	
	if not _squad_1 in settings.TURN_QUEUE:
		settings.TURN_QUEUE.append(_squad_1)
	
	if not _squad_2 in settings.TURN_QUEUE:
		settings.TURN_QUEUE.append(_squad_2)
	
	#print 'Registered for combat:', _squad_1, _squad_2

def logic():
	for squad_id in settings.TURN_QUEUE:
		_squad = entities.get_entity(squad_id)
		
		for entity_id in _squad['members']:
			_entity = entities.get_entity(entity_id)
			
			if _entity['stats']['action_points'] > 0:
				break
		
		else:
			if _squad['_id'] in settings.TURN_QUEUE:
				_was_leader = False
				
				if not settings.TURN_QUEUE.index(_squad['_id']):
					entities.trigger_event(FLOW, 'end_of_turn', squad_id=_squad['_id'])
					
					_was_leader = True
				
				settings.TURN_QUEUE.remove(_squad['_id'])
				
				if len(settings.TURN_QUEUE):
					settings.TURN_QUEUE.append(_squad['_id'])
				
				if settings.TURN_QUEUE and _was_leader:
					entities.trigger_event(FLOW, 'start_of_turn', squad_id=settings.TURN_QUEUE[0])
				
				for entity_id in _squad['members']:
					_entity = entities.get_entity(entity_id)
					
					_entity['stats']['action_points'] = _entity['stats']['action_points_max']
