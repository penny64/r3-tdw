from framework import display, numbers

import constants


X = 0
Y = 0
LAST_X = 0
LAST_Y = 0
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
	
	if not LAST_X == X or not LAST_Y == Y:
		display.blit_surface_viewport('tiles', X, Y, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
		display.set_surface_camera('tiles', X, Y)
		
		LAST_X = X
		LAST_Y = Y
