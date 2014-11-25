from framework import display, events, numbers, controls

import libtcodpy as tcod

import constants
import random

TEXT = 'Insurgence: ', 'Shadow Operation'
FADE_ALPHA = 0.0
MENU_ITEM_SELECTED = 1
NOISE = None
ZOOM = .5
SPARK_SIZE = 8.0
REDRAW_RATE = 0.0


def create():
	global NOISE
	
	display.create_surface('background')
	
	NOISE = tcod.noise_new(2,h=tcod.NOISE_DEFAULT_HURST, random=tcod.random_new())
	
	paint_map(initial=True)

def paint_map(initial=False):
	global SPARK_SIZE, REDRAW_RATE
	
	if REDRAW_RATE:
		REDRAW_RATE -= 1
		
		return
	
	REDRAW_RATE = 3.0
	
	if initial:
		_x_range = 0, constants.WINDOW_WIDTH
		_y_range = 0, constants.WINDOW_HEIGHT
	
	else:
		_x_range = 30, 50
		_y_range = 5, 20
		
	SPARK_SIZE = numbers.clip(SPARK_SIZE + random.uniform(-3, 3), 6.0, 12.0)
		
	for y in range(_y_range[0], _y_range[1]):
		for x in range(_x_range[0], _x_range[1]):
			_noise_values = [(ZOOM * x / (constants.WINDOW_WIDTH)),
			                 (ZOOM * y / (constants.WINDOW_HEIGHT))]
			_height = 1 - tcod.noise_get_turbulence(NOISE, _noise_values, tcod.NOISE_SIMPLEX)
			_dist_to_crosshair = numbers.clip((abs(y - 12) * (abs(x - 38))) / (SPARK_SIZE + random.uniform(-3.5, 1)), 0, 1)
			#_height *= _dist_to_crosshair
			
			_crosshair_mod = abs((_dist_to_crosshair - 1))
			
			#if not initial and not _crosshair_mod:
			#	continue
			
			if _height > .4:
				_height = (_height - .4) / .4
				_r, _g, _b = numbers.clip(30 * _height, 20, 255), 50 * _height, numbers.clip(30 * _height, 30, 255)
			
			else:
				_r, _g, _b = 20, 0, 30
				#_height = 1 - (_height / .5)
				#_r, _g, _b = 60 * _height, 60 * _height, 100 * _height
			
			_r += 80 * _crosshair_mod
			
			display._set_char('background', x, y, ' ', (0, 0, 0), (_r, _g, _b))
	
	display.blit_background('background')

def handle_input():
	global MENU_ITEM_SELECTED
	
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	if controls.get_input_char_pressed('s'):
		MENU_ITEM_SELECTED += 1
	
	elif controls.get_input_char_pressed('w'):
		MENU_ITEM_SELECTED -= 1	
	
	MENU_ITEM_SELECTED = numbers.clip(MENU_ITEM_SELECTED, 0, 2)
	
	if controls.get_input_char_pressed('\r'):
		return False
	
	return True

def draw():
	#Title
	#display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(''.join(TEXT)) / 2),
	#                     12, TEXT[0],
	#                     fore_color=(200 * FADE_ALPHA, 200 * FADE_ALPHA, 200 * FADE_ALPHA))
	_i = 0
	for c in TEXT[0]:
		_alpha = numbers.clip(FADE_ALPHA * numbers.clip(16 - _i, 7, 16) / SPARK_SIZE, 0, 1)
		
		display.write_char('text', ((constants.WINDOW_WIDTH / 2) - (len(''.join(TEXT)) / 2)) + _i,
		                   12,
		                   c,
		                   fore_color=(200 * _alpha, 200 * _alpha, 200 * _alpha))
		
		_i += 1
	
	_i = 0
	for c in TEXT[1]:
		_alpha = numbers.clip(FADE_ALPHA * numbers.clip(18 - _i, 0, 18) / SPARK_SIZE, 0, 1)
		display.write_char('text', ((constants.WINDOW_WIDTH / 2) - (len(TEXT[1]) / 2)) + _i,
		                   13,
		                   c.upper(),
		                   fore_color=(200 * _alpha, 60 * _alpha, 80 * _alpha))
		
		_i += 1
	#display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(TEXT[1]) / 2),
	#                     13, TEXT[1].upper(),
	#                     fore_color=(200 * FADE_ALPHA, 60 * FADE_ALPHA, 80 * FADE_ALPHA))
	
	#Menu
	_i = 0
	for item in [('Continue', False), ('New', True), ('Quit', True)]:
		if item[1]:
			_fore_color = (200 * FADE_ALPHA, 200 * FADE_ALPHA, 200 * FADE_ALPHA)
		
		else:
			_fore_color = (100 * FADE_ALPHA, 100 * FADE_ALPHA, 100 * FADE_ALPHA)
		
		if MENU_ITEM_SELECTED == _i:
			_text = '> %s <' % item[0]
		
		else:
			_text = item[0]
		
		display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(_text) / 2),
			                 18 + _i,
			                 _text,
			                 fore_color=_fore_color)
		
		_i += 1
	
	paint_map()

	display.blit_surface_viewport('background', 0, 0, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
	display.blit_surface('text')

def tick():
	global FADE_ALPHA
	
	FADE_ALPHA = numbers.clip(FADE_ALPHA + .01, 0, 1)

def loop():
	if not handle_input():
		return False
	
	tick()
	draw()
	
	events.trigger_event('draw')
	return True
