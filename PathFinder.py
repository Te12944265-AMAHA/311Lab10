from tkinter import *
import math 
import copy
from visualize import *

class Obstacle(object):
    def __init__(self, L, dx, w, h, corners):
        self.corners = corners
        if corners != None:
            self.corners = [(y, x) for (x, y) in corners]
        self.B = math.ceil(L / 2) # The amount of inch we wanna bloat
        self.dx = dx
        self.w = w # in pixels
        self.h = h
        self.outlines_small = None
        self.blob_small = set() # For visualization
        self.blob_big = set() # Bloated blob, a list of tuples of indices

    def construct_line(self, p1, p2): 
        x1, y1 = p1 
        x2, y2 = p2
        if x1 == x2:
            line = (0, x1, 'v')
        elif y1 == y2:
            line = (0, y1, 'h')
        else:
            a = (y2 - y1) / (x2 - x1)
            b = y1 - x1 * a
            line = (a, b, 'n')
        return line


    def process_outlines(self): #Assumption: lines are 0, 45, 90, 135 degrees
        outlines_small = [] # the bounding lines of the rectangle 
        # ax + b = y, (a, b, 'h or v or n')
        for i in range(0, 4):
            p1 = self.corners[i]
            p2 = self.corners[(i+1)%4]
            line = self.construct_line(p1, p2)
            outlines_small.append(line)
        self.outlines_small = outlines_small
            
    def bounded(self, coord):
        x, y = coord
        for i in range(4):
            a, b, t = self.outlines_small[i]
            if i == 0 or i == 3: # ge
                if t == 'h':
                    if y < b: return False
                elif t == 'v':
                    if x < b: return False 
                else:
                    if y < a * x + b: return False
            else: # le
                if t == 'h':
                    if y > b: return False
                elif t == 'v':
                    if x > b: return False 
                else:
                    if y > a * x + b: return False
        return True

    # Fills in self.blob_small
    def fill(self):
        dxx = self.dx / 2
        for i in range(self.w):
            for j in range(self.h):
                coord = (i * self.dx + dxx, j * self.dx + dxx)
                if self.bounded(coord):
                    self.blob_small.add((i, j))

    def in_bloat_range(self, coord, line):
        a, b, t = line 
        x, y = coord
        if t == 'v':
            if abs(x - b) <= self.B: return True
        elif t == 'h':
            if abs(y - b) <= self.B: return True 
        else:
            dist = abs(a*x - y + b)/math.sqrt(a**2 + 1)
            if dist <= self.B: return True
        return False

    def bounded_by_line(self, coord, line, arg):
        a, b, t = line 
        x, y = coord
        if arg == 'gt':
            if t == 'v':
                if x > b and x - b <= self.B: return True
            elif t == 'h':
                if y > b and y - b <= self.B: return True 
            else:
                if y > a*x + b:
                    dist = abs(a*x - y + b)/math.sqrt(a**2 + 1)
                    if dist <= self.B: return True
        elif arg == 'lt':
            if t == 'v':
                if x < b and b - x <= self.B: return True
            elif t == 'h':
                if y < b and b - y <= self.B: return True 
            else:
                if y < a*x + b:
                    dist = abs(a*x - y + b)/math.sqrt(a**2 + 1)
                    if dist <= self.B: return True
        return False

    # Fills in self.blob_big
    def bloat0(self):
        dxx = self.dx / 2
        self.blob_big = copy.deepcopy(self.blob_small)
        for i in range(self.w):
            for j in range(self.h):
                coord = (i * self.dx + dxx, j * self.dx + dxx)
                for k in range(4):
                    cur_line = self.outlines_small[k]
                    prev_line = self.outlines_small[(k-1)%4]
                    next_line = self.outlines_small[(k+1)%4]
                    if self.in_bloat_range(coord, cur_line):
                        if k < 2: # prev: gt, next: lt
                            arg1 = 'gt'
                            arg2 = 'lt'
                        else:
                            arg1 = 'lt'
                            arg2 = 'gt'
                        # Case 1:
                        if (self.bounded_by_line(coord, prev_line, arg1)
                            and self.bounded_by_line(coord, next_line, arg2)):
                            self.blob_big.add((i, j))
                        # Case 2
                        elif self.in_bloat_range(coord, prev_line):
                            self.blob_big.add((i, j))

    def dot(self, u, v):
        return u[0]*v[0] + u[1]*v[1]

    def distance(self, p0, p1, coord):
        x0, y0 = p0 
        x1, y1 = p1
        x, y = coord
        u = [x - x0, y - y0]
        v = [x1 - x0, y1 - y0]

        u_dot_v = self.dot(u, v)
        v_dot_v = self.dot(v, v)

        if u_dot_v > v_dot_v:
            u_minus_v = [u[0] - v[0], u[1] - v[1]]
            return math.sqrt(self.dot(u_minus_v, u_minus_v))
        elif u_dot_v < 0:
            return math.sqrt(self.dot(u, u))
        else:
            coeff = u_dot_v/v_dot_v
            d = [u[0] - coeff*v[0], u[1] - coeff*v[1]]
            return math.sqrt(self.dot(d, d))


    def bloat(self):
        dxx = self.dx / 2
        self.blob_big = copy.deepcopy(self.blob_small)
        for i in range(self.w):
            for j in range(self.h):
                coord = (i * self.dx + dxx, j * self.dx + dxx)
                for k in range(4):
                    p0 = self.corners[k]
                    p1 = self.corners[(k+1)%4]
                    dist = self.distance(p0, p1, coord)
                    if dist <= self.B: 
                        self.blob_big.add((i, j))
                        
    def initialize(self):
        self.process_outlines()
        self.fill()
        self.bloat()


