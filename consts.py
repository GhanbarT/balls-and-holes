import bcolors

UUID_LEN = 36

HAVING_ORB = bcolors.RED
ORB_CELL = bcolors.GRAY_HIGHLIGHT
HOLE_CELL = bcolors.GREEN_HIGHLIGHT

BOX_TOP_LEFT = '╚'
BOX_TOP_RIGHT = '╝'
BOX_BOTTOM_LEFT = '╔'
BOX_BOTTOM_RIGHT = '╗'
BOX_HORIZONTAL = '═'
BOX_VERTICAL = '║'
BOX_VERTICAL_RIGHT = '╠'
BOX_VERTICAL_LEFT = '╣'
BOX_HORIZONTAL_DOWN = '╦'
BOX_HORIZONTAL_UP = '╩'
BOX_CROSS = '╬'

EMPTY = 'empty'
AGENT = 'agent'
HOLE = 'hole'
ORB = 'orb'
FILLED_HOLE = 'filled'
OBSTACLE = 'obstacle'
OUTSIDE = 'out'

UP = 'up'
RIGHT = 'right'
DOWN = 'down'
LEFT = 'left'

icons = {
    EMPTY: ' ' * 5,
    AGENT: '🤖',
    HOLE: ' 🕳️ ',
    ORB: ' ⚾ ',
    FILLED_HOLE: ' ⛳ ',
    OBSTACLE: '█' * 5
}

arrows = {
    UP: '⮙',
    RIGHT: '⮚',
    DOWN: '⮛',
    LEFT: '⮘'
}
