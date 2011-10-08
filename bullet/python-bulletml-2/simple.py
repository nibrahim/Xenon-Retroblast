#!/usr/bin/env python

import pygame
from pygame.locals import *

import bulletml

SCREENRECT = Rect(0, 0, 640, 480)

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, containers):
        super(Particle,self).__init__(containers)
        self.image = pygame.Surface((3, 3)).convert()
        self.image.fill((0,0,0))
        self.rect = self.image.get_rect(center = pos)
        self.x, self.y = self.rect.center

    def update(self):
        self.rect.center = (self.x, self.y)


def init():
    global screen,empty
    screen = pygame.display.set_mode(SCREENRECT.size,DOUBLEBUF)#)|FULLSCREEN)
    empty = pygame.Surface(SCREENRECT.size).convert()
    empty.fill((255, 255, 255))
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(True)
    return clock

def get_bullet(f):
    target = bulletml.Bullet()
    doc = bulletml.BulletML.FromDocument(f)
    bullet = bulletml.Bullet.FromDocument(doc, x=320, y=240, target=target, rank=0.5)
    bullet.vanished = True
    return target, bullet

def update_bullet(bullet, target, particle):
    target.x, target.y = pygame.mouse.get_pos()
    target.x /= 2
    target.y /= 2
    target.y = 120 - target.y
    target.px = target.x
    target.py = target.y


def run(clock):
    everything = pygame.sprite.Group()
    target, bullet = get_bullet(open("examples/popcorn/close.xml", "rU"))
    print bullet
    p = Particle((320,240), everything)
    while True:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
        update_bullet(bullet, target, p)
        n = bullet.step()
        if n:
            bullet = n[0]
        else:
            print "Nope"
        x,y = bullet.x*1.1, bullet.y*1.1
        print x,y
        p.x, p.y = x, y
        
            
        everything.clear(screen,empty)
        everything.update()
        everything.draw(screen)
        pygame.display.flip()

def main():
    clock = init()
    run(clock)


if __name__ == "__main__":
    main()