class Frame_o(Obstacle):
    def __init__(self, L, dx, w, h, corners=None):
        super().__init__(L, dx, w, h, corners)
        self.max_grid = math.ceil(self.B / self.dx)
        #it only has blob_big

    # It has different fill function
    def fill(self):
        for i in range(self.w):
            for j in range(0, self.max_grid+1):
                self.blob_big.add((i, j))
            for j in range(self.h - self.max_grid, self.h):
                self.blob_big.add((i, j))
        for j in range(self.h):
            for i in range(self.w - self.max_grid, self.w):
                self.blob_big.add((i, j))
            for i in range(0, self.max_grid+1):
                self.blob_big.add((i,j))

    def initialize(self):
        self.fill()


class Path(object):
    def __init__(self, coords, cost):
        self.coords = coords # List of tuples
        self.cost = cost # Scaler

    def add_node(self, coord, cost):
        self.coords.append(coord)
        self.cost = self.cost + cost

    def ends_at(self, idx):
        if self.coords[-1] == idx:
            return True
        return False

    def copy_path(self):
        coords = copy.deepcopy(self.coords)
        path = Path(coords, self.cost)
        return path



class PriorityQueue(object): 
    def __init__(self, criteria): 
        self.queue = [] 
        self.criteria = criteria # 'high' cost is high priority, vice versa
        self.highest_priority_idx = -1
        self.highest_priority_cost = -1
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 
  
    # Check if the queue is empty 
    def isEmpty(self): 
        return len(self.queue) == 0

    def lookup_path(self, path):
        for p in range(len(self.queue)-1, -1, -1):
            pat = self.queue[p]
            if pat.coords[-1] == path.coords[-1]: # The end nodes are the same
                c = pat.cost
                return p, c
        return -1, -1


    def _update_highest_priority(self, p, c):
        self.highest_priority_idx = p
        self.highest_priority_cost = c

    def update_highest_priority(self, p, c): # new idx, new cost
        if self.highest_priority_idx == -1:
            self._update_highest_priority(p, c)
            return
        pat = self.queue[self.highest_priority_idx]
        if self.criteria == 'high':
            if c > pat.cost:
                self._update_highest_priority(p, c)
        elif self.criteria == 'low':
            if c < pat.cost:
                self._update_highest_priority(p, c)

    # Path has to be not in Q
    def insert(self, path):
        self.queue.append(path) 
        self.update_highest_priority(len(self.queue)-1, path.cost)
  
    # Case 1: path not in Q, insert directly
    # Case 2: path in Q with high priority, do nothing
    # Case 3: path in Q with low priority, pop, insert new
    def update(self, path):
        p, c = self.lookup_path(path)
        # path in Q
        if self.criteria == 'high':
            if c < path.cost:
                self.queue.pop(p)
                self.queue.append(path)
                self.update_highest_priority(len(self.queue)-1, path.cost)
        elif self.criteria == 'low':
            if path.cost < c:
                self.queue.pop(p)
                self.queue.append(path)
                self.update_highest_priority(len(self.queue)-1, path.cost)


    # Pop the path in Q with highest priority 
    # no matter which one is the last node
    # shouldn't return None
    def dequeue(self): 
        if self.highest_priority_idx != -1:
            item = self.queue.pop(self.highest_priority_idx)
            # Update the Q's properties
            if len(self.queue) == 0:
                self.highest_priority_idx = -1
                self.highest_priority_cost = -1
            else:
                idx = None
                c = None
                for i in range(len(self.queue)):
                    c_pat = self.queue[i].cost
                    if self.criteria == 'high':
                        if c == None or c_pat > c:
                            c = c_pat
                            idx = i
                    elif self.criteria == 'low':
                        if c == None or c_pat < c:
                            c = c_pat
                            idx = i
                self.highest_priority_idx = idx 
                self.highest_priority_cost = c
            return item 
        else: return None
        

