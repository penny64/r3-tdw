from framework import entities, timers, events


PROCESSOR = None


def start():
	global PROCESSOR
	
	_entity = entities.create_entity(group='systems')
	
	PROCESSOR = _entity
	
	timers.register(_entity, use_system_event='post_process')


def run(*args, **kwargs):
	entities.trigger_event(PROCESSOR, 'create_timer', *args, **kwargs)