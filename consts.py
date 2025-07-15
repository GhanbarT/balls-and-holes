import bcolors

UUID_LEN = 36

HAVING_BALL = bcolors.RED
BALL_CELL = bcolors.CYAN_HIGHLIGHT
HOLE_CELL = bcolors.YELLOW_HIGHLIGHT
FILLED_HOLE_CELL = bcolors.GREEN_HIGHLIGHT

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
BALL = 'ball'
FILLED_HOLE = 'filled'
OBSTACLE = 'obstacle'
OUTSIDE = 'out'
VISITED = 'visited'
GONE = 'gone'
LOCK = 'lock'

UP = 'up'
RIGHT = 'right'
DOWN = 'down'
LEFT = 'left'

CELL_COLORS = {
    BALL: BALL_CELL,
    HOLE: HOLE_CELL,
    FILLED_HOLE: FILLED_HOLE_CELL
}

ICONS = {
    EMPTY: ' ' * 5,
    AGENT: '🤖',
    HOLE: ' 🕳️ ',
    BALL: ' ⚾ ',
    FILLED_HOLE: ' ⛳',
    OBSTACLE: '█' * 5
}

ARROWS = {
    UP: '⮙',
    RIGHT: '⮚',
    DOWN: '⮛',
    LEFT: '⮘'
}
