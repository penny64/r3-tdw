from framework import movement, entities, timers, controls, pathfinding, numbers, stats

import ai_factions
import settings
import ui_cursor
import ui_menu
import camera
import items
import nodes
import zones


SELECTED_SQUAD_MEMBER = None
WALK_PATH = None
WALK_DEST = None


def handle_squad_member_select(x, y):
	for squad_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(squad_id)
		
		if not _squad['faction'] == 'Rogues':
			continue
		
		for entity_id in _squad['members']:
			if movement.get_position_via_id(entity_id) == (x, y):
				select_squad_member(entity_id)
				
				return True

def handle_fire_order(x, y):
	global WALK_PATH, WALK_DEST
	
	if not is_squad_member_selected():
		return False
	
	_entity = get_selected_squad_member()
	
	for entity_id in [t for t in _entity['ai']['visible_life'] if _entity['ai']['life_memory'][t]['can_see']]:
		if entity_id == _entity['_id']:
			continue
		
		_x, _y = movement.get_position_via_id(entity_id)
		
		if (_x, _y) == (x, y):
			create_life_interact_menu(_entity, entity_id)
			
			WALK_PATH = None
			WALK_DEST = None
			
			return True
	
	return False

def handle_movement_order(x, y):
	global WALK_PATH, WALK_DEST
	
	if not is_squad_member_selected() or (x, y) in zones.get_active_solids({}, ignore_calling_entity=True):
		return False
	
	_entity = get_selected_squad_member()
	
	movement.walk_to_position(_entity, x, y, zones.get_active_astar_map(), zones.get_active_weight_map())
	
	WALK_PATH = _entity['movement']['path']['positions']
	WALK_DEST = _entity['movement']['path']['destination']
	
	settings.set_tick_mode('normal')
	
	return True

def handle_mouse_movement(x, y):
	global WALK_PATH, WALK_DEST
	
	if ui_menu.get_active_menu() or ui_menu.DELAY or not is_squad_member_selected():
		return
	
	_x = x+camera.X
	_y = y+camera.Y
	
	if (_x, _y) in zones.get_active_solids({}, ignore_calling_entity=True, no_life=True):
		return
	
	_s_x, _s_y = movement.get_position(get_selected_squad_member())
	
	if (_x, _y) == WALK_DEST or (_x, _y) == (_s_x, _s_y):
		return
	
	WALK_PATH = pathfinding.astar((_s_x, _s_y), (_x, _y), zones.get_active_astar_map(), zones.get_active_weight_map())
	WALK_DEST = (_x, _y)

def handle_mouse_pressed(x, y, button):
	if ui_menu.get_active_menu() or ui_menu.DELAY:
		return
	
	_x = x+camera.X
	_y = y+camera.Y
	
	if button == 1:
		if handle_squad_member_select(_x, _y):
			return
		
		if handle_fire_order(_x, _y):
			return
		
		if handle_movement_order(_x, _y):
			return

def handle_keyboard_input():
	global SELECTED_SQUAD_MEMBER, WALK_PATH, WALK_DEST
	
	#TODO: Check for multiple movement changes at this location
	if not is_squad_member_selected():
		return
	
	_entity = get_selected_squad_member()
	_x, _y = movement.get_position(_entity)
	
	if timers.has_timer_with_name(_entity, 'passout'):
		return
	
	if controls.get_input_char_pressed('z'):
		entities.trigger_event(_entity, 'set_motion', motion='crawl')
		settings.set_tick_mode('normal')
	
	elif controls.get_input_char_pressed('x'):
		entities.trigger_event(_entity, 'set_motion', motion='crouch')
		settings.set_tick_mode('normal')
	
	elif controls.get_input_char_pressed('c'):
		entities.trigger_event(_entity, 'set_motion', motion='stand')
		settings.set_tick_mode('normal')
	
	elif controls.get_input_char_pressed(' '):
		_entity['stats']['action_points'] = 0
		SELECTED_SQUAD_MEMBER = None
		WALK_DEST = None
		WALK_PATH = []
		_broken = False
		
		for squad_id in entities.get_entity_group('squads'):
			_squad = entities.get_entity(squad_id)
			
			if not _squad['faction'] == 'Rogues':
				continue
		
			for entity_id in _squad['members']:
				_entity = entities.get_entity(entity_id)
				
				if _entity['stats']['action_points'] > 0:
					_broken = True
					break
			
			if _broken:
				break
		
		else:
			settings.set_tick_mode('normal')

def create_life_interact_menu(entity, target_id):
	if not items.get_items_in_holder(entity, 'weapon'):
		return
	
	_target = entities.get_entity(target_id)
	_is_enemy = ai_factions.is_enemy(entity, target_id)
	_menu = ui_menu.create(ui_cursor.CURSOR['tile']['x']+2, ui_cursor.CURSOR['tile']['y']-4, title='Context')
	
	if not _is_enemy:
		if _target['missions']['inactive']:
			ui_menu.add_selectable(_menu, 'Talk', lambda: create_talk_menu(entity, target_id))
		
		ui_menu.add_selectable(_menu, 'Inquire', lambda: create_mission_menu(entity, target_id))
		ui_menu.add_selectable(_menu, 'Trade', lambda: create_mission_menu(entity, target_id))
	
	ui_menu.add_selectable(_menu, 'Shoot%s' % (' (Friendly fire)' * (not _is_enemy)), lambda: create_shoot_menu(entity, target_id))

def create_shoot_menu(entity, target_id):
	_tx, _ty = movement.get_position_via_id(target_id)
	_weapon = entities.get_entity(items.get_items_in_holder(entity, 'weapon')[0])
	_menu = ui_menu.create(_tx-camera.X+2, _ty-camera.Y-4, title='Shoot')
	_accuracy = stats.get_accuracy(entity, _weapon['_id'])
	_x, _y = movement.get_position(entity)
	_direction = numbers.direction_to((_x, _y), (_tx, _ty))
	_final_direction = _direction + (_accuracy * numbers.distance((_x, _y), (_tx, _ty)))
	_spray_accuracy = (100 * (_direction / float(_final_direction)))
	
	entities.trigger_event(_weapon, 'get_actions', menu=_menu)
	ui_menu.add_selectable(_menu, 'Spray (Acc: %.2d)' % _spray_accuracy, lambda: entities.trigger_event(entity, 'shoot', target_id=target_id) and settings.set_tick_mode('normal'))
	ui_menu.add_selectable(_menu, 'Snipe (Acc: %s)' % _accuracy, lambda: _)

def select_squad_member(entity_id):
	global SELECTED_SQUAD_MEMBER
	
	SELECTED_SQUAD_MEMBER = entity_id
	
	entities.register_event(entities.get_entity(SELECTED_SQUAD_MEMBER), 'delete', reset_selected_squad_member)

def reset_selected_squad_member(entity=None):
	global SELECTED_SQUAD_MEMBER, WALK_PATH, WALK_DEST
	
	if SELECTED_SQUAD_MEMBER:
		entities.unregister_event(entities.get_entity(SELECTED_SQUAD_MEMBER), 'delete', reset_selected_squad_member)
	
	SELECTED_SQUAD_MEMBER = None
	WALK_PATH = None
	WALK_DEST = None

def is_squad_member_selected():
	return not SELECTED_SQUAD_MEMBER == None

def get_selected_squad_member():
	return entities.get_entity(SELECTED_SQUAD_MEMBER)
