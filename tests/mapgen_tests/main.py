from framework import entities, controls, display, events, worlds, tile, timers, movement, pathfinding, stats, numbers

import framework

import post_processing
import constants
import mapgen

import numpy
import time
import sys


CURSOR = None
CAMERA_X = 0
CAMERA_Y = 0
CAMERA_LAST_X = 0
CAMERA_LAST_Y = 0


def handle_input():
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	return True

def handle_mouse_movement(x, y, **kwargs):
	entities.trigger_event(CURSOR, 'set_position', x=x, y=y)

def handle_mouse_pressed(x, y, button):
	global CAMERA_X
	global CAMERA_Y
	
	_c_x = (CAMERA_X+x) - (constants.MAP_VIEW_WIDTH/2)
	_c_y = (CAMERA_Y+y) - (constants.MAP_VIEW_HEIGHT/2)
	
	if button == 1:
		set_camera_pos(_c_x, _c_y)

def draw_map():
	_surface = display.get_surface('tiles')
	
	for y in range(mapgen.LEVEL_HEIGHT):
		for x in range(mapgen.LEVEL_WIDTH):
			_tile = mapgen.TILE_MAP[y][x]
			
			display._set_char('tiles', _tile['x'], _tile['y'], _tile['c'], _tile['c_f'], _tile['c_b'])
	
	display.blit_surface_viewport('tiles', CAMERA_X, CAMERA_Y, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)

def draw():
	entities.trigger_event(CURSOR, 'draw')
	events.trigger_event('post_process')
	display.blit_surface('ui')
	events.trigger_event('draw')

def set_camera_pos(x, y):
	global CAMERA_X
	global CAMERA_Y
	
	CAMERA_X = numbers.clip(x, 0, mapgen.LEVEL_WIDTH-constants.MAP_VIEW_WIDTH)
	CAMERA_Y = numbers.clip(y, 0, mapgen.LEVEL_HEIGHT-constants.MAP_VIEW_HEIGHT)

def scroll_map(xscroll=0, yscroll=0):
	global CAMERA_X
	global CAMERA_Y
	
	_surface = display.get_surface('tiles')
	
	if xscroll:
		if xscroll > 0:
			_xd = -1
		else:
			_xd = 1
	
		_surface['c'] = numpy.roll(_surface['c'], _xd, axis=1)
		_surface['f'][0] = numpy.roll(_surface['f'][0], _xd, axis=1)
		_surface['f'][1] = numpy.roll(_surface['f'][1], _xd, axis=1)
		_surface['f'][2] = numpy.roll(_surface['f'][2], _xd, axis=1)	
		_surface['b'][0] = numpy.roll(_surface['b'][0], _xd, axis=1)
		_surface['b'][1] = numpy.roll(_surface['b'][1], _xd, axis=1)
		_surface['b'][2] = numpy.roll(_surface['b'][2], _xd, axis=1)
		
		for y in range(constants.MAP_VIEW_HEIGHT):
			_tile = entities.get_entity(str(mapgen.TILE_MAP[y][constants.MAP_VIEW_WIDTH-1+CAMERA_X+1]))
			
			entities.trigger_event(_tile, 'draw', x=constants.MAP_VIEW_WIDTH-1, y=y, direct=True)
		
		CAMERA_X += 1
	
	if yscroll:
		if yscroll > 0:
			_xd = -1
		else:
			_xd = 1
	
		_surface['c'] = numpy.roll(_surface['c'], _xd, axis=0)
		_surface['f'][0] = numpy.roll(_surface['f'][0], _xd, axis=0)
		_surface['f'][1] = numpy.roll(_surface['f'][1], _xd, axis=0)
		_surface['f'][2] = numpy.roll(_surface['f'][2], _xd, axis=0)	
		_surface['b'][0] = numpy.roll(_surface['b'][0], _xd, axis=0)
		_surface['b'][1] = numpy.roll(_surface['b'][1], _xd, axis=0)
		_surface['b'][2] = numpy.roll(_surface['b'][2], _xd, axis=0)
		
		for x in range(constants.MAP_VIEW_WIDTH):
			_tile = entities.get_entity(str(mapgen.TILE_MAP[constants.MAP_VIEW_HEIGHT-1+CAMERA_Y+1][x]))
			
			entities.trigger_event(_tile, 'draw', x=x, y=constants.MAP_VIEW_HEIGHT-1, direct=True)	
		
		CAMERA_Y += 1

def main():
	#pathfinding.setup(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, [])
	global CURSOR
	
	CURSOR = entities.create_entity(group='systems')
	
	framework.tile.register(CURSOR, surface='ui')
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	
	_t = time.time()
	mapgen.swamp(400, 400)	
	print 'Took:', time.time()-_t
	
	display.create_surface('tiles', width=mapgen.LEVEL_WIDTH, height=mapgen.LEVEL_HEIGHT)
	
	draw_map()
	
	while loop():
		events.trigger_event('cleanup')
		
		continue
	
	framework.shutdown()

def loop():
	global CAMERA_LAST_X
	global CAMERA_LAST_Y
	global CAMERA_X
	global CAMERA_Y
	
	events.trigger_event('input')
	events.trigger_event('tick')
	
	if not handle_input():
		return False
	
	if not CAMERA_LAST_X == CAMERA_X or not CAMERA_LAST_Y == CAMERA_Y:
		display.blit_surface_viewport('tiles', CAMERA_X, CAMERA_Y, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
		
		CAMERA_LAST_X = CAMERA_X
		CAMERA_LAST_Y = CAMERA_Y
		
		display.set_surface_camera('tiles', CAMERA_X, CAMERA_Y)
	
	draw()
	
	if '--fps' in sys.argv:
		print display.get_fps()
	
	return True

if __name__ == '__main__':
	framework.init()
	
	worlds.create('test')
	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('systems')
	entities.create_entity_group('ui')
	display.create_surface('background')
	display.create_surface('ui')
	display.set_clear_surface('ui', 'tiles')
	post_processing.start()
	
	framework.run(main)
