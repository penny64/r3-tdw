from framework import display, controls, entities, movement

import world_strategy
import constants


def draw_map_grid():
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
						
						if not _x + _y:
							if _hover:
								_char = chr(201)
								_fore_color = (255, 255, 255)
							
							else:
								_char = chr(218)
						
						elif _x == constants.MAP_CELL_SPACE-1 and not _y:
							if _hover:
								_char = chr(187)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(191)
							
						elif not _x and _y == constants.MAP_CELL_SPACE-1:
							if _hover:
								_char = chr(200)
								_fore_color = (255, 255, 255)

							else:
								_char = chr(192)
						
						elif _x + _y == (constants.MAP_CELL_SPACE-1)*2:
							if _hover:
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
						if _hover:
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

def draw_squads():
	for entity_id in entities.get_entity_group('squads'):
		_squad = entities.get_entity(entity_id)
		
		if _squad['faction'] == 'Terrorists':
			continue
		
		_x, _y = movement.get_position(_squad)
		_r_x = (_x * constants.MAP_CELL_SPACE) + constants.MAP_CELL_SPACE / 2
		_r_y = (_y * constants.MAP_CELL_SPACE) + constants.MAP_CELL_SPACE / 2
		
		display.write_char('map_squads', _r_x, _r_y, 'S')
