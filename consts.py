UUID_LEN = 36

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
