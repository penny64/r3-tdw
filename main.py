from framework import entities, events

import framework

import world_strategy
import world_action
import world_intro
import world_menu

import cProfile
import time
import sys


def main():
	#world_action.create()
	world_intro.create()
	
	#while world_intro.loop():
	#	events.trigger_event('cleanup')
	
	#world_menu.create()
	
	#while world_menu.loop():
	#	events.trigger_event('cleanup')
	
	world_strategy.create()	
	
	while world_strategy.loop():
		events.trigger_event('cleanup')

	framework.shutdown()

if __name__ == '__main__':
	framework.init()
	
	if '--debug' in sys.argv:
		cProfile.run('framework.run(main)', 'profile.dat')
	
	else:
		framework.run(main)
