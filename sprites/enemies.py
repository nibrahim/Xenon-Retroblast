import random
import pygame
import pygame.gfxdraw
import logging
from pygame.locals import *

import constants
import propulsion

from weapons import Explosion, Damage

class RomulanFire(pygame.sprite.Sprite):
    def __init__(self):
        pass
        

class Romulan(pygame.sprite.Sprite):
    def __init__(self, ship, egroup):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("%s/enemy1.png"%constants.IMG_DIR).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        x,y = random.randrange(1024), random.randrange(768)
        self.rect.center = (x,y)
        self.vx = random.randrange(1,20)
        self.vy = random.randrange(1,20)
        self.ship = ship
        self.alive = True
        self.direction_counter = 0
        self.group = egroup
        self.engine = iter(propulsion.Engine("%s/foo.json"%constants.DATA_DIR, self.rect.center))
        self.health = 100

    def update(self):
        x,y = self.engine.next()
        if x>1024 or y>752:
            pygame.sprite.Sprite.kill(self)
        self.rect.center = (x,y)

    def kill(self):
        Explosion(self.rect.center, 2,  2)
        self.ship.score += 5
        if self.sound:
            self.sound.play(0)
        super(Romulan, self).kill()

    def damage(self, weapon):
        for i in range(2):
            x0, y0 = self.rect.center
            Damage((random.randrange(x0-10,x0+10), random.randrange(y0-10,y0+10)))
        self.health -= weapon.power
        if self.health <= 0:
            self.kill()
