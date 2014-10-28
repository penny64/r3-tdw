from framework import numbers, shapes

import libtcodpy as tcod

import constants
import mapgen
import tiles
import life

import random


def generate(width, height):
	_weight_map, _tile_map, _solids, _node_grid = mapgen.create_map(width, height)
	_zoom = .95
	_noise = tcod.noise_new(3)
	_low_grass = 25
	_fsl = {}
	_building_space = set()
	_walls = set()
	_possible_trees = set()
	_river_direction = 270
	_turn_rate = random.randint(-1, 1)
	_river_tiles = set()
	_river_size = random.randint(7, 10)
	_ground_tiles = set()
	_possible_camps = set()
	_trees = {}
	_num_walls = 10
	
	for i in range(_num_walls):
		_x = random.randint(int(round(width * .15)), int(round(width * .85)))
		_y = random.randint(int(round(height * .15)), int(round(height * .85)))
		
		for pos in shapes.circle(_x, _y, random.randint(5, 7)):
			_tile = tiles.wooden_fence(pos[0], pos[1])
			_tile_map[pos[1]][pos[0]] = _tile
			_weight_map[pos[1]][pos[0]] = _tile['w']
			_solids.add((pos[0], pos[1]))
	
	for y in range(height):
		for x in range(width):
			if (x, y) in _solids:
				continue
			
			_tile = tiles.grass(x, y)
			_tile_map[y][x] = _tile
			_weight_map[y][x] = _tile['w']
			_ground_tiles.add((x, y))
	
	mapgen.build_node_grid(_node_grid, _solids)
	
	_fsl = {'Runners': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_runner, 'spawn_pos': (15, 50)},
	        'Bandits': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.human_bandit, 'spawn_pos': (60, 50)}}
	#        'Wild Dogs': {'bases': 0, 'squads': 1, 'trader': False, 'type': life.wild_dog}}
	
	return width, height, _node_grid, mapgen.NODE_SETS.copy(), _weight_map, _tile_map, _solids, _fsl, _trees, _building_space - _walls