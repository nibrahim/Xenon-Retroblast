import random
import pygame
import pygame.gfxdraw
import logging
from pygame.locals import *

import constants
import propulsion

from weapons import Explosion, Damage, Charge

class EnemyFire(pygame.sprite.Sprite):
    def __init__(self):
        super(EnemyFire,self).__init__(self.containers)



class BossFireBullet(EnemyFire):
    def __init__(self, boss):
        super(BossFireBullet, self).__init__()
        self.boss = boss
        self.image = pygame.Surface((6, 6)).convert()
        colour = random.randrange(125, 200)
        pygame.gfxdraw.filled_circle(self.image, 3,3,3, (255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center
        pos = lambda: self.boss.ship.rect.center
        self.engine = iter(propulsion.Engine("%s/bossfire.json"%constants.DATA_DIR, self.rect.center, pos))
        self.energy = 10
        
        
    def update(self):
        x,y = self.engine.next()
        if x>1024 or y>752:
            pygame.sprite.Sprite.kill(self)
        self.rect.center = (x,y)

    def kill(self):
        self.boss.ship.decrement(self.energy)
        super(BossFireBullet, self).kill()


class BossFireLaser(EnemyFire):
    def __init__(self, boss):
        super(BossFireLaser, self).__init__()
        self.boss = boss
        self.image = pygame.Surface((5,768)).convert()
        self.image.fill((180,180,200))
        self.rect = self.image.get_rect()
        self.rect.midtop = self.boss.rect.midbottom
        self.energy = 20
        
    def update(self):
        self.rect.midtop = self.boss.rect.midbottom

    def kill(self, hit_ship = True):
        if hit_ship:
            self.boss.ship.decrement(self.energy)
        else:
            super(BossFireLaser, self).kill()



class Boss(pygame.sprite.Sprite):
    def __init__(self, ship, egroup, pos = (512, 384)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("%s/enemy2.png"%constants.IMG_DIR).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        x,y = pos
        self.rect.center = (x,y)
        self.vx = random.randrange(1,20)
        self.vy = random.randrange(1,20)
        self.ship = ship
        self.alive = True
        self.direction_counter = 0
        self.group = egroup
        self.engine = iter(propulsion.Engine("%s/boss.json"%constants.DATA_DIR, self.rect.center))
        self.health = 5000
        self.fire_counter = 0
        self.laser = False
        self.laser_counter = 0
        
    def update(self):
        x,y = self.engine.next()
        if x>1024 or y>752:
            pygame.sprite.Sprite.kill(self)
        self.rect.center = (x,y)
        self.fire_counter += 1
        x0, y0 = self.rect.midbottom
        if self.fire_counter > 30:
            for i in range(5): BossFireBullet(self)
            self.fire_counter = 0
        
        if self.laser:
            self.laser_counter -= 2
            if not self.laser_counter:
                self.laser.kill(False)
                self.laser = False
        
        if not self.laser:
            self.laser_counter += 1
            if self.laser_counter == 30:
                self.laser = BossFireLaser(self)

    def kill(self):
        if self.laser:
            self.laser.kill(False)
            self.laser = False
        Explosion(self.rect.center, 2,  2)
        self.ship.score += 5
        if self.sound:
            self.sound.play(0)
        self.ship.decrement(self.health)
        super(Boss, self).kill()

    def damage(self, weapon):
        for i in range(2):
            x0, y0 = self.rect.center
            Damage((random.randrange(x0-10,x0+10), random.randrange(y0-10,y0+10)))
        self.health -= weapon.power
        if self.health <= 0:
            self.kill()

class RomulanFire(pygame.sprite.Sprite):
    def __init__(self):
        pass
        

class Romulan(pygame.sprite.Sprite):
    def __init__(self, ship, egroup, pos = (512, 384)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("%s/enemy1.png"%constants.IMG_DIR).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        x,y = pos
        self.rect.center = (x,y)
        self.vx = random.randrange(1,20)
        self.vy = random.randrange(1,20)
        self.ship = ship
        self.alive = True
        self.direction_counter = 0
        self.group = egroup
        ship_pos = lambda : self.ship.rect.center
        self.engine = iter(propulsion.Engine("%s/romulan.json"%constants.DATA_DIR, self.rect.center, ship_pos))
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
