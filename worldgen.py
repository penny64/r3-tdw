from framework import numbers

import world_strategy
import mapgen_forest
import mapgen_swamp
import mapgen_arena
import constants
import ai_factions
import ai_squads
import ai_flow
import zones
import life

import logging
import random
import sys


def generate():
	logging.info('Generating world...')
	
	ai_factions.boot()
	ai_squads.boot()
	ai_flow.boot()
	
	create_bases()
	create_runners()
	
	#if '--arena' in sys.argv:
	#	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside = mapgen_arena.generate(100, 100)
	#else:
	#	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside = mapgen_swamp.generate(300, 300)
	
	#_swamp_id = zones.create('swamps', _width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside)
	
	#zones.populate_life(_swamp_id)
	#zones.activate(_swamp_id)

def create_bases():
	_width = constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE
	_height = constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE
	_bases = []
	
	for i in range(4):
		while 1:
			_new_base_pos = random.randint(0, _width), random.randint(0, _height)
			
			for base_pos in _bases:
				if numbers.distance(_new_base_pos, base_pos) <= 2:
					break
			
			else:
				_bases.append(_new_base_pos)
				
				break
	
	for b_x, b_y in _bases:
		world_strategy.MAP['map_grid'][b_x, b_y]['is_ownable'] = True

def create_runners():
	_squad = ai_squads.create_human_squad('Rogues')
	
	_e = life.human(15, 15, 'Tester Toaster')
	
	ai_squads.register_with_squad(_e, _squad['squad_id'])