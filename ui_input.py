from framework import movement, entities, controls, events, stats, numbers

import ai_debugger
import constants
import ui_cursor
import ui_panel
import ui_menu
import effects
import camera
import zones

import settings

import random


def boot():
	events.register_event('input', handle_keyboard_input)

def handle_keyboard_input():
	if controls.get_input_char_pressed('\t'):
		if settings.TICK_MODE == 'strategy':
			if ui_panel.ACTIVE_MENU:
				ui_panel.close()
			else:
				ui_panel.show_inventory(entity)
		
		else:
			_x, _y = movement.get_position(entity)
			
			camera.set_pos(_x - constants.MAP_VIEW_WIDTH/2, _y - constants.MAP_VIEW_HEIGHT/2)
	
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
				ui_menu.add_selectable(_menu, 'Kill', lambda: entities.trigger_event(_entity, 'kill'))
				ui_menu.add_selectable(_menu, 'Overwatch', lambda: ai_debugger.register(_entity))
				
				break
	
	if controls.get_input_char_pressed('l'):
		_x, _y = ui_cursor.get_screen_position()
		_mx, _my = ui_cursor.get_map_position()
		_weight = zones.get_active_weight_map()[_my, _mx]
		_menu = ui_menu.create(_x, _y, title='Tile Info')
		
		ui_menu.add_selectable(_menu, 'Warp', lambda: entities.trigger_event(entity, 'set_position', x=_mx, y=_my))
		ui_menu.add_selectable(_menu, 'Light', lambda: effects.light(_mx, _my, 15, r=random.uniform(1.0, 1.5), g=random.uniform(1.0, 1.5), light_map='static_lighting'))
		ui_menu.add_selectable(_menu, 'Weight: %s' % _weight, lambda: _)
				
def _show_metas(entity):
	_keys = entity['ai']['meta'].keys()
	_keys.sort()
	
	for meta_key in _keys:
		print meta_key, entity['ai']['meta'][meta_key]
	return
	_menu = ui_menu.create(0, 0, title='Metas')
	_keys = entity['ai']['meta'].keys()
	_keys.sort()
	
	for meta_key in _keys:
		if entity['ai']['meta'][meta_key]:
			_color = (0, 200, 0)
		else:
			_color = (200, 0, 0)
		
		ui_menu.add_selectable(_menu, '%s: %s' % (meta_key, entity['ai']['meta'][meta_key]), lambda: _show_metas(_entity), fore_color=_color)
