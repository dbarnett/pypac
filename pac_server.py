from SimpleXMLRPCServer import SimpleXMLRPCServer
import time
import threading

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
X...XX................XX...X
XXX.XX.XX.XXXXXXXX.XX.XX.XXX
XXX.XX.XX.XXXXXXXX.XX.XX.XXX
X......XX....XX....XX......X
X.XXXXXXXXXX.XX.XXXXXXXXXX.X
X.XXXXXXXXXX.XX.XXXXXXXXXX.X
X..........................X
XXXXXXXXXXXXXXXXXXXXXXXXXXXX""".splitlines()[1:]

pos = (13, 22)
score = 0
map_clear = False
update_screen = True

directions = {
    'u': (0, -1),
    'd': (0, 1),
    'l': (-1, 0),
    'r': (1, 0),
    '.': (0, 0)}

def chk_eat(pos_x, pos_y):
    global score, map_clear, pac_map
    map_line = pac_map[pos_y]
    if map_line[pos_x] == '.':      # eat pellet
        line_cells = list(map_line)
        line_cells[pos_x] = ' '
        pac_map[pos_y] = ''.join(line_cells)
        score += 10
        if all('.' not in chk_line for chk_line in pac_map):
            map_clear = True

def get_pos():
    return pos

def get_map():
    return pac_map

def move(direction):
    global pos, pac_map
    global update_screen

    # don't move until the screen updates for the previous move
    while update_screen == True:
        time.sleep(.01)

    direction = direction.lower()
    if direction in directions.keys():
        old_x, old_y = pos
        move_x, move_y = directions[direction]
        new_x = (old_x + move_x) % 28
        new_y = (old_y + move_y) % 30
        map_line = pac_map[new_y]
        if map_line[new_x] != 'X':      # don't go through walls
            pos = (new_x, new_y)
            chk_eat(new_x, new_y)
            update_screen = True
            return pos
    return -1

s = SimpleXMLRPCServer(('', 8888), logRequests=0)
s.register_function(move)
s.register_function(get_pos)
s.register_function(get_map)
t = threading.Thread(target=s.serve_forever)
t.setDaemon(True)
t.start()

last_update_time = time.time()
chk_eat(*pos)
while map_clear is False or update_screen:
    if update_screen and time.time() - last_update_time > .2:
        last_update_time = time.time()
        pos_x, pos_y = pos
        print
        for line_y, line in enumerate(pac_map):
            if line_y != pos_y:
                print line
            else:
                pixels = list(line)
                pixels[pos_x] = '[0;33;48mO[0;0;0m'
                print ''.join(pixels)
        print 'score:', score
        update_screen = False
    time.sleep(.01)
