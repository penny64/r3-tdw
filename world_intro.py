from framework import display, events, numbers

import constants
import random

COMPANY_STRING = 'flagsdev LLC.'
UNSCRAMBLE_TO = 0#len(COMPANY_STRING) - 1
WHITE_VALUE = 255
SUBTITLE_TEXT = 'presents...'
SUBTITLE_COLOR = 0


def create():
	display.create_surface('text')

def loop():
	global UNSCRAMBLE_TO, WHITE_VALUE, SUBTITLE_COLOR
	
	for i in range(len(COMPANY_STRING)):
		if i > UNSCRAMBLE_TO:
			_char = random.choice(COMPANY_STRING)
			_gray_color = int(round(255 * (UNSCRAMBLE_TO / i))) + random.randint(-15, 15)
			_fore_color = (_gray_color, _gray_color, _gray_color)
			
		else:
			_char = COMPANY_STRING[i]
			_r = numbers.clip(WHITE_VALUE - random.randint(0, 90), 0, 255)
			_g = _r
			_b = _r
			
			_fore_color = _r, _g, _b
		
		display.write_char('text', (constants.WINDOW_WIDTH / 2) + i - (len(COMPANY_STRING) / 2),
		                   (constants.WINDOW_HEIGHT / 2) - 1, _char, fore_color=_fore_color)
	
	display.write_string('text', (constants.WINDOW_WIDTH / 2) - (len(SUBTITLE_TEXT) / 2),
	                     (constants.WINDOW_HEIGHT / 2) + 1,
	                     SUBTITLE_TEXT,
	                     fore_color=(SUBTITLE_COLOR, SUBTITLE_COLOR, SUBTITLE_COLOR))
	
	if UNSCRAMBLE_TO > 6:
		SUBTITLE_COLOR = numbers.clip(SUBTITLE_COLOR + 2, 0, 255)
	
	if UNSCRAMBLE_TO > 25:
		WHITE_VALUE -= 2
		
		SUBTITLE_COLOR = numbers.clip(SUBTITLE_COLOR - 6, 0, 255)
	
	if UNSCRAMBLE_TO > 38:
		return False
	
	display.blit_surface('text')
	
	events.trigger_event('draw')
	
	UNSCRAMBLE_TO += .1
	
	return True