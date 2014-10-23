from framework import entities, movement, shapes, stats, numbers

import libtcodpy as tcod

import ai_factions
import constants
import zones

import time


def create_position_map(squad, member_id):
	_member = entities.get_entity(member_id)
	_coverage_positions = set()
	_solids = zones.get_active_solids({}, no_life=True)
	_known_targets = set()
	_known_squads = set()
	_x, _y = movement.get_position(_member)
	_sight = stats.get_vision(_member)
	
	if member_id in squad['member_position_maps']:
		_old_coverage_positions = squad['member_position_maps'][member_id].copy()
	
	else:
		_old_coverage_positions = set()
	
	_map_size = zones.get_active_size()
	squad['member_position_maps'][member_id] = set()
	squad['member_los_maps'][member_id] = tcod.map_new(_map_size[0], _map_size[1])
	
	tcod.map_copy(zones.get_active_los_map(), squad['member_los_maps'][member_id])
	
	_t = time.time()
	tcod.map_compute_fov(squad['member_los_maps'][member_id], _x, _y, radius=_sight, light_walls=False, algo=tcod.FOV_PERMISSIVE_1)
	
	for pos in shapes.circle(_x, _y, _sight):
		if not tcod.map_is_walkable(squad['member_los_maps'][member_id], pos[0], pos[1]):
			continue
	
		_coverage_positions.add(pos)
		squad['member_position_maps'][member_id].add(pos)
	
	#print time.time()-_t

	#TODO: Do this elsewhere
	for target_id in _member['ai']['visible_targets']:
		if not target_id in entities.ENTITIES:
			continue
		
		_target = entities.get_entity(target_id)
		_known_squads.add((_target['ai']['faction'], _target['ai']['squad']))
	
	#TODO: Is this right?
	_known_targets.update(_member['ai']['visible_targets'])
	
	_positions_to_remove = _old_coverage_positions - _coverage_positions
	
	squad['known_targets'].update(_known_targets)
	squad['known_squads'].update(_known_squads)
	squad['coverage_positions'].update(_coverage_positions)
	squad['coverage_positions'] = squad['coverage_positions'] - _positions_to_remove
	
	if squad['known_targets']:
		squad['update_position_maps'] = True

def update_position_maps(squad):
	if not squad['update_position_maps']:
		return
	
	squad['update_position_maps'] = False
	
	_coverage_positions = squad['coverage_positions']
	_known_targets = squad['known_targets']
	_known_squads = squad['known_squads']
	_known_targets_left_to_check = _known_targets.copy()
	_score_map = {pos: {'coverage': 0, 'vantage': 100, 'danger': 0, 'targets': [], 'owned': False} for pos in _coverage_positions}
	
	for faction_name, squad_id in _known_squads:
		_squad = ai_factions.FACTIONS[faction_name]['squads'][squad_id]
		_member_set = set(_squad['members'])
		_check_members = _known_targets_left_to_check & _member_set
		_known_targets_left_to_check = _known_targets_left_to_check - _member_set
		
		for target_id in list(_check_members):
			_target_position = movement.get_position_via_id(target_id)
			_closest_member = {'distance': 0, 'member_id': None}
			
			for member_id in squad['members']:
				_member_position = movement.get_position_via_id(member_id)
				_distance = numbers.clip(numbers.distance(_target_position, _member_position), 0, 60)
				
				if not _closest_member['member_id'] or _distance < _closest_member['distance']:
					_closest_member['distance'] = _distance
					_closest_member['member_id'] = member_id
			
			_target_coverage_map = _squad['member_position_maps'][target_id]
			_overlap_positions = _coverage_positions & _target_coverage_map
			_distance = _closest_member['distance']
			
			for pos in _overlap_positions:
				if _distance < _score_map[pos]['vantage']:
					_score_map[pos]['vantage'] = _distance
				
				_score_map[pos]['danger'] = 60 - _distance
				_score_map[pos]['targets'].append(target_id)
	
	squad['position_map_scores'] = _score_map

def get_vantage_point(squad, member_id):
	_member = entities.get_entity(member_id)
	_best_vantage = {'position': None, 'score': 1000}
	_vision = stats.get_vision(_member)
	_engage_range = int(round(_vision * .75))
	
	for pos in squad['position_map_scores']:
		_scores = squad['position_map_scores'][pos]
		_score = _scores['vantage'] + _scores['coverage']
		
		if _score < 6 or _score > _engage_range or not _scores['targets']:
			continue

		if _score < _best_vantage['score']:
			_best_vantage['score'] = _score
			_best_vantage['position'] = pos[:]
	
	if not _best_vantage['position']:
		print 'No good firing position.'
		#_member['ai']['meta']['has_firing_position'] = False
		return
	
	print 'Has firing position'
	_x, _y = movement.get_position(_member)
	
	#for coverage_pos in shapes.circle(_best_vantage['position'][0], _best_vantage['position'][1], 3):
	#	if not coverage_pos in squad['position_map_scores']:
	#		continue
	#	
	#	_c_dist = 10 * (1 - (numbers.distance(coverage_pos, (_x, _y)) / 3.0))
	#	
	#	squad['position_map_scores'][coverage_pos]['coverage'] += _c_dist
	
	squad['position_map_scores'][_best_vantage['position']]['coverage'] += 20
	
	return _best_vantage['position']