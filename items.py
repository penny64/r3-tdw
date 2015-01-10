from framework import entities, movement, numbers, flags, timers, tile

import skeleton
import ui_dialog
import ui_menu
import effects
import camera
import zones
import life

import logging
import random
import sys


def register(entity):
	entity['inventory'] = {'items': [],
	                       'holders': {},
	                       'containers': {}}
	
	entities.create_event(entity, 'give_item')
	entities.register_event(entity, 'give_item', give_item)
	entities.create_event(entity, 'disown_item')
	entities.register_event(entity, 'disown_item', disown_item)
	entities.create_event(entity, 'store_item')
	entities.register_event(entity, 'store_item', store_item)
	entities.create_event(entity, 'hold_item')
	entities.register_event(entity, 'hold_item', hold_item)
	entities.create_event(entity, 'create_holder')
	entities.register_event(entity, 'create_holder', add_holder)

def _create(x, y, name, char, weight, item_type, equip_to=None, fore_color=(255, 255, 255), kind=None):
	_entity = entities.create_entity(group='items')
	
	_entity['stats'] = {'name': name,
	                    'display_name': name,
	                    'type': item_type,
	                    'weight': weight,
	                    'owner': None,
	                    'kind': kind,
	                    'equip_to': equip_to,
	                    'in_container': None}
	
	movement.register(_entity)
	flags.register(_entity)
	tile.register(_entity, surface='items', char=char, fore_color=fore_color)
	
	entities.create_event(_entity, 'collision_with_solid')
	entities.create_event(_entity, 'collision_with_entity')
	entities.create_event(_entity, 'get_interactions')
	entities.create_event(_entity, 'get_actions')
	entities.create_event(_entity, 'get_display_name')
	entities.create_event(_entity, 'seen')
	entities.register_event(_entity, 'get_display_name', get_display_name)
	
	entities.trigger_event(_entity, 'set_position', x=x, y=y)
	
	return _entity

def create_container(x, y, name, char, weight, max_weight, equip_to=None):
	_item = _create(x, y, name, char, weight, 'container', equip_to=equip_to)
	
	_item['stats']['max_weight'] = max_weight
	
	return _item

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

def get_display_name(entity):
	entity['stats']['display_name'] = entity['stats']['name']

def _handle_weapon_display_name(entity):
	_weapon_ammo = flags.get_flag(entity, 'ammo')
	_weapon_ammo_max = flags.get_flag(entity, 'ammo_max')	
	
	entity['stats']['display_name'] += ' (%s/%s)' % (_weapon_ammo, _weapon_ammo_max)

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
	entity['stats']['owner'] = None

def disown_item(entity, item_id):
	disown(entities.get_entity(item_id))

def own_item(entity, item_id):
	_item = entities.get_entity(item_id)
	_item['stats']['owner'] = entity['_id']
	
	if _item['stats']['type'] == 'container':
		entity['inventory']['containers'][item_id] = {'items': [], 'weight': 0, 'max_weight': _item['stats']['max_weight']}
	
	entity['inventory']['items'].append(item_id)

def give_item(entity, item_id, target_id):
	_target = entities.get_entity(target_id)
	
	entities.trigger_event(entity, 'disown_item', item_id=item_id)
	entities.trigger_event(_target, 'store_item', item_id=item_id)

def store_item(entity, item_id, container_id=None):
	if not container_id:
		_containers = get_list_of_free_containers(entity, item_id)
		
		if not _containers:
			return
		
		container_id = _containers[0]
	
	_item = entities.get_entity(item_id)
	
	if _item['stats']['owner']:
		raise Exception('Item is already owned.')
	
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

def _corpse_seen(entity, target_id):
	_target = entities.get_entity(target_id)
	
	if not entity['owner_id'] in _target['ai']['life_memory']:
		life.create_life_memory(_target, entity['owner_id'])
	
	_target['ai']['life_memory'][entity['owner_id']]['is_dead'] = True

def corpse(x, y, char, owner_id):
	_entity = _create(x, y, '', char, 4, 'corpse', fore_color=(130, 110, 110))
	_entity['owner_id'] = owner_id
	
	entities.register_event(_entity, 'seen', _corpse_seen)
	entities.register_event(_entity, 'get_interactions', lambda e, menu, target_id: ui_menu.add_selectable(menu,
	                                                                                            'Examine',
	                                                                                            lambda: ui_dialog.create(x-camera.X,
	                                                                                                                     y-camera.Y,
	                                                                                                                     'Dead?')))
	
	return _entity

