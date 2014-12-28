from framework import display, events, numbers, controls

import libtcodpy as tcod

import words
import life

import constants
import random
import time
import math


SKILL_NAMES = ['mobility', 'smgs', 'rifles', 'pistols', 'explosives']
CLASS_SKILLS = ['smgs', 'rifles', 'pistols', 'explosives']
HIRED_MEMBERS = []
FEATS = []
NOISE = None
ZOOM = .5
SIDEBAR_WIDTH = 44
TITLE = 'Hire New Squad'


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
			_crosshair_mod = abs((_dist_to_crosshair - 1))
			
			if _height > .4:
				_height = (_height - .4) / .4
				_r, _g, _b = numbers.clip(30 * _height, 20, 255), 50 * _height, numbers.clip(30 * _height, 30, 255)
			
			else:
				_r, _g, _b = 20, 0, 30
			
			_r += 30# * _crosshair_mod
			
			if x < SIDEBAR_WIDTH:
				if y < 7:
					_r = numbers.interp(_r, .0, .4)
					_g = numbers.interp(_g, .0, .4)
					_b = numbers.interp(_b, .0, .4)
					
				elif y < 43:
					_r = numbers.interp(_r, .0, .6)
					_g = numbers.interp(_g, .0, .6)
					_b = numbers.interp(_b, .0, .6)
					
				elif y < constants.WINDOW_HEIGHT:
					_r = numbers.interp(_r, 1, .7)
					_g = numbers.interp(_g, 1, .7)
					_b = numbers.interp(_b, 1, .7)

				else:
					_r = (int(round(_r * 1.0)))
					_g = (int(round(_g * .2)))
					_b = (int(round(_b * .2)))
			
			if x > SIDEBAR_WIDTH + 3 and x < constants.WINDOW_WIDTH - 6:
				if y > 18 and y < 36:
					_r = numbers.interp(_r, 255, .1)
					_g = numbers.interp(_g, 255, .1)
					_b = numbers.interp(_b, 255, .1)
			
			if x > SIDEBAR_WIDTH + 3 and x < constants.WINDOW_WIDTH - 6:
				if y > 10 and y < 16:
					_r = numbers.interp(_r, .0, .4)
					_g = numbers.interp(_g, .0, .4)
					_b = numbers.interp(_b, .0, .4)
			
			display._set_char('background', x, y, ' ', (0, 0, 0), (_r, _g, _b))

def roll():
	global HIRED_MEMBERS, FEATS
	
	HIRED_MEMBERS = []
	FEATS = []
	
	words.reset()
	
	_skill_cost = {_skill: 1 for _skill in SKILL_NAMES}
	_skill_cost['mobility'] = .3
	_skill_cost['smgs'] = .48
	_skill_cost['rifles'] = .75
	_skill_cost['pistols'] = .41
	_skill_cost['explosives'] = .65
	_max_skill_points = 0
	_mvp = {'name': '', 'stat': None, 'amount': 0}
	
	for i in range(5):
		_levels = {_skill: 1 for _skill in SKILL_NAMES}
		_total_cost = 0
		_skill_focus = {'stat': None, 'amount': 0}
		_levels['name'] = words.get_male_name()
		
		for skill_name in SKILL_NAMES:
			_levels[skill_name] = random.randint(20 + random.randint(-8, 8), 55 + random.randint(-20, 12))
			_total_cost += _levels[skill_name] * _skill_cost[skill_name]
			
			if skill_name in CLASS_SKILLS and (not _skill_focus['stat'] or _levels[skill_name] > _skill_focus['amount']):
				_skill_focus['amount'] = _levels[skill_name]
				_skill_focus['stat'] = skill_name
				
				if not _mvp['name'] or _skill_focus['amount'] > _mvp['amount']:
					_mvp['name'] = _levels['name']
					_mvp['amount'] = _skill_focus['amount']
					_mvp['stat'] = skill_name
		
		_levels['intelligence'] = random.randint(1, 5)
		_levels['skill_points'] = 80 + ((_levels['intelligence'] - 1) * 32)
		_levels['pay'] = _total_cost
		_levels['skill_focus'] = _skill_focus['stat']
		_max_skill_points += _levels['skill_points']
		
		HIRED_MEMBERS.append(_levels)
	
	if _max_skill_points > 750:
		FEATS.append([('Adaptable', (0, 180, 255)), 'Able to learn'])
	
	elif _max_skill_points < 650:
		FEATS.append([('Experienced', (0, 180, 255)), 'Unable to learn'])
	
	if _mvp['amount'] > 55:
		FEATS.append([('%s expert' % _mvp['stat'].title()[:-1], (255, 40, 40)), _mvp['name']])

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
		_name = squad_member['name']
		
		display.write_string('text', _x, _y - 2, _name, fore_color=(255, 255, 255))
		display.write_string('text', _x, _y - 1, squad_member['skill_focus'].title() + ' ' * (len(_name) - len(squad_member['skill_focus'])), fore_color=(180, 180, 180), back_color=(40, 40, 40))
		
		for stat in SKILL_NAMES:
			_r = int(round(220 * (1 - (squad_member[stat] / 75.0))))
			_g = int(round(250 * (squad_member[stat] / 75.0)))
			
			display.write_string('text', _x, _y + 1, '%s' % stat.upper())
			display.write_string('text', _x + len(stat), _y + 1, '.' * (15 - len(stat)), fore_color=(80, 80, 80))
			display.write_string('text', _x + 15, _y + 1, '%s' % squad_member[stat], fore_color=(_r, _g, 0))
			
			_y += 1
	
		display.write_string('text', _x, _y + 2, 'Pay: ')
		display.write_string('text', _x + 6, _y + 2, '$%.2f' % squad_member['pay'], fore_color=(0, 200, 0), back_color=(0, 40, 0))
		display.write_string('text', _x + 6 + len('$%.2f' % squad_member['pay']) + 0, _y + 2, '/week', fore_color=(150, 150, 150), back_color=(0, 0, 0))
		
		_x += 20
		
		if _x > 40:
			_x = 3
			_y_mod += 12
		
		_total_money += squad_member['pay']
	
	#for y in range(12, 14):
		#for x in range(SIDEBAR_WIDTH + 10, constants.WINDOW_WIDTH - 14):
	display.write_string('text', SIDEBAR_WIDTH + 10, 12, 'Operation', fore_color=(255, 255, 255))
	display.write_string('text', SIDEBAR_WIDTH + 10, 13, 'Dark Wing', fore_color=(255, 255, 255))
	
	for y in range(20, 28):
		for x in range(SIDEBAR_WIDTH + 10, constants.WINDOW_WIDTH - 14):
			display.write_char('text', x, y, '#', fore_color=(255, 255, 255))
	
	display.write_string('text', SIDEBAR_WIDTH + 5, 29, 'No contact outside the town.', fore_color=(255, 255, 255))
	
	_i = 0
	
	for feat in FEATS:
		display.write_string('text', 3, _y + 5 + _i, feat[0][0], fore_color=feat[0][1])
		display.write_string('text', 3 + len(feat[0][0]), _y + 5 + _i, '- ' + feat[1], fore_color=(255, 255, 255))
		
		_i += 1
	
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
