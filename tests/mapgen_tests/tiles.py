import constants

import random


def _tile(x, y, char, weight, fore_color, back_color):
	return {'x': x,
	        'y': y,
	        'c': char,
	        'c_f': fore_color,
	        'c_b': back_color,
	        'w': weight}

def swamp(x, y):
	_c_1, _c_2 = random.sample([constants.SATURATED_GREEN_1,
	                           constants.SATURATED_GREEN_2,
	                           constants.SATURATED_GREEN_3],
	                          2)
	
	return _tile(x, y, ' ', 6, _c_1, _c_2)

def swamp_water(x, y):
	_c_1, _c_2 = random.sample([constants.SWAMP_WATER_1,
	                           constants.SWAMP_WATER_2,
	                           constants.SWAMP_WATER_3],
	                          2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 10, _c_1, _c_2)

def grass(x, y):
	_c_1, _c_2 = random.sample([constants.FOREST_GREEN_1,
	                           constants.FOREST_GREEN_2,
	                           constants.FOREST_GREEN_3],
	                          2)
	
	return _tile(x, y, random.choice(['.', ',', '\'']), 3, _c_1, _c_2)

def water(x, y):
	_c_1, _c_2 = random.sample([constants.WATER_1,
	                           constants.WATER_2,
	                           constants.WATER_3],
	                          2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 20, _c_1, _c_2)

def wooden_fence(x, y):
	_c_1, _c_2 = random.sample([constants.GRAY_1,
	                           constants.GRAY_2,
	                           constants.GRAY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 100, _c_1, _c_2)

def concrete(x, y):
	_c_1, _c_2 = random.sample([constants.DARK_GRAY_1,
	                            constants.DARK_GRAY_2,
	                            constants.DARK_GRAY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 100, _c_1, _c_2)

def concrete_striped(x, y):
	if not y % 2 or not y % 2:
		_c_1 = constants.DARK_GRAY_1
		_c_2 = constants.DARK_GRAY_1
	else:
		_c_1, _c_2 = random.sample([constants.DARK_GRAY_3,
			                        constants.DARK_GRAY_2],
			                       2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 100, _c_1, _c_2)