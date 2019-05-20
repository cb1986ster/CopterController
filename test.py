import pygame
from display import display
from time import sleep
from widgets import background
import math

run_no = 0.0



def main(window):
    global run_no
    pos_x = 200
    pos_y = 200
    size_x = 200
    size_y = 200
    x_limit = size_x/2
    y_limit = size_y/2

    a=run_no*3.14
    b=0.0

    def getHorizonOffset(alfa,beta,x):
        x0 = x+pos_x
        y0 = -(math.tan(alfa*math.pi)*x + beta) + pos_y + size_y/2
        if x0 < pos_x:
            x0 = pos_x
        elif x0 > pos_x+size_x:
            x0 = pos_x+size_x
        if y0 < pos_y:
            y0 = pos_y
        elif y0 > pos_y+size_y:
            y0 = pos_y+size_y
        return (x0+pos_x+size_x/2,y0)

    sky_color = (64,128,255)
    soil_color = (255,128,64)
    pygame.draw.rect(window, sky_color , [pos_x,pos_y, size_x, size_y] )
    pygame.draw.polygon(window, soil_color , (
        (pos_x,pos_y + size_y),
        (pos_x+size_x,pos_y + size_y),
        getHorizonOffset(a,b,x_limit),
        getHorizonOffset(a,b,-x_limit)
    ))
    pygame.draw.ellipse(window, (0,0,0), (pos_x+size_x/2-5,pos_y+size_y/2-5, 10,10))
    pygame.draw.ellipse(window, (255,0,0), (pos_x+size_x/2-6,pos_y+size_y/2-6, 12,12),2)
    # pygame.draw.ellipse(window, (255,0,0), [225, 10, 20+run_no, 20+run_no], 2)

    run_no += 0.001





d = display()
bg = background( (0,0,0) )
d.addWidget(bg.fill)
d.addWidget(main)
d.open()
sleep(10)
