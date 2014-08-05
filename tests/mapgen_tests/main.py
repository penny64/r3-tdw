from framework import entities, controls, display, events, worlds, tile, timers, movement, pathfinding, stats, numbers

import framework

import post_processing
import constants
import mapgen
import camera
import nodes
import maps

import numpy
import time
import sys

FPSS = 0
CURSOR = None
MODE = 'strategy'


def create_player():
	_entity = entities.create_entity(group='life')
	
	tile.register(_entity, surface='life')
	movement.register(_entity)
	timers.register(_entity)
	stats.register(_entity, 10, 10, 10, 5)
	nodes.register(_entity)
	
	entities.trigger_event(_entity, 'set_position', x=5, y=5)
	
	return _entity

def handle_input():
	global MODE
	
	if MODE in ['normal', 'strategy']:
		if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
			if MODE == 'strategy':
				MODE = 'normal'
			else:
				return False
		
		if CURSOR['tile']['x'] > constants.MAP_VIEW_WIDTH - 5:
			camera.set_pos(camera.X + (CURSOR['tile']['x'] - (constants.MAP_VIEW_WIDTH - 5)), camera.Y)
		
		elif CURSOR['tile']['x'] <= 5:
			camera.set_pos(camera.X + (CURSOR['tile']['x'] - 5), camera.Y)
		
		if CURSOR['tile']['y'] > constants.MAP_VIEW_HEIGHT - 5:
			camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - (constants.MAP_VIEW_HEIGHT - 5)))
		
		elif CURSOR['tile']['y'] <= 5:
			camera.set_pos(camera.X, camera.Y + (CURSOR['tile']['y'] - 5))
		
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

def draw():
	entities.trigger_event(CURSOR, 'draw')
	
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	events.trigger_event('post_process')
	
	if MODE == 'strategy':
		display.blit_surface('nodes')
	
	display.blit_surface('life')
	display.blit_surface('ui')
	events.trigger_event('draw')

def main():
	global CURSOR, PLAYER
	
	PLAYER = create_player()
	CURSOR = entities.create_entity(group='systems')
	
	framework.tile.register(CURSOR, surface='ui')
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('tick', camera.update)
	
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
	events.trigger_event('tick')
	
	if not handle_input():
		return False
	
	draw()
	
	if '--fps' in sys.argv:
		FPSS += 1
		
		if FPSS == 60:
			print display.get_fps()
			FPSS = 0
	
	return True

if __name__ == '__main__':
	framework.init()
	
	worlds.create('test')
	
	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('life')
	entities.create_entity_group('systems')
	entities.create_entity_group('ui')
	entities.create_entity_group('nodes')

	display.create_surface('life')
	display.create_surface('nodes')
	display.create_surface('ui')
	display.set_clear_surface('ui', 'tiles')
	
	post_processing.start()
	
	framework.run(main)
