from framework import entities, events

import framework

import world_action

import cProfile
import time
import sys


def main():
	world_action.create()
	world_strategy.create()
	
	while world_action.loop():
		events.trigger_event('cleanup')

		continue

	framework.shutdown()

if __name__ == '__main__':
	framework.init()
	
	if '--debug' in sys.argv:
		cProfile.run('framework.run(main)', 'profile.dat')
	
	else:
		framework.run(main)
