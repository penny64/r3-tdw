from framework import entities, display, events

import ui_cursor

ACTIVE_DIALOG = None


def boot():
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_moved)
	events.register_event('draw', lambda: draw_all('ui_dialogs'))

def create(x, y, text, buttons=None, title='Dialog'):
	global ACTIVE_DIALOG
	
	_entity = entities.create_entity(group='ui_dialogs')
	_entity.update({'text': text,
	                'title': title,
	                'buttons': buttons,
	                'x': x,
	                'y': y})
	
	entities.create_event(_entity, 'reactivated')
	
	ACTIVE_DIALOG = _entity
	
	return _entity

def delete(dialog):
	global ACTIVE_DIALOG
	
	entities.delete_entity(dialog)
	
	if ACTIVE_DIALOG == dialog:
		_dialogs = entities.get_entity_group('ui_dialogs')
		
		if _dialogs:		
			ACTIVE_DIALOG = entities.get_entity(_dialogs[len(_dialogs)-1])
			entities.trigger_event(ACTIVE_DIALOG, 'reactivated')
			
		else:
			ACTIVE_DIALOG = None

def get_active_dialog():
	return ACTIVE_DIALOG

def handle_mouse_moved(x, y, dx, dy):
	_dialog = get_active_dialog()
	
	if not _dialog:
		return

def handle_mouse_pressed(x, y, button):
	_dialog = get_active_dialog()
	
	if not _dialog:
		return

def draw(dialog, surface):
	_y_mod = 0
	_text = dialog['text'].split('\n')
	_widest = max([len(l) for l in _text]) + 2
	
	for i in range(-3, 3):
		if i == -3:
			display.write_string(surface,
			                     dialog['x'],
			                     dialog['y']+_y_mod,
			                     ' %s ' % dialog['title'] + ' ' * ((_widest - len(dialog['title']))-2),
			                     fore_color=(250, 250, 250),
			                     back_color=(60, 60, 60))
			_y_mod += 1
			
		elif i:
			display.write_string(surface, dialog['x'], dialog['y']+_y_mod, ' ' * _widest, back_color=(10, 10, 10))
			
			_y_mod += 1
		
		else:
			for line in _text:
				display.write_string(surface, dialog['x'], dialog['y']+_y_mod, ' %s ' % (line + ' ' * (_widest-len(line)-2)), back_color=(10, 10, 10))
				
				_y_mod += 1

def draw_all(surface):
	for dialog_id in entities.get_entity_group('ui_dialogs'):
		draw(entities.get_entity(dialog_id), surface)