PLAN_TICK_RATE = 4
TICK_MODE = 'normal'
SHOW_NODE_GRID = False
OBSERVER_MODE = False


def set_tick_mode(mode):
	global TICK_MODE
	
	TICK_MODE = mode

def set_plan_tick_rate(rate):
	global PLAN_TICK_RATE
	
	PLAN_TICK_RATE = rate

def toggle_show_node_grid():
	global SHOW_NODE_GRID
	
	if SHOW_NODE_GRID:
		SHOW_NODE_GRID = False
	else:
		SHOW_NODE_GRID = True

def toggle_observer_mode():
	global OBSERVER_MODE
	
	if OBSERVER_MODE:
		OBSERVER_MODE = False
	else:
		OBSERVER_MODE = True