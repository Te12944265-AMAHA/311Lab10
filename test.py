from tkinter import *
import math


def draw(canvas):
    canvas.create_rectangle(5, 5, 25, 25)
    bin_centers = [(440, 60), (320, 380), (580, 220), (640, 280), (780, 220)]
    # bin original pos
    for i in range(5):
        x, y = bin_centers[i]
        canvas.create_rectangle(x-10, y-10, x+10, y+10, width=1)

    canvas.create_oval(100, 10, 180, 90, width=5) # dumping area
    # charging area
    for i in range(4):
        center = 340 + 40 * i
        canvas.create_oval(20, center-15, 50, center+15, width=2)

    canvas.create_rectangle([200, 0, 220, 210], fill='black', width=0)
    canvas.create_rectangle([220, 190, 320, 210], fill='black', width=0)
    canvas.create_rectangle(100, 100, 200, 120, fill='black', width=0)

    canvas.create_rectangle(280, 320, 300, 500, fill='black', width=0)
    canvas.create_rectangle(300, 400, 450, 420, fill='black', width=0)
    canvas.create_rectangle(100, 320, 280, 340, fill='black', width=0)

    canvas.create_rectangle(460, 0, 480, 100, fill='black', width=0)
    canvas.create_rectangle(300, 80, 460, 100, fill='black', width=0)

    canvas.create_rectangle(450, 240, 800, 260, fill='black', width=0)
    canvas.create_rectangle(600, 80, 620, 420, fill='black', width=0)


def run(w, h, d):
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    canvas = Canvas(root, width=h*d, height=w*d)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    draw(canvas)
    root.mainloop()
    print('Done test')

run(50, 80, 10)