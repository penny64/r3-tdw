from framework import movement, controls, events, stats

import constants
import camera

import settings


def boot(entity):
	events.register_event('input', lambda: handle_keyboard_input(entity))

def handle_keyboard_input(entity):
	if controls.get_input_char_pressed('1'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .1)))
	
	elif controls.get_input_char_pressed('2'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .25)))
	
	elif controls.get_input_char_pressed('3'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .4)))
	
	elif controls.get_input_char_pressed('4'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .55)))
	
	if controls.get_input_char_pressed('\t'):
		_x, _y = movement.get_position(entity)
		
		camera.set_pos(_x - constants.MAP_VIEW_WIDTH/2, _y - constants.MAP_VIEW_HEIGHT/2)	