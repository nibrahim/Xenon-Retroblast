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
    def __init__(self,pos,init_mag,init_dir,image,velocities,homing = False,homing_radius=5):
        super(Spot,self).__init__(self.containers)
        self.image = pygame.Surface((1,1)).convert()
        self.image.fill((200,200,200))
#         self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos
#         self.disp = complex(pos[0],pos[1]) # Displacement vector
        self.velocity = velocities.next()
        self.velocities =  velocities # Acceleration assignments over time [magnitude, angle, time] (time == None means forever)
        self.time = 0
        self.mag = init_mag
        self.angle = init_dir
        self.homing = homing
        self.homing_radius = homing_radius

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
#             cosine = math.cos(math.radians(self.angle))
#             sine = math.sin(math.radians(self.angle))
            x = lx+math.ceil(self.mag * round(math.cos(math.radians(self.angle)),2))
            y = ly-math.ceil(self.mag * round(math.sin(math.radians(self.angle)),2))
            dvector = complex(x,y)
            # Homing calculations
            cvector = complex(*pygame.mouse.get_pos())
            homing_vector = cvector - dvector
            pygame.draw.circle(screen,(255,255,255),(lx,ly),self.homing_radius,1)
            pygame.draw.circle(screen,(0,255,0),(x,y),self.homing_radius,1)
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
#             print round(cosine,2),"  ",round(sine,2)
            print (lx,ly),"--",(x,y)

            pygame.draw.aaline(screen,(0,0,0),(lx,ly),(x,y))
            self.rect.center = (x,y)
        
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

    s1=Spot((300,400),                            # Start position
            1,                                    # Initial magnitude
            135,                                   # Initial angle
            'marker-red.png',                     # Marker 
            itertools.chain([[0,0,50],
                             [0,-5,27]],
                            itertools.cycle([[0.1,0,50],
                                             [0,-5,18],
                                             [0,0,50],
                                             [0,-5,18],
                                             [0,0,50],
                                             [0,-5,18],
                                             [-0.1,0,50],
                                             [0,-5,18]
                                             #                              [-1,10,20],
                                             #                              [0,10,100],
                                             #                              [1,10,20]
                             ])),           # List of linear_velocity, angular_velocity, time 3tuples
            10,
            100
            )

    s2=Spot((50,20),                            # Start position
            8,                                    # Initial magnitude
            0,                                   # Initial angle
            'marker-red.png',                     # Marker 
            itertools.cycle([[0,0,100],
                             [0,-30,3],
                             [0,0,5],
                             [0,-30,3],
                             [0,0,100],
                             [0,30,3],
                             [0,0,5],
                             [0,30,3]
                             ]),           # List of linear_velocity, angular_velocity, time 3tuples
            10,
            100
            )

    s3=Spot((512,512),                            # Start position
            -10,                                    # Initial magnitude
            0,                                   # Initial angle
            'marker-red.png',                     # Marker 
            itertools.cycle([[0.1,5,None]]),
            # List of linear_velocity, angular_velocity, time 3tuples
            10,
            100
            )

    s4=Spot((512,10),                            # Start position
            -5,                                    # Initial magnitude
            -5,                                   # Initial angle
            'marker-red.png',                     # Marker 
            itertools.cycle([[0,0,100],
                             [0,-5,33],
                             [0,0,170],
                             [0,5,33],
                             ]),
            # List of linear_velocity, angular_velocity, time 3tuples
            10,
            100
            )



    


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

