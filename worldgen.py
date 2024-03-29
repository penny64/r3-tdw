from framework import numbers, display, pathfinding, entities, movement

import libtcodpy as tcod

import world_strategy
import mapgen_forest
import mapgen_swamp
import mapgen_arena
import mapgen
import constants
import ai_factions
import ai_squads
import ai_flow
import tiles
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
	
	_weight_map, _tile_map, _solids, _node_grid = mapgen.create_map(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE, constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE)
	
	_ownable_plots = create_map()
	create_bases(_ownable_plots)
	create_factions()
	
	_node_sets = {}
	_fsl = {}
	world_strategy.MAP
	
	for y in range(0, constants.STRAT_MAP_HEIGHT):
		for x in range(0, constants.STRAT_MAP_WIDTH):
			_m_x = x / constants.MAP_CELL_SPACE
			_m_y = y / constants.MAP_CELL_SPACE
			#_camp = world_strategy.MAP['grid'][_m_x, _m_y]
			_tile_map[_m_y][_m_x] = tiles.grass(_m_x, _m_y)
	
	_zone_id = zones.create('arena', constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE, constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE, _node_grid, _node_sets, _weight_map, _tile_map, {}, _fsl, {}, {}, [], [])
	zones.activate(_zone_id)
	#if '--arena' in sys.argv:
	#	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside = mapgen_arena.generate(100, 100)
	#else:
	#	_width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside = mapgen_swamp.generate(300, 300)
	
	#_swamp_id = zones.create('swamps', _width, _height, _node_grid, _node_sets, _weight_map, _tile_map, _solids, _fsl, _trees, _inside)
	
	#zones.populate_life(_swamp_id)
	#zones.activate(_swamp_id)

def create_map():
	_grid = world_strategy.MAP['grid']
	_color_map = world_strategy.MAP['color_map']
	_ownable_plots = set()
	_banned_plots = set()
	
	#Mountains
	_noise = tcod.noise_new(3)
	_zoom = 1.25
	_c_pos = constants.STRAT_MAP_WIDTH/2, constants.STRAT_MAP_HEIGHT/2
	_solids = set()
	
	for y in range(0, constants.STRAT_MAP_HEIGHT):
		for x in range(0, constants.STRAT_MAP_WIDTH):
			_m_x = x / constants.MAP_CELL_SPACE
			_m_y = y / constants.MAP_CELL_SPACE
			
			_m_x = numbers.clip(_m_x, 1, (constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE) - 2)
			_m_y = numbers.clip(_m_y, 1, (constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE) - 2)
			_c_mod = numbers.float_distance(_c_pos, (x, y))/max([constants.STRAT_MAP_WIDTH/2, constants.STRAT_MAP_HEIGHT/2])
			_noise_values = [(_zoom * x / (constants.STRAT_MAP_WIDTH)),
					         (_zoom * y / (constants.STRAT_MAP_HEIGHT))]
			_height = tcod.noise_get_turbulence(_noise, _noise_values, tcod.NOISE_SIMPLEX) * _c_mod
			_char = ' '
			
			#Mountain
			if _height > .55:
				_color_map[x, y] = random.choice([constants.DARKER_GRAY_1,
				                                  constants.DARKER_GRAY_2,
				                                  constants.DARKER_GRAY_3])
				
				_grid[_m_x, _m_y]['is_ownable'] = False
				_banned_plots.add((_m_x, _m_y))
				
				_c_1 = int(round(_color_map[x, y][0] * (1.8 * _height)))
				_c_2 = int(round(_color_map[x, y][1] * (1.8 * _height)))
				_c_3 = int(round(_color_map[x, y][2] * (1.8 * _height)))
			
			else:
				_color_map[x, y] = random.choice([constants.FOREST_GREEN_1,
				                                  constants.FOREST_GREEN_2,
				                                  constants.FOREST_GREEN_3])
				
				_ownable_plots.add((_m_x, _m_y))

				if _height <= .2:
					_char = random.choice([',', '.', '\'', ' ' * (1 + (20 * int(round(_height))))])
				
				_height -= .1

				_c_1 = int(round(_color_map[x, y][0] * (.7 + _height * 2.8)))
				_c_2 = int(round(_color_map[x, y][1] * (1.0 + _height * .9)))
				_c_3 = int(round(_color_map[x, y][2] * (.75 + _height * 1.2)))
			
			display._set_char('map', x, y, _char, (int(round(_c_1 * .8)), int(round(_c_2 * .8)), int(round(_c_3 * .8))), (_c_1, _c_2, _c_3))
	
	_solids = [(x, y) for x, y in list(_banned_plots)]
	
	world_strategy.MAP['astar_map'] = pathfinding.setup(constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE,
	                                                    constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE,
	                                                    _solids)
	
	return list(_ownable_plots - _banned_plots)

