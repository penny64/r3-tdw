from framework import entities, display, events

import ui_cursor

ACTIVE_MENU = None
DELAY = 0


def boot():
	events.register_event('mouse_pressed', handle_mouse_pressed)
	events.register_event('mouse_moved', handle_mouse_moved)
	events.register_event('draw', draw_all)
	events.register_event('tick', tick)

def tick():
	global DELAY
		
	if DELAY > 0:
		DELAY -= 1

def create(x, y, title=None, surface='ui_menus', click_offset=(0, 0)):
	global ACTIVE_MENU
	
	_entity = entities.create_entity(group='ui_menus')
	_entity.update({'items': {},
	                'active': True,
	                'index': 0,
	                'item_id': 0,
	                'surface': surface,
	                'click_offset': click_offset,
	                'x': x,
	                'y': y})
	
	entities.create_event(_entity, 'reactivated')
	
	if title:
		add_title(_entity, title)
		
		_entity['index'] = 1
	
	ACTIVE_MENU = _entity
	
	return _entity

def delete(menu):
	global ACTIVE_MENU, DELAY
	
	entities.delete_entity(menu)
	
	if ACTIVE_MENU == menu:
		_menus = entities.get_entity_group('ui_menus')
		
		if _menus:		
			ACTIVE_MENU = entities.get_entity(_menus[len(_menus)-1])
			entities.trigger_event(ACTIVE_MENU, 'reactivated')
			
		else:
			ACTIVE_MENU = None
	
	DELAY = 30

def get_next_item_id(menu):
	_id = menu['item_id']
	
	menu['item_id'] += 1
	
	return _id

def set_active_menu(menu):
	global ACTIVE_MENU
	
	ACTIVE_MENU = menu

def get_active_menu():
	return ACTIVE_MENU

def handle_mouse_moved(x, y, dx, dy):
	_menu = get_active_menu()
	
	if not _menu:
		return
	
	_m_x, _m_y = _menu['x'] + _menu['click_offset'][0], _menu['y'] + _menu['click_offset'][1]
	
	if x >= _m_x and x <= _m_x+10 and y >= _m_y and y <= _m_y+(len(_menu['items']) * 3):
		_selected_index = (y-_m_y) / 3
		
		if _selected_index >= len(_menu['items']):
			return False
		
		_item = _menu['items'][_selected_index]
		
		if not _item['selectable']:
			return
		
		_menu['index'] = _selected_index
	else:
		_menu['index'] = -1

def handle_mouse_pressed(x, y, button):
	_menu = get_active_menu()
	
	if not _menu:
		return
	
	_m_x, _m_y = _menu['x'] + _menu['click_offset'][0], _menu['y'] + _menu['click_offset'][1]
	
	if button == 2:
		delete(ACTIVE_MENU)
		
		return
	
	if x >= _m_x and x <= _m_x+10 and y >= _m_y and y <= _m_y+(len(_menu['items']) * 3):
		_selected_index = (y-_m_y) / 3
		
		if _selected_index >= len(_menu['items']):
			return False
		
		_item = _menu['items'][_selected_index]
		
		if not _item['selectable']:
			return
		
		_menu['index'] = _selected_index
		
		select(_menu)

def move_up(menu):
	_walk_index = menu['index']-1
	
	while _walk_index >= 0:
		if menu['items'][_walk_index]['selectable']:
			menu['index'] = _walk_index
			
			return
		
		_walk_index -= 1
		

def move_down(menu):
	_walk_index = menu['index']+1
	
	while _walk_index < len(menu['items']):
		if menu['items'][_walk_index]['selectable']:
			menu['index'] = _walk_index
			
			return
		
		_walk_index += 1

def get_current_item(menu):
	return menu['items'][menu['index']]

def select(menu):
	_item = get_current_item(menu)
	
	if _item['close_on_select']:
		delete(menu)
	
	return _item['callback'](**_item['kwargs'])

def add_title(menu, text, fore_color=(255, 255, 255), back_color=(45, 45, 45)):
	_id = get_next_item_id(menu)
	
	menu['items'][_id] = {'text': text,
	                      'selectable': False,
	                      'fore_color': fore_color,
	                      'back_color': back_color}

def add_selectable(menu, text, callback, fore_color=(230, 230, 230), back_color=(1, 1, 1), close_on_select=True, **kwargs):
	_id = get_next_item_id(menu)
	
	menu['items'][_id] = {'text': text,
	                      'callback': callback,
	                      'kwargs': kwargs,
	                      'selectable': True,
	                      'fore_color': fore_color,
	                      'back_color': back_color,
	                      'close_on_select': close_on_select}

def draw(menu):
	_y_mod = 0
	_yy_mod = 0
	
	for item_id in menu['items']:
		_item = menu['items'][item_id]
		_text = ' %s '% _item['text']
	
		if ACTIVE_MENU == menu and menu['index'] == _y_mod:
			_back_color = (65, 65, 65)
		else:
			_back_color = _item['back_color']
		
		for i in range(-1, 2):
			if i:
				display.write_string(menu['surface'], menu['x'], menu['y']+_y_mod+_yy_mod, ' ' * len(_text), fore_color=_item['fore_color'], back_color=_back_color)
			else:
				display.write_string(menu['surface'], menu['x'], menu['y']+_y_mod+_yy_mod, _text, fore_color=_item['fore_color'], back_color=_back_color)
			
			_yy_mod += 1
		
		_yy_mod -= 1
		_y_mod += 1

def draw_all():
	for menu_id in entities.get_entity_group('ui_menus'):
		draw(entities.get_entity(menu_id))
