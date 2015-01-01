import entities
import events

import logging


def register(entity, use_system_event=None, use_entity_event='tick'):
	entity['timers'] = []
	
	entities.create_event(entity, 'create_timer')
	entities.create_event(entity, 'clear_timers')
	entities.register_event(entity, 'create_timer', create_timer)
	entities.register_event(entity, 'clear_timers', clear_timers)
	
	if use_system_event:
		events.register_event(use_system_event, lambda: tick(entity))
	else:
		entities.register_event(entity, use_entity_event, tick)

def create_timer(entity, time, name='', repeat=0, callback=None, enter_callback=None, exit_callback=None, delete_callback=None, repeat_callback=None):
	entity['timers'].append({'callback': callback,
	                         'name': name.lower(),
	                         'enter_callback': enter_callback,
	                         'exit_callback': exit_callback,
	                         'repeat_callback': repeat_callback,
	                         'delete_callback': delete_callback,
	                         'time': time,
	                         'time_max': time,
	                         'repeat': repeat,
	                         'entered': False,
	                         'stop': False})

def clear_timers(entity):
	entity['timers'] = []

def get_nearest_timer(entity):
	_nearest_timer = {'timer': None, 'time': 0}
	
	for timer in entity['timers']:
		_time = timer['time'] + (timer['time_max'] * timer['repeat'])
		
		if not _nearest_timer['time'] or _time < _nearest_timer['time']:
			_nearest_timer['time'] = _time
			_nearest_timer['timer'] = timer
	
	return _nearest_timer['timer']

def has_timer_with_name(entity, name, next_only=False, fuzzy=False):
	for timer in entity['timers']:
		if timer['stop']:
			continue
		
		if fuzzy and timer['name'].count(name.lower()):
			return True
		
		if timer['name'] == name.lower():
			return True
		
		if next_only:
			return False
	
	return False

def delete_timer(entity, name):
	for timer in entity['timers']:
		if timer['stop']:
			continue
		
		if timer['name'].count(name.lower()):
			entity['timers'].remove(timer)
			
			break

def stop_timer(entity, name):
	for timer in entity['timers']:
		if timer['stop']:
			continue
		
		if timer['name'].count(name.lower()):
			timer['stop'] = True
			print 'Stopped timer'
			
			break

def tick(entity):
	_remove_timers = []
	
	for timer in entity['timers']:
		if timer['stop']:
			_remove_timers.append(timer)
			
			continue
		
		if not timer['entered']:
			if timer['enter_callback']:
				timer['enter_callback'](entity)
			
			timer['entered'] = True
		
		if timer['time'] > 0:
			timer['time'] -= 1
			
			if timer['callback']:
				timer['callback'](entity)
		elif timer['repeat'] > 0 or timer['repeat'] == -1:
			timer['time'] = timer['time_max']
			
			if timer['repeat'] > 0:
				timer['repeat'] -= 1
			
			if timer['repeat_callback']:
				timer['repeat_callback'](entity)
		else:
			if timer['exit_callback']:
				timer['exit_callback'](entity)
			
			_remove_timers.append(timer)
	
	for timer in _remove_timers:
		if timer['delete_callback']:
			timer['delete_callback'](entity)

		if timer in entity['timers']:
			entity['timers'].remove(timer)
		
		else:
			logging.warning('Removing a timer in a timer... hopefully')