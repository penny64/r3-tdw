from framework import display, entities, tile

import mapgen


def render_map(tile_map, width, height):
	_surface = display.get_surface('tiles')
	_node_grid_set = set(mapgen.NODE_GRID)
	
	for y in range(height):
		for x in range(width):
			_tile = tile_map[y][x]
			
			display._set_char('tiles', _tile['x'], _tile['y'], _tile['c'], _tile['c_f'], _tile['c_b'])
			
			if (x, y) in _node_grid_set:
				_e = entities.create_entity(group='node_grid')
				
				tile.register(_e, surface='node_grid', fore_color=(255, 0, 255))
				entities.trigger_event(_e, 'set_position', x=x, y=y)
