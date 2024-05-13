import curses

UUID_LEN = 36

HAVING_ORB = 1
ORB_CELL = 2
HOLE_CELL = 3
FILLED_HOLE_CELL = 4

COLORS_MAP = {
    0: curses.COLOR_BLACK,
    1: curses.COLOR_RED,
    2: curses.COLOR_CYAN,
    3: curses.COLOR_YELLOW,
    4: curses.COLOR_GREEN,
}

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
VISITED = 'visited'
GONE = 'gone'
LOCK = 'lock'

UP = 'up'
RIGHT = 'right'
DOWN = 'down'
LEFT = 'left'

CELL_COLORS = {
    ORB: ORB_CELL,
    HOLE: HOLE_CELL,
    FILLED_HOLE: FILLED_HOLE_CELL
}

ICONS = {
    EMPTY: ' ' * 5,
    AGENT: '🤖',
    HOLE: ' 🕳️ ',
    ORB: ' 🥎 ',
    FILLED_HOLE: ' 🚩 ',
    OBSTACLE: '█' * 5
}

ARROWS = {
    UP: '⬆',
    RIGHT: '➡',
    DOWN: '⬇',
    LEFT: '⬅'
}
