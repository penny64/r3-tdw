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
	
	events.register_event('mouse_moved', handle_mouse_moved)
	
	_grid = {}
	_color_map = {}
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_grid[x, y] = {'owned_by': None,
			               'is_ownable': x == 6 and y == 6,
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

def draw_map_grid():
	display.blit_surface_viewport('map', 0, 0, constants.STRAT_MAP_WIDTH, constants.STRAT_MAP_HEIGHT)
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_tile = MAP['grid'][x, y]
			
			if x == controls.get_mouse_pos()[0]/constants.MAP_CELL_SPACE and y == controls.get_mouse_pos()[1]/constants.MAP_CELL_SPACE:
				_hover = True
			
			else:
				_hover = False
			
			for _x in range(constants.MAP_CELL_SPACE):
				for _y in range(constants.MAP_CELL_SPACE):
					_d_x = (x * constants.MAP_CELL_SPACE) + _x
					_d_y = (y * constants.MAP_CELL_SPACE) + _y
					_back_color = None
					
					if _tile['is_ownable']:
						_fore_color = (180, 180, 180)
						_back_color = (100, 100, 100)
						
						if not _x + _y:
							if _hover:
								_char = chr(201)
								_fore_color = (255, 255, 255)
							
							else:
								_char = chr(218)
						
						elif _x == constants.MAP_CELL_SPACE-1 and not _y:
							if _hover:
								_char = chr(187)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(191)
							
						elif not _x and _y == constants.MAP_CELL_SPACE-1:
							if _hover:
								_char = chr(200)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(192)
						
						elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
							if _hover:
								_char = chr(188)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(217)
						
						elif _y > 0 and _y < constants.MAP_CELL_SPACE-1 and (not _x or _x == constants.MAP_CELL_SPACE-1):
							_char = chr(179)
						
						elif _x > 0 and _x < constants.MAP_CELL_SPACE-1 and (not _y or _y == constants.MAP_CELL_SPACE-1):
							_char = chr(196)
						
						else:
							_char = '.'
							_back_color = (120, 120, 120)
						
						display.write_char('map_markers',
							               _d_x,
							               _d_y,
							               _char,
						                   fore_color=_fore_color,
						                   back_color=_back_color)
					
					else:
						if _hover:
							if not _x + _y:
								_char = chr(201)
							
							elif _x == constants.MAP_CELL_SPACE-1 and not _y:
								_char = chr(187)
								
							elif not _x and _y == constants.MAP_CELL_SPACE-1:
								_char = chr(200)
							
							elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
								_char = chr(188)
							
							else:
								_char = ' '
							
							_color = display.get_color_at('map', _d_x, _d_y)[1]
							display.write_char('map_markers',
								               _d_x,
								               _d_y,
								               _char,
							                   back_color=(int(round(_color[0]*1.4)), int(round(_color[1]*1.4)), int(round(_color[2]*1.4))))

def draw():
	draw_map_grid()
	
	display.blit_surface('map_markers')
	
	events.trigger_event('draw')

def loop():
	if not handle_input():
		return False
	
	draw()
	
	return True
