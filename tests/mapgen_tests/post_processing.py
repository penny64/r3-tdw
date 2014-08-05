from framework import display, entities, timers, events, flags, workers, numbers

import libtcodpy as tcod

import constants

import numpy

PROCESSOR = None
CLOUD_X = 0
CLOUD_Y = 0


def start():
	global PROCESSOR
	
	_entity = entities.create_entity(group='systems')
	
	PROCESSOR = _entity
	
	timers.register(_entity, use_system_event='post_process')

def run(*args, **kwargs):
	entities.trigger_event(PROCESSOR, 'create_timer', *args, **kwargs)


#########
#Effects#
#########

def _post_process_water(x, y, clouds, zoom, clouds_x, clouds_y, size, noise):
	_noise_values = [(zoom * x / (size)) + clouds_x,
	                 (zoom * y / (size)) + clouds_y]
	_shade = tcod.noise_get_turbulence(noise, _noise_values, tcod.NOISE_SIMPLEX)
	_shade_mod = numbers.clip(abs(_shade), .6, 1)
	
	clouds[y][x] -= _shade_mod

def post_process_water(width, height, passes, noise):
	global CLOUD_X, CLOUD_Y
	
	_clouds = numpy.zeros((height, width))
	_clouds += 1.6
	_zoom = 2.0
	_clouds_x = (display.get_surface('tiles')['start_x']*.015)+CLOUD_X
	_clouds_y = (display.get_surface('tiles')['start_y']*.015)+(CLOUD_X * -.5)
	_size = 100.0
	
	CLOUD_X -= .003
	
	_worker = workers.counter_2d(width,
	                             height,
	                             passes,
	                             lambda x, y: _post_process_water(x, y, _clouds, _zoom, _clouds_x, _clouds_y, _size, noise))
	
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_fore('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT))
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_back('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT))