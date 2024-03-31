import os
from consts import UP, RIGHT, DOWN, LEFT


def clear_screen() -> None:
    """
    Clears the terminal screen. Works on both Windows ('nt') and Unix-based ('posix') systems.
    """
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


def get_key_action():
    """
    Detects a key press from the user and returns an action based on the key pressed.
    It detects 'd', 'a', 'Enter', and arrow keys.

    Returns:
        'next' if 'd' or right arrow key is pressed.
        'previous' if 'a' or left arrow key is pressed.
        'enter' if 'Enter' key is pressed.
        None if any other key is pressed.
    """
    if os.name == 'nt':  # Windows
        import msvcrt
        key = msvcrt.getch()
        if key == b'\x03':  # if 'Ctrl + C' is pressed
            exit(-1)
        if key == b'\xe0':  # if the first byte of an arrow key escape sequence is received
            key += msvcrt.getch()  # get the second byte and form the escape sequence
        if key in [b'd', b'D', b'\xe0M']:  # if 'd' or 'right' arrow key is pressed
            return 'next'
        elif key in [b'a', b'A', b'\xe0K']:  # if 'a' or 'left' arrow key is pressed
            return 'previous'
        elif key == b'\r':  # if 'Enter' key is pressed
            return 'enter'
    else:  # Unix-based
        import curses
        stdscr = curses.initscr()
        curses.cbreak()
        stdscr.keypad(True)
        key = stdscr.getch()
        if key in [curses.KEY_RIGHT, ord('d')]:  # if 'right' arrow key or 'd' is pressed
            return 'next'
        elif key in [curses.KEY_LEFT, ord('a')]:  # if 'left' arrow key or 'a' is pressed
            return 'previous'
        elif key == curses.KEY_ENTER or key == 10:  # if 'Enter' key is pressed
            return 'enter'
        # Restore the terminal settings
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
    return None


def get_new_position(direction: str, position: tuple[int, int]) -> tuple[int, int]:
    """
    Returns a new position based on the current position and direction.

    Args:
        direction: A string representing the direction (UP, RIGHT, DOWN, LEFT).
        position: A tuple containing two integers representing the current row and column indices.

    Returns:
        A tuple containing two integers representing the row and column indices of the new position.
    """
    x, y = position
    if direction == UP:
        return x, y - 1
    elif direction == RIGHT:
        return x + 1, y
    elif direction == DOWN:
        return x, y + 1
    elif direction == LEFT:
        return x - 1, y

    return x, y
