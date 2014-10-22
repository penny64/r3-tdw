import mapgen_forest
import mapgen_swamp
import zones

import logging


def generate():
	logging.info('Generating world...')
	
	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside = mapgen_swamp.generate(350, 350)
	_swamp_id = zones.create('swamps', _width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside)
	
	zones.populate_life(_swamp_id)
	zones.activate(_swamp_id)