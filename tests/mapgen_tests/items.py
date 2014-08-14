from framework import entities, movement, numbers, flags, timers, tile


def register(entity):
	entity['inventory'] = {'items': [],
	                       'holders': {},
	                       'containers': {}}
	
	entities.create_event(entity, 'store_item')
	entities.register_event(entity, 'store_item', store_item)
	entities.create_event(entity, 'hold_item')
	entities.register_event(entity, 'hold_item', hold_item)
	entities.create_event(entity, 'create_holder')
	entities.register_event(entity, 'create_holder', add_holder)
	entities.register_event(entity, 'delete', disown)

def _create(x, y, name, char, weight, item_type, equip_to=None):
	_entity = entities.create_entity(group='items')
	
	_entity['stats'] = {'name': name,
	                    'type': item_type,
	                    'weight': weight,
	                    'owner': None,
	                    'equip_to': equip_to}
	
	movement.register(_entity)
	flags.register(_entity)
	tile.register(_entity, surface='items', char=char)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity

def create_container(x, y, name, char, weight, max_weight, equip_to=None):
	_item = _create(x, y, name, char, weight, 'container', equip_to=equip_to)
	
	_item['stats']['max_weight'] = max_weight

def get_list_of_free_containers(entity, item_id):
	_containers = []
	_item = entities.get_entity(item_id)
	
	for container_id in entity['inventory']['containers']:
		_container = entities.get_entity(container_id)
		
		if _item['stats']['weight'] + _container['stats']['weight'] > _container['stats']['max_weight']:
			continue
		
		_containers.append(container_id)
	
	return _containers

def get_list_of_free_holders(entity, item_id):
	_holders = []
	_item = entities.get_entity(item_id)
	
	for holder_name in entity['inventory']['holders']:
		_holder = entity['inventory']['holders'][holder_name]
		
		if not _item['stats']['equip_to'] == holder_name:
			continue
		
		if _item['stats']['weight'] + _holder['weight'] > _holder['max_weight']:
			continue
		
		_holders.append(holder_name)
	
	return _holders

def get_items_in_holder(entity, holder_name):
	return entity['inventory']['holders'][holder_name]['items']

def get_items_matching(entity, match):
	_items = []
	
	for item_id in entity['inventory']['items']:
		_item = entities.get_entity(item_id)
		_continue = False
		
		for key in match:
			if not key in _item['stats'] or not _item['stats'][key] == match[key]:
				_continue = True
				
				break
		
		if _continue:
			continue
		
		_items.append(item_id)
	
	return _items

############
#Operations#
############

def disown(entity):
	if not entity['stats']['owner']:
		return
	
	_owner = entities.get_entity(entity['stats']['owner'])
	_x, _y = movement.get_position(_owner)
	
	entities.trigger_event(entity, 'set_position', x=_x, y=_y)
	
	if entity['stats']['type'] == 'container':
		for item_id in entity['inventory']['containers'][entity['_id']]:
			_item = entities.get_entity(item_id)
			
			disown(_item)
		
		del entity['inventory']['containers'][entity['_id']]
	
	_owner['inventory']['items'].remove(entity['_id'])

def own_item(entity, item_id):
	_item = entities.get_entity(item_id)
	_item['stats']['owner'] = entity['_id']
	
	if _item['stats']['type'] == 'container':
		entity['inventory']['containers'][item_id] = {'items': [], 'weight': 0, 'max_weight': _item['stats']['max_weight']}
	
	entity['inventory']['items'].append(item_id)

def store_item(entity, item_id, container_id=None):
	if not container_id:
		_containers = get_list_of_free_containers(entity, item_id)
		
		if not _containers:
			return
		
		container_id = _containers[0]
	
	_item = entities.get_entity(item_id)
	
	own_item(entity, item_id)
	
	entity['inventory']['containers'][container_id]['items'].append(item_id)
	entity['inventory']['containers'][container_id]['weight'] += _item['stats']['weight']

def add_holder(entity, name, max_weight):
	entity['inventory']['holders'][name] = {'items': [], 'weight': 0, 'max_weight': max_weight}

def hold_item(entity, item_id, holder_name=None):
	if not holder_name:
		_holders = get_list_of_free_holders(entity, item_id)
		
		if not _holders:
			return
		
		holder_name = _holders[0]
	
	_item = entities.get_entity(item_id)
	
	own_item(entity, item_id)
	
	entity['inventory']['holders'][holder_name]['items'].append(item_id)
	entity['inventory']['holders'][holder_name]['weight'] += _item['stats']['weight']

#######
#Items#
#######

def leather_backpack(x, y):
	return create_container(x, y, 'Leather Backpack', 'H', 4, 14, equip_to='backpack')

def glock(x, y, ammo=0):
	_entity = _create(x, y, 'Glock', 'P', 4, 'weapon', equip_to='weapon')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=ammo)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=17)
	
	return _entity

def ammo_9x19mm(x, y):
	_entity = _create(x, y, '9x19mm rounds', '+', 4, 'ammo')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=17)
	
	return _entity

def _bullet_tick(entity):
	_direction = movement.get_direction(entity)
	
	entities.trigger_event(entity, 'push_tank', direction=_direction)

def bullet(x, y, tx, ty, speed):
	_entity = _create(x, y, 'Bullet', 'o', 0, 'bullet')
	
	entities.add_entity_to_group(_entity, 'bullets')
	timers.register(_entity)
	
	entities.trigger_event(_entity, 'set_direction', direction=numbers.direction_to((x, y), (tx, ty)))
	entities.trigger_event(_entity, 'create_timer', time=speed, repeat=-1, enter_callback=_bullet_tick, repeat_callback=_bullet_tick)