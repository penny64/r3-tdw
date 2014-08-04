from framework import entities, controls, display, events, worlds, tile, timers, movement, pathfinding, stats

import framework

import post_processing
import constants
import mapgen

import time



def handle_input():
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	return True

def handle_mouse_movement(x, y, **kwargs):
	pass

def handle_mouse_pressed(x, y, button):
	pass

def draw_map():
	for entity_id in entities.get_entity_group('tiles'):
		#_x, _y = 
		
		#if _x >= constants.WINDOW_WIDTH or _y >= constants.WINDOW_HEIGHT:
		#	continue
		
		entities.trigger_event(entities.get_entity(entity_id), 'draw')
	
	display.blit_surface('tiles')
	events.trigger_event('draw')
	display.blit_background('tiles')

def draw():
	events.trigger_event('post_process')
	events.trigger_event('draw')

def main():
	#pathfinding.setup(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, [])
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	
	_t = time.time()
	mapgen.swamp(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)	
	print 'Took:', time.time()-_t
	
	draw_map()
	
	while loop():
		events.trigger_event('cleanup')
		
		continue
	
	framework.shutdown()

def loop():
	events.trigger_event('input')
	events.trigger_event('tick')
	
	if not handle_input():
		return False
	
	#draw_map()
	draw()
	
	#print display.get_fps()
	
	return True

if __name__ == '__main__':
	framework.init()
	
	worlds.create('test')
	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('systems')
	display.create_surface('background')
	display.create_surface('tiles')
	post_processing.start()
	
	framework.run(main)
