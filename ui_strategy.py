from framework import display, controls, entities, movement, shapes, numbers

import world_strategy
import ai_factions
import ai_squads
import constants

import time


def draw_map_grid(selected_grid=None):
	display.blit_surface_viewport('map', 0, 0, constants.STRAT_MAP_WIDTH, constants.STRAT_MAP_HEIGHT)
	
	for x in range(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE):
		for y in range(constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE):
			_tile = world_strategy.MAP['grid'][x, y]
			
			if x == controls.get_mouse_pos()[0]/constants.MAP_CELL_SPACE and y == controls.get_mouse_pos()[1]/constants.MAP_CELL_SPACE:
				_hover = True
			
			else:
				_hover = False
			
			for _x in range(constants.MAP_CELL_SPACE):
				for _y in range(constants.MAP_CELL_SPACE):
					_d_x = (x * constants.MAP_CELL_SPACE) + _x
					_d_y = (y * constants.MAP_CELL_SPACE) + _y
					_back_color = None
					
					if _tile['is_ownable']:
						if _tile['owned_by'] == 'Terrorists':
							_fore_color = (200, 0, 0)
							_back_color = (125, 0, 0)
						
						elif _tile['owned_by'] == 'Rogues':
							_fore_color = (0, 200, 0)
							_back_color = (0, 125, 0)
						
						else:
							_fore_color = (180, 180, 180)
							_back_color = (100, 100, 100)
						
						if (x, y) == selected_grid:
							_fore_color = int(round(_fore_color[0] * 1.2)), int(round(_fore_color[1] * 1.2)), int(round(_fore_color[2] * 1.2))
							_back_color = int(round(_back_color[0] * 1.2)), int(round(_back_color[1] * 1.2)), int(round(_back_color[2] * 1.2))
						
						if not _x + _y:
							if _hover or (x, y) == selected_grid:
								_char = chr(201)
								_fore_color = (255, 255, 255)
							
							else:
								_char = chr(218)
						
						elif _x == constants.MAP_CELL_SPACE-1 and not _y:
							if _hover or (x, y) == selected_grid:
								_char = chr(187)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(191)
							
						elif not _x and _y == constants.MAP_CELL_SPACE-1:
							if _hover or (x, y) == selected_grid:
								_char = chr(200)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(192)
						
						elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
							if _hover or (x, y) == selected_grid:
								_char = chr(188)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(217)
						
						elif _y > 0 and _y < constants.MAP_CELL_SPACE-1 and (not _x or _x == constants.MAP_CELL_SPACE-1):
							_char = chr(179)
						
						elif _x > 0 and _x < constants.MAP_CELL_SPACE-1 and (not _y or _y == constants.MAP_CELL_SPACE-1):
							_char = chr(196)
						
						else:
							_char = '.'
						
						display.write_char('map_markers',
							               _d_x,
							               _d_y,
							               _char,
						                   fore_color=_fore_color,
						                   back_color=_back_color)
					
					else:
						if _hover or (x, y) == selected_grid:
							if not _x + _y:
								_char = chr(201)
							
							elif _x == constants.MAP_CELL_SPACE-1 and not _y:
								_char = chr(187)
								
							elif not _x and _y == constants.MAP_CELL_SPACE-1:
								_char = chr(200)
							
							elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
								_char = chr(188)
							
							else:
								_char = ' '
							
							_color = display.get_color_at('map', _d_x, _d_y)[1]
							
							display.write_char('map_markers',
								               _d_x,
								               _d_y,
								               _char,
							                   back_color=(int(round(_color[0]*1.4)), int(round(_color[1]*1.4)), int(round(_color[2]*1.4))))

def draw_squads(selected_squad=None):
	for entity_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(entity_id)
		
		if _squad['faction'] == 'Terrorists':
			continue
		
		_x, _y = movement.get_position(_squad)
		_r_x = (_x * constants.MAP_CELL_SPACE) + constants.MAP_CELL_SPACE / 2
		_r_y = (_y * constants.MAP_CELL_SPACE) + constants.MAP_CELL_SPACE / 2
		_fore_color = (200, 200, 200)
		
		if selected_squad == entity_id:
			if time.time() % 1 >= .5:
				_fore_color = (100, 150, 100)
		
		display.write_char('map_squads', _r_x, _r_y, 'S', fore_color=_fore_color)

def clear_bar():
	for y in range(constants.WINDOW_HEIGHT-constants.STRAT_MAP_HEIGHT):
		display.write_string('ui_bar', 0, y, ' ' * constants.WINDOW_WIDTH, back_color=(0, 0, 0))

def draw_time():
	_minutes = int(round(world_strategy.TIME))
	_time = '%s:%02d' % (_minutes / 60, _minutes - ((_minutes / 60) * 60))
	
	display.write_string('ui_bar', constants.WINDOW_WIDTH - len(_time) - 1, 1, _time, back_color=(0, 0, 0))

