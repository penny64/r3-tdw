from framework import entities, timers

import ui_squad_control
import ai_squads
import constants

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
	
	if not _squad in FIGHTING_SQUADS:
		return True
	
	if _squad in settings.TURN_QUEUE:
		return _squad == get_active_squad() and entity['stats']['action_points'] > 0
	
	return True

def register_combat(entity, target_id):
	_target = entities.get_entity(target_id)
	_squad_1 = ai_squads.get_assigned_squad(entity)
	_squad_2 = ai_squads.get_assigned_squad(_target)['_id']

	FIGHTING_SQUADS.add(_squad_1['_id'])
	FIGHTING_SQUADS.add(_squad_2)
	
	if not settings.TURN_QUEUE:
		entities.trigger_event(FLOW, 'start_of_turn', squad_id=_squad_1['_id'])
	
	if not _squad_1['_id'] in settings.TURN_QUEUE:
		settings.TURN_QUEUE.append(_squad_1['_id'])
	
	if not _squad_2 in settings.TURN_QUEUE:
		settings.TURN_QUEUE.append(_squad_2)
	
	#print 'Registered for combat:', _squad_1, _squad_2

def logic():
	for squad_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(squad_id)
				
		for entity_id in _squad['members']:
			_entity = entities.get_entity(entity_id)
			
			entities.trigger_event(_entity, 'logic')
	
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

def tick():
	if settings.TURN_QUEUE:
		_squads = [settings.TURN_QUEUE[0]]
	
	else:
		_squads = entities.get_entity_group('squads')
		
		for squad_id in entities.get_entity_group('squads'):
			_squad = entities.get_entity(squad_id)
			_break = False
			
			if not _squad['faction'] == 'Rogues':
				continue
			
			for member_id in _squad['members']:
				_entity = entities.get_entity(member_id)
				
				if timers.has_timer_with_name(_entity, 'shoot') or _entity['movement']['path']['positions'] or timers.has_timer_with_name(_entity, 'move'):
					_break = True
					
					break
			
			if _break:
				break
		else:
			settings.set_tick_mode('strategy')
	
	for squad_id in _squads:
		_squad = entities.get_entity(squad_id)
		_waiting = False
		
		#if not _squad['faction'] == 'Rogues':
		#	settings.set_tick_mode('normal')
		
		for entity_id in _squad['members']:
			_entity = entities.get_entity(entity_id)
			
			if not settings.TURN_QUEUE:
				_entity['stats']['action_points'] = _entity['stats']['action_points_max']
			
			if _entity['stats']['action_points'] <= 0:
				continue
			
			_had_action = False
			
			if timers.has_timer_with_name(_entity, 'shoot') or _entity['movement']['path']['positions'] or timers.has_timer_with_name(_entity, 'move'):
				_had_action = True
			
			elif _entity['ai']['is_player']:
				_waiting = True
				
				continue
			
			entities.trigger_event(_entity, 'tick')
			
			if _had_action and not timers.has_timer_with_name(_entity, 'shoot') and not _entity['movement']['path']['positions'] and not timers.has_timer_with_name(_entity, 'move') and _entity['stats']['action_points'] > 0:
				if _entity['ai']['is_player'] and (ui_squad_control.is_squad_member_selected() and _entity == ui_squad_control.get_selected_squad_member()):
					settings.set_tick_mode('strategy')
					
					break
			
			if _entity['ai']['is_player'] and _entity['stats']['action_points'] <= 0:
				ui_squad_control.reset_selected_squad_member()
				settings.set_tick_mode('strategy')
			
			if not _entity['movement']['path']['positions'] and not timers.has_timer_with_name(_entity, 'shoot') and not timers.has_timer_with_name(_entity, 'move'):
				_entity['stats']['action_points'] -= constants.IDLE_COST
			
			if _entity['stats']['action_points'] <= 0 and list(_squad['members']).index(entity_id)+1 == len(_squad['members']):
				entities.trigger_event(_squad, 'update_position_map')
			
			#print _entity['stats']['name'], _entity['stats']['action_points']
			
			break
		
		else:
			if _entity['ai']['is_player'] and not _waiting:
				settings.set_tick_mode('normal')
