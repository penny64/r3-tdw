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

def create_surface(surface_name, width=constants.WINDOW_WIDTH, height=constants.WINDOW_HEIGHT):
	SURFACES[surface_name] = {}
	SURFACES[surface_name]['c'] = numpy.zeros((height, width), dtype=numpy.int32)
	SURFACES[surface_name]['r'] = []
	SURFACES[surface_name]['cr'] = []
	SURFACES[surface_name]['d'] = '0'*(width*height)
	SURFACES[surface_name]['bg'] = None
	SURFACES[surface_name]['start_x'] = 0
	SURFACES[surface_name]['start_y'] = 0
	SURFACES[surface_name]['width'] = width
	SURFACES[surface_name]['height'] = height
	
	SURFACES[surface_name]['f'] = []
	SURFACES[surface_name]['f'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['f'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['f'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['fo'] = []
	SURFACES[surface_name]['fo'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['fo'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['fo'].append(numpy.zeros((height, width), dtype=numpy.int16))
	
	SURFACES[surface_name]['b'] = []
	SURFACES[surface_name]['b'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['b'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['b'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['bo'] = []
	SURFACES[surface_name]['bo'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['bo'].append(numpy.zeros((height, width), dtype=numpy.int16))
	SURFACES[surface_name]['bo'].append(numpy.zeros((height, width), dtype=numpy.int16))

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
	
	SCREEN['f'][0][y][x] = fore_color[0]
	SCREEN['f'][1][y][x] = fore_color[1]
	SCREEN['f'][2][y][x] = fore_color[2]
	
	if back_color:
		SCREEN['b'][0][y][x] = back_color[0]
		SCREEN['b'][1][y][x] = back_color[1]
		SCREEN['b'][2][y][x] = back_color[2]	

def shade_surface_fore(surface_name, shader, width, height):
	_surface = SURFACES[surface_name]
	_start_x = _surface['start_x']
	_start_y = _surface['start_y']
	_surface['f'][0][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['fo'][0][_start_y:_start_y+height, _start_x:_start_x+width]
	_surface['f'][1][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['fo'][1][_start_y:_start_y+height, _start_x:_start_x+width]
	_surface['f'][2][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['fo'][2][_start_y:_start_y+height, _start_x:_start_x+width]
	
	_f0 = _surface['fo'][0][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	_f1 = _surface['fo'][1][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	_f2 = _surface['fo'][2][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	
	SCREEN['f'][0][0:height, 0:width] = _f0
	SCREEN['f'][1][0:height, 0:width] = _f1
	SCREEN['f'][2][0:height, 0:width] = _f2

def shade_surface_back(surface_name, shader, width, height):
	_surface = SURFACES[surface_name]
	_start_x = _surface['start_x']
	_start_y = _surface['start_y']
	_surface['b'][0][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['bo'][0][_start_y:_start_y+height, _start_x:_start_x+width]
	_surface['b'][1][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['bo'][1][_start_y:_start_y+height, _start_x:_start_x+width]
	_surface['b'][2][_start_y:_start_y+height, _start_x:_start_x+width] = _surface['bo'][2][_start_y:_start_y+height, _start_x:_start_x+width]
	
	_f0 = _surface['bo'][0][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	_f1 = _surface['bo'][1][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	_f2 = _surface['bo'][2][_start_y:_start_y+height, _start_x:_start_x+width] * shader
	
	SCREEN['b'][0][0:height, 0:width] = _f0.clip(0, 255)
	SCREEN['b'][1][0:height, 0:width] = _f1.clip(0, 255)
	SCREEN['b'][2][0:height, 0:width] = _f2.clip(0, 255)

def _clear_screen():
	for rect in SCREEN['r']:
		if len(rect) == 5:
			_background = SURFACES[rect[4]]
		else:
			_background = BACKGROUND
		
		for y in range(rect[1], rect[3]):
			for x in range(rect[0], rect[2]):
				SCREEN['c'][y][x] = _background['c'][y][x]
				
				_pre = SCREEN['d'][:x+(y*constants.WINDOW_WIDTH)]
				_post = SCREEN['d'][x+(y*constants.WINDOW_WIDTH)+1:]
				SCREEN['d'] = _pre+'0'+_post
				
				SCREEN['f'][0][y][x] = _background['f'][0][y][x]
				SCREEN['f'][1][y][x] = _background['f'][1][y][x]
				SCREEN['f'][2][y][x] = _background['f'][2][y][x]
				
				if _background['b'][0][y][x] or _background['b'][1][y][x] or _background['b'][2][y][x]:
					SCREEN['b'][0][y][x] = _background['b'][0][y][x]
					SCREEN['b'][1][y][x] = _background['b'][1][y][x]
					SCREEN['b'][2][y][x] = _background['b'][2][y][x]
	
	SCREEN['r'] = []

def _blit_surface(src_surface, dst_surface, clear=True, src_name=None):
	for rect in src_surface['r']:
		if clear and src_name:
			_rect = list(rect[:])
			_rect.append(src_name)
			
			SCREEN['r'].append(_rect)
		
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

def _blit_surface_viewport(src_surface, dst_surface, start_x, start_y, width, height):
	dst_surface['f'][0][0:height, 0:width] = src_surface['f'][0][start_y:start_y+height, start_x:start_x+width]
	dst_surface['f'][1][0:height, 0:width] = src_surface['f'][1][start_y:start_y+height, start_x:start_x+width]
	dst_surface['f'][2][0:height, 0:width] = src_surface['f'][2][start_y:start_y+height, start_x:start_x+width]
	dst_surface['b'][0][0:height, 0:width] = src_surface['b'][0][start_y:start_y+height, start_x:start_x+width]
	dst_surface['b'][1][0:height, 0:width] = src_surface['b'][1][start_y:start_y+height, start_x:start_x+width]
	dst_surface['b'][2][0:height, 0:width] = src_surface['b'][2][start_y:start_y+height, start_x:start_x+width]

def blit_surface(surface_name, clear=True):
	_blit_surface(SURFACES[surface_name], SCREEN, clear=clear, src_name=surface_name)

def blit_surface_viewport(surface_name, x, y, width, height):
	_blit_surface_viewport(SURFACES[surface_name], SCREEN, x, y, width, height)

def set_clear_surface(surface_name, background_surface_name):
	SURFACES[surface_name]['bg'] = background_surface_name

def set_surface_camera(surface_name, x, y):
	_surface = SURFACES[surface_name]
	
	_surface['start_x'] = x
	_surface['start_y'] = y

def clear_surface(surface_name, background_surface_name):
	_surface = SURFACES[surface_name]
	_background_surface = SURFACES[background_surface_name]
	
	for rect in _surface['cr']:
		for y in range(rect[1], rect[3]):
			for x in range(rect[0], rect[2]):
				_surface['c'][y][x] = _background_surface['c'][y][x]
				
				_pre = _surface['d'][:x+(y*constants.WINDOW_WIDTH)]
				_post = _surface['d'][x+(y*constants.WINDOW_WIDTH)+1:]
				_surface['d'] = _pre+'0'+_post
				
				_surface['f'][0][y][x] = _background_surface['f'][0][y][x]
				_surface['f'][1][y][x] = _background_surface['f'][1][y][x]
				_surface['f'][2][y][x] = _background_surface['f'][2][y][x]
				
				if _background_surface['b'][0][y][x] or _background_surface['b'][1][y][x] or _background_surface['b'][2][y][x]:
					_surface['b'][0][y][x] = _background_surface['b'][0][y][x]
					_surface['b'][1][y][x] = _background_surface['b'][1][y][x]
					_surface['b'][2][y][x] = _background_surface['b'][2][y][x]
	
	_surface['cr'] = []

def screenshot(name):
	tcod.sys_save_screenshot(name)

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
