from framework import entities, controls, display, events, worlds, movement, pathfinding, numbers, stats, timers, shapes

import framework

import post_processing
import mapgen_arena
import ai_factions
import ai_visuals
import ai_squads
import ai_flow
import constants
import settings
import ui_squad_control
import ui_director
import ui_dialog
import ui_cursor
import ui_panel
import ui_input
import ui_menu
import ui_draw
import missions
import worldgen
import mapgen
import camera
import zones
import items
import nodes
import maps
import life
import ai

import cProfile
import random
import numpy
import time
import sys

MOVIE_TIME = 0
MOVIE_TIME_MAX = 10
PLAYER_HAS_SHOOT_TIMER = False


def create():
	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('bullets', static=True)
	entities.create_entity_group('node_grid', static=True)
	entities.create_entity_group('missions', static=True)
	entities.create_entity_group('ui')
	entities.create_entity_group('ui_menus')
	entities.create_entity_group('ui_dialogs')
	entities.create_entity_group('nodes')
	entities.create_entity_group('effects_freetick')
	entities.create_entity_group('ui_effects_freetick')
	entities.create_entity_group('contexts')
	entities.create_entity_group('effects', static=True)
	entities.create_entity_group('ui_effects', static=True)

	display.create_surface('life', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('items', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('nodes', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('node_grid', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('effects', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('ui_inventory', width=35, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('ui')
	display.create_surface('ui_menus')
	display.create_surface('ui_dialogs')
	
	display.set_clear_surface('effects', 'tiles')
	display.set_clear_surface('ui_menus', 'tiles')
	display.set_clear_surface('ui_dialogs', 'tiles')
	display.set_clear_surface('ui', 'tiles')
	display.set_clear_surface('life', 'tiles')
	display.set_clear_surface('nodes', 'tiles')
	display.set_clear_surface('effects', 'tiles')
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('camera', camera.update)
	
	camera.set_pos(0, 0)
	
	ui_cursor.boot()
	ai.boot()
	ui_input.boot()
	ui_draw.boot()
	ui_menu.boot()
	ui_dialog.boot()
	ui_director.boot()

def start_battle(attacking_squads=[], defending_squads=[]):
	create()
	
	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside, _lights, _spawns = mapgen_arena.generate(200, 200)
	_zone = zones.create('swamps', _width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside, _lights, _spawns)
	_attacking_spawn_x, _attacking_spawn_y = random.choice(list(_spawns['attacking']))
	_attacking_spawn_positions = [(x, y) for x, y in shapes.circle(_attacking_spawn_x, _attacking_spawn_y, 5) if not (x, y) in _solids]
	
	for squad_id in attacking_squads:
		_squad = entities.get_entity(squad_id)
		
		for member_id in _squad['members']:
			_member = entities.get_entity(member_id)
			_spawn_x, _spawn_y = _attacking_spawn_positions.pop(random.randint(0, len(_attacking_spawn_positions) - 1))
			
			entities.trigger_event(_member, 'set_position', x=_spawn_x, y=_spawn_y)
	
	_defending_spawn_x, _defending_spawn_y = random.choice(list(_spawns['defending']))
	_attacking_spawn_positions = [(x, y) for x, y in shapes.circle(_defending_spawn_x, _defending_spawn_y, 5) if not (x, y) in _solids]
	
	for squad_id in defending_squads:
		_squad = entities.get_entity(squad_id)
		
		for member_id in _squad['members']:
			_member = entities.get_entity(member_id)
			_spawn_x, _spawn_y = _attacking_spawn_positions.pop(random.randint(0, len(_attacking_spawn_positions) - 1))
			
			entities.trigger_event(_member, 'set_position', x=_spawn_x, y=_spawn_y)

	zones.activate(_zone)
	
	display.blit_background('tiles')
	
	while loop():
		events.trigger_event('cleanup')

def handle_input():
	if settings.TICK_MODE in ['normal', 'strategy']:
		if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
			if ui_dialog.get_active_dialog():
				ui_dialog.delete(ui_dialog.get_active_dialog())
				
			elif ui_menu.get_active_menu():
				_menu = ui_menu.get_active_menu()

				ui_menu.delete(_menu)

				if ui_panel.ACTIVE_MENU == _menu:
					ui_panel.close()
			else:
				return False

		if settings.TICK_MODE == 'strategy':
			ui_squad_control.handle_keyboard_input()

	if controls.get_input_char_pressed('k'):
		display.screenshot('screenshot-%s.bmp' % time.time())

	return True

def handle_mouse_movement(x, y, **kwargs):
	if settings.TICK_MODE == 'strategy':
		ui_squad_control.handle_mouse_movement(x, y)

def handle_mouse_pressed(x, y, button):
	if settings.TICK_MODE == 'strategy':
		ui_squad_control.handle_mouse_pressed(x, y, button)

	elif settings.TICK_MODE == 'normal':
		_c_x = (camera.X+x) - (constants.MAP_VIEW_WIDTH/2)
		_c_y = (camera.Y+y) - (constants.MAP_VIEW_HEIGHT/2)

		if button == 1:
			camera.set_pos(_c_x, _c_y)

def tick():
	if entities.get_entity_group('bullets'):
		for i in range(4):
			for entity_id in entities.get_entity_group('bullets'):
				entities.trigger_event(entities.get_entity(entity_id), 'tick')
	
	else:
		ai_flow.tick()

	for entity_id in entities.get_entity_group('effects'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

	for entity_id in entities.get_entity_group('ui_effects'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

	ai_visuals.reset_moved_entities()
	post_tick()

def free_tick():
	for entity_id in entities.get_entity_group('effects_freetick'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

def post_tick():
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'post_tick')

def draw():
	global MOVIE_TIME, MOVIE_TIME_MAX

	if settings.OBSERVER_MODE:
		_draw_life = entities.get_entity_group('life')
		_draw_items = entities.get_entity_group('items')
	else:
		_draw_life = set()
		_draw_items = set()
		
		for squad_id in entities.get_entity_group('squads'):
			_squad = entities.get_entity(squad_id)
			
			if not _squad['faction'] == 'Rogues':
				continue
			
			for member_id in _squad['members']:
				_member = entities.get_entity(member_id)
				_draw_life.add(member_id)
				_draw_life.update([i for i in _member['ai']['life_memory'] if _member['ai']['life_memory'][i]['can_see'] and i in entities.ENTITIES])

		_draw_life = list(_draw_life)

	for entity_id in _draw_life:
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	if settings.SHOW_NODE_GRID:
		for entity_id in zones.get_active_node_grid().values():
			entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	for entity_id in entities.get_entity_groups(['ui_effects', 'ui_effects_freetick']):
		entities.trigger_event(entities.get_entity(entity_id), 'draw')

	for entity_id in entities.get_entity_groups(['effects', 'effects_freetick']):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	for entity_id in entities.get_entity_group('contexts'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	for entity_id in _draw_items:
		if not entity_id in entities.ENTITIES:
			continue

		_entity = entities.get_entity(entity_id)

		if _entity['stats']['owner']:
			continue

		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)

	ui_draw.draw_status_bar(planning=settings.TICK_MODE == 'strategy',
	                        executing=not settings.TICK_MODE == 'strategy',
	                        execute_speed=settings.PLAN_TICK_RATE_STRING,
	                        selecting=nodes.SELECTING_TARGET_CALLBACK)

	#if settings.TICK_MODE == 'strategy':
	#	ui_draw.draw_item_labels()
	
	if '--labels' in sys.argv:
		ui_draw.draw_life_labels()
	
	ui_draw.draw_long_range_life()
	ui_draw.draw_life_memory()
	ui_draw.draw_walk_path()
	#ui_draw.draw_mission_details()
	ui_draw.draw_turn_bar()

	if '--fps' in sys.argv:
		ui_draw.draw_fps()

	events.trigger_event('post_process')
	
	#display.reset_surface_shaders('tiles')
	
	#_zone = zones.ZONES[zones.ACTIVE_ZONE]	
	#for shader in _zone['shaders']:
	#	display.apply_surface_shader('tiles', shader, constants.MAP_VIEW_WIDTH, constants.MAP_VIEW_HEIGHT)
	
	if ui_director.HAS_FOCUS:
		ui_director.draw()
	
	display.blit_surface('effects')
	display.blit_surface('nodes')
	display.blit_surface('items')
	display.blit_surface('life')
	display.blit_surface('ui')
	display.blit_surface('ui_menus')
	display.blit_surface('ui_dialogs')

	if ui_panel.ACTIVE_MENU:
		display.blit_surface_viewport('ui_inventory', 0, 0, 35, constants.MAP_VIEW_HEIGHT, dx=constants.MAP_VIEW_WIDTH-35)

	if settings.SHOW_NODE_GRID:
		display.blit_surface('node_grid')

	events.trigger_event('draw')

	if '--record' in sys.argv:
		MOVIE_TIME += 1
	
		if MOVIE_TIME == MOVIE_TIME_MAX:
			display.screenshot('screenshot-%s.bmp' % time.time())
			
			MOVIE_TIME = 0

def loop():
	global PLAYER_HAS_SHOOT_TIMER
	
	events.trigger_event('input')

	if not settings.TICK_MODE == 'strategy' and not ((ui_dialog.ACTIVE_DIALOG and ui_director.PAUSE) or ui_menu.ACTIVE_MENU or ui_director.PAUSE):
		_has_action = False
		
		_check_life = set()
		
		for squad_id in entities.get_entity_group('squads'):
			_squad = entities.get_entity(squad_id)
			
			if not _squad['faction'] == 'Rogues':
				continue
			
			for member_id in _squad['members']:
				_member = entities.get_entity(member_id)
				
				_check_life.add(member_id)
				_check_life.update([i for i in _member['ai']['life_memory'] if _member['ai']['life_memory'][i]['can_see'] and i in entities.ENTITIES])

		_check_life = list(_check_life)
		
		#_check_life = 
		#_check_life.append(PLAYER['_id'])
		
		for entity_id in _check_life:
			if timers.has_timer_with_name(entities.get_entity(entity_id), 'shoot'):
				_has_action = True
				
				break
		
		if _has_action:
			_ticks_per_tick = 1
		
		else:
			_ticks_per_tick = settings.PLAN_TICK_RATE
		
		for _ in range(_ticks_per_tick):
			if settings.TICK_MODE == 'strategy':
				break
			
			ai_flow.logic()
			events.trigger_event('logic')
			tick()
			free_tick()
	
	else:
		ai_flow.logic()
		free_tick()

	if pathfinding.wait_for_astar():
		pass

	if not handle_input():
		return False

	events.trigger_event('tick')
	events.trigger_event('camera')
	
	draw()

	return True
