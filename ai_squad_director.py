from framework import entities, movement, shapes, stats, numbers

import libtcodpy as tcod

import ai_factions
import constants
import zones

import logging
import time


def create_position_map(squad, member_id):
	_member = entities.get_entity(member_id)
	_coverage_positions = set()
	#_solids = zones.get_active_solids({}, no_life=True)
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
	
	#for squad_member_id in squad['members']:
	#	if squad_member_id == member_id:
	#		continue
	#	
	#	_m_x, _m_y = movement.get_position_via_id(squad_member_id)
	#	
	#	tcod.map_set_properties(squad['member_los_maps'][member_id], _m_x, _m_y, False, False)
	
	tcod.map_compute_fov(squad['member_los_maps'][member_id], _x, _y, radius=_sight, light_walls=False, algo=tcod.FOV_PERMISSIVE_2)
	
	for pos in shapes.circle(_x, _y, _sight):
		if pos[0] < 0 or pos[0] >= _map_size[0] or pos[1] < 0 or pos[1] >= _map_size[1]:
			continue
		
		if not tcod.map_is_walkable(squad['member_los_maps'][member_id], pos[0], pos[1]):
			continue
	
		_coverage_positions.add(pos)
		squad['member_position_maps'][member_id].add(pos)

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
		
		logging.debug('Updated local position map - requesting squad update')
	else:
		logging.debug('Updated local position map.')
	
	#print time.time()-_t

def update_position_maps(squad):
	if not squad['update_position_maps']:
		return
	
	_t = time.time()
	squad['update_position_maps'] = False
	
	_coverage_positions = squad['coverage_positions']
	_known_targets = squad['known_targets']
	_known_squads = squad['known_squads']
	_known_targets_left_to_check = _known_targets.copy()
	_score_map = {pos: {'coverage': 0, 'vantage': 100, 'member_coverage': 0, 'danger': 0, 'targets': [], 'owned': False} for pos in _coverage_positions}
	
	for faction_name, squad_id in _known_squads:
		_squad = entities.get_entity(ai_factions.FACTIONS[faction_name]['squads'][squad_id])
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
			_cover_positions = _coverage_positions - _target_coverage_map
			
			if not _closest_member['member_id']:
				logging.warning('Couldn\'t find closest member for target during squad positioning.')
				
				continue
			
			_closest_member_pos = movement.get_position_via_id(_closest_member['member_id'])
			
			for pos in _overlap_positions:
				_distance = numbers.distance(_closest_member_pos, pos)
				
				if _distance < _score_map[pos]['vantage']:
					_score_map[pos]['vantage'] = _distance
				
				#_score_map[pos]['danger'] = 60 - _distance
				_score_map[pos]['targets'].append(target_id)
			
			for pos in _cover_positions:
				_distance = numbers.distance(_closest_member_pos, pos)
								
				if _distance > _score_map[pos]['coverage']:
					_score_map[pos]['coverage'] = _distance
				
				_score_map[pos]['danger'] = 60 - _distance
	
	squad['position_map_scores'] = _score_map
	
	#print time.time()-_t

def build_push_map(squad):
	for member_id in squad['members']:
		_member = entities.get_entity(member_id)
		_non_visible_targets = _member['ai']['targets'] - set(_member['ai']['visible_targets'])
		
		for target_id in _non_visible_targets:
			_target = entities.get_entity(target_id)
			_target_squad = entities.get_entity(ai_factions.FACTIONS[_target['ai']['faction']]['squads'][_target['ai']['squad']])

def _reset_fire_position(entity):
	entity['ai']['meta']['has_firing_position'] = True

