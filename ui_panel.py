from framework import display, entities, events

import constants
import ui_menu
import items

ACTIVE_MENU = None
REDRAW_TIMES = 0


def close():
	global ACTIVE_MENU

	ui_menu.delete(ACTIVE_MENU)

	ACTIVE_MENU = None

def show_inventory(entity):
	global ACTIVE_MENU

	display.fill_surface('ui_inventory', (45, 45, 45))
	events.register_event('draw', draw)

	_holder_menu = ui_menu.create(1, 1, title='Inventory', surface='ui_inventory', click_offset=(constants.MAP_VIEW_WIDTH-35, 0))
	ACTIVE_MENU = _holder_menu

	ui_menu.add_selectable(_holder_menu, 'Weapon', lambda: show_weapons(entity))

def show_weapons(entity):
	global ACTIVE_MENU, REDRAW_TIMES

	_holder_menu = ui_menu.create(1, 1, title='Weapons', surface='ui_inventory', click_offset=(constants.MAP_VIEW_WIDTH-35, 0))
	ACTIVE_MENU = _holder_menu
	REDRAW_TIMES = 3

	_equipped_weapon = items.get_items_in_holder(entity, 'weapon')
	_weapons = []
	
	if _equipped_weapon:
		_weapons.append(_equipped_weapon[0])
	
	for item_id in items.get_items_matching(entity, {'type': 'weapon'}):
		if item_id in _weapons:
			continue
		
		_weapons.add(item_id)
	
	for item_id in _weapons:
		_item = entities.get_entity(item_id)
		
		entities.trigger_event(_item, 'get_display_name')
		
		if item_id in _equipped_weapon:
			_fg = (245, 245, 245)
		else:
			_fg = (230, 230, 230)

		ui_menu.add_selectable(_holder_menu,
		                       _item['stats']['display_name'],
		                       show_weapon_menu,
		                       fore_color=_fg,
		                       item_id=item_id)

def show_weapon_menu(item_id):
	global ACTIVE_MENU, REDRAW_TIMES
	
	_holder_menu = ui_menu.create(1, 1, title='Actions', surface='ui_inventory', click_offset=(constants.MAP_VIEW_WIDTH-35, 0))
	ACTIVE_MENU = _holder_menu
	REDRAW_TIMES = 3
	
	_item = entities.get_entity(item_id)
	
	#entities.trigger_event(_item, 'get_actions', menu=_holder_menu)
	
	ui_menu.add_selectable(_holder_menu,
	                       'Reload',
	                       lambda: show_weapon_menu,
	                       item_id=item_id)
	ui_menu.add_selectable(_holder_menu,
	                       'Store',
	                       lambda: show_weapon_menu,
	                       item_id=item_id)

def draw():
	global REDRAW_TIMES
	
	if REDRAW_TIMES:
		display.fill_surface('ui_inventory', (45, 45, 45))
		
		REDRAW_TIMES -= 1