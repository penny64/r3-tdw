from framework import entities, controls, display, events, worlds, movement, pathfinding, numbers

import framework

import post_processing
import constants
import mapgen
import camera
import nodes
import maps
import life
import ui

import numpy
import time
import sys

CURSOR = None
MODE = 'strategy'
PAUSED = True
TICK_SPEED = 2


def handle_input():
	global MODE, PAUSED, TICK_SPEED
	
	if MODE in ['normal', 'strategy']:
		if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
			return False
		
		#Center on player
		if controls.get_input_char_pressed('\t'):
			_x, _y = movement.get_position(PLAYER)
			
			camera.set_pos(_x - constants.MAP_VIEW_WIDTH/2, _y - constants.MAP_VIEW_HEIGHT/2)
		
		#Change tick speed
		if controls.get_input_char_pressed('1'):
			TICK_SPEED = 1
		
		elif controls.get_input_char_pressed('2'):
			TICK_SPEED = 2
		
		elif controls.get_input_char_pressed('3'):
			TICK_SPEED = 3
		
		elif controls.get_input_char_pressed('4'):
			TICK_SPEED = 4
		
		if CURSOR['tile']['x'] > constants.MAP_VIEW_WIDTH - 5:
			camera.set_pos(camera.X + (CURSOR['tile']['x'] - (constants.MAP_VIEW_WIDTH - 5)), camera.Y)
		
		elif CURSOR['tile']['x'] <= 5:
			camera.set_pos(camera.X + (CURSOR['tile']['x'] - 5), camera.Y)
		
		if CURSOR['tile']['y'] > constants.MAP_VIEW_HEIGHT - 5:
			camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - (constants.MAP_VIEW_HEIGHT - 5)))
		
		elif CURSOR['tile']['y'] <= 5:
			camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - 5))
		
		if controls.get_input_char_pressed(' '):
			if MODE == 'strategy':
				MODE = 'normal'
			else:
				MODE = 'strategy'
		
		if MODE == 'strategy':
			nodes.handle_keyboard_input(PLAYER)
	
	return True

def handle_mouse_movement(x, y, **kwargs):
	entities.trigger_event(CURSOR, 'set_position', x=x, y=y)
	
	if MODE == 'strategy':
		nodes.handle_mouse_movement(PLAYER, x, y, x+camera.X, y+camera.Y)

def handle_mouse_pressed(x, y, button):
	if MODE == 'strategy':
		nodes.handle_mouse_pressed(PLAYER, x, y, button)
	
	elif MODE == 'normal':
		_c_x = (camera.X+x) - (constants.MAP_VIEW_WIDTH/2)
		_c_y = (camera.Y+y) - (constants.MAP_VIEW_HEIGHT/2)
		
		if button == 1:
			camera.set_pos(_c_x, _c_y)

def logic():
	if MODE == 'normal':
		for entity_id in entities.get_entity_group('life'):
			entities.trigger_event(entities.get_entity(entity_id), 'logic')

def tick():
	if MODE == 'strategy':
		return
	
	if PLAYER['node_path']['path']:
		_ticks_per_tick = TICK_SPEED
	else:
		_ticks_per_tick = 1
	
	for _ in range(_ticks_per_tick):
		for entity_id in entities.get_entity_group('life'):
			entities.trigger_event(entities.get_entity(entity_id), 'tick')

def draw():
	entities.trigger_event(CURSOR, 'draw')
	
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	ui.draw_status_bar(planning=MODE == 'strategy',
	                   executing=MODE == 'normal' and PLAYER['node_path']['path'])
	ui.draw_life_labels()
	ui.draw_node_path(PLAYER)
	
	if '--fps' in sys.argv:
		ui.draw_fps()
	
	events.trigger_event('post_process')
	display.blit_surface('nodes')
	display.blit_surface('life')
	display.blit_surface('ui')
	events.trigger_event('draw')

def main():
	global CURSOR, PLAYER
	
	PLAYER = life.human(150, 150, 'Tester Toaster')
	CURSOR = entities.create_entity(group='systems')
	
	ui.boot(PLAYER)
	framework.tile.register(CURSOR, surface='ui')
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('camera', camera.update)
	events.register_event('tick', tick)
	
	_t = time.time()
	mapgen.swamp(400, 400)	
	print 'Took:', time.time()-_t
	
	pathfinding.setup(mapgen.LEVEL_WIDTH, mapgen.LEVEL_HEIGHT, [])	
	
	display.create_surface('tiles', width=mapgen.LEVEL_WIDTH, height=mapgen.LEVEL_HEIGHT)
	maps.render_map(mapgen.TILE_MAP, mapgen.LEVEL_WIDTH, mapgen.LEVEL_HEIGHT)	
	
	camera.set_limits(0, 0, mapgen.LEVEL_WIDTH-constants.MAP_VIEW_WIDTH, mapgen.LEVEL_HEIGHT-constants.MAP_VIEW_HEIGHT)
	
	while loop():
		events.trigger_event('cleanup')
		
		continue
	
	framework.shutdown()

def loop():
	global FPSS
	
	events.trigger_event('input')
	logic()
	events.trigger_event('tick')
	
	events.trigger_event('camera')
	
	if not handle_input():
		return False
	
	draw()
	
	return True

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
