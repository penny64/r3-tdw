from framework import entities, events

import framework

import world_strategy
import world_action
import world_intro
import world_hire
import world_menu
import words

import cProfile
import time
import sys


def main():
	if not '--dev' in sys.argv:
		#world_action.create()
		world_intro.create()
		
		#while world_intro.loop():
		#	events.trigger_event('cleanup')
		
		world_menu.create()
		
		while world_menu.loop():
			events.trigger_event('cleanup')
	
	#world_hire.create()
	
	#while world_hire.loop():
	#	events.trigger_event('cleanup')
	
	world_strategy.create()	
	
	while world_strategy.loop():
		events.trigger_event('cleanup')

	framework.shutdown()

if __name__ == '__main__':
	framework.init()
	
	framework.events.register_event('boot', words.boot)
	
	if '--debug' in sys.argv:
		cProfile.run('framework.run(main)', 'profile.dat')
	
	else:
		framework.run(main)
