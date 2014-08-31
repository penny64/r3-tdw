from framework import entities

import random


def _limb():
	return {'critical': False, 'stat_mod': {}, 'accuracy': .2}

def register(entity):
	entity['skeleton'] = {}
	
	entities.create_event(entity, 'hit')
	entities.register_event(entity, 'hit', hit)
	
	return entity

def create_limb(entity, name, parent_limbs, critical, accuracy, stat_mod={}):
	entity['skeleton'][name] = {'critical': critical,
	                            'stat_mod': stat_mod,
	                            'accuracy': accuracy,
	                            'parent_limbs': parent_limbs,
	                            'child_limbs': [],
	                            'health': 100,
	                            'max_health': 100}
	
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
	
	print _limb_name, _limb['health']
	
	if _limb['health'] <= 0:
		if _limb['critical']:
			entities.delete_entity(entity)
			
			print 'DIE'
	else:
		entities.trigger_event(entity, 'damage')