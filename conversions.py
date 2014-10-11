from constants import YARDS, METERS


def get_real_direction(direction, short=False):
	if abs(direction)<22 or abs(direction-360)<22:
		if short:
			return 'e'
		
		return 'east'
	elif abs(direction-45)<22:
		if short:
			return 'ne'
		
		return 'northeast'
	elif abs(direction-90)<22:
		if short:
			return 'n'
		
		return 'north'
	elif abs(direction-135)<22:
		if short:
			return 'nw'
		
		return 'northwest'
	elif abs(direction-180)<22:
		if short:
			return 'w'
		
		return 'west'
	elif abs(direction-225)<22:
		if short:
			return 'sw'
		
		return 'southwest'
	elif abs(direction-270)<22:
		if short:
			return 's'
		
		return 'south'
	elif abs(direction-315)<22:
		if short:
			return 'se'
		
		return 'southeast'
	else:
		if short:
			return 'e'
		
		return 'east'

def get_real_distance(distance, yards=True):
	"""Returns the real-life representation of a distance."""
	
	if yards:
		return distance*YARDS
	else:
		return distance*METERS