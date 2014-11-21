from framework import display, worlds, entities, events, controls, movement

import world_action
import ui_strategy
import constants
import worldgen
import main

import random

SELECTED_SQUAD = None
SELECTED_CAMP = None
DRAW_MODE = 'news'
MAP = None
_DEBUG_ORD = 10


def create():
	global MAP
	
	worlds.create('strategy')
	
	display.create_surface('map', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_markers', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_squads', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('ui_bar', width=constants.WINDOW_WIDTH, height=constants.WINDOW_HEIGHT-constants.STRAT_MAP_HEIGHT)
	
	events.register_event('mouse_moved', handle_mouse_moved)
	events.register_event('mouse_pressed', handle_mouse_pressed)
	
	entities.create_entity_group('life', static=True)
	entities.create_entity_group('items', static=True)
	entities.create_entity_group('factions', static=True)
	entities.create_entity_group('squads', static=True)
	
	_grid = {}
	_color_map = {}
	
	MAP = {'grid': _grid,
	       'color_map': _color_map}	
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_grid[x, y] = {'owned_by': None,
			               'is_ownable': False,
			               'squads': []}
	
	worldgen.generate()

def set_draw_mode(mode):
	global DRAW_MODE
	
	DRAW_MODE = mode
	
	ui_strategy.clear_bar()

def handle_input():
	global _DEBUG_ORD
	
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		if not DRAW_MODE == 'news':
			set_draw_mode('news')
		
		else:
			return False
	
	if controls.get_input_char_pressed('z'):
		_DEBUG_ORD -= 1
	
	elif controls.get_input_char_pressed('x'):
		_DEBUG_ORD += 1
	
	return True

def handle_mouse_moved(x, y, dx, dy):
	return

def handle_mouse_pressed(x, y, button):
	global SELECTED_SQUAD, SELECTED_CAMP
	
	_s1, _s2 = entities.get_entity_group('squads')[:2]
	_m_x, _m_y = x / constants.MAP_CELL_SPACE, y / constants.MAP_CELL_SPACE
	
	if button == 1:
		#for x, y in MAP['grid'].keys():
		_camp = MAP['grid'][_m_x, _m_y]
		
		if _camp['owned_by'] == 'Rogues' and not SELECTED_CAMP:
			SELECTED_CAMP = (_m_x, _m_y)
			
			set_draw_mode('camp_info')
		
		elif not _camp['owned_by'] == 'Rogues':
			if SELECTED_SQUAD:
				if _camp['owned_by']:
					set_draw_mode('raid')
				
				else:
					set_draw_mode('occupy')
				
				SELECTED_CAMP = (_m_x, _m_y)
			#set_draw_mode('camp_info')
		
		else:
			for squad_id in entities.get_entity_group('squads'):
				if squad_id == SELECTED_SQUAD:
					continue
				
				_squad = entities.get_entity(squad_id)
				
				if not movement.get_position(_squad) == (_m_x, _m_y):
					continue
				
				if not _squad['faction'] == 'Rogues':
					continue
				
				SELECTED_SQUAD = squad_id
				SELECTED_CAMP = None
				
				set_draw_mode('squad_info')
				
				break
	
	elif button == 2:
		events.unregister_event('mouse_moved', handle_mouse_moved)
		events.unregister_event('mouse_pressed', handle_mouse_pressed)
		
		world_action.start_battle(attacking_squads=[_s1], defending_squads=[_s1])
		
		set_draw_mode('news')

def draw():
	if SELECTED_SQUAD:
		_x, _y = movement.get_position(entities.get_entity(SELECTED_SQUAD))
		_selected_grid = _x, _y
	
	else:
		_selected_grid = None
	
	ui_strategy.draw_map_grid(selected_grid=_selected_grid)
	ui_strategy.draw_squads(selected_squad=SELECTED_SQUAD)
	
	if DRAW_MODE == 'squad_info':
		ui_strategy.draw_squad_info(SELECTED_SQUAD)
	
	elif DRAW_MODE == 'camp_info':
		ui_strategy.draw_camp_info(SELECTED_CAMP)
	
	elif DRAW_MODE == 'news':
		ui_strategy.draw_time()
		ui_strategy.draw_money()
		ui_strategy.draw_news()
	
	elif DRAW_MODE == 'raid':
		ui_strategy.draw_raid_info(SELECTED_SQUAD, SELECTED_CAMP)
	
	display.blit_surface('map_markers')
	display.blit_surface('map_squads')
	display.blit_surface_viewport('ui_bar',
	                              0,
	                              0,
	                              constants.WINDOW_WIDTH,
	                              constants.WINDOW_HEIGHT-constants.STRAT_MAP_HEIGHT,
	                              dy=constants.STRAT_MAP_HEIGHT)
	
	events.trigger_event('draw')

def loop():
	if not handle_input():
		return False
	
	draw()
	
	return True
