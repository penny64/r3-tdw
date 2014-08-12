from framework import entities, movement, tile


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

def _create(x, y, name, char, weight, item_type):
	_entity = entities.create_entity(group='items')
	
	_entity['stats'] = {'name': name, 'type': item_type, 'weight': weight, 'owner': None}
	
	movement.register(_entity)
	tile.register(_entity, surface='items', char=char)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity

def get_list_of_free_containers(entity, item_id):
	_containers = []
	_item = entities.get_entity(item_id)
	
	for container_id in entity['inventory']['containers']:
		_container = entities.get_entity(container_id)
		
		if _item['stats']['weight'] + _container['weight'] > _container['max_weight']:
			continue
		
		_containers.append(container_id)
	
	return _containers

def get_list_of_free_holders(entity, item_id):
	_holders = []
	_item = entities.get_entity(item_id)
	
	for holder_name in entity['inventory']['holders']:
		_holder = entity['inventory']['holders'][holder_name]
		
		if _item['stats']['weight'] + _holder['weight'] > _holder['max_weight']:
			continue
		
		_holders.append(holder_name)
	
	return _holders

############
#Operations#
############

def own_item(entity, item_id):
	_item = entities.get_entity(item_id)
	_item['stats']['owner'] = entity['_id']
	
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

def glock(x, y):
	return _create(x, y, 'Glock', 'P', 4, 'gun')