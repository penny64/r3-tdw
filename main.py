from framework import entities, controls, display, events, worlds, movement, pathfinding, numbers, stats

import framework

import post_processing
import ai_factions
import ai_visuals
import constants
import settings
import ui_cursor
import ui_input
import ui_menu
import ui_draw
import worldgen
import mapgen
import camera
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


def handle_input():
	if settings.TICK_MODE in ['normal', 'strategy']:
		if controls.get_input_ord_pressed(constants.KEY_ESCAPE):
			if ui_menu.get_active_menu():
				ui_menu.delete(ui_menu.get_active_menu())
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
	
	for entity_id in entities.get_entity_group('bullets'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')
	
	for entity_id in entities.get_entity_group('effects'):
		entities.trigger_event(entities.get_entity(entity_id), 'tick')
	
	ai_visuals.reset_moved_entities()

def draw():
	global MOVIE_TIME, MOVIE_TIME_MAX
	
	if settings.OBSERVER_MODE:
		_draw_life = entities.get_entity_group('life')
		_draw_items = entities.get_entity_group('items')
	else:
		_draw_life = [i for i in PLAYER['ai']['life_memory'] if PLAYER['ai']['life_memory'][i]['can_see']]
		_draw_life.append(PLAYER['_id'])
		
		_items = PLAYER['ai']['visible_items'].values()
		_draw_items = [item for _items in PLAYER['ai']['visible_items'].values() for item in _items]
	
	for entity_id in _draw_life:
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	for entity_id in entities.get_entity_group('nodes'):
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	if settings.SHOW_NODE_GRID:
		for entity_id in entities.get_entity_group('node_grid'):
			entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	for entity_id in entities.get_entity_groups(['effects', 'effects_freetick']):
		entities.trigger_event(entities.get_entity(entity_id), 'draw')
	
	for entity_id in _draw_items:
		_entity = entities.get_entity(entity_id)
		
		if _entity['stats']['owner']:
			continue
		
		entities.trigger_event(entities.get_entity(entity_id), 'draw', x_mod=camera.X, y_mod=camera.Y)
	
	ui_draw.draw_status_bar(planning=settings.TICK_MODE == 'strategy',
	                        executing=settings.TICK_MODE == 'normal' and PLAYER['node_grid']['path'],
	                        execute_speed='>' * numbers.clip(5-(stats.get_speed(PLAYER)/settings.PLAN_TICK_RATE), 1, 4) * (len(PLAYER['node_grid']['path'])>0),
	                        selecting=nodes.SELECTING_TARGET_CALLBACK)
	ui_draw.draw_life_labels()
	ui_draw.draw_item_labels()
	ui_draw.draw_node_grid(PLAYER)
	
	if '--fps' in sys.argv:
		ui_draw.draw_fps()
	
	events.trigger_event('post_process')
	display.blit_surface('nodes')
	display.blit_surface('items')
	display.blit_surface('life')
	display.blit_surface('ui')
	display.blit_surface('ui_menus')
	
	if settings.SHOW_NODE_GRID:
		display.blit_surface('node_grid')
	
	events.trigger_event('draw')
	
	#MOVIE_TIME += 1
	
	#if MOVIE_TIME == MOVIE_TIME_MAX:
	#	display.screenshot('screenshot-%s.bmp' % time.time())
	#	
	#	MOVIE_TIME = 0

def loop():
	events.trigger_event('input')
	
	if not settings.TICK_MODE == 'strategy':
		if PLAYER['node_grid']['path']:
			_ticks_per_tick = settings.PLAN_TICK_RATE
		else:
			_ticks_per_tick = 12
		
		_t = time.time()
		for _ in range(_ticks_per_tick):
			events.trigger_event('logic')
			tick()
	
	events.trigger_event('tick')
	events.trigger_event('camera')
	
	if not handle_input():
		return False
	
	draw()
	
	return True

def main():
	global PLAYER
	
	ai_factions.boot()
	
	PLAYER = life.human(170, 170, 'Tester Toaster')
	PLAYER['ai']['is_player'] = True

	#life.human_bandit(195, 135, 'Test NPC 3')
	items.ammo_9x19mm(170, 176)
	items.leather_backpack(176, 171)
	items.ammo_9x19mm(180, 175)
	items.leather_backpack(186, 170)
	items.glock(175, 176)
	items.glock(165, 166)
	#life._get_and_hold_item(PLAYER, items.glock(20, 20, ammo=17)['_id'])
	
	ui_cursor.boot()
	ai.boot()
	ui_input.boot(PLAYER)
	ui_draw.boot(PLAYER)
	ui_menu.boot()
	
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_movement)
	events.register_event('camera', camera.update)
	
	worldgen.generate()
	
	camera.set_pos(120, 120)
	
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
	entities.create_entity_group('systems')
	entities.create_entity_group('ui')
	entities.create_entity_group('ui_menus')
	entities.create_entity_group('nodes')
	entities.create_entity_group('effects_freetick')
	entities.create_entity_group('effects', static=True)

	display.create_surface('life', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('items', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('nodes', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('node_grid', width=constants.MAP_VIEW_WIDTH, height=constants.MAP_VIEW_HEIGHT)
	display.create_surface('ui')
	display.create_surface('ui_menus')
	display.set_clear_surface('ui', 'tiles')
	display.set_clear_surface('ui_menus', 'tiles')
	
	post_processing.start()
	
	framework.run(main)
