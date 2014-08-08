from framework import entities, controls, display, events, worlds, movement, pathfinding, numbers, stats

import framework

import post_processing
import constants
import settings
import ui_cursor
import ui_input
import ui_draw
import mapgen
import camera
import nodes
import maps
import life

import numpy
import time
import sys

CURSOR = None
PAUSED = True


def handle_input():
	global PAUSED, TICK_SPEED
	
	if settings.TICK_MODE in ['normal', 'strategy']:
		if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
			return False
		
		if controls.get_input_char_pressed(' '):
			if settings.TICK_MODE == 'strategy':
				settings.TICK_MODE = 'normal'
			else:
				settings.TICK_MODE = 'strategy'
		
		if settings.TICK_MODE == 'strategy':
			nodes.handle_keyboard_input(PLAYER)
	
	return True

def handle_mouse_movement(x, y, **kwargs):
	if settings.TICK_MODE == 'strategy':
		nodes.handle_mouse_movement(PLAYER, x, y, x+camera.X, y+camera.Y)

def handle_mouse_pressed(x, y, button):
	if settings.TICK_MODE == 'strategy':
		nodes.handle_mouse_pressed(PLAYER, x, y, button)
	
	elif settings.TICK_MODE == 'normal':
		_c_x = (camera.X+x) - (constants.MAP_VIEW_WIDTH/2)
		_c_y = (camera.Y+y) - (constants.MAP_VIEW_HEIGHT/2)
		
		if button == 1:
			camera.set_pos(_c_x, _c_y)

def logic():
	if settings.TICK_MODE == 'normal':
		for entity_id in entities.get_entity_group('life'):
			entities.trigger_event(entities.get_entity(entity_id), 'logic')

def tick():
	if settings.TICK_MODE == 'strategy':
		return
	
	if PLAYER['node_path']['path']:
		_ticks_per_tick = settings.PLAN_TICK_RATE
	else:
		_ticks_per_tick = 1
	
	for _ in range(_ticks_per_tick):
		for entity_id in entities.get_entity_group('life'):
			entities.trigger_event(entities.get_entity(entity_id), 'tick')

def draw():
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	ui_draw.draw_status_bar(planning=settings.TICK_MODE == 'strategy',
	                        executing=settings.TICK_MODE == 'normal' and PLAYER['node_path']['path'],
	                        execute_speed='>' * numbers.clip(5-(stats.get_speed(PLAYER)/settings.PLAN_TICK_RATE), 1, 4) * (len(PLAYER['node_path']['path'])>0))
	ui_draw.draw_life_labels()
	ui_draw.draw_node_path(PLAYER)
	
	if '--fps' in sys.argv:
		ui_draw.draw_fps()
	
	events.trigger_event('post_process')
	display.blit_surface('nodes')
	display.blit_surface('life')
	display.blit_surface('ui')
	events.trigger_event('draw')

def loop():
	global FPSS
	
	events.trigger_event('input')
	events.trigger_event('logic')
	events.trigger_event('tick')
	events.trigger_event('camera')
	
	if not handle_input():
		return False
	
	draw()
	
	return True

def main():
	global CURSOR, PLAYER
	
	PLAYER = life.human(150, 150, 'Tester Toaster')
	
	ui_cursor.boot()
	ui_input.boot(PLAYER)
	ui_draw.boot(PLAYER)
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('camera', camera.update)
	events.register_event('logic', logic)
	events.register_event('tick', tick)
	
	_t = time.time()
	mapgen.swamp(400, 400)	
	print 'Took:', time.time()-_t
	
	pathfinding.setup(mapgen.LEVEL_WIDTH, mapgen.LEVEL_HEIGHT, mapgen.SOLIDS, mapgen.WEIGHT_MAP)	
	
	display.create_surface('tiles', width=mapgen.LEVEL_WIDTH, height=mapgen.LEVEL_HEIGHT)
	maps.render_map(mapgen.TILE_MAP, mapgen.LEVEL_WIDTH, mapgen.LEVEL_HEIGHT)	
	
	camera.set_limits(0, 0, mapgen.LEVEL_WIDTH-constants.MAP_VIEW_WIDTH, mapgen.LEVEL_HEIGHT-constants.MAP_VIEW_HEIGHT)
	
	while loop():
		events.trigger_event('cleanup')
		
		continue
	
	framework.shutdown()

if __name__ == '__main__':
	framework.init()
	
	worlds.create('test')
	
	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('life', static=True)
	entities.create_entity_group('systems')
	entities.create_entity_group('ui')
	entities.create_entity_group('nodes')

	display.create_surface('life', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('nodes', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('ui')
	display.set_clear_surface('ui', 'tiles')
	
	post_processing.start()
	
	framework.run(main)
