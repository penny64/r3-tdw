from framework import entities, display, movement

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
	
	return entity

def create_limb(entity, name, parent_limbs, critical, accuracy, stat_mod={}, health=100):
	entity['skeleton'][name] = {'critical': critical,
	                            'stat_mod': stat_mod,
	                            'accuracy': accuracy,
	                            'parent_limbs': parent_limbs,
	                            'child_limbs': [],
	                            'health': health,
	                            'max_health': health}
	
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
	_limb['health'] -= int(round(70 * _accuracy))
	
	_x, _y = movement.get_position(entity)
	_x += int(round(random.uniform(-1, 1)))
	_y += int(round(random.uniform(-1, 1)))
	_mod = _limb['health']/float(_limb['max_health'])
	
	if not (_x, _y) in zones.get_active_solids(entity, ignore_calling_entity=True):
		effects.blood(_x, _y)
		entities.trigger_event(entity, 'animate', animation=['X', '@@'], repeat=4 * int(round((1-_mod))), delay=20 * _mod)
	
	if _limb['health'] <= 0:
		if _limb['critical']:
			entities.delete_entity(entity)
	else:
		entities.trigger_event(entity, 'damage')


############
#Operations#
############

def has_critical_injury(entity):
	for limb_name in entity['skeleton']:
		_limb = entity['skeleton'][limb_name]
		
		if _limb['health'] / float(_limb['max_health']) <= .75:
			return True

	return False
