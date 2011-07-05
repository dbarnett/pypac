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
                'up':    ( 0, -1),
                'down':  ( 0,  1),
                'left':  (-1,  0),
                'right': ( 1,  0)
            }[self.action]

class PacGame(object):
    def __init__(self):
        self.gui_thread = None
        self.action_queue = Queue.Queue(1)

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
            def __init__(self, action_queue):
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
                self.action_queue = action_queue
                self.score = 0

            def update(self, dt):
                if self.cur_action is not None:
                    if time.time() > self.cur_action.start_time + self.cur_action.duration:
                        self.cur_action = None
                if self.cur_action is None:
                    try:
                        self.cur_action = self.action_queue.get(block=False)
                    except Queue.Empty, e:
                        pass
                    else:
                        self.cur_action.start()
                        move_x, move_y = self.cur_action.get_move_direction()
                        if pac_map[self.pac.y+move_y][self.pac.x+move_x] != 'X':
                            self.pac.x += move_x
                            self.pac.y += move_y
                            on_pellets, off_pellets = [], []
                            for p in self.pellets:
                                if p.x == self.pac.x and p.y == self.pac.y:
                                    on_pellets.append(p)
                                    p.sprite.delete()
                                    self.score += 10
                                else:
                                    off_pellets.append(p)
                            self.pellets[:] = off_pellets
                self.window.clear()
                self.wall_sprites_batch.draw()
                self.pellets_batch.draw()
                self.pac.update(dt)
                self.pac.sprite.draw()
                self.score_label.text = 'Score: %d'%self.score
                self.score_label.draw()
        _game = _PacGame(self.action_queue)
        pyglet.clock.schedule_interval(_game.update, 1./60)
        pyglet.app.run()

    def start(self):
        self.gui_thread = threading.Thread(target=self._run)
        self.gui_thread.setDaemon(True)
        self.gui_thread.start()

def runGame():
    global _defaultGame
    _defaultGame = PacGame()
    _defaultGame.start()

def up():
    _defaultGame.action_queue.put(PacAction('up', 1.0))

def down():
    _defaultGame.action_queue.put(PacAction('down', 1.0))

def left():
    _defaultGame.action_queue.put(PacAction('left', 1.0))

def right():
    _defaultGame.action_queue.put(PacAction('right', 1.0))

