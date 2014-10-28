from framework import display, movement, entities, tile, timers, shapes, events, controls

import ui_dialog
import effects

import sys

DIRECTOR = False
HAS_FOCUS = None
PAUSE = False


def boot():
	global DIRECTOR
	
	_entity = entities.create_entity(group='systems')
	DIRECTOR = _entity
	
	events.register_event('input', handle_keyboard_input)
	
	timers.register(_entity)

def handle_keyboard_input():
	pass
	#if not HAS_FOCUS or not controls.get_input_char_pressed(' '):
	#	return False
	
	#lose_focus()

def focus_on_entity(entity, target_id, show_line=False, pause=False):
	global HAS_FOCUS, PAUSE
	
	if HAS_FOCUS or '--no-fx' in sys.argv:
		return
	
	HAS_FOCUS = target_id
	PAUSE = pause
	
	_entity = ui_dialog.create(18, 7, 'Enemy spotted!')
	
	entities.register_event(_entity, 'delete', lambda e: lose_focus())
	entities.trigger_event(DIRECTOR, 'create_timer', time=120, exit_callback=lambda e: ui_dialog.delete(_entity))
	
	if show_line:
		for x, y in shapes.line(movement.get_position(entity), movement.get_position_via_id(target_id)):
			effects.vapor(x, y, group='effects_freetick', start_alpha=1.0, fade_rate=.01)

def lose_focus():
	global HAS_FOCUS, PAUSE
	
	HAS_FOCUS = None
	PAUSE = False

def draw():
	_entity = entities.get_entity(HAS_FOCUS)
	_x, _y = movement.get_position(_entity)
	_char = tile.get_char(_entity)
	
	for y in range(12):
		display.write_char('ui', 4, 4 + y + 1, ' ', back_color=(20, 20, 20))
		display.write_char('ui', 4 + 12, 4 + y, ' ', back_color=(40, 40, 40))
		display.write_char('ui', 4 + y, 4, ' ', back_color=(20, 20, 20))
		display.write_char('ui', 4 + y + 1, 4 + 12, ' ', back_color=(40, 40, 40))
	
	display.blit_surface_viewport('tiles', _x-5, _y-5, 11, 11, dx=5, dy=5)
	display.write_char('ui', 10, 10, _char, fore_color=_entity['tile']['fore_color'])
