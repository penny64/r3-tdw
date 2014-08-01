from framework import entities, display

import logging


def register(entity, surface=None, animated=True):
	entity['tile'] = {'char': 'X',
	                  'x': -1,
	                  'y': -1,
	                  'fore_color': (255, 255, 255),
	                  'back_color': None,
	                  'surface': surface,
	                  'flags': {},
	                  'animation': {}}
	
	entities.create_event(entity, 'set_char')
	entities.create_event(entity, 'set_position')
	entities.create_event(entity, 'set_fore_color')
	entities.create_event(entity, 'set_back_color')
	entities.create_event(entity, 'tint_fore_color')
	entities.create_event(entity, 'tint_back_color')
	entities.create_event(entity, 'set_surface')
	entities.create_event(entity, 'draw')
	entities.create_event(entity, 'flag')
	entities.create_event(entity, 'unflag')
	entities.create_event(entity, 'animate')
	entities.register_event(entity, 'set_char', set_char)
	entities.register_event(entity, 'set_position', set_tile_position)
	entities.register_event(entity, 'set_fore_color', set_fore_color)
	entities.register_event(entity, 'set_back_color', set_back_color)
	entities.register_event(entity, 'tint_fore_color', tint_fore_color)
	entities.register_event(entity, 'tint_back_color', tint_back_color)
	entities.register_event(entity, 'set_surface', set_surface)
	
	if animated:
		entities.register_event(entity, 'tick', tick)
	
	entities.register_event(entity, 'draw', draw)
	entities.register_event(entity, 'flag', flag_tile)
	entities.register_event(entity, 'unflag', unflag_tile)
	entities.register_event(entity, 'animate', animate)

def set_char(entity, char):
	entity['tile']['char'] = char

def flag_tile(entity, flag, value=True):
	entity['tile']['flags'][flag] = value

def unflag_tile(entity, flag):
	del entity['tile']['flags'][flag]

def set_tile_position(entity, x, y):
	entity['tile']['x'] = int(round(x))
	entity['tile']['y'] = int(round(y))

def set_fore_color(entity, color):
	entity['tile']['fore_color'] = color

def set_back_color(entity, color):
	entity['tile']['back_color'] = color

def tint_fore_color(entity, color, amount):
	entity['tile']['fore_color'] = numbers.interp_velocity(entity['tile']['fore_color'], color, amount)

def tint_back_color(entity, color, amount):
	entity['tile']['back_color'] = numbers.interp_velocity(entity['tile']['back_color'], color, amount)

def set_surface(entity, surface):
	entity['tile']['surface'] = surface

def cancel_animation(entity):
	entity['tile']['animation'] = {}

def cancel_animation_with_name(entity, name):
	if not entity['tile']['animation']:
		return

	if entity['tile']['animation']['name'] == name:
		cancel_animation(entity)

def animate(entity, animation, repeat=0, delay=10, name=None):
	entity['tile']['animation'] = {'name': name, 'tiles': animation, 'repeat': repeat, 'delay': delay, 'delay_max': delay, 'index': 0}

def tick(entity):
	_animation = entity['tile']['animation']

	if not _animation:
		return

	if _animation['delay']:
		_animation['delay'] -= 1
	else:
		_animation['delay'] = _animation['delay_max']
		_animation['index'] += 1

		if _animation['index'] == len(_animation['tiles']):
			if _animation['repeat']:
				_animation['repeat'] -= 1
				_animation['index'] = 0
			else:
				entity['tile']['animation'] = {}

def draw(entity):
	_char = entity['tile']['char']

	if entity['tile']['animation']:
		_animation = entity['tile']['animation']
		_char = _animation['tiles'][_animation['index']]

		if _char == '@@':
			_char = entity['tile']['char']

		if _animation['delay']:
			_animation['delay'] -= 1
		else:
			_animation['delay'] = _animation['delay_max']
			_animation['index'] += 1

			if _animation['index'] == len(_animation['tiles']):
				_animation['index'] = 0

	display.write_char(entity['tile']['surface'],
	                             entity['tile']['x'],
	                             entity['tile']['y'],
	                             _char,
								 fore_color=entity['tile']['fore_color'],
								 back_color=entity['tile']['back_color'])