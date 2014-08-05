from framework import display


def render_map(tile_map, width, height):
	_surface = display.get_surface('tiles')
	
	for y in range(height):
		for x in range(width):
			_tile = tile_map[y][x]
			
			display._set_char('tiles', _tile['x'], _tile['y'], _tile['c'], _tile['c_f'], _tile['c_b'])
