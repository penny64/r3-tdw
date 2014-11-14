from framework import display, worlds, entities, events, controls

import constants
import random

MAP = None
_DEBUG_ORD = 177


def create():
	global MAP
	
	worlds.create('strategy')
	
	display.create_surface('map', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_markers', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	
	_grid = {}
	_color_map = {}
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_grid[x, y] = {'owned_by': None,
			               'is_ownable': x == 6 and y == 6,
			               'squads': []}
	
	for x in range(constants.STRAT_MAP_WIDTH):
		for y in range(constants.STRAT_MAP_HEIGHT):
			_color_map[x, y] = random.choice([constants.SATURATED_GREEN_1,
			                                  constants.SATURATED_GREEN_2,
			                                  constants.SATURATED_GREEN_3])
			
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

def draw_map_grid():
	display.blit_surface_viewport('map', 0, 0, constants.STRAT_MAP_WIDTH, constants.STRAT_MAP_HEIGHT)
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_tile = MAP['grid'][x, y]
			
			for _x in range(constants.MAP_CELL_SPACE):
				for _y in range(constants.MAP_CELL_SPACE):
					_d_x = (x * constants.MAP_CELL_SPACE) + _x
					_d_y = (y * constants.MAP_CELL_SPACE) + _y
					
					if _tile['is_ownable']:
						if not _x + _y:
							_char = chr(201)
						
						elif _x == constants.MAP_CELL_SPACE-1 and not _y:
							_char = chr(187)
							
						elif not _x and _y == constants.MAP_CELL_SPACE-1:
							_char = chr(200)
						
						elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
							_char = chr(188)
						
						elif _y > 0 and _y < constants.MAP_CELL_SPACE-1 and (not _x or _x == constants.MAP_CELL_SPACE-1):
							_char = chr(179)
						
						elif _x > 0 and _x < constants.MAP_CELL_SPACE-1 and (not _y or _y == constants.MAP_CELL_SPACE-1):
							_char = chr(196)
						
						else:
							_char = '.'
						
						display.write_char('map_markers',
							               _d_x,
							               _d_y,
							               _char,
						                   fore_color=(255, 255, 255))
					
					else:
						display.write_char('map_markers',
							               _d_x,
							               _d_y,
							               ' ')

def draw():
	draw_map_grid()
	
	display.blit_surface('map_markers')
	
	events.trigger_event('draw')

def loop():
	if not handle_input():
		return False
	
	draw()
	
	return True
