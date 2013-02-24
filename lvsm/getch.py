# Code from: http://code.activestate.com/recipes/134892/

class _GetchUnix():
    """Implementing a getch call to read a single character from stdin"""
    def __init__(self):
        import sys, tty

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

getch = _GetchUnix()
