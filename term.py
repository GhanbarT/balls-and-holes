import curses

class Term:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Term, cls).__new__(cls)
            cls._instance._term = curses.initscr()
        return cls._instance
    
    def get_term(self):
        return self._term
    
    def print(self,text):
        self._term.addstr(text)
    