def draw_money():
	_money = ai_factions.FACTIONS['Rogues']['money']
	_money_string = '%s' % int(round(_money))
	
	display.write_string('ui_bar', constants.WINDOW_WIDTH - len(_money_string) - 3, 2,
	                     '$')
	
	display.write_string('ui_bar', constants.WINDOW_WIDTH - len(_money_string) - 1, 2,
	                     _money_string,
	                     fore_color=(60, 200, 60))

def draw_news(news):
	_chr = chr(65 + 1)
	_text_y_mod = 0
	
	for text, fore_color, back_color in news:
		display.write_string('ui_bar', 1, 1 + _text_y_mod, text, fore_color=fore_color, back_color=back_color)
		
		_text_y_mod += 1

def draw_camp_info(camp_id):
	_camp = world_strategy.MAP['grid'][camp_id]
	
	flavor_print(1, 1, [('Squads: ', '[1]', (55, 200, 55)),
	                    ('Condition: ', 'Bad', constants.STATUS_BAD),
	                    ('Favor: ', 'Good', constants.STATUS_GOOD),
	                    ('Supplies: ', 'Low', (200, 55, 55))])

def draw_squad_info(squad_id):
	_text_y_mod = 0
	_squad = entities.get_entity(squad_id)
	
	for member_id in _squad['members']:
		_member = entities.get_entity(member_id)
		_health_string = '[OK]'
		_weapon_name = '<Glock>'
		_rank = 'Shooter'
		
		display.write_string('ui_bar', 1, 1 + _text_y_mod,
		                     _member['stats']['name'],
		                     fore_color=(204, 200, 204))
		
		display.write_string('ui_bar', 2 + len(_member['stats']['name']), 1 + _text_y_mod,
		                     _health_string,
		                     fore_color=(200, 200, 34))		
		
		display.write_string('ui_bar', 3 + len(_member['stats']['name']) + len(_health_string), 1 + _text_y_mod,
		                     _weapon_name,
		                     fore_color=(0, 200, 34))
		
		display.write_string('ui_bar', 4 + len(_member['stats']['name']) + len(_health_string) + len(_weapon_name), 1 + _text_y_mod,
		                     _rank,
		                     fore_color=(200, 50, 200),
		                     back_color=(50, 12, 50))
		
		_text_y_mod += 1

def flavor_print(x, y, lines):
	_y = y
	
	for _favor_text in lines:
		display.write_string('ui_bar', x, _y, _favor_text[0])
		display.write_string('ui_bar', x + len(_favor_text[0]), _y, _favor_text[1], fore_color=_favor_text[2])
		
		_y += 1

def draw_raid_info(squad_id, camp_id):
	_camp = world_strategy.MAP['grid'][camp_id]
	_squad = entities.get_entity(squad_id)
	_travel_distance = numbers.distance(movement.get_position_via_id(squad_id), camp_id)
	_highest_speed = 0
	_cost = ai_squads.get_attack_cost(_squad, camp_id)
	
	for member_id in _squad['members']:
		_member = entities.get_entity(member_id)
		_speed = movement.get_move_cost(_member)
		
		if _speed > _highest_speed:
			_highest_speed = _speed
	
	_travel_time = _travel_distance * (_highest_speed * 80)
	_time_string = '%s hours %s minutes' % (_travel_time / 60, _travel_time - ((_travel_time / 60) * 60))
	_info = 'Right Click Camp to Confirm Order, ESC to cancel'
	
	if time.time() % 1 >= .5:
		_info_color = (200, 0, 0)
	
	else:
		_info_color = (200, 80, 80)
	
	display.write_string('ui_bar', (constants.WINDOW_WIDTH / 2) - (len(_info) / 2), 0,
	                     _info,
	                     fore_color=_info_color)
	
	display.write_string('ui_bar', 1, 1,
	                     'Raid Order',
	                     fore_color=(200, 50, 70))
	
	flavor_print(1, 3, [('Risk: ', 'Low', constants.STATUS_GOOD),
	                    ('Cost: $ ', '%i' % _cost, constants.STATUS_GOOD),
	                    ('Supplies needed: ', '%i' % 12, constants.STATUS_OK),
	                    ('Travel time: ', _time_string, constants.STATUS_OK)])
	
	flavor_print(35, 3, [('Test value: ', 'Low', constants.STATUS_GOOD)])

def draw_raid_path(path):
	_start_pos = path[0]
	
	for pos in path[1:]:
		_r_pos_1 = _start_pos[0] * constants.MAP_CELL_SPACE, _start_pos[1] * constants.MAP_CELL_SPACE
		_r_pos_2 = pos[0] * constants.MAP_CELL_SPACE, pos[1] * constants.MAP_CELL_SPACE
		_line = shapes.line(_r_pos_1, _r_pos_2)
		
		for x, y in _line[:len(_line)-1]:
			display.write_char('map_path', x + constants.MAP_CELL_SPACE/2,
			                   y + constants.MAP_CELL_SPACE/2,
			                   chr(176))
		
		_start_pos = pos[:]
