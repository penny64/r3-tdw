from framework import display, entities, timers, events, flags, workers, numbers, shapes

import libtcodpy as tcod

import constants
import settings
import camera

import numpy

PROCESSOR = None
CLOUD_X = 0
CLOUD_Y = 0
SHADOWS = None
LIGHTS = None
SUN = None
SUNLIGHT = -1.0


def start():
	global PROCESSOR
	
	_entity = entities.create_entity(group='systems')
	
	PROCESSOR = _entity
	
	timers.register(_entity, use_system_event='post_process')

def run(*args, **kwargs):
	entities.trigger_event(PROCESSOR, 'create_timer', *args, **kwargs)

def get_light_map():
	return LIGHTS

#########
#Effects#
#########

def _post_process_clouds(x, y, clouds, zoom, clouds_x, clouds_y, size, sunlight, noise, inside):
	_noise_values = [(zoom * x / (constants.MAP_VIEW_WIDTH)) + clouds_x,
	                 (zoom * y / (constants.MAP_VIEW_HEIGHT)) + clouds_y]
	_shade = tcod.noise_get_turbulence(noise, _noise_values, tcod.NOISE_SIMPLEX)
	_shade_mod = numbers.clip(abs(_shade), sunlight, 1)
	
	#TODO: Inside lighting
	#if not (camera.X+x, camera.Y+y) in inside:
	clouds[y][x] -= _shade_mod
	clouds[y][x] *= SHADOWS[camera.Y+y][camera.X+x].clip(SUNLIGHT-.5, 1)
	#else:
	#	clouds[y][x] *= SHADOWS[camera.Y+y][camera.X+x] #TODO: Inside lighting here
	
	#TODO: Future
	#clouds *= LIGHTS[camera.Y:camera.Y+y, camera.X:camera.X+x]
	
	clouds[y][x] *= LIGHTS[camera.Y+y, camera.X+x]

def post_process_clouds(width, height, passes, noise, inside):
	global CLOUD_X, CLOUD_Y
	
	_clouds = numpy.zeros((height, width))
	_clouds += 1.6
	_zoom = 2.0
	_clouds_x = (display.get_surface('tiles')['start_x']*.016)+CLOUD_X
	_clouds_y = (display.get_surface('tiles')['start_y']*.016)+(CLOUD_X * -.5)
	_size = 100.0
	_sunlight = SUNLIGHT
	
	if settings.TICK_MODE == 'normal':
		CLOUD_X -= numbers.clip(.003 * (settings.PLAN_TICK_RATE * .75), .003, 1)
	
	_worker = workers.counter_2d(width,
	                             height,
	                             passes,
	                             lambda x, y: _post_process_clouds(x, y, _clouds, _zoom, _clouds_x, _clouds_y, _size, _sunlight, noise, inside))
	
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_fore('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT,
	                                                             g=.9, b=.8))
	entities.register_event(_worker,
	                        'finish',
	                        lambda e: display.shade_surface_back('tiles',
	                                                             _clouds,
	                                                             constants.MAP_VIEW_WIDTH,
	                                                             constants.MAP_VIEW_HEIGHT,
	                                                             g=.9, b=.8))

def tick_sun():
	global SUNLIGHT
	
	SUNLIGHT += .0001

#def sunlight():
#	global SUN
#	
#	display.shade_surface_fore_ext('tiles', SUN, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
#	display.shade_surface_back_ext('tiles', SUN, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)

def post_process_lights():
	global LIGHTS
	
	if not settings.TICK_MODE == 'normal':
		return
	
	LIGHTS *= .98
	LIGHTS = LIGHTS.clip(1, 2)

def generate_shadow_map(width, height, solids, trees):
	global SHADOWS
	
	SHADOWS = numpy.ones((height, width))
	_taken = set()
	
	for x, y in solids:
		if (x, y) in trees:
			continue
		
		for i in range(1, 4):
			if (x+i, y+i) in solids or (x+i, y+i) in _taken or x+i >= width or y+i >= height:
				break
			
			_shadow = numbers.clip((i)/5.0, .35, .9)
			
			if _shadow < SHADOWS[y+i][x+i]:
				SHADOWS[y+i][x+i] = _shadow
			
			_taken.add((x+1, y+1))
	
	_taken = set()
	
	for _x, _y in trees.keys():
		_tree_size = float(trees[_x, _y])
		
		for x, y in shapes.circle(_x, _y, int(_tree_size)):
			if (x, y) in solids or x >= width or y >= height or x < 0 or y <0:
				continue
			
			_distance = numbers.float_distance((x, y), (_x, _y))*1.25
			_shadow = numbers.clip(1 - ((_distance / _tree_size) + .25), .1, .9)
			
			SHADOWS[y][x] = numbers.clip(SHADOWS[y][x]-_shadow, .45, 1)

def generate_light_map(width, height, solids, trees):
	global LIGHTS#, SUN
	
	LIGHTS = numpy.ones((height, width))
#	SUN = numpy.ones((constants.MAP_VIEW_HEIGHT, constants.MAP_VIEW_WIDTH))
#	SUN -= .5