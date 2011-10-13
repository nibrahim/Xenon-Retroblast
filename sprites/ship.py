import random
import pygame
import pygame.gfxdraw
import logging
from pygame.locals import *

import constants

from weapons import Explosion

        
class ShipSprite(pygame.sprite.Sprite):
    def __init__(self, image, position, sound):
        pygame.sprite.Sprite.__init__(self)
        self.sound = pygame.mixer.Sound(sound)
        self.image = pygame.image.load(image).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.firing = False # Are we firing?
        self.energy = constants.SHIP_HEALTH # Energy
        self.vx, self.vy = (0,0) # X and Y velocities
        self.tp = 10 # Thruster power
        self.maxvel = 20 # Maximum velocity
        self.weapons = [] # List of weapons
        self.score = 0 # Score

    def move(self,direction):
        logging.debug("MOVE: Direction is %s"%direction)
        if direction in (constants.RIGHT,constants.LEFT):
            self.vx = {constants.RIGHT :  self.tp,
                       constants.LEFT  : -self.tp}[direction]
        if direction in (constants.TOP,constants.BOTTOM):
            self.vy = {constants.TOP   : -self.tp,
                       constants.BOTTOM:  self.tp}[direction]
        logging.debug("MOVE: New velocities are %d,%d"%(self.vx,self.vy))

    def stop(self,direction):
        logging.debug("MOVE: Direction is %s"%direction)
        if direction in (constants.RIGHT,constants.LEFT):
            self.vx = 0
        if direction in (constants.TOP,constants.BOTTOM):
            self.vy = 0
        logging.debug("MOVE: New velocities are %d,%d"%(self.vx,self.vy))

    def update(self):
        cx,cy = self.rect.center
        cx+=self.vx
        cy+=self.vy
        if cx > 1024:
            cx = 1024
        if cy > 700:
            cy = 700
        if cx < 0:
            cx =0
        if cy < 0:
            cy = 0
        self.rect.center = (cx,cy)
        for i in self.weapons:
            i.rect.center = (cx + i.offset[0],
                             cy + i.offset[1])
        self.vx *= 1.2
        self.vy *= 1.2
        if self.vx >= self.maxvel:
            self.vx = self.maxvel
        if self.vx <= -self.maxvel:
            self.vx = -self.maxvel
        if self.vy >= self.maxvel:
            self.vy = self.maxvel
        if self.vy <= -self.maxvel:
            self.vy = -self.maxvel

    def fire(self):
        logging.debug("WEAPON : Weapons activated")
        self.firing = True

    def unfire(self):
        logging.debug("WEAPON : Weapons deactivated")
        self.firing = False

    def decrement(self, q = 10):
        if self.energy > 0:
            x,y = self.rect.center
            for i in range(2):
                Explosion((x + random.randrange(-20, 20),
                           y + random.randrange(-20, 20)),
                          1, 4)
            self.energy -= q
            logging.debug("SHIP : Energy %d"%self.energy)
            if self.energy <= 0:
                self.kill()

    def attach(self,weapon):
        logging.debug("WEAPON : Attaching %s"%weapon.name)
        weapon.ship = self
        bounding_rect = self.rect
        logging.debug("ATTACH : Bounding rectangle is %s centered at %s"%(str(bounding_rect),str(bounding_rect.center)))
        if self.weapons:
            logging.debug("ATTACH : Unionising with following rects")
            for j in self.weapons:
                logging.debug("ATTACH :  Unionising with %s positioned at %s and centered at %s"%(str(j),str(j.rect),str(j.rect.center)))
            bounding_rect = self.rect.unionall([x.rect for x in self.weapons])
        logging.debug("ATTACH : Bounding rectange (after union) is %s centered at %s"%(str(bounding_rect),str(bounding_rect.center)))
        weapon.rect.center = bounding_rect.center
        logging.debug("ATTACH : Weapon rect is %s centered at %s"%(str(weapon.rect),str(weapon.rect.center)))
        if weapon.position == constants.TOP:
            weapon.rect.bottom = bounding_rect.top
        elif weapon.position == constants.BOTTOM:
            weapon.rect.top = bounding_rect.bottom
        elif weapon.position == constants.LEFT:
            weapon.rect.right = bounding_rect.left - 10
        elif weapon.position == constants.RIGHT:
            weapon.rect.left = bounding_rect.right + 10
        logging.debug("ATTACH : Weapon attached at %s with center %s"%(str(weapon.rect),str(weapon.rect.center)))
        if not weapon.coupled:
            weapon.couple()
            self.weapons.append(weapon)
        weapon.offset = (weapon.rect.center[0] - self.rect.center[0] ,
                         weapon.rect.center[1] - self.rect.center[1] )

    def kill(self):
        pygame.sprite.Sprite.kill(self)
        x, y = self.rect.center
        if self.sound:
            self.sound.play(0)
        for i in self.weapons:
            i.kill()
        Explosion((x, y), 10, 1)
