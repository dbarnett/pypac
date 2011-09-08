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
        pass

    def do_action(self, action):
        print "Hi"
        for a in action.split():
            self._game.cur_action = a
            print "Start"
            a.start()
            time.sleep(a.duration)
            print "Waiting for action..."
            while self._game.cur_action is not None:
                time.sleep(.001)
            print "Finished waiting for action"

    def start(self):
        from . import gui       # NOTE: this imports pyglet, which has
                                # side-effects and must happen in this thread
        self._game = gui._PacGame(pac_map)

def runGame():
    global _default_game
    _default_game = PacGame()
    _default_game.start()

def up():
    _default_game.do_action(PacAction('up', .5))

def down():
    _default_game.do_action(PacAction('down', .5))

def left():
    print "Foo"
    _default_game.do_action(PacAction('left', .5))

def right():
    _default_game.do_action(PacAction('right', .5))

