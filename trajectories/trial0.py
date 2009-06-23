#!/usr/bin/python

import sys
import math
import pygame
import random
import inspect
from pygame.locals import *

SHIP = (512,500)

def perpvector(vec,normalise = False):
    if normalise:
        mod = 1
    else:
        mod = abs(vec)
    arg = math.tanh(vec.imag/vec.real)
    arg+=math.pi/2
    retval=complex(mod*math.cos(arg),mod*math.sin(arg))
    return retval


class Spot(pygame.sprite.Sprite):
    def __init__(self,pos,image,initvel,acceleration,homing = False):
        #         pygame.sprite.Sprite.__init__(self, self.containers)
        super(Spot,self).__init__(self.containers)
        self.image = pygame.Surface((2,2)).convert()
        self.image.fill((200,200,200))
#         self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.disp = complex(pos[0],pos[1]) # Displacement vector
        self.vel = initvel #Velocity vector
        self.accelerations = [0.2+0.2j,
                              0.2-0.2j,
                              -0.2-0.2j,
                              -0.2+0.2j]

        self.accelerations = [+0.3j,
                              -0.3j,
                              ]
        self.accelerations = acceleration
        self.accindex = 0
        self.acc = self.accelerations[self.accindex]
        #         self.acc = 0
        self.homing = homing
        self.homing_vel = 0
        self.change = False
    def update(self,time):
        ship_pos = pygame.mouse.get_pos()
        if self.homing:
            if abs(self.vel) > self.homing_vel:
                self.homing_vel = abs(self.vel)
                #                 print "Increasing to %s"%self.homing_vel
                #             self.disp += self.homingvector(self.disp,complex(*ship_pos))   # Calculate and apply homing velocity
                self.disp += self.homingvector(self.disp,complex(*ship_pos),self.homing_vel)   # Calculate and apply homing velocity
        self.vel += self.acc
        self.disp += self.vel
        if self.change:
            self.vel += self.change
            self.change = False
        x= self.disp.real
        y= self.disp.imag
        self.rect.center = (x,y)
        if time%20 == 0:
            self.accindex+=1
            self.accindex %= len(self.accelerations)
            next = self.accelerations[self.accindex]
            if inspect.isfunction(next):
                self.acc = next(self.vel)
            else:
                self.acc = self.accelerations[self.accindex]
            print "X velocity is %s"%self.vel.real


    def homingvector(self,pos,ship,vel=False):
        dir_vector = ship  - pos
        if not vel:
            #             vel = 3
            vel = abs(dir_vector)/10
#         print "vel is ", vel
        return (dir_vector/(abs(dir_vector)+0.001))*vel
        
        

def initialiseGame():
    global screen,empty,clock
    screen = pygame.display.set_mode((1024,768),DOUBLEBUF)
#    screen.fill((0,0,0))
    screen.fill((255,255,255))
    empty = pygame.Surface((1024,768)).convert()
#     empty.fill((0,0,0))
    clock = pygame.time.Clock()

if __name__ == "__main__":
    initialiseGame()
    all = pygame.sprite.RenderPlain()
    Spot.containers = all
    pygame.mouse.set_cursor(*pygame.cursors.ball) 

    sins = []
    # Sinusoidal
#     x=100
    #     for i in range(10):
    #         x+=90
    sins.append(Spot((512,10),
                     'marker-green.png',
                     0+0j,
                     [-0.5+0.5j],
                     #-0.5,
                      #0.5],
                     True))



    t=-1
    while 1:
        t+=1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit(0)
        clock.tick(30)
#         if t%100 == 0:
#             for i in sins:
#                 if i.homing:
#                     i.homing = False
#                     i.change = complex(random.randrange(-2,2),0)
#                 else:
#                     i.homing = True

        all.clear(screen,empty)
        all.update(t)
        all.draw(screen)
        pygame.display.flip()
