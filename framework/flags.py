import entities


def register(entity):
	entity['flags'] = {}

	entities.create_event(entity, 'set_flag')
	entities.create_event(entity, 'delete_flag')
	entities.create_event(entity, 'flag_add')
	entities.create_event(entity, 'flag_sub')
	entities.create_event(entity, 'flag_changed')
	entities.register_event(entity, 'set_flag', set_flag)
	entities.register_event(entity, 'delete_flag', delete_flag)
	entities.register_event(entity, 'flag_add', flag_add)
	entities.register_event(entity, 'flag_sub', flag_sub)
	entities.register_event(entity, 'save', save)

def save(entity, snapshot):
	snapshot['flags'] = entity['flags']

def set_flag(entity, flag, value):
	if flag in entity['flags']:
		entities.trigger_event(entity,
		                       'flag_changed',
		                       flag=flag,
		                       value=value,
		                       last_value=entity['flags'][flag]['last_value'])
	
	entity['flags'][flag] = {'value': value,
							 'last_value': value,
							 'start_value': value}

def has_flag(entity, flag):
	return flag in entity['flags']

def get_flag(entity, flag):
	return entity['flags'][flag]['value']

def delete_flag(entity, flag):
	del entity['flags'][flag]

def flag_add(entity, flag, value):
	entity['flags'][flag]['last_value'] = entity['flags'][flag]['value']
	entity['flags'][flag]['value'] += value
	
	entities.trigger_event(entity,
						   'flag_changed',
						   flag=flag,
						   value=entity['flags'][flag]['value'],
						   last_value=entity['flags'][flag]['last_value'])

def flag_sub(entity, flag, value):
	entity['flags'][flag]['last_value'] = entity['flags'][flag]['value']
	entity['flags'][flag]['value'] -= value
	
	entities.trigger_event(entity,
						   'flag_changed',
						   flag=flag,
						   value=entity['flags'][flag]['value'],
						   last_value=entity['flags'][flag]['last_value'])