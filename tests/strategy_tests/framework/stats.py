from framework import entities, numbers

import random


def register(entity, health, strength, defense, speed, faction='Neutral', panic=0, name='Unknown'):
	_stats = {'health': health,
			  'max_health': health,
			  'speed': speed,
			  'strength': strength,
			  'defense': defense,
			  'panic': panic,
	          'faction': faction,
	          'name': name,
	          'last_engaged': None,
	          'perks': [],
	          'kills': 0}

	entities.create_event(entity, 'kill')
	entities.create_event(entity, 'log_kill')
	entities.create_event(entity, 'heal')
	entities.create_event(entity, 'hurt')
	entities.create_event(entity, 'haste')
	entities.create_event(entity, 'slow')
	entities.create_event(entity, 'stress')
	entities.create_event(entity, 'calm')
	entities.create_event(entity, 'strengthen')
	entities.create_event(entity, 'weaken')
	entities.create_event(entity, 'fortify')
	entities.create_event(entity, 'expose')
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
	#TODO: Let events modify this value
	_strength = entity['stats']['strength']
	
	#if items:
	#	for item in inventory.get_items(entity):
	#		_strength += item['stats']['strength']
	
	return _strength

def get_speed(entity, items=True):
	#TODO: Let events modify this value
	_speed = entity['stats']['speed']
	
	#if items:
	#	for item in inventory.get_items(entity):
	#		_speed += item['stats']['speed']
	
	return _speed

def get_damage_mod(entity):
	return numbers.clip(random.randint(0, get_strength(entity)) / float(get_strength(entity)), .50, 1)
