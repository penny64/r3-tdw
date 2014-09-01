from framework import entities

import ai_factions
import zones


def register_human(entity):
	entities.register_event(entity, 'logic', _human_logic)
	
	return entity

def register_animal(entity):
	entities.register_event(entity, 'logic', _human_animal)
	
	return entity

def _human_logic(entity):
	pass

def _human_animal(entity):
	_camps = zones.get_active_node_sets()
	
	for camp_id in _camps:
		_camp = _camps[camp_id]
		
		if not _camp['owner']['faction'] in entity['enemies']:
			continue
	
		for squad_id in entity['squads']:
			_squad = entity['squads'][squad_id]
			
			if _squad['task']:
				continue
			
			entities.trigger_event(_squad, 'raid', camp=_camps[camp_id])
			
			_squad['task'] = 'raid'
	

############
#Operations#
############

