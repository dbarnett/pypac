import threading
import time

_default_game = None

pac_map = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXX
X............XX............X
X.XXXX.XXXXX.XX.XXXXX.XXXX.X
X.XXXX.XXXXX.XX.XXXXX.XXXX.X
X..........................X
X.XXXX.XX.XXXXXXXX.XX.XXXX.X
X.XXXX.XX.XXXXXXXX.XX.XXXX.X
X......XX....XX....XX......X
XXXXXX.XXXXX XX XXXXX.XXXXXX
     X.XXXXX XX XXXXX.X     
     X.XX          XX.X     
     X.XX XXXXXXXX XX.X     
XXXXXX.XX X      X XX.XXXXXX
      .   X      X   .      
XXXXXX.XX X      X XX.XXXXXX
     X.XX XXXXXXXX XX.X     
     X.XX          XX.X     
     X.XX.XXXXXXXX.XX.X     
XXXXXX.XX.XXXXXXXX.XX.XXXXXX
X............XX............X
X.XXXX.XXXXX.XX.XXXXX.XXXX.X
X.XXXX.XXXXX.XX.XXXXX.XXXX.X
X...XX.......  .......XX...X
XXX.XX.XX.XXXXXXXX.XX.XX.XXX
XXX.XX.XX.XXXXXXXX.XX.XX.XXX
X......XX....XX....XX......X
X.XXXXXXXXXX.XX.XXXXXXXXXX.X
X.XXXXXXXXXX.XX.XXXXXXXXXX.X
X..........................X
XXXXXXXXXXXXXXXXXXXXXXXXXXXX""".splitlines()[1:]

class PacAction(object):
    def __init__(self, action, duration):
        self.action = action
        self.duration = duration
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def get_move_direction(self):
        return {
                'up':    ( 0, -2),
                'down':  ( 0,  2),
                'left':  (-2,  0),
                'right': ( 2,  0)
            }[self.action]

    def split(self):
        dur = self.duration
        while dur > .5:
            yield type(self)(self.action, .5)
            dur -= .5
        yield type(self)(self.action, dur)

class PacGame(object):
    def __init__(self):
        self.gui_thread = None

    def _run(self):
        from . import gui       # NOTE: this imports pyglet, which has
                                # side-effects and must happen in this thread
        self._game = gui._PacGame(pac_map, self)
        self._game.run()

    def do_action(self, direction):
        self._game.pac.direction_lock.acquire()
        self._game.pac.direction = direction
        self._game.advance()
        self._game.pac.direction_lock.release()

    def start(self):
        self.gui_thread = threading.Thread(target=self._run)
        self.gui_thread.setDaemon(True)
        self.gui_thread.start()

    def stop(self):
        while not hasattr(self, '_game'):
            pass
        self._game.stop()
        self.gui_thread.join()

def runGame():
    global _default_game
    _default_game = PacGame()
    _default_game.start()

def stopGame():
    global _default_game
    _default_game.stop()

def up():
    _default_game.do_action('u')

def down():
    _default_game.do_action('d')

def left():
    _default_game.do_action('l')

def right():
    _default_game.do_action('r')