def mutated_wild_dog_tail(x, y, owner_id):
	_entity = _create(x, y, 'Mutated Wild Dog Tail', '`', 4, 'corpse', fore_color=(250, 110, 110))
	_entity['owner_id'] = owner_id
	
	return _entity

def leather_backpack(x, y):
	return create_container(x, y, 'Leather Backpack', 'H', 4, 14, equip_to='backpack')

def glock(x, y, ammo=0):
	_entity = _create(x, y, 'Glock', 'P', 4, 'weapon', equip_to='weapon', kind='pistol')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=ammo)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=17)
	entities.trigger_event(_entity, 'set_flag', flag='damage', value=135)
	entities.trigger_event(_entity, 'set_flag', flag='accuracy', value=2.35)
	entities.trigger_event(_entity, 'set_flag', flag='shoot_cost', value=15)
	entities.trigger_event(_entity, 'set_flag', flag='rounds_per_shot', value=3)
	entities.trigger_event(_entity, 'set_flag', flag='is_throwable', value=False)
	entities.register_event(_entity, 'get_display_name', _handle_weapon_display_name)
	
	#entities.register_event(_entity, 'get_actions', lambda e, menu: ui_menu.add_selectable(menu,
	#                                                                                       'Single shot',
	#                                                                                       lambda: ui_dialog.create(x-camera.X,
	#                                                                                                                y-camera.Y,
	#                                                                                                                'Dead?')))
	#entities.register_event(_entity, 'get_actions', lambda e, menu: ui_menu.add_selectable(menu,
	#                                                                                       '3-burst',
	#                                                                                       lambda: ui_dialog.create(x-camera.X,
	#                                                                                                                y-camera.Y,
	#                                                                                                                'Dead?')))	
	
	return _entity

def shortrifle():
	_entity = _create(0, 0, '.22 Short Rifle', 'P', 4, 'weapon', equip_to='weapon', kind='rifle')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=6)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=6)
	entities.trigger_event(_entity, 'set_flag', flag='accuracy', value=1.25)
	entities.trigger_event(_entity, 'set_flag', flag='shoot_cost', value=40)
	entities.trigger_event(_entity, 'set_flag', flag='damage', value=189)
	entities.trigger_event(_entity, 'set_flag', flag='rounds_per_shot', value=1)
	entities.trigger_event(_entity, 'set_flag', flag='is_throwable', value=False)
	
	return _entity

def chaingun():
	_entity = _create(0, 0, 'Chaingun', 'P', 4, 'weapon', equip_to='weapon', kind='rifle')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=100)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=100)
	entities.trigger_event(_entity, 'set_flag', flag='accuracy', value=3.00)
	entities.trigger_event(_entity, 'set_flag', flag='shoot_cost', value=15)
	entities.trigger_event(_entity, 'set_flag', flag='damage', value=148)
	entities.trigger_event(_entity, 'set_flag', flag='rounds_per_shot', value=6)
	entities.trigger_event(_entity, 'set_flag', flag='is_throwable', value=False)
	
	return _entity

def frag_grenade():
	_entity = _create(0, 0, 'Frag. Grenade', 'O', 2, 'weapon', equip_to='weapon', kind='explosive')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=6)
	entities.trigger_event(_entity, 'set_flag', flag='ammo_max', value=6)
	entities.trigger_event(_entity, 'set_flag', flag='accuracy', value=4.00)
	entities.trigger_event(_entity, 'set_flag', flag='shoot_cost', value=100)
	entities.trigger_event(_entity, 'set_flag', flag='damage', value=240)
	entities.trigger_event(_entity, 'set_flag', flag='rounds_per_shot', value=1)
	entities.trigger_event(_entity, 'set_flag', flag='is_throwable', value=True)
	
	return _entity

