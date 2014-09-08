from framework import entities, flags, timers, display, numbers, tile, movement

import constants
import settings
import camera
import zones
import life

import random


def _create(x, y, surface='effects', group='effects'):
	_entity = entities.create_entity()

	movement.register(_entity)
	tile.register(_entity, surface=surface)
	
	timers.register(_entity)
	entities.add_entity_to_group(_entity, group)

	entities.trigger_event(_entity, 'set_position', x=x, y=y)

	return _entity

def blood(x, y, surface='effects', group='effects'):
	_blood = _create(x, y)
	_x, _y = (int(round(x)), int(round(y)))
	
	entities.trigger_event(_blood, 'set_char', char=random.choice([';', '3', '.', '^']))

	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], random.choice([constants.BLOOD_1, constants.BLOOD_2, constants.BLOOD_3]), 0.4)
	_color[1] = numbers.interp_velocity(_color[1], random.choice([constants.BLOOD_1, constants.BLOOD_2, constants.BLOOD_3]), 0.4)
	
	entities.trigger_event(_blood, 'set_fore_color', color=_color[0])
	entities.trigger_event(_blood, 'set_back_color', color=_color[1])

	return _blood

def _muzzle_flash(entity):
	_direction = movement.get_direction(entity)
	_nx, _ny = numbers.velocity(_direction, 1)
	
	entity['alpha'] -= 0.05
	
	_color = list(display.get_color_at('tiles', _nx, _ny))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), entity['alpha'])
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), entity['alpha'])
	
	entities.trigger_event(entity, 'set_fore_color', color=_color[0])
	entities.trigger_event(entity, 'set_back_color', color=_color[1])	
	
	movement.push(entity, _nx, _ny, time=3)

def _muzzle_delete(entity):
	entities.delete_entity(entity)

def muzzle_flash(x, y, direction, surface='effects', group='effects'):
	_blood = _create(x, y)
	_x, _y = (int(round(x)), int(round(y)))
	
	entities.trigger_event(_blood, 'set_char', char=random.choice([';', '3', '.', '^']))
	_blood['alpha'] = 0.4

	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), 0.4)
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), 0.4)
	
	entities.trigger_event(_blood, 'set_direction', direction=direction+random.randint(-35, 35))
	
	_muzzle_flash(_blood)
	entities.trigger_event(_blood, 'set_fore_color', color=_color[0])
	entities.trigger_event(_blood, 'set_back_color', color=_color[1])
	entities.trigger_event(_blood, 'create_timer', time=2, repeat=random.randint(1, 3), repeat_callback=_muzzle_flash, exit_callback=_muzzle_delete)

	return _blood

def _printer_tick(entity):
	entities.trigger_event(entity, 'flag_add', flag='text_index', value=1)

def _printer_draw(entity):
	_text = flags.get_flag(entity, 'text')
	_text_index = flags.get_flag(entity, 'text_index')
	_text_center = flags.get_flag(entity, 'text_center')
	_text_fore_color = flags.get_flag(entity, 'text_fore_color')
	_text_back_color = flags.get_flag(entity, 'text_back_color')
	_x, _y = flags.get_flag(entity, 'text_pos')
	
	if _text_center:
		if _x + len(_text[:_text_index])/2 >= camera.X + constants.MAP_VIEW_WIDTH-1:
			return
		
		if _x - len(_text[:_text_index])/2 < camera.X:
			return
		
		if _y >= camera.Y + constants.MAP_VIEW_HEIGHT:
			return
		
		_x -= len(_text[:_text_index])/2
		display.write_string('ui', _x-camera.X, _y-camera.Y, _text[:_text_index], fore_color=_text_fore_color, back_color=_text_back_color)

def _printer_move(entity):
	_x, _y = flags.get_flag(entity, 'text_pos')
	_move_direction = flags.get_flag(entity, 'move_direction')
	_vx, _vy = numbers.velocity(_move_direction, 1)
	_x += int(round(_vx))
	_y += int(round(_vy))
	
	entities.trigger_event(entity, 'set_flag', flag='text_pos', value=(_x, _y))

def _printer_exit(entity):
	entities.delete_entity(entity)

def printer(x, y, text, center=True, fore_color=(255, 255, 255), moving=True, move_direction=90, back_color=(10, 10, 10), speed_mod=1.0, show_mod=1.0, free_tick=True):
	_entity = entities.create_entity(group='ui_effects' + ('_freetick' * free_tick))
	
	timers.register(_entity)
	flags.register(_entity)
	
	entities.create_event(_entity, 'draw')
	entities.register_event(_entity, 'draw', _printer_draw)
	entities.trigger_event(_entity, 'set_flag', flag='text', value=text)
	entities.trigger_event(_entity, 'set_flag', flag='text_index', value=0)
	entities.trigger_event(_entity, 'set_flag', flag='text_center', value=center)
	entities.trigger_event(_entity, 'set_flag', flag='text_pos', value=(x, y))
	entities.trigger_event(_entity, 'set_flag', flag='text_fore_color', value=fore_color)
	entities.trigger_event(_entity, 'set_flag', flag='text_back_color', value=back_color)
	entities.trigger_event(_entity, 'set_flag', flag='move_direction', value=move_direction)
	entities.trigger_event(_entity, 'create_timer', time=12*speed_mod, repeat=len(text), repeat_callback=_printer_tick)
	entities.trigger_event(_entity, 'create_timer', time=((10*speed_mod)*len(text))+(60*show_mod), exit_callback=_printer_exit)
	
	if moving:
		entities.trigger_event(_entity, 'create_timer', time=25, repeat=len(text)/2, repeat_callback=_printer_move)

def show_noise(entity, x, y, accuracy, direction, text, show_on_sight, callback):
	if settings.OBSERVER_MODE:
		return
	
	if not zones.is_zone_active():
		return
	
	if life.can_see_position(entity, (x, y)) and not show_on_sight:
		return
	
	#TODO: Hearing stat
	if accuracy <= .75 and accuracy < random.uniform(0, 1):
		return
	
	if not direction == -1000:
		_moving = True
		_move_direction = direction
	else:
		_moving = False
		_move_direction = 90
	
	#TODO: Redo
	if not show_on_sight:
		while 1:
			_nx, _ny = numbers.velocity(random.randint(0, 359), 5 * (1-accuracy))
			_x = int(round(x + _nx))
			_y = int(round(y + _ny))
			
			if not life.can_see_position(entity, (_x, _y)):
				break
	else:
		_x, _y = x, y
		
		if show_on_sight:
			_y -= 1
	
	printer(_x, _y, text, moving=_moving, move_direction=_move_direction, show_mod=1, speed_mod=0.3, free_tick=False)