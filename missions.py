from framework import entities

#Steps:
#Create mission
#Add goals
#Add mission to character
#Character registers with get_item/kill/etc?


def register(entity):
	entity['missions'] = {'id': 0,
	                      'active': {}}
	
	entities.create_event(entity, 'add_mission')
	entities.register_event(entity, 'add_mission', add_mission)

def add_mission(entity, mission_id):
	entity['missions']['id'] += 1
	entity['missions']['active'][entity['missions']['id']] = mission_id

def create():
	_mission = entities.create_entity(group='missions')
	_mission.update({'goals': []})
	
	return _mission

def add_goal_kill_npc(mission, target_id):
	#TODO: Register 
	_goal = {'intent': 'kill', 'target_id': target_id}
	
	mission['goals'].append(_goal)