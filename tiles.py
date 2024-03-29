import constants

import random


def _tile(x, y, char, weight, fore_color, back_color):
	return {'x': x,
	        'y': y,
	        'c': char,
	        'c_f': fore_color,
	        'c_b': back_color,
	        'w': weight}

def tree(x, y):
	_c_1, _c_2 = random.sample([(77, 54, 29),
	                           (67, 44, 19),
	                           (57, 54, 29)],
	                          2)
	
	return _tile(x, y, ' ', 6, _c_1, _c_2)

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
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 125, _c_1, _c_2)

def grass(x, y):
	_c_1, _c_2 = random.sample([constants.FOREST_GREEN_1,
	                           constants.FOREST_GREEN_2,
	                           constants.FOREST_GREEN_3],
	                          2)
	
	return _tile(x, y, random.choice(['.', ',', '\'']), 8, _c_1, _c_2)

def tall_grass(x, y):
	_c_1, _c_2 = random.sample([constants.DARK_FOREST_GREEN_1,
	                           constants.DARK_FOREST_GREEN_2,
	                           constants.DARK_FOREST_GREEN_3],
	                          2)
	
	return _tile(x, y, random.choice(['.', ',', '\'', '^']), 15, _c_1, _c_2)

def water(x, y):
	_c_1, _c_2 = random.sample([constants.WATER_1,
	                           constants.WATER_2,
	                           constants.WATER_3],
	                          2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 150, _c_1, _c_2)

def wooden_fence(x, y):
	_c_1, _c_2 = random.sample([constants.GRAY_1,
	                           constants.GRAY_2,
	                           constants.GRAY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 100, _c_1, _c_2)

def rock(x, y):
	_c_1, _c_2 = random.sample([constants.DARK_GRAY_1,
	                            constants.DARK_GRAY_2,
	                            constants.DARK_GRAY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 100, _c_1, _c_2)

def concrete(x, y):
	_c_1, _c_2 = random.sample([constants.DARK_GRAY_1,
	                            constants.DARK_GRAY_2,
	                            constants.DARK_GRAY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 3, _c_1, _c_2)

def concrete_striped(x, y):
	if random.randint(0, 1):
		if not x % 2 or not y % 4:
			_c_1 = constants.DARKER_GRAY_1
			_c_2 = constants.DARKER_GRAY_1
		else:
			_c_1, _c_2 = random.sample([constants.DARKER_GRAY_3,
				                        constants.DARKER_GRAY_2],
				                       2)
	else:
		_c_1, _c_2 = random.sample([constants.DARKER_GRAY_1,
			                        constants.DARKER_GRAY_2,
			                        constants.DARKER_GRAY_3],
			                       2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 3, _c_1, _c_2)

def wood_floor(x, y):
	if random.randint(0, 1):
		if not x % 2 or not y % 4:
			_c_1 = constants.WOOD_3
			_c_2 = constants.WOOD_3
		else:
			_c_1, _c_2 = random.sample([constants.WOOD_1,
				                        constants.WOOD_2],
				                       2)
	else:
		_c_1, _c_2 = random.sample([constants.WOOD_1,
			                        constants.WOOD_2,
			                        constants.WOOD_3],
			                       2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 2, _c_1, _c_2)

def wood_block(x, y):
	_c_1, _c_2 = random.sample([constants.DARK_WOOD_1,
	                            constants.DARK_WOOD_2,
	                            constants.DARK_WOOD_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 1, _c_1, _c_2)

def tile_checkered(x, y):
	if not x % 2 or not y % 2:
		_c_1 = (160, 160, 160)
		_c_2 = (160, 160, 160)
	else:
		_c_1 = (205, 205, 205)
		_c_2 = (205, 205, 205)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 2, _c_1, _c_2)

def tile_domino(x, y):
	if not x % 2 or not y % 2:
		_c_1 = (20, 20, 20)
		_c_2 = (20, 20, 20)
	
	else:
		_c_1 = (255, 255, 255)
		_c_2 = (255, 255, 255)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 2, _c_1, _c_2)

def carpet_burgandy(x, y):
	_c_1, _c_2 = random.sample([constants.BURGANDY_1,
	                            constants.BURGANDY_2,
	                            constants.BURGANDY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(176), chr(178)]), 1, _c_1, _c_2)

def carpet_burgandy_specs(x, y):
	_c_1, _c_2 = random.sample([constants.SPEC_BURGANDY_1,
	                            constants.SPEC_BURGANDY_2,
	                            constants.SPEC_BURGANDY_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(176), chr(178)]), 1, _c_1, _c_2)

def carpet_blue(x, y):
	_c_1, _c_2 = random.sample([constants.BLUE_1,
	                            constants.BLUE_2,
	                            constants.BLUE_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(176), chr(178)]), 1, _c_1, _c_2)

def carpet_light_blue(x, y):
	_c_1, _c_2 = random.sample([constants.LIGHT_BLUE_1,
	                            constants.LIGHT_BLUE_2,
	                            constants.LIGHT_BLUE_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(176), chr(178)]), 1, _c_1, _c_2)

def carpet_brown(x, y):
	_c_1, _c_2 = random.sample([constants.BROWN_1,
	                            constants.BROWN_2,
	                            constants.BROWN_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(176), chr(178)]), 1, _c_1, _c_2)

def countertop(x, y):
	_c_1, _c_2 = random.sample([constants.MARBLE_1,
	                            constants.MARBLE_2,
	                            constants.MARBLE_3],
	                           2)
	
	return _tile(x, y, random.choice([chr(176), chr(177), chr(178)]), 1, _c_1, _c_2)

def trade_window(x, y):
	_c_1 = (10, 10, 10)
	_c_2 = (10, 10, 10)
	
	return _tile(x, y, '#', 100, _c_1, _c_2)

def debug(x, y):
	_c_1 = (255, 0, 255)
	_c_2 = (255, 0, 255)
	
	return _tile(x, y, 'X', 100, _c_1, _c_2)
