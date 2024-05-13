from consts import *
import sys

import term
import curses


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

    # Initialize curses
    curses.cbreak()
    term.Term().get_term().keypad(True)

    try:
        # Wait for a key press
        key = term.Term().get_term().getch()

        # Handle key presses
        if key == curses.KEY_RIGHT or key == ord('d'):  # if 'right' arrow key or 'd' is pressed
            return 'next'
        elif key == curses.KEY_LEFT or key == ord('a'):  # if 'left' arrow key or 'a' is pressed
            return 'previous'
        elif key == curses.KEY_ENTER or key == 10:  # if 'Enter' key is pressed
            return 'enter'
        
    except KeyboardInterrupt:
        curses.nocbreak()
        term.Term().get_term().keypad(False)
        curses.echo()
        curses.endwin()

        sys.exit(-1)

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