def frag_grenade_explode(entity):
	_x, _y = movement.get_position(entity)
	_damage = entity['damage']
	_size = 3 * int(round((_damage * .01)))
	
	effects.explosion(_x, _y, _size)
	
	for entity_id in entities.get_entity_group('life'):
		_entity = entities.get_entity(entity_id)
		_distance = numbers.distance((_x, _y), movement.get_position(_entity))
		
		if _distance - 1 > _size or not life.can_see_position(_entity, (_x, _y)):
			continue
		
		entities.trigger_event(_entity, 'hit', projectile=entity, damage_mod=1 - ((_distance - 1) / float(_size)))

def ammo_9x19mm(x, y):
	_entity = _create(x, y, '9x19mm rounds', '+', 4, 'ammo')
	
	entities.trigger_event(_entity, 'set_flag', flag='ammo', value=17)
	
	return _entity

def _bullet_tick(entity):
	_direction = movement.get_direction(entity)
	
	entities.trigger_event(entity, 'push_tank', direction=_direction)
	
	_x, _y = movement.get_position(entity)
	_distance = numbers.distance((_x, _y), entity['start_position'])
	_starting_target_distance = numbers.distance(entity['start_position'], entity['end_position'])
	
	if _distance > _starting_target_distance + (12 - (entity['speed'] * 2)):
		entities.delete_entity(entity)

def _explosive_tick(entity):
	_direction = movement.get_direction(entity)
	
	entities.trigger_event(entity, 'push_tank', direction=_direction)
	
	_x, _y = movement.get_position(entity)
	_distance = numbers.distance((_x, _y), entity['end_position'])
	_starting_target_distance = numbers.distance(entity['start_position'], entity['end_position'])
	
	if _distance <= entity['accuracy'] * 2.5:
		entity['slow_down'] = True
	
	if entity['slow_down']:
		entity['speed'] = numbers.clip(entity['speed'] * 1.2, 0, 40)	
	
	if entity['speed'] < 40:
		entities.trigger_event(entity, 'create_timer', time=int(round(entity['speed'])), name='movement', exit_callback=_explosive_tick)
	
	else:
		entities.trigger_event(entity, 'activate_explosive')

def check_next_position(entity):
	_x = int(round(entity['movement']['next_x']))
	_y = int(round(entity['movement']['next_y']))
	
	if (_x, _y) in zones.get_active_solids({}, no_life=True, ignore_calling_entity=True):
		entity['movement']['next_x'] = entity['movement']['x']
		entity['movement']['next_y'] = entity['movement']['y']
		
		entities.trigger_event(entity, 'collision_with_solid')
		
		return True
	
	return False

def check_for_collisions(entity):
	_x, _y = movement.get_position(entity)
	
	if _x < 0 or _x >= zones.get_active_size()[0]-1 or _y < 0 or _y >= zones.get_active_size()[1]-1:
		entities.delete_entity(entity)
		
		return
	
	if (_x, _y) in zones.get_active_solids(entity):
		entities.trigger_event(entity, 'collision_with_solid')
		
		return
	
	for entity_id in entities.get_entity_group('life'):
		if entity_id == entity['owner']:
			continue
		
		if movement.get_position(entity) == movement.get_position_via_id(entity_id):
			entities.trigger_event(entity, 'collision_with_entity', target_id=entity_id)
			
			return

def _bullet_effects(entity, x, y):
	_distance = numbers.distance((x, y), entity['start_position'])
	_target_distance = numbers.distance((x, y), entity['end_position']) + numbers.clip(10 - _distance, 0, 10) 
	_x, _y = movement.get_position(entity)
	_mod = (0.6 - (_distance / 35.0)) + random.uniform(-.1, .1)
	_alpha = numbers.clip(_mod, 0, 1)
	_crash_dist = 60 - (entity['speed'] * 2)
	
	if _alpha > 0:
		effects.vapor(x, y, start_alpha=_alpha)
	
	if _target_distance < 30:
		_size = int(round(2 * (1 - (1 * numbers.clip(numbers.clip(_target_distance, 0, 100)/60.0, 0, 1))))) + random.randint(1, 2)
		
		if _distance > _crash_dist:
			_size = int(round(_size * (_crash_dist/float(_distance))))
		
		if _size > 1:
			effects.light(_x, _y, _size, r=1.3, g=1.3, b=1.3)

