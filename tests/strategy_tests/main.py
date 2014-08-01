from framework import entities, controls, display, events, worlds, tile, timers, movement, pathfinding, stats

import framework
import constants
import nodes

import time

PLAYER = None
PAUSED = True


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
	global PAUSED
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	if controls.get_input_ord_pressed(ord(' ')):
		if PAUSED:
			PAUSED = False
		else:
			PAUSED = True
	
	if PAUSED:
		nodes.handle_keyboard_input(PLAYER)
	
	return True

def handle_mouse_pressed(x, y, button):
	if PAUSED:
		nodes.handle_mouse_pressed(PLAYER, x, y, button)

def logic():
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'logic')

def draw():
	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw')
	
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw')
	
	display.blit_surface('level')
	display.blit_surface('nodes')
	display.blit_surface('life')
	events.trigger_event('draw')

def main():
	global PLAYER
	
	pathfinding.setup(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, [])
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	
	for y in range(constants.WINDOW_HEIGHT):
		for x in range(constants.WINDOW_WIDTH):
			display.write_char('level', x, y, ' ', back_color=(20, 20, 20))
	
	display.blit_background('level')
	
	PLAYER = create_player()
	
	while loop():
		events.trigger_event('cleanup')
		
		continue
	
	framework.shutdown()

def loop():
	global PAUSED
	
	events.trigger_event('input')
	
	if not handle_input():
		return False
	
	logic()
	
	if not PAUSED:
		events.trigger_event('tick')
		
		if not PLAYER['node_path']['path']:
			PAUSED = True
	
	draw()
	
	return True

if __name__ == '__main__':
	framework.init()
	
	worlds.create('test')
	entities.create_entity_group('life')
	entities.create_entity_group('nodes')
	display.create_surface('level')
	display.create_surface('nodes')
	display.create_surface('life')
	
	framework.run(main)
