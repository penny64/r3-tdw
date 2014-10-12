from framework import entities, events, numbers, movement

import conversions
import ui_dialog
import ui_menu

import logging

#Steps:
#Create mission
#Add goals
#Add mission to character
#Character registers with get_item/kill/etc?


def boot():
	events.register_event('logic', all_logic)

def register(entity):
	entity['missions'] = {'active': [],
	                      'inactive': [],
	                      'complete': []}
	
	entities.create_event(entity, 'add_mission')
	entities.create_event(entity, 'complete_mission')
	entities.register_event(entity, 'add_mission', add_mission)
	entities.register_event(entity, 'complete_mission', complete_mission)
	entities.register_event(entity,
	                        'complete_mission',
	                        lambda e, mission_id: entities.trigger_event(entities.get_entity(mission_id),
	                                                                     'remove_member',
	                                                                     target_id=e['_id']))

def add_mission(entity, mission_id, make_active):
	_mission = entities.get_entity(mission_id)
	
	entity['missions'][('in' * (not make_active)) + 'active'].append(mission_id)
	
	_mission['members'].append(entity['_id'])
	
	logging.info('Adding entity %s to mission %s' % (entity['_id'], mission_id))

def complete_mission(entity, mission_id):
	_mission = entities.get_entity(mission_id)
	
	entity['missions']['active'].remove(mission_id)
	entity['missions']['complete'].append(mission_id)

def get_mission_details(entity, menu):
	ui_menu.add_selectable(menu, 'Details', lambda _: 1==1)

def get_mission_briefing(mission):
	ui_dialog.create(5, 5, mission['briefing'])

def remove_member(mission, target_id):
	mission['members'].remove(target_id)
	
	logging.info('Removed %s from mission %s.' % (target_id, mission['_id']))

def create(title, briefing=''):
	_mission = entities.create_entity(group='missions')
	_mission.update({'title': title,
	                 'goals': [],
	                 'members': [],
	                 'member_memory': {},  #Unused
	                 'briefing': briefing})
	
	entities.create_event(_mission, 'remove_member')
	entities.create_event(_mission, 'get_details')
	entities.create_event(_mission, 'get_briefing')
	entities.register_event(_mission, 'remove_member', remove_member)
	entities.register_event(_mission, 'logic', logic)
	entities.register_event(_mission, 'get_details', get_mission_details)
	entities.register_event(_mission, 'get_briefing', get_mission_briefing)
	
	logging.info('Creating mission: %s' % _mission['_id'])
	
	return _mission

def create_goal(mission, intent, message, logic_callback, message_callback, draw=True, **kwargs):
	_goal = entities.create_entity()
	
	_goal['intent'] = intent
	_goal['mission_id'] = mission['_id']
	_goal['message'] = message
	_goal['complete'] = False
	_goal['draw'] = draw
	_goal.update(kwargs)
	
	entities.create_event(_goal, 'get_message')
	entities.register_event(_goal, 'logic', logic_callback)
	entities.register_event(_goal, 'get_message', message_callback)
	
	mission['goals'].append(_goal['_id'])
	
	logging.info('Creating goal \'%s\' for mission %s: %s' % (intent, mission['_id'], kwargs))
	
	return _goal

def _locate_npc_logic(goal):
	pass

def _locate_npc_message(goal, member_id):
	_target_id = goal['target_id']
	_member = entities.get_entity(member_id)
	_mission = entities.get_entity(goal['mission_id'])
		
	if not _target_id in _member['ai']['life_memory'] or not _member['ai']['life_memory'][_target_id]['last_seen_at']:
		goal['message'] = 'Gather location info on target.'
		goal['complete'] = False
		
		return
		
	if _member['ai']['life_memory'][_target_id]['last_seen_at']:
		_direction = numbers.direction_to(movement.get_position(_member), _member['ai']['life_memory'][_target_id]['last_seen_at'])
		_distance = numbers.distance(movement.get_position(_member), _member['ai']['life_memory'][_target_id]['last_seen_at'])
		_real_direction = conversions.get_real_direction(_direction)
		_real_distance = conversions.get_real_distance(_distance)
		
		goal['message'] = 'Target last seen %s meters to the %s' % (_real_distance, _real_direction)
		goal['complete'] = False
	
	else:
		goal['message'] = 'Target in line of sight.'
		goal['complete'] = True
	
	_member['ai']['life_memory'][_target_id]['mission_related'] = True

def _kill_npc_logic(goal):
	_target_id = goal['target_id']
	_mission = entities.get_entity(goal['mission_id'])
	
	if not _target_id in entities.ENTITIES:
		print 'IF THIS IS A BOUNTY MISSION: MISSION INVALIDATED'
		
		#TODO: Loop through members - do any of them think this mission is active? Else, delete.
		#TOOD: We can't do that if the person who assigned the mission hasn't gotten then news the target is dead
	
	for member_id in _mission['members']:
		_member = entities.get_entity(member_id)
		
		if not _target_id in _member['ai']['life_memory']:
			continue
		
		_memory = _member['ai']['life_memory'][_target_id]
		
		if _memory['is_dead']:
			entities.trigger_event(_member, 'complete_mission', mission_id=goal['mission_id'])

def _kill_npc_message(goal, member_id):
	goal['message'] = 'Kill the target.'

def add_goal_kill_npc(mission, target_id):
	#TODO: Register
	_target = entities.get_entity(target_id)
	
	create_goal(mission, 'locate',
	            'Locate %s' % _target['stats']['name'],
	            _locate_npc_logic,
	            _locate_npc_message,
	            target_id=target_id)
	create_goal(mission, 'kill',
	            'Kill %s' % _target['stats']['name'],
	            _kill_npc_logic,
	            _kill_npc_message,
	            draw=False,
	            target_id=target_id)

def logic(mission):
	for goal_id in mission['goals']:
		_goal = entities.get_entity(goal_id)
		
		entities.trigger_event(_goal, 'logic')

def all_logic():
	for mission_id in entities.get_entity_group('missions'):
		_mission = entities.get_entity(mission_id)
		
		entities.trigger_event(_mission, 'logic')