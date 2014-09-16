from framework import entities, numbers, flags

import random


def register(entity, health, speed, accuracy=1.0, name='Unknown'):
	_stats = {'health': health,
			  'max_health': health,
			  'speed': speed,
	          'max_speed': speed,
	          'accuracy': accuracy,
	          'max_accuracy': accuracy,
	          'name': name,
	          'last_engaged': None,
	          'kills': 0}

	entities.create_event(entity, 'kill')
	entities.create_event(entity, 'log_kill')
	entities.create_event(entity, 'heal')
	entities.create_event(entity, 'hurt')
	entities.create_event(entity, 'haste')
	entities.create_event(entity, 'slow')
	entities.create_event(entity, 'get_speed')
	entities.create_event(entity, 'get_accuracy')
	entities.register_event(entity, 'hurt', hurt)
	entities.register_event(entity, 'kill', kill)
	entities.register_event(entity, 'log_kill', log_kill)

	entity['stats'] = _stats

def hurt(entity, damage, target_id):
	_target = entities.get_entity(target_id)

	entity['stats']['health'] -= damage
	
	if entity['stats']['health'] <= 0:
		entities.trigger_event(entity, 'kill')
		entities.trigger_event(_target, 'log_kill', target_id=entity['_id'])

def kill(entity, **kwargs):
	entities.delete_entity(entity)

def log_kill(entity, **kwarg):
	entity['stats']['kills'] += 1

def get_strength(entity, items=True):
	_strength = entity['stats']['strength']
	
	#if items:
	#	for item in inventory.get_items(entity):
	#		_strength += item['stats']['strength']
	
	return _strength

def get_speed(entity, items=True):
	entity['stats']['speed'] = entity['stats']['max_speed']
	
	entities.trigger_event(entity, 'get_speed')
	
	#if items:
	#	for item in inventory.get_items(entity):
	#		_speed += item['stats']['speed']
	
	return entity['stats']['speed']

def get_accuracy(entity, weapon_id):
	entity['stats']['accuracy'] = entity['stats']['max_accuracy']
	_weapon = entities.get_entity(weapon_id)
	
	entities.trigger_event(entity, 'get_accuracy')
	_weapon_accuracy = flags.get_flag(_weapon, 'accuracy')
	
	return int(round(_weapon_accuracy * entity['stats']['accuracy']))

def get_damage_mod(entity):
	return numbers.clip(random.randint(0, get_strength(entity)) / float(get_strength(entity)), .50, 1)
