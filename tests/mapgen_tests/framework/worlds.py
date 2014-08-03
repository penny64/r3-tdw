import entities
import display
import numbers
import events
import worlds
import clock

import logging
import os


WORLDS = {}
ACTIVE_WORLD = None


def _check_active_world():
	if not ACTIVE_WORLD:
		raise Exception('No world active.')

def create(world_name, width=8000, height=8000):
	global ACTIVE_WORLD

	WORLDS[world_name] = {'size': (width, height),
                          'entities': [],
                          'entity_groups': {},
	                      'static_entity_groups': set()}

	logging.debug('Created world: %s' % world_name)

	if not ACTIVE_WORLD:
		ACTIVE_WORLD = world_name

		logging.debug('Active world set: %s' % world_name)
	else:
		logging.warning('Creating world while another is active.')

def delete(world_name):
	global ACTIVE_WORLD

	if not world_name in WORLDS:
		raise Exception('World does not exist: %s' % world_name)

	for entity_id in WORLDS[world_name]['entities']:
		entities.delete_entity_via_id(entity_id)

	logging.debug('Deleted world: %s' % world_name)

	if ACTIVE_WORLD == world_name:
		ACTIVE_WORLD = None

	del WORLDS[world_name]

def register_entity(entity):
	_check_active_world()

	WORLDS[ACTIVE_WORLD]['entities'].append(entity['_id'])

def set_active_world(world_name):
	if not world_name in WORLDS:
		raise Exception('World does not exist: %s' % world_name)

	ACTIVE_WORLD = world_name

def get_active_world():
	_check_active_world()

	return WORLDS[ACTIVE_WORLD]

def get_active_entities():
	_check_active_world()

	return WORLDS[ACTIVE_WORLD]['entities']

def get_size():
	_check_active_world()

	return WORLDS[ACTIVE_WORLD]['size']

