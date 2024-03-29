from framework import entities, numbers, pathfinding, timers, shapes

import collidable
import settings
import stats

import logging


def register(entity, x=0, y=0, direction=0, turn_speed=15, collisions=False):
	_movement = {'x': x,
				 'y': y,
	             'next_x': x,
	             'next_y': y,
	             'collisions': collisions,
				 'direction': direction,
				 'turn_speed': turn_speed,
	             'override_speed': 6,
	             'path': {'positions': [],
	                      'destination': None,
	                      'refresh': False}}

	entity['movement'] = _movement

	entities.create_event(entity, 'set_position')
	entities.create_event(entity, 'set_direction')
	entities.create_event(entity, 'set_turn_speed')
	entities.create_event(entity, 'push_tank')
	entities.create_event(entity, 'push')
	entities.create_event(entity, 'warp')
	entities.create_event(entity, 'throw')
	entities.create_event(entity, 'thrown')
	entities.create_event(entity, 'position_changed')
	entities.create_event(entity, 'recovering')
	entities.create_event(entity, 'check_next_position')
	entities.create_event(entity, 'move_to_position')
	entities.create_event(entity, 'disable_collisions')
	entities.create_event(entity, 'enable_collisions')
	entities.create_event(entity, 'stop')
	entities.register_event(entity, 'save', save)
	entities.register_event(entity, 'tick', _walk_path)
	entities.register_event(entity, 'push', _push)
	entities.register_event(entity, 'stop', stop)
	entities.register_event(entity, 'set_turn_speed', set_turn_speed)
	entities.register_event(entity, 'set_position', set_position)
	entities.register_event(entity, 'set_direction', _set_tank_direction)
	entities.register_event(entity, 'push_tank', _push_tank)
	entities.register_event(entity, 'move_to_position', walk_to_position)
	entities.register_event(entity, 'enable_collisions', _enable_collisions)
	entities.register_event(entity, 'disable_collisions', _disable_collisions)

def save(entity, snapshot):
	snapshot['movement'] = entity['movement']

def _enable_collisions(entity):
	entity['movement']['collisions'] = True

def _disable_collisions(entity):
	entity['movement']['collisions'] = False

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


def get_position_via_id(entity_id):
	return get_position(entities.get_entity(entity_id))

def get_move_cost(entity):
	_mobility = stats.get_mobility(entity)
	
	return int(round(2.75 * (2 - (_mobility / 100.0))))

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
	entity['movement']['next_x'] = entity['movement']['x'] + x
	entity['movement']['next_y'] = entity['movement']['y'] + y
	
	entities.trigger_event(entity, 'check_next_position')
	
	_nx = entity['movement']['next_x']
	_ny = entity['movement']['next_y']
	
	if entity['movement']['collisions']:
		_solids = [get_position_via_id(p) for p in entities.get_entity_group('life') if not p == entity['_id']]
		
		if (_nx, _ny) in _solids:
			entity['movement']['path']['refresh'] = True
			
			return
	
	set_position(entity, _nx, _ny)

def push(entity, x, y, time=-1, name='move'):
	#TODO: Placeholder. See note in controls for player movement
	if time == -1:
		raise Exception('Outdated push (still using speed)')

	entities.trigger_event(entity,
	                       'create_timer',
	                       time=time,
	                       exit_callback=lambda e: entities.trigger_event(e, 'push', x=x, y=y),
	                       name=name)

def sub_move_cost(entity):
	if 'stats' in entity:
		entity['stats']['action_points'] -= get_move_cost(entity)

def recover(entity, time=15):
	#TODO: Placeholder
	#TODO: Show 'you stand back up'
	entities.trigger_event(entity,
	                       'create_timer',
	                       time=time,
	                       exit_callback=lambda e: entities.trigger_event(e, 'recovering'),
	                       name='recovering')

def walk_to_position(entity, x, y, astar_map, weight_map, avoid=[], smp=-1):
	_start_position = get_position(entity)
	_target_position = (x, y)
	
	if _start_position == _target_position:
		return False
	
	if smp == True or (smp == -1 and numbers.distance(_start_position, _target_position) > settings.SMP_MIN_PATH_DISTANCE):
		smp = settings.ALLOW_SMP
	
	if entity['movement']['path']['destination']:
		if not numbers.distance(entity['movement']['path']['destination'], _target_position):
			return False
	
	if smp == True:
		pathfinding.astar_mp(_start_position, _target_position, astar_map, weight_map,
		                     lambda path: set_path(entity, path), avoid=avoid)
	else:
		entity['movement']['path']['positions'] = pathfinding.astar(get_position(entity), _target_position, astar_map, weight_map, avoid=avoid)
		entity['movement']['path']['destination'] = _target_position
		entity['movement']['path']['refresh'] = False
	
	return True

def stop(entity):
	timers.delete_timer(entity, 'move')
	
	entity['movement']['path']['positions'] = []
	entity['movement']['path']['destination'] = None
	entity['movement']['path']['refresh'] = False

def set_path(entity, path):
	if not path:
		return
	
	entity['movement']['path']['positions'] = path
	entity['movement']['path']['destination'] = path[len(path)-1]
	entity['movement']['path']['refresh'] = False

def get_override_speed(entity):
	return entity['movement']['override_speed']

def _walk_path(entity):
	if not entity['movement']['path']['positions']:
		return False

	if timers.has_timer_with_name(entity, 'move') or timers.has_timer_with_name(entity, 'move', fuzzy=True):
		return False
	
	if entity['movement']['path']['refresh']:
		set_path(entity, [get_position(entity)])

	_next_pos = entity['movement']['path']['positions'].pop(0)
	_x, _y = get_position(entity)
	_d_x, _d_y = _next_pos[0]-_x, _next_pos[1]-_y

	if not _d_x in [-1, 0, 1] or not _d_y in [-1, 0, 1]:
		_clear_movement(entity)

		return

	if not entity['movement']['path']['positions']:
		entity['movement']['path']['destination'] = None

	push(entity, x=_d_x, y=_d_y, name='move', time=get_override_speed(entity))