from framework import entities, events

import framework

import world_strategy
import world_action

import cProfile
import time
import sys

ACTIVE_WORLD = None


def main():
	global ACTIVE_WORLD
	
	#world_action.create()
	world_strategy.create()
	
	ACTIVE_WORLD = world_strategy
	
	while ACTIVE_WORLD.loop():
		events.trigger_event('cleanup')

		continue

	framework.shutdown()

if __name__ == '__main__':
	framework.init()
	
	if '--debug' in sys.argv:
		cProfile.run('framework.run(main)', 'profile.dat')
	
	else:
		framework.run(main)