def create_bases(ownable_plots):
	_width = constants.STRAT_MAP_WIDTH/constants.MAP_CELL_SPACE
	_height = constants.STRAT_MAP_HEIGHT/constants.MAP_CELL_SPACE
	_bases = []
	
	for i in range(6):
		while 1:
			_new_base_pos = random.choice(ownable_plots)
			_min_distance = 0
			
			for base_pos in _bases:
				_distance = numbers.distance(_new_base_pos, base_pos)
				
				if _distance <= 2:
					break
				
				_min_distance = _distance
			
			else:
				if _min_distance >= 7:
					continue
				
				_bases.append(_new_base_pos)
				ownable_plots.remove(_new_base_pos)
				
				break
	
	for b_x, b_y in _bases:
		world_strategy.MAP['grid'][b_x, b_y]['is_ownable'] = True

def create_factions():
	_ownable_spots = [p for p in world_strategy.MAP['grid'].keys() if world_strategy.MAP['grid'][p]['is_ownable'] and not world_strategy.MAP['grid'][p]['owned_by']]
	
	for faction_name in ['Rogues', 'Terrorists']:
		_plot_pos = _ownable_spots.pop(0)
		_plot = world_strategy.MAP['grid'][_plot_pos]
		_squad = ai_squads.create_human_squad(faction_name, _plot_pos[0], _plot_pos[1])
		_plot['owned_by'] = faction_name
		
		if faction_name == 'Rogues':
			entities.register_event(_squad, 'raid', lambda e, **kwargs: world_strategy.news('Order: Squad %s is raiding %s, %s.' % (e['squad_id'], _plot_pos[0], _plot_pos[1]),
			                                                                                fore_color=(200, 40, 40)))
			entities.register_event(_squad, 'position_changed', lambda e, **kwargs: _handle_squad_position_update(e))
		
		for i in range(3):
			if faction_name == 'Rogues':
				if i == 0:
					_e = life.engineer(30 + i * 2, 7, 'Good Dude %i' % i, faction_name, is_player=True)
				else:
					continue
					#_e = life.turret(30, 7 + i * 2, 'Turret %i' % i, faction_name)
					#_e = life.engineer(30 + i * 2, 17, 'Good Dude %i' % i, faction_name)
			
			else:
				if random.randint(0, 1):
					#_e = life.sniper(50 + i * 2, 50, 'Bad Dude %i' % i, faction_name)
					#_e = life.turret(10, 70 + i * 2, 'Turret', faction_name)
					#_e = life.engineer(50 + i * 2, 50, 'Bad Dude %i' % i, faction_name)
					_e = life.grenadier(50 + i * 2, 50, 'Bad Dude %i' % i, faction_name)
				
				else:
					_e = life.grenadier(50 + i * 2, 50, 'Bad Dude %i' % i, faction_name)
					#_e = life.turret(10, 70 + i * 2, 'Turret', faction_name)
	
			ai_squads.register_with_squad(_e, _squad['squad_id'])

def _handle_squad_position_update(entity):
	if len(entity['movement']['path']['positions']) == 1:
		world_strategy.news('Alert: Squad %s is arriving at %s, %s.' % (entity['squad_id'],
		                                                                entity['movement']['path']['destination'][0],
		                                                                entity['movement']['path']['destination'][1]),
		                    fore_color=(200, 40, 40), back_color=(80, 0, 0))
	
	elif not len(entity['movement']['path']['positions']):
		_x, _y = movement.get_position(entity)
		_camp = world_strategy.MAP['grid'][_x, _y]
		
		if _camp['owned_by'] and not entity['faction'] == _camp['owned_by']:
			_defending_squads = []
			
			for squad_id in entities.get_entity_group('squads'):
				_squad = entities.get_entity(squad_id)
				
				if _squad['faction'] == _camp['owned_by']:
					_defending_squads.append(squad_id)
			
			world_strategy.unregister_input()
			world_strategy.world_action.start_battle(attacking_squads=[entity['_id']], defending_squads=_defending_squads)