# Obstacle: -2; start: 1; end: -1, others: >= 2
def assign_freespace(grids, start_idx, end_idx):
    print(end_idx)
    if (grids[start_idx[0]][start_idx[1]] == -2
     or grids[end_idx[0]][end_idx[1]] == -2):
        return False
    # Start from the starting pixel
    # For each pixel in the queue, pop and see its neighbors
    queue = []
    w = len(grids)
    h = len(grids[0])
    print(w, h)
    grids[start_idx[0]][start_idx[1]] = 1
    grids[end_idx[0]][end_idx[1]] = -1
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
    return True

# Find non-obstacle neighbors which are strictly 1 greater than 
# cur value or the goal.
# Also calculate the L2 distance to them
def find_neighbors(grids, cur_idx):
    w = len(grids)
    h = len(grids[0])
    cur_r, cur_c = cur_idx
    cur_val = grids[cur_r][cur_c]
    neighbors = []
    costs = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            r = cur_r + dr 
            c = cur_c + dc
            if (cur_r != r or cur_c != c) and r >= 0 and r < w and c >= 0 and c < h: # valid index
                new_val = grids[r][c]
                if cur_val+1 == new_val or new_val == -1: # valid wavefront
                    neighbors.append((r, c))
                    dcost = math.sqrt(dr**2 + dc**2)
                    costs.append(dcost)
    return neighbors, costs


def find_path0(grids, start_idx, end_idx):
    explored = []
    frontier = PriorityQueue('low')
    p0 = Path([start_idx], 0)
    frontier.update(p0)
    while frontier.isEmpty() == False:
        p = frontier.dequeue()
        if p.ends_at(end_idx):
            return p.coords
        neighbors, costs = find_neighbors(grids, p.coords[-1]) # a list of node coord tuples, VALID neighbors
        for n in range(len(neighbors)):
            neighbor = neighbors[n]
            cost = costs[n]
            p_tmp = p.copy_path()
            p_tmp.add_node(neighbor, cost)
            if neighbor not in explored:
                frontier.insert(p_tmp)
                explored.append(neighbor)
            else:
                frontier.update(p_tmp)
    return None

def find_path(grids, start_idx, end_idx):
    explored = []
    queue = []
    p0 = Path([start_idx], 0)
    queue.append(p0)
    while len(queue) != 0:
        length = len(queue)
        queue_tmp = []
        for i in range(length):
            p = queue.pop()
            if p.ends_at(end_idx):
                return p.coords
            neighbors, costs = find_neighbors(grids, p.coords[-1])
            for n in range(len(neighbors)):
                neighbor = neighbors[n]
                cost = costs[n]
                if neighbor not in explored:
                    p_tmp = p.copy_path()
                    p_tmp.add_node(neighbor, cost)
                    queue_tmp.append(p_tmp)
                    explored.append(neighbor)
        queue = queue_tmp
    return None

# L: wheelbase; start, end: tuple; obstacles: list of Obstacles
def get_path(L, width, height, dx, start, end, obstacles, visualize=True):
    # First, discretize the map
    # we need (width / dx) by (height / dx) grids
    start_idx = (round(start[1] / dx), round(start[0] / dx))
    end_idx = (round(end[1] / dx), round(end[0] / dx))
    w = int(math.floor(width / dx))
    h = int(math.floor(height / dx))
    grids = [([0] * h) for dw in range(w)] # initialize everything to 0 

    # Then, fill in the grid map with objects
    # Create an obstacle list
    obstacle = []
    for corners in obstacles:
        obs = Obstacle(L, dx, w, h, corners)
        obs.initialize()
        obstacle.append(obs)
    frame = Frame_o(L, dx, w, h)
    frame.initialize()
    obstacle.append(frame)
    for obj in obstacle:
        for pixel in obj.blob_big: # pixel is (rcoord, ccoord)
            grids[pixel[0]][pixel[1]] = -2
    
    # Now we need to assign the free space with numbers
    success = assign_freespace(grids, start_idx, end_idx)
    print('Done assign_freespace')
    if success == False: return None

    # Then we need to find a good path, which is a list of idx tuples
    # This list will then be passed to visualization function
    path = find_path(grids, start_idx, end_idx)
    print('Done find_path')
    if path == None: return None
    if visualize == True:
        visualize_path(obstacle, path, w, h, 6)
    # now we need to convert the idx to real coords tuples
    # This list will be passed to the path following function
    path_real = []
    dxx = dx / 2
    for coord in path:
        x, y = coord
        path_real.append((x*dx+dxx, y*dx+dxx))
    print(path_real)
    return path_real





