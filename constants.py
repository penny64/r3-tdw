#########
#Release#
#########

VERSION = 0.3
VERSION_INFO = 'This is a prototype. Do not distribute.'


#########
#Display#
#########

WINDOW_TITLE = 'Insurgence: Shadow Operation'
WINDOW_WIDTH = 100
WINDOW_HEIGHT = 70
MAP_VIEW_WIDTH = WINDOW_WIDTH
MAP_VIEW_HEIGHT = WINDOW_HEIGHT-1
STRAT_MAP_WIDTH = 100
STRAT_MAP_HEIGHT = 60
MAP_CELL_SPACE = 5
FPS = 60
MAX_DRAW_CALLS_PER_FRAME = (WINDOW_WIDTH*WINDOW_HEIGHT) * 2
SHOW_MOUSE = True

#########
#Content#
#########

#######
#Input#
#######

KEY_ESCAPE = 27
KEY_UP = 14
KEY_DOWN = 17
KEY_LEFT = 15
KEY_RIGHT = 16
KEY_1 = 49
KEY_2 = 50
KEY_3 = 51
KEY_4 = 52
KEY_5 = 53
KEY_6 = 54
KEY_7 = 55
KEY_8 = 56
KEY_9 = 57
KEY_ENTER = 13


#######
#Units#
#######

YARDS = 0.5
METERS = 0.4572
IDLE_COST = 1.25


####
#AI#
####

MAX_SQUAD_LEADER_DISTANCE = 60


##########
#Graphics#
##########

SHOW_MESSAGES_FOR = 6 #Seconds


########
#Colors#
########

LIGHT_WASHED_GREEN_1 = (158, 255, 125)
LIGHT_WASHED_GREEN_2 = (190, 255, 125)
LIGHT_WASHED_GREEN_3 = (223, 255, 125)

SAND_1 = (255, 190, 125)
SAND_2 = (225, 223, 125)
SAND_3 = (255, 255, 125)

WATER_1 = (125, 158, 255)
WATER_2 = (125, 190, 255)
WATER_3 = (125, 223, 255)

SWAMP_WATER_1 = (64, 128, 96)
SWAMP_WATER_2 = (44, 108, 76)
SWAMP_WATER_3 = (24, 88, 56)

ROCK_1 = (162, 162, 162)
ROCK_2 = (182, 182, 182)
ROCK_3 = (203, 203, 203)

DARK_GRAY_1 = (70, 70, 70)
DARK_GRAY_2 = (80, 80, 80)
DARK_GRAY_3 = (85, 85, 85)

DARKER_GRAY_1 = (60, 60, 60)
DARKER_GRAY_2 = (70, 70, 70)
DARKER_GRAY_3 = (75, 75, 75)

GRAY_1 = (100, 100, 100)
GRAY_2 = (110, 110, 110)
GRAY_3 = (115, 115, 115)

BLUE_1 = (0, 60, 109)
BLUE_2 = (0, 60, 109)
BLUE_3 = (0, 60, 109)

LIGHT_BLUE_1 = (30, 90, 139)
LIGHT_BLUE_2 = (30, 90, 139)
LIGHT_BLUE_3 = (30, 90, 139)

LIGHT_GRAY_1 = (200, 200, 200)
LIGHT_GRAY_2 = (210, 210, 210)
LIGHT_GRAY_3 = (215, 215, 215)

BLACK_1 = (56, 56, 56)
BLACK_2 = (69, 69, 69)
BLACK_3 = (81, 81, 81)

DARKER_BLACK_1 = (56-40, 56-40, 56-40)
DARKER_BLACK_2 = (69-40, 69-40, 69-40)
DARKER_BLACK_3 = (81-45, 81-45, 81-45)

FIRE_1 = (255, 100, 0)
FIRE_2 = (255, 0, 0)
FIRE_3 = (255, 65, 0)

BLOOD_1 = (140, 0, 0)
BLOOD_2 = (155, 0, 0)
BLOOD_3 = (170, 0, 0)

DARKER_BLOOD_1 = (50, 0, 0)
DARKER_BLOOD_2 = (60, 0, 0)
DARKER_BLOOD_3 = (70, 0, 0)

SWAMP_1 = (113, 56, 0)
SWAMP_2 = (113, 85, 0)
SWAMP_3 = (113, 113, 0)

FOREST_GREEN_1 = (48, 65, 0)
FOREST_GREEN_2 = (32, 65, 0)
FOREST_GREEN_3 = (16, 65, 0)

DARK_FOREST_GREEN_1 = (38, 55, 0)
DARK_FOREST_GREEN_2 = (22, 55, 0)
DARK_FOREST_GREEN_3 = (6, 55, 0)

SATURATED_GREEN_1 = (65, 56, 32)
SATURATED_GREEN_2 = (65, 65, 32)
SATURATED_GREEN_3 = (56, 65, 32)

LIGHT_PURPLE_1 = (125, 125, 255)
LIGHT_PURPLE_2 = (158, 125, 255)
LIGHT_PURPLE_3 = (190, 125, 255)

DARK_PURPLE_1 = (113, 81, 105)
DARK_PURPLE_2 = (113, 81, 97)
DARK_PURPLE_3 = (113, 81, 89)

BURGANDY_1 = (65, 0, 32)
BURGANDY_2 = (65, 0, 16)
BURGANDY_3 = (65, 0, 0)

SPEC_BURGANDY_1 = (70, 18, 16)
SPEC_BURGANDY_2 = (70, 10, 8)
SPEC_BURGANDY_3 = (70, 2, 0)

MARBLE_1 = (240, 234, 214)
MARBLE_2 = (240, 234, 214)
MARBLE_3 = (240, 234, 214)

BRIGHT_GREEN_1 = (190, 255, 0)
BRIGHT_GREEN_2 = (125, 255, 0)
BRIGHT_GREEN_3 = (65, 255, 0)

WOOD_1 = (158-20, 134-20, 100-20)
WOOD_2 = (127, 101, 63)
WOOD_3 = (94, 75, 47)

DARK_WOOD_1 = (94-15, 75-15, 47-15)
DARK_WOOD_2 = (94-25, 75-25, 47-25)#(127-45, 101-45, 63-45)
DARK_WOOD_3 = (94-35, 75-35, 47-35)

BROWN_1 = (127, 101, 63)
BROWN_2 = (127-20, 101-20, 63-20)
BROWN_3 = (127-20, 101-20, 63-20)

STATUS_GOOD = (55, 200, 55)
STATUS_BAD = (200, 55, 55)
STATUS_OK = (200, 200, 200)
