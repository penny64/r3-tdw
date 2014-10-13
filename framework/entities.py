import framework
import display
import worlds
import events

import logging
import numpy
import json
import time
import os


ENTITIES = {}
ENTITIES_TO_DELETE = set()
NEXT_ENTITY_ID = 1
REVOKED_ENTITY_IDS_HOLDING = set()
REVOKED_ENTITY_IDS = set()
CLEANING = False
TICKS_PER_SECOND = 0
CURRENT_TICKS_PER_SECOND = 0
LAST_TICK_TIME = time.time()


def boot():
	events.register_event('cleanup', cleanup)
	events.register_event('shutdown', shutdown)
	events.register_event('tick', tick)

def shutdown():
	pass

	#For debug
	#delete_all()
	#events.trigger_event('cleanup')

def save():
	logging.info('Offloading entities...')
	
	_snapshots = {}
	
	for entity_id in ENTITIES.keys():
		_entity = ENTITIES[entity_id]
		_snapshots[entity_id] = {}
		
		trigger_event(_entity, 'save', snapshot=_snapshots[entity_id])

	with open(os.path.join('data', 'entities.dat'), 'w') as save_file:
		save_file.write(json.dumps(_snapshots, indent=2))
	
	logging.info('Done!')

def load():
	global NEXT_ENTITY_ID

	logging.debug('Loading entities from disk...')

	with open(os.path.join('data', 'entities.dat'), 'r') as save_file:
		_entities = json.loads(''.join(save_file.readlines()))
		
		for entity_id in _entities:
			#TODO: Create an entity here
			_entity = _entities[entity_id]
			
			#This won't work until we remap the entity to its systems
			trigger_event(_entity, 'load')
			
			ENTITIES[entity_id] = _entity

			if int(entity_id) >= NEXT_ENTITY_ID:
				NEXT_ENTITY_ID = int(entity_id) + 1

	logging.debug('Loaded entities from disk')

def create_entity(group=None, etype='', force_id=None):
	global NEXT_ENTITY_ID

	if force_id:
		_entity_id = force_id

		if force_id in ENTITIES:
			logging.error('`force_id` overwriting existing ID')

		if int(force_id) >= NEXT_ENTITY_ID:
			NEXT_ENTITY_ID = int(force_id) + 1
	else:
		if REVOKED_ENTITY_IDS:
			_entity_id = REVOKED_ENTITY_IDS.pop()
		else:
			_entity_id = str(NEXT_ENTITY_ID)
			NEXT_ENTITY_ID += 1

	#NOTE: If this happens, you're doing something you shouldn't.
	if _entity_id in ENTITIES.keys():
		logging.fatal('New entity overwriting existing. Dumping to disk...')

		crash_dump(ENTITIES[_entity_id], ['_id', '_groups', '_etype'])

	_entity = {'_id': _entity_id,
	           '_events': {},
	           '_groups': [],
	           '_etype': etype}

	ENTITIES[_entity['_id']] = _entity

	create_event(_entity, 'save')
	create_event(_entity, 'load')
	create_event(_entity, 'delete')
	create_event(_entity, 'logic')
	create_event(_entity, 'tick')
	create_event(_entity, 'post_tick')

	if group:
		add_entity_to_group(_entity, group)

	worlds.register_entity(_entity)

	return _entity

def restore_floating_entity(entity, group_map={}):
	_new_groups = []
	
	for group_name in entity['_groups']:
		if group_name in group_map:
			_new_groups.append(group_map[group_name])
		else:
			_new_groups.append(group_name)
	
	ENTITIES[entity['_id']] = entity
	entity['_groups'] = []
	
	for group_name in _new_groups:
		add_entity_to_group(entity, group_name)
	
	logging.debug('Floating entity restored')
	
	return entity

def crash_dump(entity, dump_keys):
	with open('crashdump.txt', 'w') as dump:
		for key in dump_keys:
			dump.write('%s: %s\n' % (key, json.dumps(entity[key])))

	raise Exception('Entity crash dump requested. See `crashdump.txt`')

def delete_all():
	ENTITIES_TO_DELETE.update(ENTITIES.keys())

def delete_entity(entity):
	if not entity['_id'] in ENTITIES:
		return False

	trigger_event(entity, 'delete')
	
	if worlds.ACTIVE_WORLD:
		remove_entity_from_all_groups(entity)
	
	REVOKED_ENTITY_IDS_HOLDING.add(entity['_id'])

	del ENTITIES[entity['_id']]

