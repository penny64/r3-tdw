from framework import entities

import logging

WATCHING = []


def register(entity):
	entities.register_event(entity, 'target_found', _target_found)
	entities.register_event(entity, 'target_lost', _target_lost)
	entities.register_event(entity, 'target_search_failed', _target_search_failed)
	entities.register_event(entity, 'squad_inform_lost_target', _squad_inform_lost_target)
	
	WATCHING.append(entity['_id'])


############
#Operations#
############

def _log(entity, label, **kwargs):
	logging.info('%s: %s - %s' % (entity['stats']['name'], label, kwargs))

def _target_found(entity, **kwargs):
	_log(entity, 'TARGET FOUND', **kwargs)

def _target_lost(entity, **kwargs):
	_log(entity, 'TARGET LOST', **kwargs)

def _target_search_failed(entity, **kwargs):
	_log(entity, 'TARGET SEARCH FAILED', **kwargs)

def _squad_inform_lost_target(entity, **kwargs):
	_log(entity, 'INFORM SQUAD: LOST TARGET', **kwargs)