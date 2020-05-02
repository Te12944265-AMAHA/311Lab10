from tkinter import *
import math
from visualize import *
from PathFinder import *

# the map of one floor of the building
class Floor(object):
    def __init__(self, width, height, floor=0):
        self.width = width
        self.height = height
        self.floor = 0
        self.bins = {}
        # obstacles include walls but exclude robots and bins
        self.obstacle_pos = {} # set of pixels wrt the floor

    def add_bin(self, bin):
        self.bins.add(bin)
        


class Dest(object):
    def __init__(self, pos, floor=0):
        # tuple (row, col), center position wrt the floor
        self.pos = pos
        self.floor = floor


# for simplicity, every bin is a square with side length 5
class Bin(Dest):
    def __init__(self, pos, num=0, floor=0, loaded=False):
        super().__init__(pos, floor)
        self.loaded = loaded
        self.state = None # collect, carry, dump, None
        self.num = num # bin number
        self.d = 5
        self.collector = None

    def operate_bin(self, state):
        self.state = state 

    # this should be called by the overall update fn at each time step
    def update_pos(self):
        if self.state == 'carry':
            #assert self.collector != None
            self.pos = self.collector.pos

    def add_collector(self, robot):
        self.collector = robot

    def draw(self, canvas):
        if self.state == None:
            if self.loaded == False:
                draw_pixel(canvas, self.pos[0], self.pos[1], self.d, color='white', w=2, out='blue')
            else:
                draw_pixel(canvas, self.pos[0], self.pos[1], self.d, color='blue', w=0, out='blue')


class Robot(object):
    def __init__(self, pos, num=0, floor=0):
        self.pos = pos 
        self.num = num 
        self.floor = floor 
        self.state = None # approach, collect, carry, elevator, dump, charge, None
        self.error = False
        self.job = None # will be assigned a bin

    def approach(self, start, end):






    

    



