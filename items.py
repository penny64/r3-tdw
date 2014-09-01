from framework import entities, movement, numbers, flags, timers, tile

import skeleton

import logging
import random


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

def _create(x, y, name, char, weight, item_type, equip_to=None, fore_color=(255, 255, 255)):
	_entity = entities.create_entity(group='items')
	
	_entity['stats'] = {'name': name,
	                    'type': item_type,
	                    'weight': weight,
	                    'owner': None,
	                    'equip_to': equip_to,
	                    'in_container': None}
	
	movement.register(_entity)
	flags.register(_entity)
	tile.register(_entity, surface='items', char=char, fore_color=fore_color)
	
	entities.register_event(_entity, 'delete', disown)
	
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
	
	if entity['stats']['in_container']:
		_owner['inventory']['containers'][entity['stats']['in_container']]['items'].remove(entity['_id'])
		_owner['inventory']['containers'][entity['stats']['in_container']]['weight'] -= entity['stats']['weight']
		
		entity['stats']['in_container'] = None
	
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
	_item['stats']['in_container'] = container_id
	
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

def corpse(x, y, char):
	return _create(x, y, '', char, 4, 'corpse', fore_color=(130, 110, 110))

def leather_backpack(x, y):
	return create_container(x, y, 'Leather Backpack', 'H', 4, 14, equip_to='backpack')

def glock(x, y, ammo=0):
	_entity = _create(x, y, 'Glock', 'P', 4, 'weapon', equip_to='weapon')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=ammo)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=17)
	entities.trigger_event(_entity, 'set_flag', flag='accuracy', value=4)
	
	return _entity

def ammo_9x19mm(x, y):
	_entity = _create(x, y, '9x19mm rounds', '+', 4, 'ammo')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=17)
	
	return _entity

def _bullet_tick(entity):
	_direction = movement.get_direction(entity)
	
	entities.trigger_event(entity, 'push_tank', direction=_direction)

def check_for_collisions(entity):
	for entity_id in entities.get_entity_group('life'):
		if entity_id == entity['owner']:
			continue
		
		if movement.get_position(entity) == movement.get_position_via_id(entity_id):
			entities.trigger_event(entities.get_entity(entity_id), 'hit', projectile=entity)
			#skeleton.hit(entities.get_entity(entity_id), entity)
			entities.delete_entity(entity)
			
			return

def bullet(entity, x, y, tx, ty, speed, accuracy):
	_entity = _create(x, y, 'Bullet', '.', 0, 'bullet')
	_entity['owner'] = entity['_id']
	
	entities.add_entity_to_group(_entity, 'bullets')
	timers.register(_entity)
	
	entities.trigger_event(_entity, 'set_direction', direction=numbers.direction_to((x, y), (tx, ty))+random.randint(-accuracy, accuracy))
	entities.trigger_event(_entity, 'create_timer', time=speed, repeat=-1, enter_callback=_bullet_tick, repeat_callback=_bullet_tick)
	entities.register_event(_entity, 'position_changed', lambda e, **kwargs: check_for_collisions(e))