from framework import entities, flags, timers, display, numbers, tile, movement, shapes

import post_processing
import constants
import settings
import camera
import zones
import life

import random
import sys

MESSAGES_ACTIVE = 0


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
	
	for c in range(len(_color)):
		for i in range(len(_color)):
			_color[c][i] = int((round(_color[c][i])))
	
	entities.trigger_event(_blood, 'set_fore_color', color=_color[0])
	entities.trigger_event(_blood, 'set_back_color', color=_color[1])

	return _blood

def _muzzle_flash_move(entity):
	_direction = movement.get_direction(entity)
	_nx, _ny = numbers.velocity(_direction, 1)
	
	movement.push(entity, _nx, _ny, time=3)

def _muzzle_flash_fade(entity):
	entity['alpha'] -= 0.07
	
	_x, _y = movement.get_position(entity)
		
	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), entity['alpha'])
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), entity['alpha'])
	
	for c in range(len(_color)):
		for i in range(len(_color)):
			_color[c][i] = int((round(_color[c][i])))
	
	entities.trigger_event(entity, 'set_fore_color', color=_color[0])
	entities.trigger_event(entity, 'set_back_color', color=_color[1])		

def _muzzle_delete(entity):
	entities.delete_entity(entity)

def muzzle_flash(x, y, direction, surface='effects', group='effects', start_alpha=0.4, no_move=False):
	if '--no-fx' in sys.argv:
		return
	
	_blood = _create(x, y)
	_x, _y = (int(round(x)), int(round(y)))
	
	entities.trigger_event(_blood, 'set_char', char=random.choice([';', '3', '.', '^']))
	_blood['alpha'] = start_alpha

	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), start_alpha)
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), start_alpha)
	
	for c in range(len(_color)):
		for i in range(len(_color)):
			_color[c][i] = int((round(_color[c][i])))
	
	entities.trigger_event(_blood, 'set_direction', direction=direction+random.randint(-35, 35))
	
	_muzzle_flash_move(_blood)
	entities.trigger_event(_blood, 'set_fore_color', color=_color[0])
	entities.trigger_event(_blood, 'set_back_color', color=_color[1])
	
	if not no_move:
		entities.trigger_event(_blood, 'create_timer', time=2, repeat=random.randint(1, 3), repeat_callback=_muzzle_flash_move, exit_callback=_muzzle_delete)
	
	entities.trigger_event(_blood, 'create_timer', time=1, repeat=6, repeat_callback=_muzzle_flash_fade)

	return _blood

def _vapor_fade(entity):
	entity['alpha'] -= entity['fade_rate']
	
	if entity['alpha'] <= 0:
		entities.delete_entity(entity)
		
		return
	
	_x, _y = movement.get_position(entity)
		
	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), entity['alpha'])
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), entity['alpha'])
	
	for c in range(len(_color)):
		for i in range(len(_color)):
			_color[c][i] = int((round(_color[c][i])))
	
	entities.trigger_event(entity, 'set_fore_color', color=_color[0])
	entities.trigger_event(entity, 'set_back_color', color=_color[1])		