def get_vantage_point(squad, member_id):
	_member = entities.get_entity(member_id)
	_best_vantage = {'position': None, 'score': 1000}
	_vision = stats.get_vision(_member)
	_engage_range = int(round(_vision * .75))
	
	if _member['movement']['path']['destination']:
		if _member['movement']['path']['destination'] in squad['position_map_scores']:
			_scores = squad['position_map_scores'][_member['movement']['path']['destination']]
			_score = _scores['vantage'] + _scores['member_coverage']
			
			if _scores['targets'] and _score >= 6 and _score <= _engage_range:
				return _member['movement']['path']['destination']
	
	for pos in squad['position_map_scores']:
		_scores = squad['position_map_scores'][pos]
		_score = _scores['vantage'] + _scores['member_coverage']
		
		if not _scores['targets'] or _score < 6 or _score > _engage_range:
			continue

		if _score < _best_vantage['score']:
			_best_vantage['score'] = _score
			_best_vantage['position'] = pos[:]
	
	if not _best_vantage['position']:
		_member['ai']['meta']['has_firing_position'] = False
		
		entities.trigger_event(_member, 'create_timer', time=90, exit_callback=_reset_fire_position)
		
		return
	
	_x, _y = movement.get_position(_member)
	_member_positions = set()
	
	for squad_member_id in squad['members']:
		if squad_member_id == member_id:
			continue
		
		_member_positions.add(movement.get_position_via_id(squad_member_id))
	
	_v_p = _best_vantage['position']
	_friendly_fire = False
	
	for pos in shapes.line((_x, _y), _best_vantage['position']):
		if pos in _member_positions:
			_friendly_fire = True
			
			break

	if _friendly_fire:
		for n_pos in [(_v_p[0]-1, _v_p[1]-1), (_v_p[0], _v_p[1]-1), (_v_p[0]+1, _v_p[1]-1), (_v_p[0]-1, _v_p[1]), (_v_p[0]+1, _v_p[1]), (_v_p[0]-1, _v_p[1]+1), (_v_p[0], _v_p[1]+1), (_v_p[0]+1, _v_p[1]+1)]:
			if not n_pos in squad['position_map_scores']:
				continue
			
			_break = False
			for nn_pos in shapes.line((_x, _y), n_pos):
				if nn_pos in _member_positions:
					_break = True
					
					break
			else:
				_v_p = n_pos
				
				break
			
			if _break:
				continue
	
	for coverage_pos in shapes.circle(_v_p[0], _v_p[1], 6):
		if not coverage_pos in squad['position_map_scores']:
			continue
		
		_c_dist = 15 * (1 - (numbers.distance(coverage_pos, (_x, _y)) / 6.0))
		
		squad['position_map_scores'][coverage_pos]['member_coverage'] += _c_dist
	
	squad['position_map_scores'][_v_p]['member_coverage'] += 20
	
	return _v_p

def get_push_position(squad, member_id):
	_member = entities.get_entity(member_id)
	_best_vantage = {'position': None, 'score': 1000}
	_vision = stats.get_vision(_member)
	_engage_range = int(round(_vision * .75))
	
	for pos in squad['position_map_scores']:
		_scores = squad['position_map_scores'][pos]
		_score = _scores['vantage'] + _scores['member_coverage']
		
		if not _scores['targets'] or _score < 6 or _score > _engage_range:
			continue

		if _score < _best_vantage['score']:
			_best_vantage['score'] = _score
			_best_vantage['position'] = pos[:]
	
	if not _best_vantage['position']:
		_member['ai']['meta']['has_firing_position'] = False
		
		return
	
	_x, _y = movement.get_position(_member)
	
	for coverage_pos in shapes.circle(_best_vantage['position'][0], _best_vantage['position'][1], 6):
		if not coverage_pos in squad['position_map_scores']:
			continue
		
		_c_dist = 15 * (1 - (numbers.distance(coverage_pos, (_x, _y)) / 6.0))
		
		squad['position_map_scores'][coverage_pos]['member_coverage'] += _c_dist
	
	squad['position_map_scores'][_best_vantage['position']]['member_coverage'] += 20
	
	return _best_vantage['position']

def get_cover_position(squad, member_id):
	_member = entities.get_entity(member_id)
	_best_coverage = {'position': None, 'score': 0}
	
	if _member['movement']['path']['destination']:
		_hide_pos = _member['movement']['path']['destination']
	
	else:
		_hide_pos = movement.get_position(_member)
	
	if _hide_pos in squad['position_map_scores']:
		_scores = squad['position_map_scores'][_hide_pos]
		_score = _scores['coverage'] + _scores['member_coverage']
		
		if not _scores['targets'] and _score > 0:
			return _hide_pos
	
	for pos in squad['position_map_scores']:
		_scores = squad['position_map_scores'][pos]
		#TODO: Add or subtract here? Subtraction will make some NPCs run away from teammates
		_score = _scores['coverage'] + _scores['member_coverage']
		
		if _scores['targets'] or _score <= 0:
			continue

		if _score > _best_coverage['score']:
			_best_coverage['score'] = _score
			_best_coverage['position'] = pos[:]
	
	if not _best_coverage['position']:
		#print 'no good coverage position'
		return
	
	_x, _y = movement.get_position(_member)
	
	for coverage_pos in shapes.circle(_best_coverage['position'][0], _best_coverage['position'][1], 6):
		if not coverage_pos in squad['position_map_scores']:
			continue
		
		_c_dist = 10 * (1 - (numbers.distance(coverage_pos, (_x, _y)) / 3.0))
		
		squad['position_map_scores'][coverage_pos]['member_coverage'] += _c_dist
	
	squad['position_map_scores'][_best_coverage['position']]['member_coverage'] += 15
	
	return _best_coverage['position']
