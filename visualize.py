######
# For visualization
######
from tkinter import *
import math

def draw_pixel(canvas, i, j, d, color="black", w=0, out='black'): # i j are world coord, not tk coord
    startx = j * d
    endx = (j+1) * d
    starty = i * d
    endy = (i+1) * d
    canvas.create_rectangle(startx, starty, endx, endy, fill=color, width=w, outline=out)

def draw_line(canvas, p1, p2, d, color="black", thick=2):
    startx = p1[1] * d + round(d/2)
    starty = p1[0] * d + round(d/2)
    endx = p2[1] * d + round(d/2)
    endy = p2[0] * d + round(d/2)
    canvas.create_line(startx, starty, endx, endy, fill=color, width=thick)

def draw_dot(canvas, i, j, d, color="black"):
    startx = j * d
    endx = (j+1) * (d)
    starty = i * d
    endy = (i+1) * d
    canvas.create_oval(startx, starty, endx, endy, fill=color, width=0)

def draw_obstacle(canvas, obstacle, d, color='black'):
    if obstacle.corners == None: return
    dx = obstacle.dx
    dxx = round(dx / 2)
    x1, y1 = obstacle.corners[0]
    x1 = round(x1 / dx)*d + dxx
    y1 = round(y1 / dx)*d + dxx
    x2, y2 = obstacle.corners[1]
    x2 = round(x2 / dx)*d + dxx
    y2 = round(y2 / dx)*d + dxx
    x3, y3 = obstacle.corners[2]
    x3 = round(x3 / dx)*d + dxx
    y3 = round(y3 / dx)*d + dxx
    x4, y4 = obstacle.corners[3]
    x4 = round(x4 / dx)*d + dxx
    y4 = round(y4 / dx)*d + dxx
    canvas.create_polygon(y1,x1, y2,x2, y3,x3, y4,x4, fill=color, width=0)


def draw(canvas, obstacle, path, w, h, d):
    for obj in obstacle:
        blob = obj.blob_big
        for pixel in blob:
            draw_pixel(canvas, pixel[0], pixel[1], d, "SpringGreen4")
    for obj in obstacle:
        draw_obstacle(canvas, obj, d, "SpringGreen3")
    for i in range(len(path)-1):
        p1 = path[i]
        p2 = path[i+1]
        draw_line(canvas, p1, p2, d, "midnight blue")
    start = path[0]
    end = path[-1]
    draw_dot(canvas, start[0], start[1], d, "gray60")
    draw_dot(canvas, end[0], end[1], d, "red2")


# w and h are in imaginary pixels
# d is number of screen pixels per imaginary pixel, should be even
def visualize_path(obstacle, path, w, h, d=10):
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=h*d, height=w*d)
    canvas.configure(bd=5, highlightthickness=0)
    canvas.pack()
    draw(canvas, obstacle, path, w, h, d)
    root.mainloop()
    print('Done visualize_path')