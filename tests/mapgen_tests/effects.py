from framework import entities, flags, timers, display


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
		_x -= len(_text[:_text_index])/2
		display.write_string('ui', _x, _y, _text[:_text_index], fore_color=_text_fore_color, back_color=_text_back_color)

def _printer_move(entity):
	_x, _y = flags.get_flag(entity, 'text_pos')
	_y -= 1
	entities.trigger_event(entity, 'set_flag', flag='text_pos', value=(_x, _y))

def _printer_exit(entity):
	entities.delete_entity(entity)

def printer(x, y, text, center=True, fore_color=(255, 255, 255), moving=True, back_color=(10, 10, 10), speed_mod=1.0, show_mod=1.0):
	_entity = entities.create_entity(group='effects_freetick')
	
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
	entities.trigger_event(_entity, 'create_timer', time=12*speed_mod, repeat=len(text), repeat_callback=_printer_tick)
	entities.trigger_event(_entity, 'create_timer', time=((10*speed_mod)*len(text))+(60*show_mod), exit_callback=_printer_exit)
	
	if moving:
		entities.trigger_event(_entity, 'create_timer', time=25, repeat=len(text)/2, repeat_callback=_printer_move)