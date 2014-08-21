import traceback
import logging
import sys


EVENTS = {'BOOT': {'events': {}, 'id': 1, 'banned': set()},
          'UNLOAD': {'events': {}, 'id': 1, 'banned': set()},
          'INPUT': {'events': {}, 'id': 1, 'banned': set()},
          'LOGIC': {'events': {}, 'id': 1, 'banned': set()},
          'LOOP': {'events': {}, 'id': 1, 'banned': set()},
          'TICK': {'events': {}, 'id': 1, 'banned': set()},
          'POST_PROCESS': {'events': {}, 'id': 1, 'banned': set()},
          'DRAW': {'events': {}, 'id': 1, 'banned': set()},
          'POST_UNLOAD': {'events': {}, 'id': 1, 'banned': set()},
          'CAMERA': {'events': {}, 'id': 1, 'banned': set()},
          'CLEANUP': {'events': {}, 'id': 1, 'banned': set()},
          'SHUTDOWN': {'events': {}, 'id': 1, 'banned': set()}}


def create_event(event_name):
	EVENTS[event_name.upper()] = {'events': {}, 'id': 1, 'banned': set()}

def register_event(event_name, callback, *args, **kargs):
	_event = {'callback': callback,
	          'args': args,
	          'kargs': kargs,
	          'id': str(EVENTS[event_name.upper()]['id'])}

	for arg in args:
		if isinstance(arg, dict) and '_id' in arg:
			_event['_world_events'] = arg['_id']

	_event_structure = EVENTS[event_name.upper()]
	_event_structure['events'][str(_event_structure['id'])] = _event
	_event_structure['id'] += 1

	logging.debug('Registered event: %s -> %s' % (event_name, callback))

	return True

def unregister_event(event_name, callback, *args, **kargs):
	for event in EVENTS[event_name.upper()]['events'].values():
		if event['callback'] == callback:
			EVENTS[event_name.upper()]['banned'].add(event['id'])

			del EVENTS[event_name.upper()]['events'][event['id']]
			return True

	raise Exception('Event not registered.')

def unregister_all_events(event_name):
	for event in EVENTS[event_name.upper()]['events'].values():
		EVENTS[event_name.upper()]['banned'].add(event['id'])

		del EVENTS[event_name.upper()]['events'][event['id']]

def trigger_event(event_name, **kwargs):
	for event in EVENTS[event_name.upper()]['events'].values():
		if event['id'] in EVENTS[event_name.upper()]['banned']:
			EVENTS[event_name.upper()]['banned'].remove(event['id'])

			continue

		_kwargs = event['kargs']
		_kwargs.update(kwargs)

		try:
			event['callback'](*event['args'], **_kwargs)
		except Exception, e:
			print
			traceback.print_exc(file=sys.stdout)
			print

			print 'Event: %s' % event_name
			print 'Callback: %s' % event['callback']

			sys.exit(1)

