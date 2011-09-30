import os
import Queue
import threading

import pyglet

class _PacMan(object):
    pac_img = pyglet.resource.image(os.path.join('assets', 'pac.png'))
    def __init__(self, x, y, direction='l'):
        self.x, self.y = x, y
        self.direction = direction
        self.direction_lock = threading.Lock()
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
    def __init__(self, _map, parent):
        self.map = _map
        self.parent = parent
        self.game_time = 0.
        self._next_pause_time = 0.
        self.advance_lock = threading.Lock()
        self.advance_queue = Queue.Queue(1)
        self.window = pyglet.window.Window(
                width=28*20, height=31*20)
        self.score_label = pyglet.text.Label('Score: 0',
                font_size=18,
                x=0, y=0)
        self.pac = _PacMan(13, 22)
        wall_img = pyglet.resource.image(os.path.join('assets', 'wall.png'))
        self.wall_sprites_batch = pyglet.graphics.Batch()
        self.wall_sprites = []
        self.pellets_batch = pyglet.graphics.Batch()
        self.pellets = []
        for y, row in enumerate(self.map):
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
        pyglet.clock.schedule_interval(self._update, 1./60)

    def run(self):
        pyglet.app.run()

    def advance(self, duration=.5):
        self.advance_lock.acquire()
        self.advance_queue.put(duration)
        self.advance_queue.join()
        self.advance_lock.release()

    def _update(self, dt):
        if self.game_time >= self._next_pause_time:
            try:
                self._next_pause_time += self.advance_queue.get(block=False)
            except Queue.Empty, e:
                pass
        if self._next_pause_time > self.game_time:
            dx, dy = {
                'u': ( 0, -2),
                'd': ( 0,  2),
                'l': (-2,  0),
                'r': ( 2,  0)}[self.pac.direction]
            #new_x = int(round(self.pac.x + dx*dt))%len(self.map[0])
            #new_y = int(round(self.pac.y + dy*dt))%len(self.map)
            new_x = (self.pac.x + dx*dt)%len(self.map[0])
            new_y = (self.pac.y + dy*dt)%len(self.map)
            #if self.map[new_y][new_x] != 'X':
            if True:
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
            self.game_time += dt
            if self.game_time >= self._next_pause_time:
                self.advance_queue.task_done()
        self.window.clear()
        self.wall_sprites_batch.draw()
        self.pellets_batch.draw()
        self.pac.update(dt)
        self.pac.sprite.draw()
        self.score_label.text = 'Score: %d'%self.score
        self.score_label.draw()

