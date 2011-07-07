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
        self.action_lock = threading.Lock()
        self.in_motion_lock = threading.Lock()

    def _run(self):
        from . import gui
        self._game = gui._PacGame(pac_map, self)
        self._game.run()

    def do_action(self, action):
        self.action_lock.acquire()
        for a in action.split():
            self.in_motion_lock.acquire()
            self._game.cur_action = a
            a.start()
            self.in_motion_lock.release()
            time.sleep(a.duration)
            while self._game.cur_action is not None:
                time.sleep(.001)
        self.action_lock.release()

    def start(self):
        self.gui_thread = threading.Thread(target=self._run)
        self.gui_thread.setDaemon(True)
        self.gui_thread.start()

def runGame():
    global _default_game
    _default_game = PacGame()
    _default_game.start()

def up():
    _default_game.do_action(PacAction('up', .5))

def down():
    _default_game.do_action(PacAction('down', .5))

def left():
    _default_game.do_action(PacAction('left', .5))

def right():
    _default_game.do_action(PacAction('right', .5))

