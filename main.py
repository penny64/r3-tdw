from framework import entities, controls, display, events, worlds, movement, pathfinding, numbers, stats, timers

import framework

import post_processing
import ai_factions
import ai_visuals
import ai_squads
import constants
import settings
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

import numpy
import time
import sys

MOVIE_TIME = 0
MOVIE_TIME_MAX = 30
PLAYER_HAS_SHOOT_TIMER = False


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

		if controls.get_input_char_pressed(' '):
			if settings.TICK_MODE == 'strategy':
				settings.TICK_MODE = 'normal'
			else:
				settings.TICK_MODE = 'strategy'

		if settings.TICK_MODE == 'strategy':
			nodes.handle_keyboard_input(PLAYER)

	return True

def handle_mouse_movement(x, y, **kwargs):
	if settings.TICK_MODE == 'strategy':
		nodes.handle_mouse_movement(PLAYER, x, y, x+camera.X, y+camera.Y)

def handle_mouse_pressed(x, y, button):
	if settings.TICK_MODE == 'strategy':
		nodes.handle_mouse_pressed(PLAYER, x, y, button)

	elif settings.TICK_MODE == 'normal':
		_c_x = (camera.X+x) - (constants.MAP_VIEW_WIDTH/2)
		_c_y = (camera.Y+y) - (constants.MAP_VIEW_HEIGHT/2)

		if button == 1:
			camera.set_pos(_c_x, _c_y)

def tick():
	for entity_id in entities.get_entity_group('life'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

	for i in range(16):
		for entity_id in entities.get_entity_group('bullets'):
			entities.trigger_event(entities.get_entity(entity_id), 'tick')

	for entity_id in entities.get_entity_group('effects'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

	for entity_id in entities.get_entity_group('ui_effects'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')

	ai_visuals.reset_moved_entities()

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
		_draw_life = [i for i in PLAYER['ai']['life_memory'] if PLAYER['ai']['life_memory'][i]['can_see']]

		if PLAYER['_id'] in entities.ENTITIES:
			_draw_life.append(PLAYER['_id'])

		_items = PLAYER['ai']['visible_items'].values()
		_draw_items = [item for _items in PLAYER['ai']['visible_items'].values() for item in _items]

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

	if settings.TICK_MODE == 'strategy':
		ui_draw.draw_life_labels()
		ui_draw.draw_item_labels()
	
	ui_draw.draw_long_range_life()
	ui_draw.draw_life_memory()
	ui_draw.draw_node_path(PLAYER)
	ui_draw.draw_mission_details()

	if '--fps' in sys.argv:
		ui_draw.draw_fps()

	events.trigger_event('post_process')
	
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

	#MOVIE_TIME += 1

	#if MOVIE_TIME == MOVIE_TIME_MAX:
	#	display.screenshot('screenshot-%s.bmp' % time.time())
	#	
	#	MOVIE_TIME = 0

def loop():
	global PLAYER_HAS_SHOOT_TIMER
	
	events.trigger_event('input')

	if not settings.TICK_MODE == 'strategy' and not (ui_dialog.ACTIVE_DIALOG or ui_menu.ACTIVE_MENU or ui_director.HAS_FOCUS):
		_has_action = False
		_check_life = [i for i in PLAYER['ai']['life_memory'] if PLAYER['ai']['life_memory'][i]['can_see']]
		_check_life.append(PLAYER['_id'])
		
		for entity_id in _check_life:
			if timers.has_timer_with_name(entities.get_entity(entity_id), 'shoot'):
				_has_action = True
				
				break
		
		if _has_action:
			_ticks_per_tick = 1
		
		else:#elif PLAYER['node_grid']['path']:
			_ticks_per_tick = settings.PLAN_TICK_RATE
		
		#else:
		#	_ticks_per_tick = 1

		for _ in range(_ticks_per_tick):
			if timers.has_timer_with_name(PLAYER, 'shoot'):
				PLAYER_HAS_SHOOT_TIMER = True
			
			else:
				if PLAYER_HAS_SHOOT_TIMER:
					settings.set_tick_mode('strategy')
					PLAYER_HAS_SHOOT_TIMER = False
					
					break
			
			if settings.TICK_MODE == 'strategy':
				break
			
			events.trigger_event('logic')
			tick()
			free_tick()
	
	else:
		free_tick()

	if pathfinding.wait_for_astar():
		pass

	events.trigger_event('tick')
	events.trigger_event('camera')

	post_tick()

	if not handle_input():
		return False

	draw()

	return True

def main():
	global PLAYER

	ai_factions.boot()
	ai_squads.boot()
	missions.boot()

	PLAYER = life.human(210, 210, 'Tester Toaster')
	PLAYER['ai']['is_player'] = True

	ui_cursor.boot()
	ai.boot()
	ui_input.boot(PLAYER)
	ui_draw.boot(PLAYER)
	ui_menu.boot()
	ui_dialog.boot()
	ui_director.boot()

	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('camera', camera.update)

	worldgen.generate()
	
	for entity_id in entities.get_entity_group('life'):
		_entity = entities.get_entity(entity_id)
		
		if _entity['stats']['name'] == 'Trader':
			_trader = _entity
			
			break
		
	_mutated_wild_dog = life.mutated_wild_dog(10, 10, 'Mutated Wild Dog')
	
	_m = missions.create('Kill the Wild Dog', '''   I\'ve got one last thing I want you to do before I set you loose:
We\'re always seeing Wild Dogs running around the swamps, so now\'s a good time
to see what kind of shooter you are.

   Take this pistol and wander around the swamps until one of those beasts shows up,
then put a round in it, cut off its tail, and bring it back here.''')
	missions.add_goal_kill_npc(_m, _mutated_wild_dog['_id'])
	missions.add_goal_get_item(_m, 'Mutated Wild Dog Tail')
	entities.trigger_event(_trader, 'add_mission', mission_id=_m['_id'], make_active=False)
	
	life.create_life_memory(_trader, _mutated_wild_dog['_id'])
	_trader['ai']['life_memory'][_mutated_wild_dog['_id']]['last_seen_at'] = movement.get_position_via_id(_mutated_wild_dog['_id'])
	
	camera.set_pos(150, 150)
	#entities.save()

	while loop():
		events.trigger_event('cleanup')

		continue

	framework.shutdown()

if __name__ == '__main__':
	framework.init()

	worlds.create('main')

	entities.create_entity_group('tiles', static=True)
	entities.create_entity_group('life', static=True)
	entities.create_entity_group('items', static=True)
	entities.create_entity_group('bullets', static=True)
	entities.create_entity_group('node_grid', static=True)
	entities.create_entity_group('squads', static=True)
	entities.create_entity_group('factions', static=True)
	entities.create_entity_group('missions', static=True)
	entities.create_entity_group('systems')
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

	post_processing.start()

	framework.run(main)