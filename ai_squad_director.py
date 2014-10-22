from framework import entities, movement, shapes, stats

import ai_factions
import constants
import zones


def create_position_maps(squad):
	_coverage_positions = set()
	_solids = zones.get_active_solids({}, no_life=True)
	_known_targets = set()
	_known_squads = set() #Temp
	
	squad['member_position_maps'] = {}
	
	for member_id in squad['members']:
		_member = entities.get_entity(member_id)
		_x, _y = movement.get_position(_member)
		_sight = stats.get_speed(_member)
		
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
	
	squad['known_targets'] = _known_targets
	squad['known_squads'] = _known_squads
	squad['coverage_positions'] = _coverage_positions

def update_position_maps(squad):
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
			#_target = entities.get_entity(target_id)
			_target_coverage_map = _squad['member_position_maps'][target_id]
			_overlap_positions = _coverage_positions & _target_coverage_map
			print _overlap_positions
			
			for pos in _overlap_positions:
				_score_map[pos]['coverage'] = 0
				_score_map[pos]['vantage'] = 0
				_score_map[pos]['danger'] = 100
