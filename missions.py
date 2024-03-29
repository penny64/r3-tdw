from framework import entities, events, numbers, movement

import conversions
import ai_dialog
import ui_dialog
import ui_menu
import items

import logging

#Steps:
#Create mission
#Add goals
#Add mission to character
#Character registers with get_item/kill/etc?


def boot():
	events.register_event('logic', all_logic)

def register(entity):
	entity['missions'] = {'active': {},
	                      'inactive': {},
	                      'complete': []}
	
	entities.create_event(entity, 'add_mission')
	entities.create_event(entity, 'complete_mission')
	entities.create_event(entity, 'complete_goal')
	entities.create_event(entity, 'uncomplete_goal')
	entities.register_event(entity, 'complete_goal', complete_goal)
	entities.register_event(entity, 'uncomplete_goal', uncomplete_goal)
	entities.register_event(entity, 'add_mission', add_mission)
	entities.register_event(entity, 'complete_mission', member_complete_mission)
	entities.register_event(entity,
	                        'complete_mission',
	                        lambda e, mission_id: entities.trigger_event(entities.get_entity(mission_id),
	                                                                     'remove_member',
	                                                                     target_id=e['_id']))

def add_mission(entity, mission_id, make_active=True):
	_mission = entities.get_entity(mission_id)
	
	entity['missions'][('in' * (not make_active)) + 'active'][mission_id] = {'goals': {k: {'complete': False, 'cleanup_events': []} for k in _mission['goals']}}
	
	_mission['members'].append(entity['_id'])
	
	if make_active:
		entities.trigger_event(_mission, 'member_added', member_id=entity['_id'])
	
	logging.info('Adding entity %s to mission %s' % (entity['_id'], mission_id))

def complete_mission(mission):
	entities.delete_entity(mission)
	
	logging.info('STUB: Mission complete.')

def member_complete_mission(entity, mission_id):
	_mission = entities.get_entity(mission_id)
	
	for goal_id in entity['missions']['active'][mission_id]['goals']:
		for event_name, event_id in entity['missions']['active'][mission_id]['goals'][goal_id]['cleanup_events']:
			entities.unregister_event_via_id(entity, event_name, event_id)
	
	del entity['missions']['active'][mission_id]
	
	entity['missions']['complete'].append(mission_id)

def complete_goal(entity, mission_id, goal_id):
	if entity['missions']['active'][mission_id]['goals'][goal_id]['complete']:
		return
	
	entity['missions']['active'][mission_id]['goals'][goal_id]['complete'] = True
	
	for goal_id in entity['missions']['active'][mission_id]['goals']:
		if not entity['missions']['active'][mission_id]['goals'][goal_id]['complete']:
			break
	else:
		entities.trigger_event(entity, 'complete_mission', mission_id=mission_id)

def uncomplete_goal(entity, mission_id, goal_id):
	if not entity['missions']['active'][mission_id]['goals'][goal_id]['complete']:
		return
	
	entity['missions']['active'][mission_id]['goals'][goal_id]['complete'] = False

def add_goal_cleanup_event(goal, member_id, event_pair):
	_member = entities.get_entity(member_id)
	_member['missions']['active'][goal['mission_id']]['goals'][goal['_id']]['cleanup_events'].append(event_pair)

def get_mission_details(mission, menu, member_id, target_id):
	_target = entities.get_entity(target_id)
	
	for goal_id in mission['goals']:
		_goal = entities.get_entity(goal_id)
		
		for detail in _goal['details']:
			ui_menu.add_selectable(menu, detail['message'], lambda: detail['callback'](member_id, target_id))

def get_mission_briefing(mission):
	ui_dialog.create(5, 5, mission['briefing'], title='Mission: %s' % mission['title'])

def member_added(mission, member_id):
	_member = entities.get_entity(member_id)
	
	for goal_id in mission['goals']:
		_goal = entities.get_entity(goal_id)
		
		entities.trigger_event(_goal, 'member_added', member_id=member_id)

