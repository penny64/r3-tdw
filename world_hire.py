from framework import display, events, numbers, controls

import libtcodpy as tcod

import life

import constants
import random
import time
import math


SKILL_NAMES = ['mobility', 'smgs', 'rifles', 'pistols', 'explosives']
HIRED_MEMBERS = []
NOISE = None
ZOOM = .5
SIDEBAR_WIDTH = 44
TITLE = 'Hire Squad'


def create():
	display.create_surface('background')
	display.create_surface('text')
	display.blit_background('background')
	
	roll()
	
	NOISE = tcod.noise_new(2, h=tcod.NOISE_DEFAULT_HURST, random=tcod.random_new())
	
	for y in range(0, constants.WINDOW_HEIGHT):
		for x in range(0, constants.WINDOW_WIDTH):
			_noise_values = [(ZOOM * x / (constants.WINDOW_WIDTH)),
			                 (ZOOM * y / (constants.WINDOW_HEIGHT))]
			_height = 1 - tcod.noise_get_turbulence(NOISE, _noise_values, tcod.NOISE_SIMPLEX)
			_dist_to_crosshair = 30
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
			
			if x < SIDEBAR_WIDTH:
				_r = (int(round(_r * 1.0)))
				_g = (int(round(_g * .2)))
				_b = (int(round(_b * .2)))
			
			display._set_char('background', x, y, ' ', (0, 0, 0), (_r, _g, _b))

def roll():
	global HIRED_MEMBERS
	
	HIRED_MEMBERS = []
	
	for i in range(5):
		_levels = {_skill: 1 for _skill in SKILL_NAMES}
		_skill_cost = {_skill: 1 for _skill in SKILL_NAMES}
		_skill_cost['mobility'] = .3
		_skill_cost['smgs'] = .48
		_skill_cost['rifles'] = .75
		_skill_cost['pistols'] = .41
		_skill_cost['explosives'] = .65
		_total_cost = 0
		
		for skill_name in SKILL_NAMES:
			_levels[skill_name] = random.randint(20 + random.randint(-8, 8), 55 + random.randint(-20, 12))
			_total_cost += _levels[skill_name] * _skill_cost[skill_name]
		
		_levels['intelligence'] = random.randint(1, 5)
		_levels['skill_points'] = 80 + ((_levels['intelligence'] - 1) * 32)
		_levels['pay'] = _total_cost
		
		HIRED_MEMBERS.append(_levels)

def handle_input():
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	if controls.get_input_char_pressed('\r'):
		return False
	
	elif controls.get_input_char_pressed(' '):
		roll()
	
	elif controls.get_input_char_pressed('k'):
		display.screenshot('screenshot-%s.bmp' % time.time())
	
	return True

def draw():
	_x = 3
	_y_mod = 0
	_total_money = 0
	
	display.write_string('text', (SIDEBAR_WIDTH / 2) - (len(TITLE) / 2), 3, TITLE, fore_color=(255, 255, 255))
	
	for squad_member in HIRED_MEMBERS:
		_y = 10 + _y_mod
		
		display.write_string('text', _x, _y - 2, 'Tester Toaster', fore_color=(255, 255, 255))
		
		for stat in SKILL_NAMES:
			_r = int(round(220 * (1 - (squad_member[stat] / 75.0))))
			_g = int(round(250 * (squad_member[stat] / 75.0)))
			
			display.write_string('text', _x, _y, '%s: ' % stat.upper())
			display.write_string('text', _x + 15, _y, '%s' % (squad_member[stat]), fore_color=(_r, _g, 0))
			
			_y += 1
	
		display.write_string('text', _x, _y + 2, 'Pay: ')
		display.write_string('text', _x + 6, _y + 2, '$%.2f' % squad_member['pay'], fore_color=(0, 200, 0), back_color=(0, 40, 0))
		display.write_string('text', _x + 6 + len('$%.2f' % squad_member['pay']) + 0, _y + 2, '/week', fore_color=(150, 150, 150), back_color=(0, 0, 0))
		
		_x += 20
		
		if _x > 40:
			_x = 3
			_y_mod += 12
		
		_total_money += squad_member['pay']
	
	display.write_string('text', 3, constants.WINDOW_HEIGHT - 4, '<Space>', fore_color=(255, 255, 255))
	display.write_string('text', 10, constants.WINDOW_HEIGHT - 4, ' - Reroll', fore_color=(200, 200, 200))
	
	display.write_string('text', 3, constants.WINDOW_HEIGHT - 5, '<Enter>', fore_color=(255, 255, 255))
	display.write_string('text', 10, constants.WINDOW_HEIGHT - 5, ' - Accept', fore_color=(200, 200, 200))
	
	display.write_string('text', 3, constants.WINDOW_HEIGHT - 2, 'Total Cost: ')
	display.write_string('text', 15, constants.WINDOW_HEIGHT - 2, '$%.2f' % _total_money, fore_color=(0, 200, 0), back_color=(0, 40, 0))
	
	display.blit_surface_viewport('background', 0, 0, constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)
	display.blit_surface('text')

def tick():
	pass

def loop():
	if not handle_input():
		return False
	
	tick()
	draw()
	
	events.trigger_event('draw')
	return True
