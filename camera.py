from framework import display, numbers

import world_action
import zones

import constants


X = 0
Y = 0
LAST_X = -1
LAST_Y = -1
X_MIN = 0
Y_MIN = 0
X_MAX = 0
Y_MAX = 0


def set_limits(x_min, y_min, x_max, y_max):
	global X_MIN, Y_MIN, X_MAX, Y_MAX
	
	X_MIN = x_min
	Y_MIN = y_min
	X_MAX = x_max
	Y_MAX = y_max

def set_pos(x, y):
	global X
	global Y
	
	X = numbers.clip(x, X_MIN, X_MAX)
	Y = numbers.clip(y, Y_MIN, Y_MAX)

def update():
	global X
	global Y	
	global LAST_X
	global LAST_Y
	
	X = numbers.clip(X, X_MIN, X_MAX)
	Y = numbers.clip(Y, Y_MIN, Y_MAX)
	
	_zone = zones.ZONES[zones.ACTIVE_ZONE]
	
	display.set_surface_camera('tiles', X, Y)
	display.reset_surface_shaders('tiles')
	
	if world_action.FADE_VALUE < 255:
		display.apply_surface_shader('tiles', zones.get_active_fader(), constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
	
	for shader in _zone['shaders']:
		display.apply_surface_shader('tiles', shader, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
	
	display.blit_surface_viewport('tiles', X, Y, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
	
	LAST_X = X
	LAST_Y = Y
