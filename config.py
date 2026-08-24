tilemap = []


WIN_WIDTH = 960
WIN_HEIGHT = 640
TILESIZE = 32
TILE_W = 32
HEAD_H = 16
BODY_H = 16
SWORD_FRAME_SIZE = 128
SWORD_FRAME_COUNT = 11
FPS = 60

ROW_FOR_DIRECTION = {
    'down': 0,
    'left': 1,
    'right': 2,
    'up': 3,
}

LAYER_ORDER_FOR_FACING = {
    'up': ('body',  'head'),     # Fej a kard mögé
    'down': ('body', 'head'),
    'left': ('body',  'head'),
    'right': ('body',  'head'),
}

POSE_IDLE = 0
POSE_WALK = 1

DIAGONAL_FOR_CARDINAL = {
    'left':  ['up-left', 'down-left'],
    'right': ['up-right', 'down-right'],
    'up':    ['up-left', 'up-right'],
    'down':  ['down-left', 'down-right'],
}

IDLE_SWORD_VARIANT_FOR_FACING = {
    'up': 'up-right',
    'down': 'down-right',
    'left': 'up-left',
    'right': 'up-right',
}


SWORD_OFFSET_FOR_VARIANT = {
    'up-left':    (48, 48),
    'up-right':   (48, 48),
    'down-left':  (48, 48),
    'down-right': (48, 48),
}



HP_BAR_OFFSET_Y = -10
PLAYER_LAYER = 4 #the players layer drawn above everything
ENEMY_LAYER = 3
PLAYER_SPEED = 3
PLAYER_DAMAGE = 1
ENEMY_SPEED = 1
ENEMY_DAMAGE = 2
NEW_ENEMY_SPAWN_RADIUS = 3
ENEMY_HP = 4
BLOCK_LAYER = 2
GROUND_LAYER = 1
POTION_HEALING = 10

XP_PER_LEVEL = {
    1: 100,
    2: 200,
    3: 400,
    4: 800,
    5: 1600,
    6: 3200,
    7: 6400,
    8: 12800,
    9: 25600,
    10: 51200
}

TILEMAP_FILE = "map.json"