def delete_entity_via_id(entity_id):
	if not entity_id in ENTITIES:

		return False

	ENTITIES_TO_DELETE.add(entity_id)

def get_entity(entity_id):
	return ENTITIES[entity_id]

def create_entity_group(group_name, static=False):
	_world = worlds.get_active_world()

	if group_name in _world['entity_groups']:
		raise Exception('Trying to create duplicate entity group:' % group_name)

	_world['entity_groups'][group_name] = []
	
	if static:
		_world['static_entity_groups'].add(group_name)

	logging.debug('Created entity group: %s' % group_name)

def clear_entity_group(group_name):
	for entity_id in get_entity_group(group_name):
		delete_entity_via_id(entity_id)

	logging.debug('Cleared entity group: %s' % group_name)

def get_entity_group(group_name):
	_world = worlds.get_active_world()
	
	return _world['entity_groups'][group_name]

def get_entity_groups(group_names):
	_world = worlds.get_active_world()
	_entities = []

	for group_name in group_names:
		_entities.extend(_world['entity_groups'][group_name])

	return [entity_id for entity_id in _entities if entity_id in ENTITIES]

def add_entity_to_group(entity, group_name):
	_world = worlds.get_active_world()
	
	if entity['_id'] in _world['entity_groups'][group_name]:
		return False

	entity['_groups'].append(group_name)
	_world['entity_groups'][group_name].append(entity['_id'])

def remove_entity_from_group(entity, group_name):
	_world = worlds.get_active_world()
	
	if not entity['_id'] in _world['entity_groups'][group_name]:
		print('Trying to remove entity from a group it isn\'t in: %s (%s)' % (entity['_id'], group_name))
		entity['_groups'].remove(group_name)

		return False

	_world['entity_groups'][group_name].remove(entity['_id'])
	entity['_groups'].remove(group_name)

def remove_entity_from_all_groups(entity):
	for group_name in entity['_groups'][:]:
		remove_entity_from_group(entity, group_name)

def create_event(entity, event_name):
	if event_name in entity['_events']:
		logging.debug('Trying to create duplicate event for entity: %s' % event_name)
		
		return
	
	entity['_events'][event_name] = {'events': {}, 'id': 1, 'banned': set()}

def register_event(entity, event_name, callback):
	_event_structure = entity['_events'][event_name]
	_event = {'callback': callback,
	          'id': str(_event_structure['id'])}
	_event_structure['events'][str(_event_structure['id'])] = _event
	_event_structure['id'] += 1

def unregister_event(entity, event_name, callback):
	_event_structure = entity['_events'][event_name]

	for event in _event_structure['events'].values():
		if event['callback'] == callback:
			_event_structure['banned'].add(event['id'])

			del _event_structure['events'][event['id']]
			return True

	logging.warning('Trying to unregister unregistered event: %s' % event_name)

def trigger_event(entity, event_name, _ban_events=[], **kwargs):
	_event_structure = entity['_events'][event_name]

	for event in _event_structure['events'].values():
		if event['callback'] in _ban_events:
			continue
		
		if event['id'] in _event_structure['banned']:
			_event_structure['banned'].remove(event['id'])

			continue
		
		event['callback'](entity, **kwargs)

	return True

def tick():
	_world = worlds.get_active_world()

	for entity_group in _world['entity_groups'].keys():
		if entity_group in _world['static_entity_groups']:
			continue

		for entity_id in _world['entity_groups'][entity_group]:
			trigger_event(ENTITIES[entity_id], 'tick')

def reset():
	global REVOKED_ENTITY_IDS_HOLDING, REVOKED_ENTITY_IDS

	REVOKED_ENTITY_IDS.update(REVOKED_ENTITY_IDS_HOLDING)
	REVOKED_ENTITY_IDS_HOLDING = set()

def cleanup():
	global ENTITIES_TO_DELETE, CLEANING
	
	CLEANING = True

	while ENTITIES_TO_DELETE:
		_entity_id = ENTITIES_TO_DELETE.pop()

		if not _entity_id in ENTITIES:
			remove_entity_from_all_groups(_entity)

			continue

		_entity = ENTITIES[_entity_id]

		trigger_event(_entity, 'delete')
		
		if worlds.ACTIVE_WORLD:
			remove_entity_from_all_groups(_entity)
		
		#REVOKED_ENTITY_IDS_HOLDING.add(_entity_id)

		del ENTITIES[_entity_id]

	ENTITIES_TO_DELETE = set()
	CLEANING = False
