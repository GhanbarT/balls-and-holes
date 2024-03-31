from os import system, name

from consts import UP, RIGHT, DOWN, LEFT


def clear_screen() -> None:
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


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
