import os

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
    def __init__(self, _map, parent):
        self.map = _map
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

    def _update(self, dt):
        self.parent.in_motion_lock.acquire()
        if self.cur_action is not None:
            dx, dy = self.cur_action.get_move_direction()
            new_x = int(round(self.pac.x + dx*self.cur_action.duration))%len(self.map[0])
            new_y = int(round(self.pac.y + dy*self.cur_action.duration))%len(self.map)
            if self.map[new_y][new_x] != 'X':
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

