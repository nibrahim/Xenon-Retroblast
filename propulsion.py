#!/usr/bin/python
from __future__ import with_statement

import sys
import math
import cmath
import random
import json
import inspect
import logging
import itertools


PI,E = cmath.pi,cmath.e


class Engine(object):
    def __init__(self, data_file, start = False, cursor_pos = False):
        self.time = 0
        self.cursor_pos = cursor_pos
        self._load_data(data_file)
        if start:
            self.cpos = start


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
            path = json.load(ip)

        self.cpos          = path['start']
        # Acceleration assignments over time [magnitude, angle, time] (time == None means forever)
        self.velocities    = itertools.cycle(path['path'])
        self.velocity      = self.velocities.next()
        self.mag           = path['initmag']
        self.angle         = path['initang']
        self.homing        = path['homvel']
        self.homing_radius = path['homrad']
    
    def __iter__(self):
        while True:
            lvel,avel,ntime = self.velocity
            self.time += 1
            if ntime != None and self.time > ntime:
                self.velocity = self.velocities.next()
                self.time = 0
            else:
                self.mag += lvel
                self.angle += avel
                self.angle %=360
                lx,ly = self.cpos
                x = lx+math.ceil(self.mag * round(math.cos(math.radians(self.angle)),2))
                y = ly-math.ceil(self.mag * round(math.sin(math.radians(self.angle)),2))
                dvector = complex(x,y)
                # Homing calculations
                if self.cursor_pos:
                    cvector = complex(*self.cursor_pos())
                    homing_vector = cvector - dvector
                    # Uncomment following two lines to draw homing region (useful for debugging)
                    # pygame.draw.circle(screen,(255,255,255),(lx,ly),self.homing_radius,1)
                    # pygame.draw.circle(screen,(0,255,0),(x,y),self.homing_radius,1)
                    if self.homing and self.homing_radius >= abs(homing_vector): #Adjust position based on homing vector
                        self.homing_radius+=1
                        try:
                            homing_vector = self.homing * (homing_vector / abs(homing_vector))
                        except ZeroDivisionError:
                            homing_vector = 0
                        dvector += homing_vector
                        x,y = dvector.real,dvector.imag
                    else:
                        if self.homing_radius > 50:
                            self.homing_radius -= 1
                self.cpos = (x,y)
                yield (x,y)

