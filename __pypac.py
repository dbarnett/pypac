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

class PacGame(object):
    def __init__(self):
        self.gui_thread = None
        self.action_queue = Queue.Queue(1)

    def _run(self):
        import pyglet
        class _PacGame(object):
            def __init__(self, action_queue):
                self.map = map(list, pac_map)
                self.window = pyglet.window.Window(
                        width=28*20, height=31*20)
                self.cur_action = None
                self.label = pyglet.text.Label('Get Ready!',
                        font_name='Arial',
                        font_size=25,
                        x=self.window.width//2, y=self.window.height//2,
                        anchor_x='center', anchor_y='center')
                self.score_label = pyglet.text.Label('Score: 0',
                        font_size=18,
                        x=0, y=0)
                pac_img = pyglet.resource.image(os.path.join('assets', 'pac.png'))
                self.pac_sprite = pyglet.sprite.Sprite(
                        pac_img,
                        x=13*20, y=8*20)
                wall_img = pyglet.resource.image(os.path.join('assets', 'wall.png'))
                self.wall_sprites_batch = pyglet.graphics.Batch()
                self.wall_sprites = []
                pellet_img = pyglet.resource.image(os.path.join('assets', 'pellet.png'))
                self.pellets_batch = pyglet.graphics.Batch()
                self.pellet_sprites = []
                for y, row in enumerate(self.map):
                    for x, elem in enumerate(row):
                        if elem == 'X':
                            wall_sprite = pyglet.sprite.Sprite(
                                    wall_img,
                                    batch=self.wall_sprites_batch,
                                    x=x*20, y=(30-y)*20)
                            self.wall_sprites.append(wall_sprite)
                        elif elem == '.':
                            pellet_sprite = pyglet.sprite.Sprite(
                                    pellet_img,
                                    batch=self.pellets_batch,
                                    x=x*20, y=(30-y)*20)
                            self.pellet_sprites.append(pellet_sprite)
                self.action_queue = action_queue
                self.score = 0

            def update(self, dt):
                if self.cur_action is not None:
                    if time.time() > self.cur_action.start_time + self.cur_action.duration:
                        self.cur_action = None
                        self.label.text = '...'
                if self.cur_action is None:
                    try:
                        self.cur_action = self.action_queue.get(block=False)
                    except Queue.Empty, e:
                        pass
                    else:
                        self.cur_action.start()
                        self.label.text = self.cur_action.action
                self.window.clear()
                self.wall_sprites_batch.draw()
                self.pellets_batch.draw()
                self.pac_sprite.draw()
                self.label.draw()
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

