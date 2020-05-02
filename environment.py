from tkinter import *
import math
from visualize import *
from PathFinder import *
import random
import copy

# the map of one floor of the building
class Floor(object):
    def __init__(self, width, height, floor=0):
        self.width = width # (width of canvas map region)
        self.height = height # (height of canvas map region)
        self.bins = []
        # obstacles include walls but exclude robots and bins
        self.obstacles = []
        self.chargers = []
        self.dump_pos = []
    

    def add_bin(self, b):
        self.bins.append(b)

    def add_charger(self, charger):
        self.chargers.append(charger)

    def add_dump_pos(self, pos):
        self.dump_pos.append(pos)

    def get_dump_pos(self):
        return self.dump_pos

    def get_bins(self):
        return self.bins

    def get_chargers(self):
        return self.chargers

    def get_available_chargers(self):
        c = []
        for charger in self.chargers:
            if charger.is_available():
                c.append(charger)
        return c

    def get_random_charger(self):
        c = self.get_available_chargers()
        if c != []:
            cc = random.choice(c)
            return cc
        else:
            return None

    def get_waiting_bins(self):
        b = []
        for bi in self.bins:
            if bi.collector == None and bi.loaded:
                b.append(bi)
        return b

    def get_free_bins(self):
        b = []
        for bi in self.bins:
            if bi.collector == None and bi.loaded == False:
                b.append(bi)
        return b

    def load_free_bins(self):
        b = self.get_free_bins()
        for bi in b:
            if random.random() > 0.4:
                bi.load_bin()

    def get_random_waiting_bin(self):
        b = self.get_waiting_bins()
        if b != []:
            bb = random.choice(b)
            return bb
        else:
            return None

    def initialize(self):
        # Add dump position
        dump_pos = Position((140, 50), floor=self)
        self.add_dump_pos(dump_pos)
        # Add obstacles. defined as (left_x, top_y, right_x, bottom_y) in tk frame
        self.obstacles = [(200, 0, 220, 210), (220, 190, 320, 210), (100, 100, 200, 120),
                          (280, 320, 300, 500), (300, 400, 450, 420), (100, 320, 280, 340),
                          (460, 0, 480, 100), (300, 80, 460, 100),
                          (450, 240, 800, 260), (600, 80, 620, 420)]
        # Add bins
        bin_centers = [(440, 60), (320, 380), (580, 220), (640, 280), (780, 220)]
        for i in range(len(bin_centers)):
            load = random.random() > 0.2 # the bin has 80% chance to be loaded
            b = Bin(bin_centers[i], num=i, floor=self, loaded=load)
            self.add_bin(b)
        # Add chargers
        charger_centers = [(35, 340+40*i) for i in range(4)]
        for i in range(len(charger_centers)):
            c = Charger(charger_centers[i], num=i, floor=self)
            self.add_charger(c)

    def get_available_pos(self, L, dx):
        w = self.width
        h = self.height
        obstacles = copy.deepcopy(self.obstacles)
        frame = [(-2,-2,w+1,-1),(-2,h,w+1,h+1),(-2,-1,-1,h),(w,-1,w+1,h)]
        obstacles.extend(frame)
        pos_available = []
        idx_available = []
        r = L//2
        for i in range(w//dx):
            x = i * dx + dx//2
            for j in range(h//dx):
                y = j * dx + dx//2
                if position_available((x, y), obstacles, r):
                    pos_available.append((x, y))
                    idx_available.append((i, j))
        return pos_available, idx_available
        

    # draw the map of the floor (not including the robots/bins)
    def draw(self, canvas):
        canvas.create_line(self.width, 1, self.width, self.height, width=2)
        canvas.create_line(1, 1, self.width, 1, width=2)
        canvas.create_line(1, self.height, self.width, self.height, width=2)
        canvas.create_line(1, 1, 1, self.height, width=2)
        # draw bin original pos
        for b in self.bins:
            x, y = b.original_pos
            canvas.create_rectangle(x-10, y-10, x+10, y+10, width=1)
        # dumping area
        canvas.create_oval(100, 10, 180, 90, width=5) 
        # draw charging area
        for c in self.chargers:
            x, y = c.pos
            canvas.create_oval(x-15, y-15, x+15, y+15, width=2)
        # draw obstacles
        for obs in self.obstacles:
            canvas.create_rectangle(obs, fill='black', width=0)


class Position(object):
    def __init__(self, pos, floor=None):
        # tuple (row, col), center position wrt the floor
        self.pos = pos
        self.floor = floor


class Charger(Position):
    def __init__(self, pos, num=0, floor=None, loaded=False):
        super().__init__(pos, floor)
        self.loaded = loaded
        self.num = num

    def is_available(self):
        return self.loaded == False


# for simplicity, every bin is a square with side length 5
class Bin(Position):
    def __init__(self, pos, num=0, floor=None, loaded=False):
        super().__init__(pos, floor)
        self.original_pos = pos
        self.loaded = loaded
        self.state = None # collect, carry, dump, None
        self.num = num # bin number
        self.d = 5
        self.collector = None

    def __repr__(self):
        return "Bin #%d" % self.num

    def operate_bin(self, state):
        self.state = state 

    def dump_bin(self):
        self.loaded = False

    def load_bin(self):
        self.loaded = True

    # this should be called by the overall update fn at each time step
    def update_pos(self):
        if self.state == 'carry':
            #assert self.collector != None
            self.pos = self.collector.pos
        elif self.state == None:
            self.original_pos = self.pos

    def set_collector(self, robot):
        self.collector = robot

    def is_loaded(self):
        return self.loaded == True

    def draw(self, canvas):
        x, y = self.pos
        if self.loaded == False:
            canvas.create_rectangle(x-10, y-10, x+10, y+10, width=2, outline='blue')
        else:
            canvas.create_rectangle(x-10, y-10, x+10, y+10, width=0, fill='blue')


class Robot(Position):
    def __init__(self, pos, num=0, floor=None, cspace=None):
        super().__init__(pos, floor)
        self.num = num 
        self.loaded = False
        self.state = None # move, collect, (*elevator,) dump, to_charge, charge, None
        self.error = False
        self.job = None # will be assigned a Bin
        self.charger = None
        self.L = 20 # wheelbase is 20 pixels
        self.dx = 10 # descretization resolution
        self.battery = 10000
        self.low_power = False
        self.path = []
        self.timer = 0
        self.on = True
        self.cspace = cspace

    def getHashables(self):
        return (self.num, ) # return a tuple of hashables

    def __hash__(self):
        return hash(self.getHashables())

    def __eq__(self, other):
        return (isinstance(other, Robot) and (self.x == other.x))

    def __repr__(self):
        return "Robot #%d" % self.num

    @staticmethod
    def get_end_positions(end_P, original):
        end_idx = []
        if original == True:
            if type(end_P) is list:
                for en in end_P:
                    end_idx.append(en.original_pos)
            else:
                end_idx.append(end_P.original_pos)
        else: 
            if type(end_P) is list:
                for en in end_P:
                    end_idx.append(en.pos)
            else:
                end_idx.append(end_P.pos)
        return end_idx

    # current state is 'move'. takes in start and end Position objs and a Floor obj
    # end is a list of Position objs
    def approach(self, end, original=False):
        if end == None or end == []:
            self.state = None
            self.job = None
            return -1
        width = self.floor.width
        height = self.floor.height
        #TODO: modify end
        path, bin_num = get_path(self.cspace, self.dx, self.pos, Robot.get_end_positions(end, original))
        self.path = path
        if path == None:
            self.state = None
            self.job = None
            return -1
        return bin_num


    def assign_job(self):
        print('assigning job for robot #%d'% (self.num))
        self.state = 'move'
        b = self.floor.get_waiting_bins()
        bin_num = self.approach(b)
        if bin_num == -1:
            return
        self.job = b[bin_num] # bin_num is not the num of the Bin!
        self.job.set_collector(self)

    def assign_charger(self):
        print('assigning job for robot #%d'% (self.num))
        c = self.floor.get_available_chargers()
        charger_num = self.approach(c)
        if charger_num == -1:
            return
        charger = c[charger_num]
        charger.loaded = True
        self.charger = charger

    def update_pos(self):
        if self.state == 'move' or self.state == 'to_charge':
            if self.path != []:
                self.pos = self.path[0]
                self.path.pop(0)

    def update_battery(self):
        if self.state == None or self.state == 'to_charge' or self.state == 'charge':
            return
        self.battery -= random.randint(20, 30)
        self.low_power = self.battery < 100

    def update_state(self):
        if self.state == 'charge':
            #print('charging....................')
            self.timer += 1
            if self.timer > 20:
                self.state = None
                self.battery = 10000
                self.low_power = False
                self.timer = 0
                #print('done charging@@@@@@@@@@@@@@@@@@@')

        elif self.low_power == True and (self.state != 'to_charge'):
            #print('here!!!!!!!!!!!!!!!--------------------------------')
            if self.job != None:
                self.job.operate_bin(None) # put down the bin
                self.job.collector = None
            self.job = None
            self.state = 'to_charge'
            self.approach(self.floor.get_random_charger()) 
            self.timer = 0
        elif self.state == 'to_charge' and self.path == []:
            #print('here---------------------------------------')
            self.state = 'charge'
        elif self.state == 'to_charge' and self.path != []:
            pass
        elif self.job == None:
            #print('here')
            self.assign_job()
        elif self.state == 'move' and self.job != None and self.path == [] and self.job.state == None:
            self.state = 'collect'
            self.job.operate_bin('collect')
        elif self.state == 'collect':
            self.timer += 1 # collection takes time
            if self.timer > 8:
                self.state = 'move'
                self.job.operate_bin('carry')
                self.approach(self.floor.get_dump_pos())
                self.timer = 0
        elif self.state == 'move' and self.job != None and self.path == [] \
                    and self.job.state == 'carry' and self.job.loaded == True:
            self.state = 'dump'
            self.job.operate_bin('dump')
        elif self.state == 'dump':
            self.timer += 1 # collection takes time
            if self.timer > 4:
                self.state = 'move'
                self.job.operate_bin('carry')
                self.job.dump_bin()
                self.approach(self.job, True) # go to the original pos of the bin
                self.timer = 0
        elif self.state == 'move' and self.job != None and self.path == [] and \
                        self.job.state == 'carry' and self.job.loaded == False:
            self.state = None
            self.job.collector = None
            self.job.operate_bin(None)
            self.job = None

    def update(self):
        self.update_pos()
        self.update_state()
        self.update_battery()
        self.on = not self.on
        self.print_info()

    def print_info(self):
        print('robot #%d: state = %s, job = %s, battery = %d, path=[]? %d' %(self.num, \
                                    self.state, self.job, self.battery, self.path == []))

    def get_robot_info(self):
        return "%s\nState: %s\tJob: %s\nBattery: %s\tError: %d" % (self, self.state, 
                                                self.job, self.battery, self.error)

    def display_robot_info(self, canvas, center_pos):
        info = self.get_robot_info()
        canvas.create_text(center_pos, text=info, fill='gray26', font="Helvetica 14")

    def draw(self, canvas):
        color = 'SpringGreen2'
        if self.error == True:
            color = 'red'
        elif self.low_power == True:
            color = 'yellow'
            if self.state == 'charge' and self.on:
                color = 'green'
        x, y = self.pos
        canvas.create_oval(x-8, y-8, x+8, y+8, fill=color, width=0)


# this environment has 1 floor, 5 bins, 4 chargers, 1 dump pos, and 3 robots
class Environment(object):
    def __init__(self):
        self.floor = Floor(800, 500)
        self.floor.initialize()
        self.dx = 10
        robot_pos_available, robot_idx_available = self.floor.get_available_pos(20, self.dx)
        self.robot_pos_available = robot_pos_available
        self.idx_available = robot_idx_available
        self.cspace = None
        self.robots = dict()
        self.bins = self.floor.get_bins()
        self.running = False
        self.timer = 0

    def add_robots(self, num):
        for i in range(num):
            robot_pos = random.choice(self.robot_pos_available)
            self.robots[i] = Robot(robot_pos, i, self.floor, cspace=self.cspace)
        
    # draw the config space
    def draw_map(self, canvas):
        for idx in self.idx_available:
            draw_pixel(canvas, idx[0], idx[1], self.dx, color='yellow')
        self.floor.draw(canvas)  

    def create_cspace(self):
        w = self.floor.width // self.dx
        h = self.floor.height // self.dx
        print(w, h)
        # all in tk frame
        cspace = np.full((w, h), -2)
        for idx in self.idx_available:
            cspace[idx[0], idx[1]] = 0
        self.cspace = cspace


    def start(self):
        self.running = True
    
    def pause(self):
        self.running = False

    def update(self):
        if self.running == True:
            for i, robot in self.robots.items():
                robot.update()
            for b in self.bins:
                b.update_pos()
        self.timer += 1


    def draw_buttons(self, canvas):
        canvas.create_rectangle(850, 50, 930, 100, fill='RoyalBlue1', )
        canvas.create_text(890, 75, text="Start", fill="black", font="Helvetica 16")
        canvas.create_rectangle(950, 50, 1030, 100, fill='RoyalBlue1', )
        canvas.create_text(990, 75, text="Pause", fill="black", font="Helvetica 16")


    def draw(self, canvas):
        self.draw_buttons(canvas)
        self.floor.draw(canvas)
        for b in self.bins:
            b.draw(canvas)
        for i, robot in self.robots.items():
            robot.draw(canvas)
            robot.display_robot_info(canvas, (950, 200+i*100))
            
def in_region(area, x, y):
    l, t, r, b = area
    return x >= l and x <= r and y >= t and y <= b

# Core animation code

def init(data):
    data.env = Environment()
    data.env.create_cspace()
    data.env.add_robots(3)


def mousePressed(event, data):
    if in_region((850, 50, 930, 100), event.x, event.y):
        data.env.start()
    elif in_region((950, 50, 1030, 100), event.x, event.y):
        data.env.pause()


def redrawAll(canvas, data):
    data.env.draw(canvas)

def keyPressed(event, data):
    pass

def timerFired(data):
    data.env.update()
    if data.env.timer % 200 == 0:
        data.env.floor.load_free_bins()


def run(width=1100, height=500):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 50 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

if __name__ == "__main__":
    run(1100, 500)





    

    



