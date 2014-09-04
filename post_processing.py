from framework import display, entities, timers, events, flags, workers, numbers

import libtcodpy as tcod

import constants
import camera

import numpy

PROCESSOR = None
CLOUD_X = 0
CLOUD_Y = 0
SHADOWS = None


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

def _post_process_clouds(x, y, clouds, zoom, clouds_x, clouds_y, size, noise):
	_noise_values = [(zoom * x / (constants.MAP_VIEW_WIDTH)) + clouds_x,
	                 (zoom * y / (constants.MAP_VIEW_HEIGHT)) + clouds_y]
	_shade = tcod.noise_get_turbulence(noise, _noise_values, tcod.NOISE_SIMPLEX)
	_shade_mod = numbers.clip(abs(_shade), .6, 1)
	
	clouds[y][x] -= _shade_mod
	clouds[y][x] *= SHADOWS[camera.Y+y][camera.X+x]

def post_process_clouds(width, height, passes, noise):
	global CLOUD_X, CLOUD_Y
	
	_clouds = numpy.zeros((height, width))
	_clouds += 1.6
	_zoom = 2.0
	_clouds_x = (display.get_surface('tiles')['start_x']*.03)+CLOUD_X
	_clouds_y = (display.get_surface('tiles')['start_y']*.03)+(CLOUD_X * -.5)
	_size = 100.0
	
	CLOUD_X -= .003
	
	#_clouds += SHADOWS[camera.Y:camera.Y+height, camera.X:camera.X+width]
	
	_worker = workers.counter_2d(width,
	                             height,
	                             passes,
	                             lambda x, y: _post_process_clouds(x, y, _clouds, _zoom, _clouds_x, _clouds_y, _size, noise))
	
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

def generate_shadow_map(width, height, solids):
	global SHADOWS
	
	SHADOWS = numpy.ones((height, width))
	_taken = set()
	
	for x, y in solids:
		for i in range(1, 4):
			if (x+i, y+i) in solids or (x+i, y+i) in _taken or x+i >= width or y+i >= height:
				break
			
			_shadow = numbers.clip((i)/5.0, .35, .9)
			
			if _shadow < SHADOWS[y+i][x+i]:
				SHADOWS[y+i][x+i] = _shadow
			
			_taken.add((x+1, y+1))
	
	