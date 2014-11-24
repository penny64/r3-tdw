from framework import display, events, numbers, controls

import libtcodpy as tcod

import constants

TEXT = 'Insurgence: ', 'Shadow Operation'
FADE_ALPHA = 0.0
MENU_ITEM_SELECTED = 1


def create():
	display.create_surface('background')
	
	_noise = tcod.noise_new(3)
	_zoom = .5
	
	for y in range(constants.WINDOW_HEIGHT):
		for x in range(constants.WINDOW_WIDTH):
			_noise_values = [(_zoom * x / (constants.WINDOW_WIDTH)),
			                 (_zoom * y / (constants.WINDOW_HEIGHT))]
			_height = 1 - tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_SIMPLEX)
			
			if _height > .5:
				_height = (_height - .5) / .5
				_r, _g, _b = 100 * _height, 60 * _height, 60 * _height
			
			else:
				_height = 1 - (_height / .5)
				_r, _g, _b = 60 * _height, 60 * _height, 100 * _height
			
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
	display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(''.join(TEXT)) / 2),
	                     12, TEXT[0],
	                     fore_color=(200 * FADE_ALPHA, 200 * FADE_ALPHA, 200 * FADE_ALPHA))
	
	display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(TEXT[1]) / 2),
	                     13, TEXT[1].upper(),
	                     fore_color=(200 * FADE_ALPHA, 60 * FADE_ALPHA, 80 * FADE_ALPHA))
	
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
