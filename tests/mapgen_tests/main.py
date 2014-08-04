from framework import entities, controls, display, events, worlds, tile, timers, movement, pathfinding, stats

import framework

import post_processing
import constants
import mapgen

import time


CAMERA_X = 0
CAMERA_Y = 0


def handle_input():
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	return True

def handle_mouse_movement(x, y, **kwargs):
	pass

def handle_mouse_pressed(x, y, button):
	pass

def draw_map():
	for y in range(constants.MAP_VIEW_HEIGHT):
		for x in range(constants.MAP_VIEW_WIDTH):
			_x = x + CAMERA_X
			_y = y + CAMERA_Y
			
			if _x >= mapgen.LEVEL_WIDTH or _y >= mapgen.LEVEL_HEIGHT:
				continue
			
			_tile = entities.get_entity(str(mapgen.TILE_MAP[_y][_x]))
			
			display.write_char_direct(x, y, _tile['tile']['char'], _tile['tile']['fore_color'], _tile['tile']['back_color'])
			
			#entities.trigger_event(_tile, 'set_position', x=x, y=y)
			#entities.trigger_event(_tile, 'draw')
	
	#display.blit_surface('tiles')
	#events.trigger_event('draw')
	#display.blit_background('tiles')

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
	global CAMERA_X
	global CAMERA_Y
	
	events.trigger_event('input')
	events.trigger_event('tick')
	
	if not handle_input():
		return False
	
	#if CAMERA_X < constants.MAP_VIEW_WIDTH/2:
	#	CAMERA_X += 1
	#elif CAMERA_Y < constants.MAP_VIEW_HEIGHT/2:
	#	CAMERA_Y += 1
	
	draw_map()
	draw()
	
	print display.get_fps()
	
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
