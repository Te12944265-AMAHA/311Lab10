from tkinter import *
import math
from visualize import *
from PathFinder import *
import random

# the map of one floor of the building
class Floor(object):
    def __init__(self, width, height, floor=0):
        self.width = width
        self.height = height
        self.bins = {}
        # obstacles include walls but exclude robots and bins
        self.obstacle_pos = {} # set of pixels wrt the floor
        self.obstacles = []
        self.chargers = {}
        self.dump_pos = []
        self.initialize()

    def add_bin(self, bin):
        self.bins.add(bin)

    def add_charger(self, charger):
        self.chargers.add(charger)

    def add_dump_pos(self, pos):
        self.dump_pos.append(pos)

    def get_dump_pos(self):
        return self.dump_pos

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
            if bi.is_loaded():
                b.append(bi)
        return b

    def get_random_waiting_bin(self):
        b = self.get_waiting_bins()
        if b != []:
            bb = random.choice(b)
            return bb
        else:
            return None

    def initialize(self):
        # TODO: add default obstacles, chargers, bins, dump_pos
        dump_pos = Position((0, 200), floor)
        floor.add_dump_pos(dump_pos)
        pass


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
        self.pos_original = pos
        self.loaded = loaded
        self.state = None # collect, carry, dump, None
        self.num = num # bin number
        self.d = 5
        self.collector = None

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

    def add_collector(self, robot):
        self.collector = robot

    def is_loaded(self):
        return self.loaded == True

    def draw(self, canvas):
        if self.state == None:
            if self.loaded == False:
                draw_pixel(canvas, self.pos[0], self.pos[1], self.d, color='white', w=2, out='blue')
            else:
                draw_pixel(canvas, self.pos[0], self.pos[1], self.d, color='blue', w=0, out='blue')


class Robot(Position):
    def __init__(self, pos, num=0, floor=None):
        super().__init__(pos, floor)
        self.num = num 
        self.loaded = False
        self.state = None # move, collect, (*elevator,) dump, to_charge, charge, None
        self.error = False
        self.job = None # will be assigned a Bin
        self.L = 5
        self.dx = 10
        self.battery = 10000
        self.low_power = False
        self.path = []
        self.timer = 0

    # current state is 'move'. takes in start and end Position objs and a Floor obj
    # end is a list of Position objs
    def approach(self, end, original=False):
        if end == None or end == []:
            self.state = None
            self.job = None
            return False
        width = self.floor.width
        height = self.floor.height
        #TODO: modify end
        if original == False:
            path = get_path(L, width, height, self.dx, self.pos, end.pos, self.floor.obstacles)
        else: 
            path = get_path(L, width, height, self.dx, self.pos, end.original_pos, self.floor.obstacles)
        self.path = path
        if path == None:
            self.state = None
            self.job = None
            return False
        return True


    def assign_job(self):
        self.state = 'move'
        self.job = self.floor.get_waiting_bins()
        self.approach(b)


    def update_pos(self):
        if self.state == 'move' or self.state == 'to_charger':
            if self.path != []:
                self.pos = self.path[0]
                self.path.pop(0)

    def update_battery(self):
        if self.state == None or self.state == 'to_charge' or self.state == 'charge':
            return
        self.battery -= random.randint(10, 35)


    def update_state(self):
        if self.low_power == True and self.state != 'to_charge':
            if self.job != None:
                self.job.operate_bin(None) # put down the bin
            self.job = None
            self.state = 'to_charge'
            self.approach(self.floor.get_chargers()) 
            self.timer = 0
        elif self.state == 'to_charge' and self.path == []:
            self.state = 'charge'
        elif self.state == 'charge':
            self.timer += 1
            if self.timer > 20:
                self.state = None
                self.battery = 10000
                self.timer = 0
        elif self.low_power == True and self.job = None and self.state = 'move'
        elif self.job == None:
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
        elif self.state == 'move' and self.job != None and self.path == [] and self.job.state == 'carry' and self.job.loaded == True:
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
        elif self.state == 'move' and self.job != None and self.path == [] and self.job.state == 'carry' and self.job.loaded == False:
            self.state = None
            self.job.operate_bin(None)
            self.job = None



# this environment has 1 floor and multiple bins and robots
class Environment(object):
    def __init__(self):
        floor = Floor(400, 600)
        robot_pos = [(,),(,),(,)]
        robots = {}
        for i in range(3):
            robots[i] = Robot(robot_pos[i], i, floor)






    

    



