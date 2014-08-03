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
REINT_MAP = {'set': set,
             'ndarray': numpy.array}


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
	_save_string = []
	_banned_keys = ['_events', 'image', 'sprite']

	for entity_id in ENTITIES.keys():
		if not ENTITIES[entity_id]['_etype']:
			continue

		_entity = ENTITIES[entity_id].copy()
		_entity['reint'] = {}

		print 'Dumping entity #%s' % entity_id

		for key in _entity.keys():
			if key in _banned_keys:
				del _entity[key]

				continue

			_value = _entity[key]

			#TODO: We need to reint these to their proper type on load
			if isinstance(_value, numpy.ndarray):
				_entity['reint'][key] = 'ndarray'
				_entity[key] = list(_value)
			elif isinstance(_value, set):
				_entity['reint'][key] = 'set'
				_entity[key] = list(_value)

		_save_string.append(json.dumps(_entity))

	with open(os.path.join('data', 'save_file.dat'), 'w') as save_file:
		save_file.write('\n'.join(_save_string))

def load():
	global NEXT_ENTITY_ID

	_entities = {}

	logging.debug('Loading entities from disk...')

	with open(os.path.join('data', 'save_file.dat'), 'r') as save_file:
		for line in save_file.readlines():
			_entity = json.loads(line.rstrip())
			_entities[int(_entity['_id'])] = _entity

			for reint_key in _entity['reint']:
				_entity[reint_key] = REINT_MAP[_entity['reint'][reint_key]](_entity[reint_key])

			if int(_entity['_id']) >= NEXT_ENTITY_ID:
				NEXT_ENTITY_ID = int(_entity['_id'])+1

	_create_order = _entities.keys()
	_create_order.sort()
	_player = None

	#TODO: Move to event system
	for entity in [_entities[_id] for _id in _create_order]:
		REVOKED_ENTITY_IDS.add(entity['_id'])

		if entity['_etype'] == 'item':
			_item = items.spawn(entity['name'], entity['position'][0], entity['position'][1])
			_item.update(entity)

			if _item['owned'] and 'hide' in _item['_events']:
				framework.entities.trigger_event(_item, 'hide')

		elif entity['_etype'] == 'soldier':
			_soldier = soldiers.create_soldier(entity['position'][0], entity['position'][1], entity['team'], no_inventory=True)
			_soldier.update(entity)

			if _soldier['team'] == 'player':
				_player = _soldier

		elif entity['_etype'] == 'weapon':
			_weapon = weapons.create(entity['name'],
			                         ENTITIES[entity['parent_id']],
			                         entity['max_rounds'],
			                         entity['recoil_time'],
			                         entity['reload_time'],
			                         skill_type=entity['skill_type'],
			                         damage=entity['damage'],
			                         spread=entity['spread'],
			                         burst_rounds=entity['burst_rounds'],
			                         can_auto=entity['can_auto'])
			_weapon.update(entity)

		elif entity['_etype'] == 'overwatch':
			_overwatch = overwatch.create(_player)
			_overwatch.update(entity)

			overwatch.show_objectives(_overwatch)

		else:
			print 'Unknown e_type', entity['_etype']

	logging.debug('Loaded entities from disk')
	print 'Remaining revoked IDs', REVOKED_ENTITY_IDS
	player.register_entity(_player)

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

	create_event(_entity, 'delete')
	create_event(_entity, 'logic')
	create_event(_entity, 'tick')

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

def delete_entity(entity, quick=False):
	if not entity['_id'] in ENTITIES:
		return False

	if not quick:
		ENTITIES_TO_DELETE.add(entity['_id'])
	else:
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

def create_entity_group(group_name):
	_world = worlds.get_active_world()

	if group_name in _world['entity_groups']:
		raise Exception('Trying to create duplicate entity group:' % group_name)

	_world['entity_groups'][group_name] = []

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
		if entity_group.count('static'):
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
		
		REVOKED_ENTITY_IDS_HOLDING.add(_entity_id)

		del ENTITIES[_entity_id]

	ENTITIES_TO_DELETE = set()
	CLEANING = False
