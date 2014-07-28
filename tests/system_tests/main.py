from framework import entities, events, worlds

import system_ai

import time


if __name__ == '__main__':
	worlds.create('test')
	entities.boot()
	entities.create_entity_group('systems')
	system_ai.boot()
	
	_a1 = entities.create_entity()
	
	system_ai.register_human(_a1)
	
	_start_time = time.time()
	
	for i in range(1):
		events.trigger_event('tick')
	
	print 'Took: ', time.time()-_start_time