def bullet(entity, x, y, tx, ty, speed, accuracy, damage):
	_entity = _create(x, y, 'Bullet', '.', 0, 'bullet')
	_entity['owner'] = entity['_id']
	_entity['start_position'] = (x, y)
	_entity['end_position'] = (tx, ty)
	_entity['speed'] = speed
	_entity['damage'] = damage
	
	entities.add_entity_to_group(_entity, 'bullets')
	timers.register(_entity)
	
	entities.trigger_event(_entity, 'set_direction', direction=numbers.direction_to((x, y), (tx, ty))+random.uniform(-accuracy, accuracy))
	entities.trigger_event(_entity, 'create_timer', time=speed, repeat=-1, enter_callback=_bullet_tick, repeat_callback=_bullet_tick)
	entities.register_event(_entity, 'position_changed', lambda e, **kwargs: check_for_collisions(e))
	entities.register_event(_entity, 'collision_with_entity', lambda e, target_id: entities.trigger_event(entities.get_entity(target_id), 'hit', projectile=e))
	entities.register_event(_entity, 'collision_with_entity', lambda e, target_id: entities.delete_entity(e))
	entities.register_event(_entity, 'collision_with_solid', lambda e: effects.light(movement.get_position(e)[0], movement.get_position(e)[1], random.randint(3, 4)))
	entities.register_event(_entity, 'collision_with_solid', lambda e: entities.delete_entity(e))
	entities.register_event(_entity, 'collision_with_solid', lambda e: effects.smoke_cloud(movement.get_position(e)[0], movement.get_position(e)[1], random.uniform(2, 2.75), start_alpha=random.uniform(0.45, .65), decay_amount=1.5))
	entities.register_event(_entity, 'check_next_position', check_next_position)
	
	if not '--no-fx' in sys.argv:
		entities.register_event(_entity, 'position_changed', lambda e, x, y, **kwargs: _bullet_effects(e, x, y))

def _explosive_stop_dumb_hack(entity):
	entity['speed'] = 40

def explosive(entity, x, y, tx, ty, speed, accuracy, damage):
	_entity = _create(x, y, 'Explosive', '.', 0, 'bullet')
	_entity['owner'] = entity['_id']
	_entity['start_position'] = (x, y)
	_entity['end_position'] = (tx, ty)
	_entity['speed'] = speed
	_entity['damage'] = damage
	_toss_distance = numbers.distance(_entity['start_position'], _entity['end_position'])
	_entity['accuracy'] = numbers.clip(random.randint(int(round(accuracy * .25)), accuracy), 0, 100) - (accuracy * (1 - (_toss_distance / 20.0)))
	_entity['slow_down'] = False
	_direction_mod = random.uniform(-accuracy, accuracy) * 2
	
	entities.create_event(_entity, 'explode')
	entities.create_event(_entity, 'activate_explosive')
	entities.register_event(_entity, 'explode', frag_grenade_explode)
	entities.register_event(_entity, 'explode', entities.delete_entity)
	entities.register_event(_entity, 'activate_explosive', lambda e: entities.trigger_event(e, 'create_timer', time=90, exit_callback=lambda ee: entities.trigger_event(ee, 'explode')))
	entities.register_event(_entity, 'check_next_position', check_next_position)
	
	entities.add_entity_to_group(_entity, 'bullets')
	timers.register(_entity)
	
	entities.trigger_event(_entity, 'set_direction', direction=numbers.direction_to((x, y), (tx, ty)) + _direction_mod)
	entities.trigger_event(_entity, 'create_timer', time=speed, enter_callback=_explosive_tick, name='movement')
	entities.register_event(_entity, 'position_changed', lambda e, **kwargs: check_for_collisions(e))
	
	if not '--no-fx' in sys.argv:
		entities.register_event(_entity, 'position_changed', lambda e, x, y, **kwargs: _bullet_effects(e, x, y))
	
	entities.register_event(_entity, 'collision_with_entity', lambda e, **kwargs: entities.trigger_event(e, 'activate_explosive'))
	entities.register_event(_entity, 'collision_with_entity', lambda e, **kwargs: _explosive_stop_dumb_hack(e))
	entities.register_event(_entity, 'collision_with_solid', lambda e: timers.stop_timer(e, 'movement'))
	entities.register_event(_entity, 'collision_with_solid', _explosive_stop_dumb_hack)
	entities.register_event(_entity, 'collision_with_solid', lambda e: entities.trigger_event(e, 'activate_explosive'))