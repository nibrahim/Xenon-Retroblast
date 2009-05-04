#!/usr/bin/python
from __future__ import with_statement

import sys
import math
import cmath
import pygame
import random
import pickle
import inspect
import itertools

from pygame.locals import *

PI,E = cmath.pi,cmath.e

SHIP = (500,500)

class Spot(pygame.sprite.Sprite):
    def __init__(self,data_file):
        super(Spot,self).__init__(self.containers)
        self.image = pygame.Surface((1,1)).convert()
        self.image.fill((200,200,200))
        self.time = 0
        self._load_data(data_file)

    def _load_data(self,f):
        """ Loads up the path information which should be of the format
        path = {
        'start' : (300,400),
        'initmag' : 1,
        'initang' : 135,
        'image'   : 'marker-red.png',
        'path'    : [[0.1,0,50],[0,-5,18],[0,0,50],[0,-5,18],[0,0,50],[0,-5,18],[-0.1,0,50],[0,-5,18]],
        'homvel'  : 10,
        'homrad'  : 5
        }
        """

        with open(f) as ip:
            path = pickle.load(ip)

        self.image         = pygame.image.load(path['image']).convert_alpha()
        self.rect          = self.image.get_rect()
        self.rect.center   = path['start']
        # Acceleration assignments over time [magnitude, angle, time] (time == None means forever)
        self.velocities    = itertools.cycle(path['path'])
        self.velocity      = self.velocities.next()
        self.mag           = path['initmag']
        self.angle         = path['initang']
        self.homing        = path['homvel']
        self.homing_radius = path['homrad']

    def update(self,time):
        lvel,avel,ntime = self.velocity
        self.time += 1
        if ntime != None and self.time > ntime:
            print self.mag
            print "Switching!!!"
            self.velocity = self.velocities.next()
            self.time = 0
        else:
            self.mag += lvel
            self.angle += avel
            self.angle %=360
            lx,ly = self.rect.center
            print "Angle is %s"%self.angle
            x = lx+math.ceil(self.mag * round(math.cos(math.radians(self.angle)),2))
            y = ly-math.ceil(self.mag * round(math.sin(math.radians(self.angle)),2))
            dvector = complex(x,y)
            # Homing calculations
            cvector = complex(*pygame.mouse.get_pos())
            homing_vector = cvector - dvector
            # Uncomment following two lines to draw homing region (useful for debugging)
            # pygame.draw.circle(screen,(255,255,255),(lx,ly),self.homing_radius,1)
            # pygame.draw.circle(screen,(0,255,0),(x,y),self.homing_radius,1)
            if self.homing and self.homing_radius >= abs(homing_vector): #Adjust position based on homing vector
                self.homing_radius+=1
                print "@@ ",self.homing_radius," @@ ",abs(homing_vector)
                try:
                    homing_vector = self.homing * (homing_vector / abs(homing_vector))
                except ZeroDivisionError:
                    homing_vector = 0
                dvector += homing_vector
                x,y = dvector.real,dvector.imag
            else:
                if self.homing_radius > 50:
                    self.homing_radius -= 1
            print (lx,ly),"--",(x,y)

            pygame.draw.aaline(screen,(0,0,0),(lx,ly),(x,y))
            self.rect.center = (x,y)
        
def initialiseGame():
    global screen,empty,clock
    screen = pygame.display.set_mode((1024,768),DOUBLEBUF)
    screen.fill((0,0,0))
    empty = pygame.Surface((1024,768)).convert()
    clock = pygame.time.Clock()

if __name__ == "__main__":
    initialiseGame()
    all = pygame.sprite.RenderPlain()
    Spot.containers = all
    pygame.mouse.set_cursor(*pygame.cursors.ball) 
    # s1=Spot("../data/foo.path")
    s2=Spot("../data/bar.path")

    # s3=Spot((512,512),                            # Start position
    #         -10,                                    # Initial magnitude
    #         0,                                   # Initial angle
    #         'marker-red.png',                     # Marker 
    #         itertools.cycle([[0.1,5,None]]),
    #         # List of linear_velocity, angular_velocity, time 3tuples
    #         10,
    #         100
    #         )

    # s4=Spot((512,10),                            # Start position
    #         -5,                                    # Initial magnitude
    #         -5,                                   # Initial angle
    #         'marker-red.png',                     # Marker 
    #         itertools.cycle([[0,0,100],
    #                          [0,-5,33],
    #                          [0,0,170],
    #                          [0,5,33],
    #                          ]),
    #         # List of linear_velocity, angular_velocity, time 3tuples
    #         10,
    #         100
    #         )



    


#     s1=Spot((150,400),                            # Start position
#             2,                                    # Initial magnitude
#             0,                                   # Initial angle
#             'marker-red.png',                     # Marker 
#             itertools.cycle([[0,0,50],
# #                              [-2,0,1],
#                              [0,-5,18],
# #                              [2,0,1],
#                              [0,0,50],
# #                              [-2,0,1],
#                              [0,-5,18],
# #                              [2,0,1],
#                              [0,0,50],
# #                              [-2,0,1],
#                              [0,-5,18],
# #                              [2,0,1],
#                              [0,0,50],
# #                              [-2,0,1],
#                              [0,-5,18],
# #                              [2,0,1],
#                              ]),           # List of linear_velocity, angular_velocity, time 3tuples
#             10,
#             100
#             )



    seconds = 0
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit(0)
        all.clear(screen,empty)
        all.update(seconds)
        seconds += 1
        all.draw(screen)
        pygame.display.flip()
        seconds += clock.tick(70)/1000.0

