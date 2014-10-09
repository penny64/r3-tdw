from framework import entities, events

import logging

#Steps:
#Create mission
#Add goals
#Add mission to character
#Character registers with get_item/kill/etc?


def boot():
	events.register_event('logic', all_logic)

def register(entity):
	entity['missions'] = {'id': 0,
	                      'active': {},
	                      'complete': []}
	
	entities.create_event(entity, 'add_mission')
	entities.create_event(entity, 'complete_mission')
	entities.register_event(entity, 'add_mission', add_mission)
	entities.register_event(entity, 'complete_mission', complete_mission)

def add_mission(entity, mission_id):
	_mission = entities.get_entity(mission_id)
	
	entity['missions']['id'] += 1
	entity['missions']['active'][entity['missions']['id']] = mission_id
	
	_mission['members'].append(entity['_id'])
	
	logging.info('Adding entity %s to mission %s' % (entity['_id'], mission_id))

def complete_mission(entity, mission_id):
	_mission = entities.get_entity(mission_id)
	
	entity['missions']['active'].remove(mission_id)
	entity['missions']['complete'].append(mission_id)

def create():
	_mission = entities.create_entity(group='missions')
	_mission.update({'goals': [],
	                 'members': []})
	
	entities.register_event(_mission, 'logic', logic)
	
	logging.info('Creating mission: %s' % _mission['_id'])
	
	return _mission

def create_goal(mission, intent, **kwargs):
	_goal = entities.create_entity()
	
	_goal['intent'] = intent
	_goal['mission_id'] = mission['_id']
	_goal.update(kwargs)
	
	mission['goals'].append(_goal['_id'])
	
	logging.info('Creating goal for mission %s: %s' % (mission['_id'], kwargs))
	
	return _goal

def _kill_npc_logic(goal):
	_target_id = goal['target_id']
	_mission = entities.get_entity(goal['mission_id'])
	
	if not _target_id in entities.ENTITIES:
		print 'MISSION INVALIDATED'
		
		#TODO: Loop through members - do any of them think this mission is active? Else, delete.
	
	for member_id in _mission['members']:
		_member = entities.get_entity(member_id)
		
		if not _target_id in _member['ai']['life_memory']:
			continue
		
		_memory = _member['ai']['life_memory'][_target_id]
		
		if _memory['is_dead']:
			entities.trigger_event(_member, 'complete_mission', mission_id=goal['mission_id'])

def add_goal_kill_npc(mission, target_id):
	#TODO: Register
	_goal = create_goal(mission, 'kill', target_id=target_id)
	
	entities.register_event(_goal, 'logic', _kill_npc_logic)

def logic(mission):
	for goal_id in mission['goals']:
		_goal = entities.get_entity(goal_id)
		
		entities.trigger_event(_goal, 'logic')

def all_logic():
	for mission_id in entities.get_entity_group('missions'):
		_mission = entities.get_entity(mission_id)
		
		entities.trigger_event(_mission, 'logic')