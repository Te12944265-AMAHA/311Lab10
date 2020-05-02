import numpy as np
import matplotlib.pyplot as plt
import math
import copy

# Check if a circle with center (h, k) and radius r intersects
# the line segment with endpoints (x0, y0) and (x1, y1)
# (credits to FRC team Dawgma and Stack Overflow)
def circle_intersect_segment(h, k, r, x0, y0, x1, y1):
    d = [x1 - x0, y1 - y0]
    f = [x0 - h, y0 - k]

    a = d[0]**2 + d[1]**2
    b = 2*(f[0]*d[0] + f[1]*d[1])
    c = f[0]**2 + f[1]**2 - r**2
    discrim = b**2 - 4*a*c

    if discrim < 0:
        return False
    else:
        discrim = math.sqrt(discrim)
        t1 = (-b - discrim)/(2*a)
        t2 = (-b + discrim)/(2*a)
        return (t1 >= 0 and t1 <= 1) or (t2 >= 0 and t2 <= 1)

# Does the position [x, y] intersect the given obstacle?
def position_intersect(position, obstacle, r):
    # Check if the circle given by the end effector intersects any obstacle boundary
    h    = position[0] # x
    k    = position[1] # y
    obs0 = obstacle[0] # left
    obs1 = obstacle[2] # right
    obs2 = obstacle[3] # bottom
    obs3 = obstacle[1] # top

    left_intersect   = circle_intersect_segment(h, k, r, obs0, obs2, obs0, obs3)
    right_intersect  = circle_intersect_segment(h, k, r, obs1, obs2, obs1, obs3)
    bottom_intersect = circle_intersect_segment(h, k, r, obs0, obs2, obs1, obs2)
    top_intersect    = circle_intersect_segment(h, k, r, obs0, obs3, obs1, obs3)

    # Return true if the position is on or enclosed by the obstacle
    return left_intersect or right_intersect or bottom_intersect or top_intersect or \
         (h >= obs0 and h <= obs1 and k >= obs2 and k <= obs3)

def position_available(position, obstacles, r):
    for obs in obstacles:
        if position_intersect(position, obs, r):
            return False
    return True


# Obstacle: -2; start: 1; end: -1, others: >= 2
def assign_freespace(grids, start_idx, end_idx):
    # Start from the starting pixel
    # For each pixel in the queue, pop and see its neighbors
    queue = []
    w = len(grids)
    h = len(grids[0])
    #print(w, h)
    grids[start_idx[0]][start_idx[1]] = 1
    for end in end_idx:
        grids[end[0]][end[1]] = -1
    queue.append(start_idx)
    while len(queue) != 0:
        cur = queue.pop(0)
        cur_r, cur_c = cur
        cur_val = grids[cur_r][cur_c]
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                r = cur_r + dr 
                c = cur_c + dc
                if (cur_r != r or cur_c != c) and r >= 0 and r < w and c >= 0 and c < h:
                    new_val = grids[r][c]
                    if new_val == 0:
                        grids[r][c] = cur_val + 1
                        queue.append((r, c))


# Find non-obstacle neighbors which are strictly 1 greater than 
# cur value or the goal.
def find_neighbors(grids, cur_idx):
    w = len(grids)
    h = len(grids[0])
    cur_r, cur_c = cur_idx
    cur_val = grids[cur_r][cur_c]
    neighbors = []
    for (dr, dc) in [(-1,0),(1,0),(0,0),(0,-1),(0,1),(1,1),(1,-1),(-1,1),(-1,-1)]:
        r = cur_r + dr 
        c = cur_c + dc
        if (cur_r != r or cur_c != c) and r >= 0 and r < w and c >= 0 and c < h: # valid index
            new_val = grids[r][c]
            if cur_val+1 == new_val or new_val == -1: # valid wavefront
                neighbors.append((r, c))
    return neighbors


class Path(object):
    def __init__(self, coords):
        self.coords = coords # List of tuples
        

    def add_node(self, coord):
        self.coords.append(coord)
        
    # a list of potential ending idxes
    def ends_at(self, idxs):
        for i in range(len(idxs)):
            if self.coords[-1] == idxs[i]:
                return i
        return -1

    def copy_path(self):
        coords = copy.deepcopy(self.coords)
        path = Path(coords)
        return path


def find_path(grids, start_idx, end_idx):
    explored = []
    queue = []
    p0 = Path([start_idx])
    queue.append(p0)
    while len(queue) != 0:
        #print('here')
        length = len(queue)
        queue_tmp = []
        for i in range(length):
            p = queue.pop()
            idx = p.ends_at(end_idx)
            if idx >= 0:
                return p.coords, idx
            neighbors = find_neighbors(grids, p.coords[-1])
            for n in range(len(neighbors)):
                neighbor = neighbors[n]
                #cost = costs[n]
                if neighbor not in explored:
                    p_tmp = p.copy_path()
                    p_tmp.add_node(neighbor)
                    queue_tmp.append(p_tmp)
                    explored.append(neighbor)
        queue = queue_tmp
    return None, -1


def get_idx_from_pos(pos, dx, w, h):
    x = int(round(pos[0]/dx))
    y = int(round(pos[1]/dx))
    if x == w: x = w-1
    if y == h: y = h-1
    return (x, y)

# get a path from one point to another
# assume square grids; dx: 10
# end is either a tk frame position or a list of positions
def get_path(cspace, dx, start_position, end_positions):
    # cspace is already discretized
    w = cspace.shape[0] #80
    h = cspace.shape[1] #50
    start_idx = get_idx_from_pos(start_position, dx, w, h)
    end_idx = [get_idx_from_pos(end_position, dx, w, h) for end_position in end_positions]
    # print(start_position)
    # print(end_positions)
    # print(start_idx)
    # print(end_idx)
    # start and end are in (i,j) form in cspace
    grids = copy.deepcopy(cspace)
    grids = grids.tolist()
    # Now we need to assign the free space with numbers
    assign_freespace(grids, start_idx, end_idx)
    print('Done assign_freespace')

    # Then we need to find a good path, which is a list of idx tuples
    # This list will then be passed to visualization function
    path, bin_num = find_path(grids, start_idx, end_idx)
    print('Done find_path')
    if path == None: 
        print('path not found')
        return None
    # now we need to convert the idx to tk coords tuples
    # approximate thetas
    path_real = []
    dxx = dx // 2
    for coord in path:
        x, y = coord
        path_real.append((x*dx+dxx, y*dx+dxx))
    return path_real, bin_num #list of tuples