def vapor(x, y, surface='effects', group='effects', start_alpha=0.6, fade_rate=0.095):
	if '--no-fx' in sys.argv:
		return
	
	_vapor = _create(x, y, surface=surface, group=group)
	_x, _y = (int(round(x)), int(round(y)))
	_vapor['fade_rate'] = fade_rate
	
	entities.trigger_event(_vapor, 'set_char', char=' ')
	_vapor['alpha'] = start_alpha

	_color = list(display.get_color_at('tiles', _x, _y))
	_color[0] = numbers.interp_velocity(_color[0], (255, 255, 255), start_alpha)
	_color[1] = numbers.interp_velocity(_color[1], (255, 255, 255), start_alpha)
	
	for c in range(len(_color)):
		for i in range(len(_color)):
			_color[c][i] = int((round(_color[c][i])))
	
	_muzzle_flash_move(_vapor)
	entities.trigger_event(_vapor, 'set_fore_color', color=_color[0])
	entities.trigger_event(_vapor, 'set_back_color', color=_color[1])
	
	entities.trigger_event(_vapor, 'create_timer', time=0, repeat=-1, repeat_callback=_vapor_fade)

	return _vapor

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
	if '--no-fx' in sys.argv:
		return
	
	_entity = entities.create_entity(group='ui_effects' + ('_freetick' * free_tick))
	
	timers.register(_entity)
	flags.register(_entity)
	
	entities.create_event(_entity, 'draw')
	entities.register_event(_entity, 'draw', _printer_draw)
	entities.trigger_event(_entity, 'set_flag', flag='text', value=text)
	entities.trigger_event(_entity, 'set_flag', flag='text_index', value=0)
	entities.trigger_event(_entity, 'set_flag', flag='text_center', value=center)
	entities.trigger_event(_entity, 'set_flag', flag='text_pos', value=(x, y))
	entities.trigger_event(_entity, 'set_flag', flag='text_orig_pos', value=(x, y))
	entities.trigger_event(_entity, 'set_flag', flag='text_fore_color', value=fore_color)
	entities.trigger_event(_entity, 'set_flag', flag='text_back_color', value=back_color)
	entities.trigger_event(_entity, 'set_flag', flag='move_direction', value=move_direction)
	entities.trigger_event(_entity, 'create_timer', time=12*speed_mod, repeat=len(text), repeat_callback=_printer_tick)
	entities.trigger_event(_entity, 'create_timer', time=((10*speed_mod)*len(text))+(60*show_mod), exit_callback=_printer_exit)
	
	if moving:
		entities.trigger_event(_entity, 'create_timer', time=25, repeat=len(text)/2, repeat_callback=_printer_move)
	
	return _entity

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
	
	return printer(_x, _y, text, moving=_moving, move_direction=_move_direction, show_mod=1, speed_mod=0.3, free_tick=True)

def light(x, y, brightness):
	if '--no-fx' in sys.argv:
		return
	
	_light_map = post_processing.get_light_map()
	
	for _x, _y in shapes.circle(x, y, brightness):
		_brightness = 1 - (numbers.float_distance((x, y), (_x, _y)) / float(brightness))
		_light_map[_y, _x] = 2 * _brightness

def _message_draw(entity):
	_text = flags.get_flag(entity, 'text')
	_index = flags.get_flag(entity, 'index')
	
	for i in range(0, 3):
		if i == 1:
			display.write_string('ui', 3, 3 + i + (4 * _index), '  %s  ' % _text, fore_color=(200, 200, 200), back_color=(60, 60, 60))
		else:
			display.write_string('ui', 3, 3 + i + (4 * _index), ' ' * (len(_text) + 4), fore_color=(20, 20, 20), back_color=(60, 60, 60))

def _message_delete(entity):
	global MESSAGES_ACTIVE
	
	MESSAGES_ACTIVE -= 1

def message(text, fore_color=(255, 255, 255), back_color=(10, 10, 10), time=-1):
	global MESSAGES_ACTIVE
	
	_entity = entities.create_entity(group='ui_effects_freetick')
	
	if time == -1:
		_time = 30 * constants.SHOW_MESSAGES_FOR
	
	else:
		_time = time
	
	timers.register(_entity, use_system_event='draw')
	flags.register(_entity)
	
	entities.create_event(_entity, 'draw')
	entities.register_event(_entity, 'draw', _message_draw)
	entities.register_event(_entity, 'delete', _message_delete)
	entities.trigger_event(_entity, 'create_timer', time=_time, exit_callback=entities.delete_entity)
	entities.trigger_event(_entity, 'set_flag', flag='text', value=text)
	entities.trigger_event(_entity, 'set_flag', flag='index', value=MESSAGES_ACTIVE)
	
	MESSAGES_ACTIVE += 1
	
	return _entity