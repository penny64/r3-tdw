from framework import display, worlds, entities, events, controls

import ui_strategy
import constants
import worldgen

import random

MAP = None
_DEBUG_ORD = 177


def create():
	global MAP
	
	worlds.create('strategy')
	
	display.create_surface('map', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_markers', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_squads', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	
	events.register_event('mouse_moved', handle_mouse_moved)
	
	entities.create_entity_group('life', static=True)
	entities.create_entity_group('items', static=True)
	entities.create_entity_group('factions', static=True)
	entities.create_entity_group('squads', static=True)
	
	worldgen.generate()
	
	_grid = {}
	_color_map = {}
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_grid[x, y] = {'owned_by': None,
			               'is_ownable': False,
			               'squads': []}
	
	for x in range(constants.STRAT_MAP_WIDTH):
		for y in range(constants.STRAT_MAP_HEIGHT):
			_color_map[x, y] = random.choice([constants.FOREST_GREEN_1,
			                                  constants.FOREST_GREEN_2,
			                                  constants.FOREST_GREEN_3])
			
			display._set_char('map', x, y, ' ', (0, 0, 0), _color_map[x, y])
	
	MAP = {'grid': _grid,
	       'color_map': _color_map}

def handle_input():
	global _DEBUG_ORD
	
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	if controls.get_input_char_pressed('z'):
		_DEBUG_ORD -= 1
	
	elif controls.get_input_char_pressed('x'):
		_DEBUG_ORD += 1
	
	return True

def handle_mouse_moved(x, y, dx, dy):
	return

def draw():
	ui_strategy.draw_map_grid()
	ui_strategy.draw_squads()
	
	display.blit_surface('map_markers')
	display.blit_surface('map_squads')
	
	events.trigger_event('draw')

def loop():
	if not handle_input():
		return False
	
	draw()
	
	return True
