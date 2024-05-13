import curses


class Term:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Term, cls).__new__(cls)
            cls._instance._term = curses.initscr()
            curses.start_color()
            # Check if the terminal supports changing colors
            if curses.can_change_color():
                curses.init_color(8, 1000, 500, 500)  # Light red
                curses.init_color(9, 500, 1000, 500)  # Light green
                curses.init_color(10, 1000, 1000, 500)  # Light yellow
                curses.init_color(11, 500, 500, 1000)  # Light blue
                curses.init_color(12, 1000, 500, 1000)  # Light magenta
                curses.init_color(13, 500, 1000, 1000)  # Light cyan
                curses.init_color(14, 1000, 1000, 1000)  # Light white
                curses.init_color(15, 500, 500, 500)  # Light black (gray)

            Term.add_color(2, curses.COLOR_WHITE, curses.COLOR_CYAN)  # Initialize color pair 2 as white on magenta

        return cls._instance

    def get_term(self):
        return self._term

    @staticmethod
    def add_color(color: int, fg: int, bg: int = 0):
        curses.init_pair(color, fg, bg)

    def print(self, text: str, color: int = 0):
        self._term.addstr(text, curses.color_pair(color))
