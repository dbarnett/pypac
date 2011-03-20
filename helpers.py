from _client_core import s

def get_cell((x,y)):
    return s.get_map()[y][x]

def path_to_nearest_pellet():
    path_queue = [[tuple(s.get_pos())]]
    while path_queue:
            cur_path = path_queue.pop(0)
            cur_pos = cur_path[-1]
            for direction in [(-1,0), (1,0), (0,-1), (0,1)]:
                    pos_x, pos_y = cur_pos
                    move_x, move_y = direction
                    new_pos = ((pos_x+move_x)%28, (pos_y+move_y)%30)
                    if any(new_pos in p for p in path_queue):
                            continue
                    new_path = cur_path + [new_pos]
                    pos_cell = get_cell(new_pos)
                    if pos_cell == '.':
                            return new_path
                    if pos_cell == 'X':
                            continue
                    else:
                            path_queue.append(new_path)

