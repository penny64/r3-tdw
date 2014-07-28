import pathfinding
import dijkstra
import controls
import display
import numbers
import shapes
import worlds
import events
import timers
import goapy
import clock
import flags

import logging
import sys


NEXT_LOADER_CALLBACK = None
NEXT_TRANSITION = None


def init(debug=False):
	logger = logging.getLogger()
	console_formatter = logging.Formatter('[%(levelname)s] %(message)s', datefmt='%H:%M:%S %m/%d/%y')
	ch = logging.StreamHandler()
	ch.setFormatter(console_formatter)
	logger.addHandler(ch)

	if debug:
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)

	events.register_event('boot', display.boot)
	events.register_event('boot', entities.boot)
	events.register_event('boot', clock.boot)
	events.register_event('boot', controls.boot)
	events.register_event('unload', display.clear_screen)
	events.register_event('input', controls.handle_input)
	events.register_event('loop', clock.tick)
	events.register_event('shutdown', display.shutdown)

def _clean():
	events.trigger_event('unload')
	events.trigger_event('cleanup')
	events.trigger_event('post_unload')

	events.unregister_all_events('unload')
	events.register_event('unload', display.clear_screen)

def load(callback, transition=None, **kwargs):
	global NEXT_LOADER_CALLBACK, NEXT_TRANSITION

	_clean()
	
	NEXT_LOADER_CALLBACK = lambda: callback(**kwargs)

	if transition:
		NEXT_TRANSITION = transition

def shutdown():
	global NEXT_LOADER_CALLBACK

	logging.info('Shutting down...')
	
	_clean()
	events.trigger_event('shutdown')

	NEXT_LOADER_CALLBACK = None

def run(callback):
	global NEXT_LOADER_CALLBACK, NEXT_TRANSITION

	events.trigger_event('boot')
	
	load(callback)

	while NEXT_LOADER_CALLBACK:
		if NEXT_TRANSITION:
			while 1:
				break
			
			NEXT_TRANSITION = None

		NEXT_LOADER_CALLBACK()
