from framework import movement, entities, controls, events, stats, numbers

import ai_debugger
import constants
import ui_cursor
import ui_menu
import camera

import settings


def boot(entity):
	events.register_event('input', lambda: handle_keyboard_input(entity))

def handle_keyboard_input(entity):
	if controls.get_input_char_pressed('1'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .1)))
	
	elif controls.get_input_char_pressed('2'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .25)))
	
	elif controls.get_input_char_pressed('3'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .4)))
	
	elif controls.get_input_char_pressed('4'):
		settings.set_plan_tick_rate(int(round(stats.get_speed(entity) * .55)))
	
	if controls.get_input_char_pressed('\t'):
		_x, _y = movement.get_position(entity)
		
		camera.set_pos(_x - constants.MAP_VIEW_WIDTH/2, _y - constants.MAP_VIEW_HEIGHT/2)
	
	if controls.get_input_char_pressed('z'):
		entities.delete_entity(entity)
	
	if controls.get_input_char_pressed('O'):
		settings.toggle_show_node_grid()
	
	elif controls.get_input_char_pressed('o'):
		settings.toggle_observer_mode()
	
	if controls.get_input_char_pressed('d'):
		_mx, _my = ui_cursor.get_map_position()
		
		for entity_id in entities.get_entity_group('life'):
			_entity = entities.get_entity(entity_id)
			
			if not numbers.distance((_mx, _my), movement.get_position(_entity)):
				_x, _y = ui_cursor.get_screen_position()
				_menu = ui_menu.create(_x, _y, title='Debug')
				ui_menu.add_selectable(_menu, 'Show Metas', lambda: _show_metas(_entity))
				ui_menu.add_selectable(_menu, 'Overwatch', lambda: ai_debugger.register(_entity))
				
				break
				
def _show_metas(entity):
	_x, _y = ui_cursor.get_screen_position()
	_menu = ui_menu.create(_x, _y, title='Metas')
	_keys = entity['ai']['meta'].keys()
	_keys.sort()
	
	for meta_key in _keys:
		if entity['ai']['meta'][meta_key]:
			_color = (0, 200, 0)
		else:
			_color = (200, 0, 0)
		
		ui_menu.add_selectable(_menu, '%s: %s' % (meta_key, entity['ai']['meta'][meta_key]), lambda: _show_metas(_entity), fore_color=_color)