def remove_member(mission, target_id):
	mission['members'].remove(target_id)
	
	for member_id in mission['members']:
		_member = entities.get_entity(member_id)
		
		if mission['_id'] in _member['missions']['active']:
			break
	else:
		entities.trigger_event(mission, 'complete')
	
	logging.info('Removed %s from mission %s.' % (target_id, mission['_id']))

def create(title, briefing=''):
	_mission = entities.create_entity(group='missions')
	_mission.update({'title': title,
	                 'goals': [],
	                 'members': [],
	                 'member_memory': {},  #Unused
	                 'briefing': briefing})
	
	entities.create_event(_mission, 'member_added')
	entities.create_event(_mission, 'remove_member')
	entities.create_event(_mission, 'get_details')
	entities.create_event(_mission, 'get_briefing')
	entities.create_event(_mission, 'complete')
	entities.register_event(_mission, 'member_added', member_added)
	entities.register_event(_mission, 'remove_member', remove_member)
	entities.register_event(_mission, 'logic', logic)
	entities.register_event(_mission, 'get_details', get_mission_details)
	entities.register_event(_mission, 'get_briefing', get_mission_briefing)
	entities.register_event(_mission, 'complete', complete_mission)
	
	logging.info('Creating mission: %s' % _mission['_id'])
	
	return _mission

