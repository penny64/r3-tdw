from framework import entities, numbers, flags

import random


def register(entity, health, speed, vision, class_name='Gunner', respect=1, accuracy=1.0, mobility=80, intelligence=90, action_points=100, smgs=50, rifles=50, pistols=50, name='Unknown', kind='unknown'):
	_stats = {'health': health,
			  'max_health': health,
			  'speed': speed,
	          'max_speed': speed,
	          'pain': 0,
	          'accuracy': accuracy,
	          'max_accuracy': accuracy,
	          'vision': vision,
	          'max_vision': vision,
	          'action_points': action_points,
	          'action_points_max': action_points,
	          'intelligence': intelligence,
	          'skill_points': int(round(100 * (intelligence/100.0))),
	          'mobility': mobility,
	          'class': class_name,
	          'smgs': smgs,
	          'rifles': rifles,
	          'pistols': pistols,
	          'name': name,
	          'kind': kind,
	          'last_engaged': None,
	          'respect': 0,
	          'rank': 'Unknown',
	          'last_rank': 'Unknown',
	          'kills': 0}
	
	entity['stats'] = _stats

	entities.create_event(entity, 'kill')
	entities.create_event(entity, 'killed_by')
	entities.create_event(entity, 'log_kill')
	entities.create_event(entity, 'heal')
	entities.create_event(entity, 'haste')
	entities.create_event(entity, 'slow')
	entities.create_event(entity, 'set_respect')
	entities.create_event(entity, 'set_rank')
	entities.create_event(entity, 'get_speed')
	entities.create_event(entity, 'get_vision')
	entities.create_event(entity, 'get_accuracy')
	entities.register_event(entity, 'kill', kill)
	entities.register_event(entity, 'set_respect', set_respect)
	entities.register_event(entity, 'set_rank', set_rank)
	entities.register_event(entity, 'log_kill', add_respect)
	entities.register_event(entity, 'log_kill', log_kill)
	entities.register_event(entity, 'save', save)
	entities.trigger_event(entity, 'set_respect', respect=respect)

def save(entity, snapshot):
	snapshot['stats'] = entity['stats']

def kill(entity, **kwargs):
	entities.delete_entity(entity)

def log_kill(entity, **kwarg):
	entity['stats']['kills'] += 1

def set_respect(entity, respect):
	entity['stats']['respect'] = respect
	
	if respect <= 3:
		entities.trigger_event(entity, 'set_rank', rank='Newcomer')
	
	elif respect <= 10:
		entities.trigger_event(entity, 'set_rank', rank='Rookie')

def set_rank(entity, rank):
	entity['stats']['last_rank'] = entity['stats']['rank']
	entity['stats']['rank'] = rank

def add_respect(entity, target_id):
	_target = entities.get_entity(target_id)
	_respect = entity['stats']['respect']
	_target_respect = _target['stats']['respect']
	
	if _respect >= _target_respect:
		_target_respect *= 1 - numbers.clip((_respect - _target_respect) / 10.0, 0, 1)
	
	entities.trigger_event(entity, 'set_respect', respect = entity['stats']['respect'] + int(round(_target_respect)))

def get_action_points(entity):
	return entity['stats']['action_points']

def get_vision(entity):
	entity['stats']['vision'] = entity['stats']['max_vision']
	
	entities.trigger_event(entity, 'get_vision')
	
	return entity['stats']['vision']

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

def get_shoot_cost(entity, weapon_id):
	_weapon = entities.get_entity(weapon_id)
	_weapon_accuracy = flags.get_flag(_weapon, 'shoot_cost')
	
	return _weapon_accuracy

def get_accuracy(entity, weapon_id):
	entity['stats']['accuracy'] = entity['stats']['max_accuracy']
	_weapon = entities.get_entity(weapon_id)
	
	entities.trigger_event(entity, 'get_accuracy')
	_weapon_accuracy = flags.get_flag(_weapon, 'accuracy')
	
	if _weapon['stats']['kind'] == 'pistol':
		_weapon_accuracy *= 1 + (1 - (entity['stats']['pistols'] / 100.0))
	
	elif _weapon['stats']['kind'] == 'rifle':
		_weapon_accuracy *= 1 + (1 - (entity['stats']['rifles'] / 100.0))
	
	else:
		raise Exception('Invalid gun type.')
	
	return int(round(_weapon_accuracy * entity['stats']['accuracy']))

def get_damage_mod(entity):
	return numbers.clip(random.randint(0, get_strength(entity)) / float(get_strength(entity)), .50, 1)
