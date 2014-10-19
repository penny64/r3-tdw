from framework import entities

import ai_factions
import items


def share_life_memory_location(entity, target_id, life_id):
	_target = entities.get_entity(target_id)
	_is_life_enemy = ai_factions.is_enemy(entity, life_id)
	
	if not life_id in entity['ai']['life_memory'] or not entity['ai']['life_memory'][life_id]['last_seen_at']:
		entities.trigger_event(_target, 'receive_memory',
		                       member_id=entity['_id'],
		                       memory={},
		                       message='I don\'t know who you\'re talking about.')
	
	else:
		_memory = entity['ai']['life_memory'][life_id]
		
		entities.trigger_event(_target, 'receive_memory',
		                       member_id=entity['_id'],
		                       memory={life_id: {'last_seen_at': _memory['last_seen_at'][:]}},
		                       message='Oh yeah, I saw them recently.')

def give_item(entity, target_id, item_match):
	_items = items.get_items_matching(entity, item_match)
	
	if not _items:
		entities.trigger_event(entity, 'receive_memory',
		                       member_id=entity['_id'],
		                       memory={},
		                       message='You got the item yet?')
		return None
	
	entities.trigger_event(entity, 'give_item', item_id=_items[0], target_id=target_id)
