def line(start_pos, end_pos):
	x1, y1 = start_pos
	x2, y2 = end_pos

	path = []
	if (x1, y1) == (x2, y2):
		return [(x2, y2)]

	start = [x1,y1]
	end = [x2,y2]

	steep = abs(end[1]-start[1]) > abs(end[0]-start[0])

	if steep:
		start = swap(start[0],start[1])
		end = swap(end[0],end[1])

	if start[0] > end[0]:
		start[0],end[0] = swap(start[0],end[0])		
		start[1],end[1] = swap(start[1],end[1])

	dx = end[0] - start[0]
	dy = abs(end[1] - start[1])
	error = 0

	try:
		derr = dy/float(dx)
	except:
		return None

	ystep = 0
	y = start[1]

	if start[1] < end[1]: ystep = 1
	else: ystep = -1

	for x in range(start[0],end[0]+1):
		if steep:
			path.append((y,x))
		else:
			path.append((x,y))

		error += derr

		if error >= 0.5:
			y += ystep
			error -= 1.0

	if not path[0] == (x1,y1):
		path.reverse()

	return path

def swap(n1, n2):
	return [n2, n1]

def circle(x, y, size):
	if not size>2:
		size = 2

	circle = 0.0
	width=size
	height=size
	center_x=(width/2.0)
	center_y=(height/2.0)
	j = 0
	i = 0

	_circle = []

	for i in range(height+1):
		for j in range(width+1):
			circle = (((i-center_y)*(i-center_y))/((float(height)/2)*(float(height)/2)))+((((j-center_x)*(j-center_x))/((float(width)/2)*(float(width)/2))));
			if circle>0 and circle<1.1:
				_circle.append((x+(j-(width/2)),y+(i-(height/2))))

	if not (x, y) in _circle:
		_circle.append((x, y))

	return _circle