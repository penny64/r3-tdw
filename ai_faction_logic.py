from framework import entities

import ai_factions
import zones


def register_human(entity):
	entities.register_event(entity, 'logic', _human_logic)
	
	return entity

def register_animal(entity):
	entities.register_event(entity, 'logic', _animal_logic)
	
	return entity

def _human_logic(entity):
	pass

def _animal_logic(entity):
	pass
	

############
#Operations#
############

