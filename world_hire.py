from framework import display, events, numbers, controls

import libtcodpy as tcod

import life

import constants
import random
import time
import math

STATS = {}


def create():
	global NOISE
	
	display.create_surface('background')
	display.create_surface('text')
	display.blit_background('background')
	
	roll()

def roll():
	#STATS['intelligence'] = random.randint(25, 100)
	#int(round(100 * (STATS['intelligence'] / 100.0)))
	#STATS['mobility'] = random.randint

	#Int
	#	low = more starting points, no customization
	#	high = less starting points, more customization
	_skill_names = ['mobility', 'smgs', 'rifles', 'pistols', 'explosives']
	_levels = {_skill: 1 for _skill in _skill_names}
	
	random.shuffle(_skill_names)
		
	#_mob = 2
	#_int = 1
	#_wep_sub = 3
	#_wep_rif = 2
	#_wep_pis = 1
	#_wep_exp = 1
	_level = 1
	_level_cap = 5
	_mob_diff = 1.5
	_wep_sub_diff = 1.65
	_wep_rif_diff = 1.75
	_wep_pis_diff = 1.58
	_wep_exp_diff = 1.45
	
	#_test_diff = _wep_sub_diff
	
	_int = 5 #+ random.randint(0, 4)
	_r_int = 1 - (_int / (_int + .5))
	_max_skill_points = 140 + ((_int - 1) * 20)
	
	_skill_diffs = {'mobility': _mob_diff}
	_skill_diffs['smgs'] = _wep_sub_diff
	_skill_diffs['rifles'] = _wep_rif_diff
	_skill_diffs['pistols'] = _wep_pis_diff
	_skill_diffs['explosives'] = _wep_exp_diff
	
	while 1:
		_lowest_cost = 99999
		
		for skill_name in _skill_names:
			_tries = 3
			
			while 1:
				_level = _levels[skill_name] + random.randint(0, 1)
				_cost = int(round(math.pow(_level * (_skill_diffs[skill_name] + _r_int), _level)))
				
				if _levels[skill_name] - _level and _cost < _lowest_cost:
					_lowest_cost = _cost
				
				if _cost < _max_skill_points:
					if _levels[skill_name] - _level:
						_levels[skill_name] = _level
						_max_skill_points -= _cost
						
						print skill_name, _cost, _level, _max_skill_points
					
					break
				
				_tries -= 1
				
				if not _tries:
					break
		
		if _lowest_cost > _max_skill_points and not _lowest_cost == 99999:
			print 'ex', _lowest_cost, _max_skill_points
			break
	
	#for skill_name in _skill_names:
	#	print skill_name, _levels[skill_name], _max_skill_points
	
	return
	
	for kind in _skills:
		print kind
		print 'Cost\tTotal\tPts. Remaining'
		_diff = _skills[kind][1]
		_total = 0
	
		for i in range(_level, min(_level_cap + 1, _level + (_level_cap + 1))):
			_cost = int(round(math.pow(_level * (_diff + _r_int), (_level + i))))
			_total += _cost
	
			print '%i\t%i\t%i' % (_cost, _total, int(round(_max_skill_points - _total)))
	
		print

def handle_input():
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		return False
	
	if controls.get_input_char_pressed('\r'):
		return False
	
	if controls.get_input_char_pressed('k'):
		display.screenshot('screenshot-%s.bmp' % time.time())
	
	return True

def draw():
	_y = 10
	
	display.write_string('text', 20, _y - 2, 'Tester Toaster')
	
	for stat in STATS:
		display.write_string('text', 20, _y, '%s: %s' % (stat, STATS[stat]))
		_y += 1
	
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
