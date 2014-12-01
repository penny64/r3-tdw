from framework import display, worlds, entities, events, controls, movement, pathfinding

import world_action
import ui_strategy
import ai_factions
import constants
import worldgen
import main

import random
import numpy

SELECTED_SQUAD = None
SELECTED_CAMP = None
MAP_PATH = []
DRAW_MODE = 'news'
MAP = None
_DEBUG_ORD = 10
TIME = 14 * 60
NEWS = [('> Contact lost with camp C2.', (200, 200, 200), None),
        ('> Supplies arrived at A6.', (200, 200, 200), (50, 50, 50))]


def create():
	global MAP
	
	worlds.create('strategy')
	
	display.create_surface('background')
	display.create_surface('map', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_markers', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_squads', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('map_path', width=constants.STRAT_MAP_WIDTH, height=constants.STRAT_MAP_HEIGHT)
	display.create_surface('ui_bar', width=constants.WINDOW_WIDTH, height=constants.WINDOW_HEIGHT-constants.STRAT_MAP_HEIGHT)
	
	display.blit_background('background')
	
	register_input()
	
	entities.create_entity_group('life', static=True)
	entities.create_entity_group('items', static=True)
	entities.create_entity_group('factions', static=True)
	entities.create_entity_group('squads', static=True)
	entities.create_entity_group('systems')
	
	_grid = {}
	_color_map = {}
	
	MAP = {'grid': _grid,
	       'color_map': _color_map,
	       'astar_map': None,
	       'astar_weight_map': numpy.ones((constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE,
	                                       constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE))}
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_grid[x, y] = {'owned_by': None,
			               'is_ownable': False,
			               'squads': [],
			               'income': .025}
	
	worldgen.generate()

def register_input():
	events.register_event('mouse_moved', handle_mouse_moved)
	events.register_event('mouse_pressed', handle_mouse_pressed)

def unregister_input():
	events.unregister_event('mouse_moved', handle_mouse_moved)
	events.unregister_event('mouse_pressed', handle_mouse_pressed)

def news(text, fore_color=(200, 200, 200), back_color=None):
	NEWS.append((text, fore_color, back_color))

def set_draw_mode(mode):
	global DRAW_MODE
	
	DRAW_MODE = mode
	
	ui_strategy.clear_bar()

def handle_input():
	global _DEBUG_ORD, SELECTED_CAMP, SELECTED_SQUAD
	
	events.trigger_event('input')
	
	if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
		if not DRAW_MODE == 'news':
			if SELECTED_SQUAD:
				SELECTED_SQUAD = None
				
				if SELECTED_CAMP:
					set_draw_mode('camp_info')
				
				else:
					set_draw_mode('news')
			
			else:
				SELECTED_SQUAD = None
				SELECTED_CAMP = None
				
				set_draw_mode('news')
		
		else:
			return False
	
	if controls.get_input_char_pressed('z'):
		_DEBUG_ORD -= 1
		print _DEBUG_ORD
	
	elif controls.get_input_char_pressed('x'):
		_DEBUG_ORD += 1
		print _DEBUG_ORD
	
	return True

def handle_mouse_moved(x, y, dx, dy):
	return

def handle_mouse_pressed(x, y, button):
	global SELECTED_SQUAD, SELECTED_CAMP, MAP_PATH
	
	_s1, _s2 = entities.get_entity_group('squads')[:2]
	_m_x, _m_y = x / constants.MAP_CELL_SPACE, y / constants.MAP_CELL_SPACE
	
	if button == 1:
		_camp = MAP['grid'][_m_x, _m_y]
		
		if _camp['owned_by'] == 'Rogues' and not SELECTED_CAMP:
			SELECTED_CAMP = (_m_x, _m_y)
			
			set_draw_mode('camp_info')
		
		elif not _camp['owned_by'] == 'Rogues':
			if SELECTED_SQUAD:
				if _camp['owned_by']:
					SELECTED_CAMP = (_m_x, _m_y)
					MAP_PATH = pathfinding.astar(movement.get_position_via_id(_s1), (_m_x, _m_y), MAP['astar_map'], MAP['astar_weight_map'])
					
					set_draw_mode('raid')
				
				elif _camp['is_ownable']:
					SELECTED_CAMP = (_m_x, _m_y)
					
					set_draw_mode('occupy')
				
				else:
					SELECTED_SQUAD = None
					SELECTED_CAMP = None
					
					set_draw_mode('news')
				
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
		_camp = MAP['grid'][_m_x, _m_y]
		
		if not _camp['owned_by'] == 'Rogues':
			if SELECTED_SQUAD:
				if DRAW_MODE == 'raid':
					entities.trigger_event(entities.get_entity(SELECTED_SQUAD), 'raid', camp_id=(_m_x, _m_y))
					
					SELECTED_SQUAD = None
					SELECTED_CAMP = None
					
					set_draw_mode('news')

def tick():
	global TIME
	
	for squad_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(squad_id)
		
		entities.trigger_event(_squad, 'logic')
	
	for x, y in MAP['grid'].keys():
		_camp = MAP['grid'][x, y]
		
		if _camp['is_ownable'] and _camp['owned_by']:
			ai_factions.FACTIONS[_camp['owned_by']]['money'] += _camp['income']
	
	for squad_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(squad_id)
		
		entities.trigger_event(_squad, 'tick')
	
	TIME += 0.01

def draw():
	if SELECTED_SQUAD:
		_x, _y = movement.get_position(entities.get_entity(SELECTED_SQUAD))
		_selected_grid = _x, _y
	
	else:
		_selected_grid = None
	
	ui_strategy.draw_map_grid(selected_grid=_selected_grid)
	ui_strategy.draw_squads(selected_squad=SELECTED_SQUAD)	
	ui_strategy.draw_time()
	ui_strategy.draw_money()
	
	if DRAW_MODE == 'squad_info':
		ui_strategy.draw_squad_info(SELECTED_SQUAD)
	
	elif DRAW_MODE == 'camp_info':
		ui_strategy.draw_camp_info(SELECTED_CAMP)
	
	elif DRAW_MODE == 'news':
		ui_strategy.draw_news(NEWS)
	
	elif DRAW_MODE == 'raid':
		ui_strategy.draw_raid_info(SELECTED_SQUAD, SELECTED_CAMP)
		ui_strategy.draw_raid_path(MAP_PATH)
		
		display.blit_surface('map_path')
	
	display.blit_surface('map_markers')
	display.blit_surface('map_squads')
	display.blit_surface_viewport('ui_bar',
	                              0,
	                              0,
	                              constants.WINDOW_WIDTH,
	                              constants.WINDOW_HEIGHT-constants.STRAT_MAP_HEIGHT,
	                              dy=constants.STRAT_MAP_HEIGHT)
	
	events.trigger_event('draw')
	display.reset_surface_shaders('map')

def loop():
	if not handle_input():
		return False
	
	tick()
	draw()
	
	return True
