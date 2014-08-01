import libtcodpy as tcod

import numbers
import events

import sys


KEY = None
MOUSE = None
MOUSE_POS = (0, 0)
LAST_MOUSE_POS = (0, 0)
INPUT = {}


def boot():
	global KEY, MOUSE
	
	KEY = tcod.Key()
	MOUSE = tcod.Mouse()
	
	events.create_event('mouse_moved')
	events.create_event('mouse_pressed')
	events.create_event('mouse_held')

def handle_input():
	global MOUSE_POS, LAST_MOUSE_POS
	
	_mouse = tcod.mouse_get_status()
	_event = tcod.sys_check_for_event(tcod.EVENT_ANY, KEY, MOUSE)
	
	if KEY.c:
		_key_code = KEY.c
	else:
		_key_code = KEY.vk
	
	if _event == tcod.KEY_PRESSED:
		if not _key_code in INPUT:
			INPUT[_key_code] = 1
		else:
			INPUT[_key_code] += 1

		if '--keyout' in sys.argv and INPUT[_key_code] == 1:
			print KEY.c, KEY.vk, INPUT[_key_code]

	elif _event == tcod.KEY_RELEASED:
		INPUT[_key_code] = 0
	
	LAST_MOUSE_POS = MOUSE_POS[:]
	MOUSE_POS = [int(round(i)) for i in numbers.interp_velocity(LAST_MOUSE_POS, (_mouse.cx, _mouse.cy), .8)]
	
	if not MOUSE_POS == LAST_MOUSE_POS:
		events.trigger_event('mouse_moved',
		                     x=MOUSE_POS[0],
		                     y=MOUSE_POS[1],
		                     dx=MOUSE_POS[0]-LAST_MOUSE_POS[0],
		                     dy=MOUSE_POS[1]-LAST_MOUSE_POS[1])
	
	if _mouse.lbutton_pressed:
		events.trigger_event('mouse_pressed', x=MOUSE_POS[0], y=MOUSE_POS[1], button=1)
	
	if _mouse.rbutton_pressed:
		events.trigger_event('mouse_pressed', x=MOUSE_POS[0], y=MOUSE_POS[1], button=2)
	
	if _mouse.lbutton:
		events.trigger_event('mouse_held', x=MOUSE_POS[0], y=MOUSE_POS[1], button=1)
	
	if _mouse.rbutton:
		events.trigger_event('mouse_held', x=MOUSE_POS[0], y=MOUSE_POS[1], button=2)

def get_input_ord(char_ord):
	if not char_ord in INPUT:
		return False
	
	return INPUT[char_ord]

def get_input_char(char):
	return get_input_ord(ord(char))

def get_input_char_pressed(char):
	if get_input_char(char) == 1:
		INPUT[ord(char)] = 2
		
		return True
	
	return False

def get_input_ord_pressed(char_ord):
	if get_input_ord(char_ord) == 1:
		INPUT[char_ord] = 2
		
		return True
	
	return False

def get_input_char_long_held(char, slow=False):
	_ret_value = get_input_ord(ord(char))
	
	if _ret_value >= 3:
		if slow and _ret_value % 3:
			return False
		
		return True
	
	return False

def get_input_ord_long_held(char_ord, slow=False):
	return get_input_char_long_held(chr(char_ord), slow=slow)

def get_input_vk_long_held(vk, slow=False):
	_ret_value = get_input_ord(vk)
	
	if _ret_value >= 3:
		if slow and _ret_value % 3:
			return False
		
		return True
	
	return False

def get_input_vk_pressed(vk, slow=False):
	return get_input_ord_pressed(vk)

def get_last_mouse_pos():
	return LAST_MOUSE_POS

def get_mouse_click(button):
	if MOUSE.lbutton == button:
		return MOUSE.lbutton
	
	if MOUSE.rbutton == button:
		return MOUSE.rbutton

def get_mouse_pos():
	global LAST_MOUSE_POS
	
	LAST_MOUSE_POS = MOUSE.cx, MOUSE.cy
	
	return MOUSE.cx, MOUSE.cy

def get_mouse_velocity():
	return MOUSE.dcx, MOUSE.dcy