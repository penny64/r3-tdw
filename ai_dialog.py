from framework import entities

import ai_factions


def share_life_memory_location(entity, target_id, life_id):
	_target = entities.get_entity(target_id)
	_is_target_enemy = ai_factions.is_enemy(entity, target_id)
	
	if not life_id in entity['ai']['life_memory'] or not entity['ai']['life_memory'][life_id]['last_seen_at']:
		print entity['ai']['life_memory'][life_id]
		
		entities.trigger_event(_target, 'receive_memory',
		                       member_id=entity['_id'],
		                       memory={},
		                       message='I don\'t know who you\'re talking about.')
	
	else:
		_memory = entity['ai']['life_memory'][life_id]
		
		entities.trigger_event(_target, 'receive_memory',
		                       member_id=entity['_id'],
		                       memory={'last_seen_at': _memory['last_seen_at'][:]},
		                       message='Oh yeah, I saw them recently.')