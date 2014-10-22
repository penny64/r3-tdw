from framework import entities, movement, shapes, stats, numbers

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
	
	squad['member_position_maps'][member_id] = set()
	
	for pos in shapes.circle(_x, _y, _sight):
		if not pos[0] % 2 and not pos[1] % 2:
			continue
		
		if pos in _solids:
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

def update_position_maps(squad):
	if not squad['update_position_maps']:
		return
	
	_t = time.time()
	squad['update_position_maps'] = False
	
	_coverage_positions = squad['coverage_positions']
	_known_targets = squad['known_targets']
	_known_squads = squad['known_squads']
	_known_targets_left_to_check = _known_targets.copy()
	_score_map = {pos: {'coverage': 100, 'vantage': 0, 'danger': 0} for pos in _coverage_positions}
	
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
			
			#_target = entities.get_entity(target_id)
			_target_coverage_map = _squad['member_position_maps'][target_id]
			_overlap_positions = _coverage_positions & _target_coverage_map
			_distance = _closest_member['distance']
			#print _coverage_positions & _target_coverage_map
			
			for pos in _overlap_positions:
				_score_map[pos]['coverage'] -= 60 - _distance
				_score_map[pos]['vantage'] = _distance
				_score_map[pos]['danger'] -= 60 - _distance
	
	print time.time()-_t