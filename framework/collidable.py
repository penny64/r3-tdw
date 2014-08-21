from framework import entities, events

import constants

import logging


COLLISION_MAP = {}


def boot():
	events.register_event('post_unload', reset_collision_map)

def register(entity, active=True, clipping=True, ignore_groups=[], ignore_entities=[]):
	_collidable = {'active': active,
	               'x': 5,
	               'y': 5,
	               'last_x': 5,
	               'last_y': 5,
	               'ignore_groups': ignore_groups,
	               'ignore_entities': ignore_entities,
	               'clipping': clipping}
	
	entity['collidable'] = _collidable
	
	entities.create_event(entity, 'set_collidable')
	entities.create_event(entity, 'set_not_collidable')
	entities.create_event(entity, 'set_position')
	entities.create_event(entity, 'position_changed')
	entities.create_event(entity, 'collision_with_entity')
	entities.create_event(entity, 'allow_clipping')
	entities.create_event(entity, 'ban_clipping')
	entities.register_event(entity, 'allow_clipping', _allow_clipping)
	entities.register_event(entity, 'ban_clipping', _ban_clipping)
	entities.register_event(entity, 'delete', delete)
	entities.register_event(entity, 'set_collidable', set_active)
	entities.register_event(entity, 'set_not_collidable', set_inactive)
	entities.register_event(entity, 'set_position', set_collidable_position)
	entities.register_event(entity, 'position_changed', handle_collisions)

def reset_collision_map():
	global COLLISION_MAP
	
	COLLISION_MAP = {}

def delete(entity):
	_pos = (entity['collidable']['x'], entity['collidable']['y'])
	
	if _pos in COLLISION_MAP and entity['_id'] in COLLISION_MAP[_pos]:
		COLLISION_MAP[_pos].remove(entity['_id'])

		if not COLLISION_MAP[_pos]:
			del COLLISION_MAP[_pos]

def set_active(entity):
	entity['collidable']['active'] = True
	
	_pos = (entity['collidable']['x'], entity['collidable']['y'])
	
	if not _pos in COLLISION_MAP:
		COLLISION_MAP[_pos] = set([entity['_id']])
	
	elif not entity['_id'] in COLLISION_MAP[_pos]:
		COLLISION_MAP[_pos].add(entity['_id'])

def set_inactive(entity):
	entity['collidable']['active'] = False
	
	_pos = (entity['collidable']['x'], entity['collidable']['y'])
	
	if _pos in COLLISION_MAP and entity['_id'] in COLLISION_MAP[_pos]:
		COLLISION_MAP[_pos].remove(entity['_id'])

		if not COLLISION_MAP[_pos]:
			del COLLISION_MAP[_pos]

def _allow_clipping(entity):
	entity['collidable']['clipping'] = True

def _ban_clipping(entity):
	entity['collidable']['clipping'] = False

def set_collidable_position(entity, x, y):
	entity['collidable']['x'] = int(round(x))
	entity['collidable']['y'] = int(round(y))

	if not entity['collidable']['active']:
		return False
	
	_last_pos = (entity['collidable']['last_x'], entity['collidable']['last_y'])
	
	if _last_pos in COLLISION_MAP and entity['_id'] in COLLISION_MAP[_last_pos]:
		COLLISION_MAP[_last_pos].remove(entity['_id'])

		if not COLLISION_MAP[_last_pos]:
			del COLLISION_MAP[_last_pos]
	
	_pos = (entity['collidable']['x'], entity['collidable']['y'])
	
	if not _pos in COLLISION_MAP:
		COLLISION_MAP[_pos] = set([entity['_id']])
	
	elif not entity['_id'] in COLLISION_MAP[_pos]:
		COLLISION_MAP[_pos].add(entity['_id'])
	
	entity['collidable']['last_x'] = entity['collidable']['x']
	entity['collidable']['last_y'] = entity['collidable']['y']

def handle_collisions(entity, x, y, old_x, old_y):
	_pos = (entity['collidable']['x'], entity['collidable']['y'])
	_collision = False
	
	if _pos[0] < 0 or _pos[1] < 0 or _pos[0] >= constants.LEVEL_WIDTH or _pos[1] >= constants.LEVEL_HEIGHT:
		entities.trigger_event(entity, 'set_position', x=old_x, y=old_y)

		return

	if _pos in COLLISION_MAP:
		_objects = COLLISION_MAP[_pos]-set([entity['_id']])
		
		if _objects:
			for entity_id in _objects:
				if entity_id in entity['collidable']['ignore_entities']:
					continue

				_entity = entities.get_entity(entity_id)
				_continue = False

				for entity_group in _entity['collidable']['ignore_groups']:
					if entity_group in _entity['_groups']:
						_continue = True

						break

				if _continue:
					continue

				if not _collision and entity['collidable']['clipping']:
					entities.trigger_event(entity, 'set_position', x=old_x, y=old_y)

					_collision = True

				entities.trigger_event(entity, 'collision_with_entity', entity_id=entity_id)