def create_goal(mission, intent, message, logic_callback, message_callback, draw=True, details=[], **kwargs):
	_goal = entities.create_entity()
	
	_goal['intent'] = intent
	_goal['mission_id'] = mission['_id']
	_goal['message'] = message
	_goal['draw'] = draw
	_goal['details'] = details
	_goal.update(kwargs)
	
	entities.create_event(_goal, 'get_message')
	entities.create_event(_goal, 'member_added')
	entities.create_event(_goal, 'add_goal_cleanup_event')
	entities.register_event(_goal, 'logic', logic_callback)
	entities.register_event(_goal, 'get_message', message_callback)
	entities.register_event(_goal, 'add_goal_cleanup_event', add_goal_cleanup_event)
	
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
		
		return
	
	if _member['ai']['life_memory'][_target_id]['is_dead']:
		goal['message'] = 'Confirmed: Target is dead.'
		
		entities.trigger_event(_member, 'complete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])
	
	elif _member['ai']['life_memory'][_target_id]['can_see']:
		goal['message'] = 'Target in line of sight.'
		
		entities.trigger_event(_member, 'complete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])
	
	elif _member['ai']['life_memory'][_target_id]['last_seen_at']:
		_direction = numbers.direction_to(movement.get_position(_member), _member['ai']['life_memory'][_target_id]['last_seen_at'])
		_distance = numbers.distance(movement.get_position(_member), _member['ai']['life_memory'][_target_id]['last_seen_at'])
		_real_direction = conversions.get_real_direction(_direction)
		_real_distance = conversions.get_real_distance(_distance)
		
		goal['message'] = 'Target last seen %s meters to the %s' % (_real_distance, _real_direction)
	
	_member['ai']['life_memory'][_target_id]['mission_related'] = True

def _locate_item_logic(goal):
	pass

def _locate_item_message(goal, member_id):
	_item_name = goal['item_name']
	_member = entities.get_entity(member_id)
	_mission = entities.get_entity(goal['mission_id'])
	
	#TODO: Check if item visible and show something different
	
	if not items.get_items_matching(_member, {'name': _item_name}):
		goal['message'] = 'Find item.'
		
		entities.trigger_event(_member, 'uncomplete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])
		
	else:
		goal['message'] = 'Item found.'
		
		entities.trigger_event(_member, 'complete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])

def _handle_return_item_item_given(goal, member_id, item_id, target_id):
	_mission = entities.get_entity(goal['mission_id'])
	_item_name = goal['item_name']
	_member = entities.get_entity(member_id)
	_item_given = entities.get_entity(item_id)
	
	if _item_name == _item_given['stats']['name']:
		entities.trigger_event(_member, 'complete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])

def _handle_return_item_member_added(goal, member_id):
	_member = entities.get_entity(member_id)
	_event_id = entities.register_event(_member, 'give_item', lambda entity, item_id, target_id: _handle_return_item_item_given(goal, member_id, item_id, target_id))
	
	entities.trigger_event(goal, 'add_goal_cleanup_event', member_id=member_id, event_pair=('give_item', _event_id))

def _return_item_logic(goal):
	pass

def _return_item_message(goal, member_id):
	_item_name = goal['item_name']
	_target_id = goal['target_id']
	_member = entities.get_entity(member_id)
	_mission = entities.get_entity(goal['mission_id'])
	
	if not items.get_items_matching(_member, {'name': _item_name}):
		goal['draw'] = False
		
	else:
		goal['draw'] = True
		goal['message'] = 'Return the item.' #TODO: To who?

def _kill_npc_logic(goal):
	_target_id = goal['target_id']
	_mission = entities.get_entity(goal['mission_id'])
	
	if not _target_id in entities.ENTITIES:
		print 'IF THIS IS A BOUNTY MISSION: MISSION INVALIDATED'
		
		#TODO: Loop through members - do any of them think this mission is active? Else, delete.
		#TOOD: We can't do that if the person who assigned the mission hasn't gotten then news the target is dead
	
	for member_id in _mission['members']:
		_member = entities.get_entity(member_id)
		
		if not goal['mission_id'] in _member['missions']['active']:
			continue
		
		_member_goal = _member['missions']['active'][_mission['_id']]['goals'][goal['_id']]
		
		if not _target_id in _member['ai']['life_memory']:
			continue
		
		_memory = _member['ai']['life_memory'][_target_id]
		
		if _memory['is_dead']:
			entities.trigger_event(_member, 'complete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])
		else:
			entities.trigger_event(_member, 'uncomplete_goal', mission_id=goal['mission_id'], goal_id=goal['_id'])
		
		#entities.trigger_event(_member, 'complete_mission', mission_id=goal['mission_id'])

def _kill_npc_message(goal, member_id):
	goal['message'] = 'Kill the target.'

def add_goal_kill_npc(mission, target_id):
	#TODO: Register
	_target = entities.get_entity(target_id)
	
	create_goal(mission, 'locate',
	            'Locate %s' % _target['stats']['name'],
	            _locate_npc_logic,
	            _locate_npc_message,
	            target_id=target_id,
	            details=[{'intent': 'last_seen_at',
	                     'message': 'Ask for location',
	                     'callback': lambda member_id, life_id: ai_dialog.share_life_memory_location(entities.get_entity(life_id), member_id, target_id)}])
	create_goal(mission, 'kill',
	            'Kill %s' % _target['stats']['name'],
	            _kill_npc_logic,
	            _kill_npc_message,
	            draw=False,
	            target_id=target_id)

def add_goal_get_item(mission, item_name, return_to_life_id):
	create_goal(mission, 'locate_item',
	            'Locate item: %s' % item_name,
	            _locate_item_logic,
	            _locate_item_message,
	            item_name=item_name,
	            details=[])
	_goal = create_goal(mission, 'return_item',
	                    'Return item: %s' % item_name,
	                    _return_item_logic,
	                    _return_item_message,
	                    draw=True,
	                    item_name=item_name,
	                    target_id=return_to_life_id,
	                    details=[{'intent': 'return_item',
	                              'message': 'Return item',
	                              'callback': lambda member_id, life_id: ai_dialog.give_item(entities.get_entity(member_id), life_id, {'name': 'Mutated Wild Dog Tail'})}])
	
	_event_id = entities.register_event(_goal, 'member_added', _handle_return_item_member_added)

def logic(mission):
	for goal_id in mission['goals']:
		_goal = entities.get_entity(goal_id)
		
		entities.trigger_event(_goal, 'logic')

def all_logic():
	for mission_id in entities.get_entity_group('missions'):
		_mission = entities.get_entity(mission_id)
		
		entities.trigger_event(_mission, 'logic')