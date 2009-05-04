#!/usr/bin/python

import sys
import math
import cmath
import pygame
import random
import inspect
import itertools
PI,E = cmath.pi,cmath.e
from pygame.locals import *

SHIP = (500,500)


class Spot(pygame.sprite.Sprite):
    def __init__(self,pos,init_mag,init_dir,image,velocities):
        super(Spot,self).__init__(self.containers)
        self.image = pygame.Surface((1,1)).convert()
        self.image.fill((200,200,200))
#         self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos
#         self.disp = complex(pos[0],pos[1]) # Displacement vector
        self.velocity = velocities.next()
        self.velocities =  velocities # Acceleration assignments over time [magnitude, angle, time] (time == None means forever)
        self.time = 0.0
        self.mag = init_mag
        self.angle = init_dir

    def update(self,time):
        lvel,avel,ntime = self.velocity
        lx,ly = self.rect.center
        self.time += time
        #         x = lx+self.mag * math.cos(math.radians(self.angle))
        #         y = ly+self.mag * math.sin(math.radians(self.angle))
#         print " %s,%s"%(avel,math.radians(avel))
#         print "Sin : %s"%math.sin(math.radians(avel))
#         print "Cos : %s"%math.cos(math.radians(avel))
#         print "Displacements = %s,%s"%(lvel*math.sin(math.radians(avel)),lvel*math.cos(math.radians(avel)))
#         print lx,ly
        x = lx+math.ceil(lvel * math.cos(math.radians(avel)))
        y = ly-math.ceil(lvel * math.sin(math.radians(avel)))

#         print x,y
        pygame.draw.aaline(screen,(0,0,0),(lx,ly),(x,y))
        self.angle += avel
        self.mag += lvel
        self.rect.center = (x,y)
#         print "(%s,%s) -- (%s,%s)"%(lx,ly,x,y)
        if ntime != None and self.time > ntime:
            self.velocity = self.velocities.next()
            self.time = 0.0

        

def initialiseGame():
    global screen,empty,clock
    screen = pygame.display.set_mode((1024,768),DOUBLEBUF)
    screen.fill((255,255,255))
    empty = pygame.Surface((1024,768)).convert()
    clock = pygame.time.Clock()

if __name__ == "__main__":
    initialiseGame()
    all = pygame.sprite.RenderPlain()
    Spot.containers = all
    pygame.mouse.set_cursor(*pygame.cursors.ball) 

    s1=Spot((400,400),1,math.radians(0),'marker-red.png',
            itertools.cycle([
                [i/30.0,i,0] for i in range(0,360,5)
                ]))

    
#     s1=Spot((400,400),1,math.radians(0),'marker-red.png',
#             itertools.cycle([[1,45,None]]))


#     for i in range(0,400,5):
#         s1=Spot((400,400),1,math.radians(0),'marker-red.png',
#                 itertools.cycle([[10,i,0]]))


#     s2=Spot((100,200),2,math.radians(0),'marker-red.png',
#             itertools.cycle([[4,0,0]]))


#     s=Spot((0,0),2,math.radians(0),'marker-red.png',
#            itertools.cycle([[0, math.cos(math.pi*float(x)/100), 1]
#                             for x in range(0,200)]))


#     s=Spot((512,300),complex(1,0),'marker-green.png',
#            itertools.cycle([[0,  45,  1],
# #                             [0.2,  90,  10],
# #                             [0.1,  -45,  5]
#                             ]))

    seconds = 0
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit(0)
#         print "Seconds - ",seconds
#         if seconds > 1:
#             seconds = 0
        all.clear(screen,empty)
        all.update(seconds)
        all.draw(screen)
        pygame.display.flip()
#         raw_input()
        seconds += clock.tick(70)/1000.0
