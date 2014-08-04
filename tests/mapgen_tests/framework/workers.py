from framework import entities, timers


def _create():
	_entity = entities.create_entity(group='systems')
	
	timers.register(_entity, use_system_event='post_process')
	
	entities.create_event(_entity, 'finish')
	
	return _entity


def _counter_2d_tick(entity):
	#print 'passes:', int(entity['passes'])
	
	for i in range(int(entity['passes'])):
		if entity['x']['current'] < entity['x']['max']-1:
			entity['callback'](entity['x']['current'], entity['y']['current'])
			
			if entity['y']['current'] < entity['y']['max']-1:
				entity['y']['current'] += 1
			else:
				entity['y']['current'] = 0
				entity['x']['current'] += 1
			
		else:
			entity['callback'](entity['x']['current'], entity['y']['current'])
			entities.trigger_event(entity, 'finish')
			
			return entities.delete_entity(entity)

def counter_2d(x, y, passes, callback):
	_entity = _create()
	_entity['x'] = {'current': 0, 'max': x}
	_entity['y'] = {'current': 0, 'max': y}
	_entity['callback'] = callback
	_entity['passes'] = (x*y) / float(passes)
	
	entities.trigger_event(_entity,
	                       'create_timer',
	                       time=0,
	                       repeat=-1,
	                       repeat_callback=_counter_2d_tick)
	
	return _entity