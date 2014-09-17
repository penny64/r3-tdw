from framework import entities, display, movement, numbers

import constants
import effects
import zones

import random


def _limb():
	return {'critical': False, 'stat_mod': {}, 'accuracy': .2}

def register(entity):
	entity['skeleton'] = {}
	
	entities.create_event(entity, 'hit')
	entities.register_event(entity, 'hit', hit)
	entities.register_event(entity, 'get_speed', get_speed_mod)
	entities.register_event(entity, 'get_accuracy', get_accuracy_mod)
	
	return entity

def create_limb(entity, name, parent_limbs, critical, accuracy, stat_mod={}, can_sever=False, health=100):
	entity['skeleton'][name] = {'critical': critical,
	                            'stat_mod': stat_mod,
	                            'accuracy': accuracy,
	                            'parent_limbs': parent_limbs,
	                            'child_limbs': [],
	                            'health': health,
	                            'max_health': health,
	                            'can_sever': can_sever}
	
	for limb in parent_limbs:
		entity['skeleton'][limb]['child_limbs'].append(name)

def hit(entity, projectile):
	_accuracy = random.uniform(.1, 1)
	_hit_map = []
	
	for limb_name in entity['skeleton']:
		_limb = entity['skeleton'][limb_name]
		
		for i in range(int(round(_limb['health']*_limb['accuracy']))):
			_hit_map.append(limb_name)
	
	_limb_name = random.choice(_hit_map)
	_limb = entity['skeleton'][_limb_name]
	_damage = int(round(70 * _accuracy))
	_limb['health'] -= _damage
	_x, _y = movement.get_position(entity)
	_x += int(round(random.uniform(-1, 1)))
	_y += int(round(random.uniform(-1, 1)))
	_mod = _limb['health']/float(_limb['max_health'])
	
	if not (_x, _y) in zones.get_active_solids(entity, ignore_calling_entity=True):
		effects.blood(_x, _y)
		entities.trigger_event(entity, 'animate', animation=['X', '@@'], repeat=4 * int(round((1-_mod))), delay=20 * _mod)
	
	if _limb['health'] <= 0:
		if _limb['critical']:
			if projectile['owner'] in entities.ENTITIES:
				entities.trigger_event(entities.get_entity(projectile['owner']), 'log_kill', target_id=entity['_id'])
				entities.trigger_event(entity, 'killed_by', target_id=projectile['owner'])
			
			entities.delete_entity(entity)
	else:
		if projectile['owner'] in entities.ENTITIES:
			entities.trigger_event(entities.get_entity(projectile['owner']), 'did_damage', target_id=entity['_id'], damage=_damage)
		
		entities.trigger_event(entity, 'damage')


############
#Operations#
############

def get_speed_mod(entity):
	for limb_name in entity['skeleton']:
		_limb = entity['skeleton'][limb_name]
		
		if 'speed' in _limb['stat_mod']:
			_mod = _limb['health'] / float(_limb['max_health'])
			
			entity['stats']['speed'] *= numbers.clip(1+(1-_mod), 1, 1+_limb['stat_mod']['speed'])
	
	entity['stats']['speed'] = int(round(entity['stats']['speed']))

def get_accuracy_mod(entity):
	for limb_name in entity['skeleton']:
		_limb = entity['skeleton'][limb_name]
		
		if 'accuracy' in _limb['stat_mod']:
			_mod = _limb['health'] / float(_limb['max_health'])
			
			entity['stats']['accuracy'] *= numbers.clip(1+(1-_mod), 1, 1+_limb['stat_mod']['accuracy'])
	
	entity['stats']['accuracy'] = int(round(entity['stats']['accuracy']))

def has_critical_injury(entity):
	for limb_name in entity['skeleton']:
		_limb = entity['skeleton'][limb_name]
		
		if _limb['health'] / float(_limb['max_health']) <= .75:
			return True

	return False
