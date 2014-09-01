from framework import entities, numbers, pathfinding, timers, shapes

import collidable
import stats

import logging


def register(entity, x=0, y=0, direction=0, turn_speed=15):
	_movement = {'x': x,
				 'y': y,
				 'direction': direction,
				 'turn_speed': turn_speed,
	             'path': {'positions': [],
	                      'destination': None}}

	entity['movement'] = _movement

	entities.create_event(entity, 'set_position')
	entities.create_event(entity, 'set_direction')
	entities.create_event(entity, 'set_turn_speed')
	entities.create_event(entity, 'push_tank')
	entities.create_event(entity, 'push')
	entities.create_event(entity, 'warp')
	entities.create_event(entity, 'dodge')
	entities.create_event(entity, 'throw')
	entities.create_event(entity, 'thrown')
	entities.create_event(entity, 'position_changed')
	entities.create_event(entity, 'recovering')
	entities.create_event(entity, 'move_to_position')
	entities.register_event(entity, 'tick', _walk_path)
	entities.register_event(entity, 'push', _push)
	entities.register_event(entity, 'dodge', _dodge)
	entities.register_event(entity, 'throw', _throw)
	entities.register_event(entity, 'set_turn_speed', set_turn_speed)
	entities.register_event(entity, 'set_position', set_position)
	entities.register_event(entity, 'set_direction', _set_tank_direction)
	entities.register_event(entity, 'push_tank', _push_tank)
	entities.register_event(entity, 'move_to_position', walk_to_position)


def set_position(entity, x, y):
	_old_x = entity['movement']['x']
	_old_y = entity['movement']['y']
	
	entity['movement']['x'] = x
	entity['movement']['y'] = y
	
	entities.trigger_event(entity,
	                       'set_position',
	                       x=int(round(x)),
	                       y=int(round(y)),
	                       _ban_events=[set_position])
	entities.trigger_event(entity, 'position_changed', x=int(round(x)), y=int(round(y)), old_x=_old_x, old_y=_old_y)

def get_position(entity):
	return int(round(entity['movement']['x'])), int(round(entity['movement']['y']))

def get_exact_position(entity):
	return entity['movement']['x'], entity['movement']['y']

def get_position_via_id(entity_id):
	return get_position(entities.get_entity(entity_id))

def get_exact_position_via_id(entity_id):
	return get_exact_position(entities.get_entity(entity_id))

def set_turn_speed(entity, speed):
	entity['movement']['turn_speed'] = speed

def get_direction(entity):
	return entity['movement']['direction']

def _clear_movement(entity, **kwargs):
	entity['movement']['path'] = {'positions': [], 'destination': None}
	
	for timer in entity['timers']:
		if timer['name'] and timer['name'].startswith('move'):
			timer['stop'] = True

def _set_tank_direction(entity, direction):
	entity['movement']['direction'] = direction

def _push_tank(entity, direction):
	_degrees_to = entity['movement']['direction']-direction
	
	if (_degrees_to > 0 and abs(_degrees_to) <= 180) or (_degrees_to < 0 and abs(_degrees_to) > 180):
		entity['movement']['direction'] -= entity['movement']['turn_speed']
	elif (_degrees_to > 0 and abs(_degrees_to) > 180) or (_degrees_to < 0 and abs(_degrees_to) <= 180):
		entity['movement']['direction'] += entity['movement']['turn_speed']
	
	_nx, _ny = numbers.velocity(entity['movement']['direction'], 1)

	_push(entity, _nx, _ny)

def _push(entity, x, y):
	_nx = entity['movement']['x'] + x
	_ny = entity['movement']['y'] + y
	
	set_position(entity, _nx, _ny)

def push(entity, x, y, time=-1, name='move'):
	#TODO: Placeholder. See note in controls for player movement
	if time == -1:
		time = stats.get_speed(entity)

	entities.trigger_event(entity,
	                       'create_timer',
	                       time=time,
	                       exit_callback=lambda e: entities.trigger_event(e, 'push', x=x, y=y),
	                       name=name)

def _throw(entity, direction, force):
	entities.trigger_event(entity, 'thrown', force=force)

	#TODO: Doing this causes the entity to pause before moving
	_dodge(entity, direction, NO_PAUSE=True, force=force)

#TODO: Here, or in `combat.py`?
def _dodge(entity, direction, NO_PAUSE=False, force=-1):
	if force == -1:
		_max_moves = stats.get_strength(entity)*1.3
	else:
		_max_moves = force

	_start_pos = (entity['movement']['x'], entity['movement']['y'])
	_time_increment = int(round(stats.get_speed(entity)*.01))
	_time = 0
	_moves = _max_moves
	_last_pos = _start_pos
	_velocity = numbers.velocity(direction, int(round(_max_moves)))
	_end_pos = (_start_pos[0]+int(round(_velocity[0])), _start_pos[1]+int(round(_velocity[1])))
	
	for pos in shapes.line(_start_pos, _end_pos):
		_moves -= 1

		if NO_PAUSE:
			NO_PAUSE = False
		else:
			_time += _time_increment+(9*(1-(_moves/_max_moves)))
		
		_x, _y = (pos[0]-_last_pos[0], pos[1]-_last_pos[1])
		
		push(entity, _x, _y, time=_time, name='thrown')
		
		if _moves <= 0:
			break
		
		_last_pos = pos[:]
	
	_time += _time_increment+45

	recover(entity, time=_time)

def recover(entity, time=15):
	#TODO: Placeholder
	#TODO: Show 'you stand back up'
	entities.trigger_event(entity,
	                       'create_timer',
	                       time=time,
	                       exit_callback=lambda e: entities.trigger_event(e, 'recovering'),
	                       name='recovering')

def walk_to_position(entity, x, y):
	_start_position = get_position(entity)
	_target_position = (x, y)
	
	if _start_position == _target_position:
		return False
	
	_avoid = [get_position_via_id(p) for p in entities.get_entity_group('life') if not p == entity['_id']]
	
	if entity['movement']['path']['destination'] and not entity['movement']['path']['destination'] in _avoid:
		if not numbers.distance(entity['movement']['path']['destination'], _target_position):
			return False

	entity['movement']['path']['positions'] = pathfinding.astar(get_position(entity), _target_position, avoid=_avoid)
	entity['movement']['path']['destination'] = _target_position

def _walk_path(entity):
	if not entity['movement']['path']['positions']:
		return False

	if timers.has_timer_with_name(entity, 'move') or timers.has_timer_with_name(entity, 'move', fuzzy=True):
		return False

	_next_pos = entity['movement']['path']['positions'].pop(0)
	_x, _y = get_position(entity)
	_d_x, _d_y = _next_pos[0]-_x, _next_pos[1]-_y

	if not _d_x in [-1, 0, 1] or not _d_y in [-1, 0, 1]:
		_clear_movement(entity)

		return

	if not entity['movement']['path']['positions']:
		entity['movement']['path']['destination'] = None

	push(entity, x=_d_x, y=_d_y, name='Move')