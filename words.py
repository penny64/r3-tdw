import random
import os


NAMES = set()
USED_NAMES = set()


def boot():
	global NAMES
	
	with open(os.path.join('data', 'names_male.csv')) as e:
		NAMES = set([l.rstrip() for l in e.readlines() if len(l) < 18])

def reset():
	global USED_NAMES
	
	USED_NAMES = set()

def get_male_name():
	_name = random.choice(list(NAMES - USED_NAMES))
	
	USED_NAMES.add(_name)
	
	return _name