import libtcodpy as tcod

import framework

import constants

import logging
import numpy
import copy


def shutdown():
	logging.debug('Display shutdown: Stub')

SURFACES = {}
SCREEN = {}
BACKGROUND = None
DRAW_CALLS = []


def boot():
	global SCREEN
	
	framework.events.register_event('draw', blit)
	
	tcod.console_init_root(constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT, constants.WINDOW_TITLE, renderer=tcod.RENDERER_GLSL)
	tcod.console_set_keyboard_repeat(200, 0)
	tcod.sys_set_fps(constants.FPS)	
	tcod.mouse_show_cursor(constants.SHOW_MOUSE)
	
	SCREEN['c'] = numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int32)
	SCREEN['d'] = '0'*(constants.WINDOW_HEIGHT*constants.WINDOW_WIDTH)
	SCREEN['r'] = []
	
	SCREEN['f'] = []
	SCREEN['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SCREEN['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SCREEN['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	
	SCREEN['b'] = []
	SCREEN['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SCREEN['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SCREEN['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))

def create_surface(surface_name):
	SURFACES[surface_name] = {}
	SURFACES[surface_name]['c'] = numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int32)
	SURFACES[surface_name]['r'] = []
	
	SURFACES[surface_name]['f'] = []
	SURFACES[surface_name]['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['f'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['fo'] = []
	SURFACES[surface_name]['fo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['fo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['fo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	
	SURFACES[surface_name]['b'] = []
	SURFACES[surface_name]['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['b'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['bo'] = []
	SURFACES[surface_name]['bo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['bo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))
	SURFACES[surface_name]['bo'].append(numpy.zeros((constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH), dtype=numpy.int16))

def delete_surface(surface_name):
	del SURFACES[surface_name]

def get_surface(surface_name):
	return SURFACES[surface_name]

def clear_rect(surface_name, x, y, width, height):
	SURFACES[surface_name]['r'].append((x, y, x+width, y+height))

def _set_char(surface_name, x, y, char, fore_color, back_color):
	SURFACES[surface_name]['c'][y][x] = ord(char)
	
	SURFACES[surface_name]['fo'][0][y][x] = fore_color[0]
	SURFACES[surface_name]['fo'][1][y][x] = fore_color[1]
	SURFACES[surface_name]['fo'][2][y][x] = fore_color[2]
	SURFACES[surface_name]['f'][0][y][x] = fore_color[0]
	SURFACES[surface_name]['f'][1][y][x] = fore_color[1]
	SURFACES[surface_name]['f'][2][y][x] = fore_color[2]
	
	if back_color:
		SURFACES[surface_name]['bo'][0][y][x] = back_color[0]
		SURFACES[surface_name]['bo'][1][y][x] = back_color[1]
		SURFACES[surface_name]['bo'][2][y][x] = back_color[2]
		SURFACES[surface_name]['b'][0][y][x] = back_color[0]
		SURFACES[surface_name]['b'][1][y][x] = back_color[1]
		SURFACES[surface_name]['b'][2][y][x] = back_color[2]

def _write_char(surface_name, x, y, c, fore_color, back_color):
	SURFACES[surface_name]['r'].append((x, y, x+1, y+1))
	
	yield surface_name, x, y, c, fore_color, back_color

def _write_string(surface_name, x, y, string, fore_color, back_color):
	SURFACES[surface_name]['r'].append((x, y, x+len(string), y+1))
	
	_i = 0
	
	for c in string:
		yield surface_name, x+_i, y, c, fore_color, back_color
		
		_i += 1

def write_char(surface_name, x, y, c, fore_color=(200, 200, 200), back_color=None):
	if SCREEN['d'][x+(y*constants.WINDOW_WIDTH)] == c:
		return False
	
	DRAW_CALLS.append(_write_char(surface_name, x, y, c, fore_color, back_color))

def write_string(surface_name, x, y, string, fore_color=(200, 200, 200), back_color=None):
	if SCREEN['d'][x+(y*constants.WINDOW_WIDTH):x+(y*constants.WINDOW_WIDTH)+len(string)] == string:
		return False
	
	DRAW_CALLS.append(_write_string(surface_name, x, y, string, fore_color, back_color))

def write_char_direct(x, y, char, fore_color, back_color):
	SCREEN['c'][y][x] = ord(char)
		
	#SCREEN['fo'][0][y][x] = fore_color[0]
	#SCREEN['fo'][1][y][x] = fore_color[1]
	#SCREEN['fo'][2][y][x] = fore_color[2]
	SCREEN['f'][0][y][x] = fore_color[0]
	SCREEN['f'][1][y][x] = fore_color[1]
	SCREEN['f'][2][y][x] = fore_color[2]
	
	if back_color:
		#SCREEN['bo'][0][y][x] = back_color[0]
		#SCREEN['bo'][1][y][x] = back_color[1]
		#SCREEN['bo'][2][y][x] = back_color[2]
		SCREEN['b'][0][y][x] = back_color[0]
		SCREEN['b'][1][y][x] = back_color[1]
		SCREEN['b'][2][y][x] = back_color[2]	

def shade_surface_fore(surface_name, shader):
	_surface = SURFACES[surface_name]
	
	#_f0 = _surface['f'][0] * shader
	#_f1 = _surface['f'][1] * shader
	#_f2 = _surface['f'][2] * shader
	
	SCREEN['f'][0] *= shader
	SCREEN['f'][1] *= shader
	SCREEN['f'][2] *= shader

def shade_surface_back(surface_name, shader):
	_surface = SURFACES[surface_name]
	
	#_f0 = _surface['b'][0] * shader
	#_f1 = _surface['b'][1] * shader
	#_f2 = _surface['b'][2] * shader
	
	SCREEN['b'][0] *= shader
	SCREEN['b'][1] *= shader
	SCREEN['b'][2] *= shader
	
	#print 'SHADE'

def _clear_screen():
	for rect in SCREEN['r']:
		for y in range(rect[1], rect[3]):
			for x in range(rect[0], rect[2]):
				SCREEN['c'][y][x] = BACKGROUND['c'][y][x]
				
				_pre = SCREEN['d'][:x+(y*constants.WINDOW_WIDTH)]
				_post = SCREEN['d'][x+(y*constants.WINDOW_WIDTH)+1:]
				SCREEN['d'] = _pre+'0'+_post
				
				SCREEN['f'][0][y][x] = BACKGROUND['f'][0][y][x]
				SCREEN['f'][1][y][x] = BACKGROUND['f'][1][y][x]
				SCREEN['f'][2][y][x] = BACKGROUND['f'][2][y][x]
				
				if BACKGROUND['b'][0][y][x] or BACKGROUND['b'][1][y][x] or BACKGROUND['b'][2][y][x]:
					SCREEN['b'][0][y][x] = BACKGROUND['b'][0][y][x]
					SCREEN['b'][1][y][x] = BACKGROUND['b'][1][y][x]
					SCREEN['b'][2][y][x] = BACKGROUND['b'][2][y][x]
	
	SCREEN['r'] = []

def _blit_surface(src_surface, dst_surface, clear=True):
	_i = 0
	
	for rect in src_surface['r']:
		if clear:
			SCREEN['r'].append(rect[:])
		
		for y in range(rect[1], rect[3]):
			for x in range(rect[0], rect[2]):
				_char = src_surface['c'][y][x]
				
				dst_surface['c'][y][x] = _char
				
				if clear:
					src_surface['c'][y][x] = 0
				
				_pre = SCREEN['d'][:x+(y*constants.WINDOW_WIDTH)]
				_post = SCREEN['d'][x+(y*constants.WINDOW_WIDTH)+1:]
				SCREEN['d'] = _pre+chr(_char)+_post
				
				dst_surface['f'][0][y][x] = src_surface['f'][0][y][x]
				dst_surface['f'][1][y][x] = src_surface['f'][1][y][x]
				dst_surface['f'][2][y][x] = src_surface['f'][2][y][x]
				
				if src_surface['b'][0][y][x] or src_surface['b'][1][y][x] or src_surface['b'][2][y][x]:
					dst_surface['b'][0][y][x] = src_surface['b'][0][y][x]
					dst_surface['b'][1][y][x] = src_surface['b'][1][y][x]
					dst_surface['b'][2][y][x] = src_surface['b'][2][y][x]
	
	src_surface['r'] = []

def screenshot(name):
	tcod.sys_save_screenshot(name)

def blit_surface(surface_name, clear=True):
	_blit_surface(SURFACES[surface_name], SCREEN, clear=clear)

def reblit_whole_surface(surface_name):
	SURFACES[surface_name]['r'].append((0, 0, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
	_blit_surface(SURFACES[surface_name], SCREEN, clear=False)

def blit_background(surface_name):
	global BACKGROUND
	
	BACKGROUND = SURFACES[surface_name]
	clear_rects(surface_name, [(0, 0, get_size()[0], get_size()[1])])
	
	_blit_surface(BACKGROUND, SCREEN, clear=False)

def clear_screen():
	SCREEN['d'] = '0'*(constants.WINDOW_HEIGHT*constants.WINDOW_WIDTH)
	
	if BACKGROUND:
		BACKGROUND['d'] = '0'*(constants.WINDOW_HEIGHT*constants.WINDOW_WIDTH)

def get_color_at(surface_name, x, y):
	return ((SURFACES[surface_name]['f'][0][y][x], SURFACES[surface_name]['f'][1][y][x], SURFACES[surface_name]['f'][2][y][x]),
	        (SURFACES[surface_name]['b'][0][y][x], SURFACES[surface_name]['b'][1][y][x], SURFACES[surface_name]['b'][2][y][x]))

def clear_rects(surface_name, rects):
	SURFACES[surface_name]['r'].extend(rects)

def update():
	global DRAW_CALLS
	
	for call in DRAW_CALLS[:constants.MAX_DRAW_CALLS_PER_FRAME]:
		_draw_list = list(call)
		
		if not _draw_list:
			continue
		
		for draw in _draw_list:
			surface_name, x, y, c, fore_color, back_color = draw
		
			_set_char(surface_name, x, y, c, fore_color=fore_color, back_color=back_color)
	
	DRAW_CALLS = DRAW_CALLS[constants.MAX_DRAW_CALLS_PER_FRAME:]
	
	tcod.console_set_default_background(0, tcod.dark_gray)
	tcod.console_fill_char(0, SCREEN['c'])
	tcod.console_fill_background(0, SCREEN['b'][0], SCREEN['b'][1], SCREEN['b'][2])
	tcod.console_fill_foreground(0, SCREEN['f'][0], SCREEN['f'][1], SCREEN['f'][2])
	
	_clear_screen()

def blit():
	update()
	tcod.console_flush()

def get_size():
	return constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT

def get_fps():
	return tcod.sys_get_fps()

def get_max_fps():
	return constants.FPS
