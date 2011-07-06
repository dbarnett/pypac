import os
import Queue
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
        import pyglet
        class _PacMan(object):
            pac_img = pyglet.resource.image(os.path.join('assets', 'pac.png'))
            def __init__(self, x, y):
                self.x, self.y = x, y
                self.sprite = pyglet.sprite.Sprite(
                        self.pac_img,
                        x=self.x*20, y=(30-self.y)*20)
            def update(self, dt):
                self.sprite.x = self.x*20
                self.sprite.y = (30-self.y)*20
        class _PacPellet(object):
            pellet_img = pyglet.resource.image(os.path.join('assets', 'pellet.png'))
            def __init__(self, x, y, batch):
                self.x, self.y = x, y
                self.sprite = pyglet.sprite.Sprite(
                        self.pellet_img,
                        batch=batch,
                        x=self.x*20, y=(30-self.y)*20)
        class _PacGame(object):
            def __init__(self, parent):
                self.parent = parent
                self.window = pyglet.window.Window(
                        width=28*20, height=31*20)
                self.cur_action = None
                self.score_label = pyglet.text.Label('Score: 0',
                        font_size=18,
                        x=0, y=0)
                self.pac = _PacMan(13, 22)
                wall_img = pyglet.resource.image(os.path.join('assets', 'wall.png'))
                self.wall_sprites_batch = pyglet.graphics.Batch()
                self.wall_sprites = []
                self.pellets_batch = pyglet.graphics.Batch()
                self.pellets = []
                for y, row in enumerate(pac_map):
                    for x, elem in enumerate(row):
                        if elem == 'X':
                            wall_sprite = pyglet.sprite.Sprite(
                                    wall_img,
                                    batch=self.wall_sprites_batch,
                                    x=x*20, y=(30-y)*20)
                            self.wall_sprites.append(wall_sprite)
                        elif elem == '.':
                            pellet = _PacPellet(x, y, batch=self.pellets_batch)
                            self.pellets.append(pellet)
                self.score = 0

            def update(self, dt):
                self.parent.in_motion_lock.acquire()
                if self.cur_action is not None:
                    dx, dy = self.cur_action.get_move_direction()
                    new_x = int(round(self.pac.x + dx*self.cur_action.duration))%len(pac_map[0])
                    new_y = int(round(self.pac.y + dy*self.cur_action.duration))%len(pac_map)
                    if pac_map[new_y][new_x] != 'X':
                        self.pac.x = new_x
                        self.pac.y = new_y
                        on_pellets, off_pellets = [], []
                        for p in self.pellets:
                            if abs(p.x - self.pac.x) < .5 and abs(p.y - self.pac.y) < .5:
                                on_pellets.append(p)
                                p.sprite.delete()
                                self.score += 10
                            else:
                                off_pellets.append(p)
                        self.pellets[:] = off_pellets
                    self.cur_action = None
                self.parent.in_motion_lock.release()
                self.window.clear()
                self.wall_sprites_batch.draw()
                self.pellets_batch.draw()
                self.pac.update(dt)
                self.pac.sprite.draw()
                self.score_label.text = 'Score: %d'%self.score
                self.score_label.draw()
        self._game = _PacGame(self)
        pyglet.clock.schedule_interval(self._game.update, 1./60)
        pyglet.app.run()

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
    global _defaultGame
    _defaultGame = PacGame()
    _defaultGame.start()

def up():
    _defaultGame.do_action(PacAction('up', .5))

def down():
    _defaultGame.do_action(PacAction('down', .5))

def left():
    _defaultGame.do_action(PacAction('left', .5))

def right():
    _defaultGame.do_action(PacAction('right', .5))

