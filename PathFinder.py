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


# Does the position given by th1, th2 intersect any obstacle?
def theta_intersect(th1, th2):
    return any([position_intersect(fk(th1, th2), obstacle) for obstacle in obstacles])

# Show the full configuration space, a boolean grid representing if each
# (th1, th2) combination puts the end effector in a valid spot
def show_cspace():
    cspace = np.array([[theta_intersect(th1_low + i*dth1, th2_low + j*dth2) \
        for i in range(num_thetas_1)] for j in range(num_thetas_2)])
    plt.imshow(cspace, \
                extent=[math.degrees(th) for th in [th1_low, th1_high, th2_low, th2_high]], \
                origin='lower')
    plt.xlabel('Theta 1')
    plt.ylabel('Theta 2')
    plt.title('Configuration Space (yellow represents obstacle)')
    plt.show()


# Obstacle: -2; start: 1; end: -1, others: >= 2
def assign_freespace(grids, start_idx, end_idx):
    print(end_idx)
    if (grids[start_idx[0]][start_idx[1]] == -2
     or grids[end_idx[0][0]][end_idx[0][1]] == -2):
        return False
    # Start from the starting pixel
    # For each pixel in the queue, pop and see its neighbors
    queue = []
    w = len(grids)
    h = len(grids[0])
    print(w, h)
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
    return True

# Find non-obstacle neighbors which are strictly 1 greater than 
# cur value or the goal.
def find_neighbors(grids, cur_idx):
    w = len(grids)
    h = len(grids[0])
    cur_r, cur_c = cur_idx
    cur_val = grids[cur_r][cur_c]
    neighbors = []
    #costs = []
    for (dr, dc) in [(-1,0),(1,0),(0,0),(0,-1),(0,1),(1,1),(1,-1),(-1,1),(-1,-1)]:
        r = cur_r + dr 
        c = cur_c + dc
        if (cur_r != r or cur_c != c) and r >= 0 and r < w and c >= 0 and c < h: # valid index
            new_val = grids[r][c]
            if cur_val+1 == new_val or new_val == -1: # valid wavefront
                neighbors.append((r, c))
                #dcost = math.sqrt(dr**2 + dc**2)
                #costs.append(dcost)
    return neighbors#, costs


class Path(object):
    def __init__(self, coords):
        self.coords = coords # List of tuples
        #self.cost = cost # Scaler

    def add_node(self, coord):
        self.coords.append(coord)
        #self.cost = self.cost + cost

    def ends_at(self, idxs):
        for idx in idxs:
            if self.coords[-1] == idx:
                return True
        return False

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
            if p.ends_at(end_idx):
                return p.coords
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
    return None


# Assume hight in range [-180, 180] and 90 grids
def get_idx2(th2, dx):
    middle = 45
    offset = -round(th2 / dx)
    if offset == middle: offset = -middle
    return int(middle + offset)


def get_idx1(th1, dx):
    offset = np.floor(th1 / dx)
    return int(offset)


# get a path from one point in config space to another
# assume square grids; width, height: 180,360; dx: degrees per grid
def get_path_seg(cspace, dx, start, end):
    # First, discretize the map
    # we need (hight / dx) by (width / dx) grids
    # start and end are in (th1, th2) form
    # convert to (th2_idx, th1_idx) form
    start_idx = (get_idx2(start[1], dx), get_idx1(start[0], dx))
    print(end)
    end_idx1 = (get_idx2(end[1], dx), get_idx1(end[0], dx)) # top
    print(end_idx1)
    w = cspace.shape[1] #45
    h = cspace.shape[0] #90
    grids = np.vstack((cspace, cspace, cspace))#.tolist() # wrap around
    # change start idx to middle and prepare 2 other end indices
    start_idx = (start_idx[0]+h, start_idx[1])
    end_idx2 = (end_idx1[0]+h, end_idx1[1]) # middle
    end_idx3 = (end_idx1[0]+2*h, end_idx1[1]) # bottom
    end_idx = [end_idx1, end_idx2, end_idx3]
    print(start_idx, end_idx1, end_idx2, end_idx3)
    # Now we need to assign the free space with numbers
    success = assign_freespace(grids, start_idx, end_idx)
    print('Done assign_freespace')
    if success == False: 
        print('assignment failed')
        return None

    # Then we need to find a good path, which is a list of idx tuples
    # This list will then be passed to visualization function
    path = find_path(grids, start_idx, end_idx)
    print('Done find_path')
    if path == None: 
        print('path not found')
        return None
    path = np.array(path) # in (th2_idx, th1_idx)
    path[:, 0] = np.mod(path[:, 0], h) # all in range ([0,90), [0,45))
    # now we need to convert the idx to real coords tuples
    # This list will be passed to the path following function
    # approximate thetas
    path_real = copy.deepcopy(path)
    path_real = np.flip(path_real, 1) # (th1_idx, th2_idx)
    path_real[:, 0] = path_real[:, 0] * dx + dx/2
    path_real[:, 1] = 180 - path_real[:, 1] * dx
    path_real = np.radians(path_real)
    return path, path_real # both are np arrays


# dx is 4; waypoints is in radians, bounded by ([0,pi],[-pi,pi])
# Returns theta_list: a list of 3 lists (with different length) of theta pairs
def get_path(dx, waypoints, visualization=False):
    cspace_int = np.load('cspace_int.npy')
    cspace_bool = np.load('cspace_bool.npy')
    theta_list = [] # real thetas
    grid_list = [] # for visualization
    for i in range(len(waypoints)-1):
        start = np.degrees(waypoints[i])
        end = np.degrees(waypoints[i+1])
        print(waypoints[i], waypoints[i+1])
        if start.any() == np.nan or end.any() == np.nan:
            print("Exists a point not in the workspace")
            return None
        path, path_real = get_path_seg(cspace_int, dx, start, end)
        print(path)
        # enclose path with accurate start and ending thetas
        path_real = path_real.tolist()
        path_real.append(waypoints[i+1])
        path_real.insert(0, waypoints[i])
        theta_list.append(path_real) # list of 3 lists of tuples
        path = path.tolist()
        grid_list.extend(path)
        print("done seg")
    if visualization:
        visualize_path(cspace_bool, grid_list)
    return theta_list


def visualize_path(cspace_bool, grid_list):
    print(grid_list)
    for grid in grid_list:
        cspace_bool[grid[0], grid[1]] = 75
    start = grid_list[0]
    end = grid_list[-1]
    cspace_bool[start[0], start[1]] = 160
    cspace_bool[end[0], end[1]] = 130
    plt.imshow(cspace_bool, extent=[math.degrees(th) for th in [th1_low, th1_high, th2_low, th2_high]], cmap='gist_ncar')
    plt.xlabel('Theta 1')
    plt.ylabel('Theta 2')
    plt.title('Configuration Space')
    plt.show()