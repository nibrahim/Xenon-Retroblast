#!/usr/bin/python

import sys
import math
import random
import pygame
import logging
import dircache
from pygame.locals import *

import sprites, constants, propulsion

class Disturbance(object):
    def __init__(self,dsprites,number,surface):
        self.sprites = dsprites
        self.group = pygame.sprite.RenderPlain()
        self.n = number
        self.surface = surface
    def display(self):
        self.group.clear(self.surface,empty) # Clear all disturbances
        for i in self.group.sprites(): # Remove all of them from the group.
            i.image = i.orig_image
            i.kill()
        for i in range(self.n): # Select n at random
            dno = random.randrange(len(self.sprites))
            dist = self.sprites[dno]
            dist.add(self.group)
        self.group.update()  # Position them
        self.group.draw(self.surface) # Update screen

def createStarField(groups):
    "Create 3 layers of stars for parallax scrolling"
    far_away = pygame.sprite.RenderPlain()
    closer = pygame.sprite.RenderPlain()
    closest = pygame.sprite.RenderPlain()
    for i in range(1,100):
        x,y = random.randrange(1024),random.randrange(768)
        sprites.StarSprite((x, y), 0.2, 25, 0, constants.STARFIELD_INIT_DECELERATION).add(far_away, *groups)
        x, y = random.randrange(1024), random.randrange(768)
        sprites.StarSprite((x, y), 0.5, 50, 4, constants.STARFIELD_INIT_DECELERATION).add(closer, *groups)
        x, y = random.randrange(1024), random.randrange(768)
        sprites.StarSprite((x, y), 0.8, 75, 6, constants.STARFIELD_INIT_DECELERATION).add(closest, *groups)
    return far_away,closer

def createDisturbances(sprite_dir, ndist):
    "Create a list of ndist disturbances using images from sprite_dir"
    try:
        images = ["%s/%s"%(sprite_dir,x) for x in dircache.listdir(sprite_dir)]
        dist_sprites = []
        for i in images:
            logging.debug("Loading %s"%i)
            dist_sprites.append(sprites.DisturbanceSprite(i))
        dist_sprites.append(sprites.CrackSprite('%s/strip.png'%constants.IMG_DIR))
        return Disturbance(dist_sprites,ndist,screen)
    except OSError,e:
        logging.info("Failed to load disturbance sprites (%s)"%e)
        return Disturbance([],0,screen)

def displayCard(text,font,background,disturbance):
    texts = []
    for i in text:
        texts.append(font.render(i,True,(150,150,150)).convert_alpha())
    multiplier = -1
    x_pos = 512 - max([x.get_width() for x in texts])/2
    y_start = 50 + (texts[0].get_height()*len(texts))# 50 is the upper and lower margin
    y_inc = texts[0].get_height()
    for i in range(1,100):
        clock.tick(10)
        # Jitter the background
        multiplier *= -1
        jitter = (multiplier * random.randrange(2),multiplier * random.randrange(2))
        screen.blit(background,jitter)
        # Render text
        y = y_start
        for i in texts:
            screen.blit(i, (x_pos+jitter[0], y+jitter[1]))
            y+=y_inc
        # Create screen disturbances (blips and stuff)
        disturbance.display()
        pygame.display.flip()

def displayCredits(disturbance):
    if pygame.mixer.get_init():
        pygame.mixer.music.load("%s/fugue2.ogg"%constants.AUDIO_DIR)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    background = pygame.image.load('%s/dialog-card.png'%constants.IMG_DIR).convert_alpha()
    gar = pygame.font.Font('%s/jGara2.ttf'%constants.DATA_DIR,75)
    displayCard(["Foulan Mihrabi","Retrogaming studios","Presents"],gar,background,disturbance)
    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(10000)
    displayCard(["Xenon Retroblast"],gar,background,disturbance)

def jitter(group,m):
    m *= -1
    jitter = (m * random.randrange(3),m * random.randrange(3))
    for i in group.sprites():
        i.rect.center = (i.rect.center[0] + jitter[0],
                         i.rect.center[1] + jitter[1])
    return m
    
def startShooter(disturbance):
    # Sprite groups
    all = pygame.sprite.OrderedUpdates() # All the sprites. This is for general frame updates
    jgroup = pygame.sprite.RenderPlain() # For jitters. All sprites that need to shake go in here.
    enemies = pygame.sprite.RenderPlain() # For enemy ships
    weapons = pygame.sprite.RenderPlain() # For weapons
    weapon_fire = pygame.sprite.RenderPlain() # For weapon fire
    createStarField([jgroup,all]) # StarField background
    ship = sprites.ShipSprite("%s/ship.png"%constants.IMG_DIR,(512,384), "%s/ship-exploding.wav"%constants.AUDIO_DIR)
    ship.add(all, jgroup)
    sprites.SheetSprite.containers = all, jgroup
    sprites.Charge.containers = all
    sprites.Particle.containers = all, jgroup
    sprites.Explosion.containers = all, jgroup
    sprites.Damage.containers = all, jgroup
    sprites.IonDischarge.containers = all, jgroup
    sprites.StatusPanel.containers = all
    spanel = sprites.StatusPanel(ship)
    multiplier = 1
    sg = sprites.SteamGun(constants.TOP, [all, weapons, jgroup], [weapon_fire, all, jgroup])
    l1 = sprites.MineGun(constants.RIGHT,[all,weapons,jgroup],[weapon_fire, all, jgroup],engine = propulsion.Engine("%s/bar.json"%constants.DATA_DIR))
    l3 = sprites.Laser(constants.RIGHT,[all,weapons,jgroup],[weapon_fire, all, jgroup],engine = propulsion.Engine("%s/bar.json"%constants.DATA_DIR))
    l2 = sprites.IonCanon(constants.LEFT,[all,weapons,jgroup],[weapon_fire, all, jgroup])


    ship.attach(sg)
    # ship.attach(l1)
    ship.attach(l2)
    deadtimer = 100
    while True:
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            if event.type == KEYDOWN:
                #                 logging.debug("Key pressed is %s"%event.key)
                if event.key == K_DOWN:  ship.move(constants.BOTTOM)
                if event.key == K_LEFT:  ship.move(constants.LEFT)
                if event.key == K_RIGHT: ship.move(constants.RIGHT)
                if event.key == K_UP:    ship.move(constants.TOP)
                if event.key == K_LCTRL: ship.fire()
            if event.type == KEYUP:
                #                 logging.debug("Key raised is %s"%event.key)
                if event.key == K_DOWN:  ship.stop(constants.BOTTOM)
                if event.key == K_LEFT:  ship.stop(constants.LEFT)
                if event.key == K_RIGHT: ship.stop(constants.RIGHT)
                if event.key == K_UP:    ship.stop(constants.TOP)
                if event.key == K_LCTRL: ship.unfire()
        # Clear screen of old sprites
        all.clear(screen,empty)
        # Update all general sprites
        all.update()
        # Create screen disturbances (blips and stuff)
        disturbance.display()
        # Jitter the jgroup sprites.
        multiplier = jitter(jgroup,multiplier)
        # Draw all the sprites and flip the display
        all.draw(screen)
        # Create new enemies if anyone is destroyed
        if len(enemies.sprites()) < 1:
            sprites.Romulan(ship, enemies).add(all,jgroup,enemies)

        # Check collisions
        for e, w in pygame.sprite.groupcollide(enemies, weapon_fire, False, False).iteritems():
            for i in w:
                e.damage(i)
        new_weapons = pygame.sprite.spritecollide(ship, weapons, False)
        for i in new_weapons:
            ship.attach(i)
        if not ship.groups():
            deadtimer -= 1
            if not deadtimer:
                return
        else:
            if pygame.sprite.spritecollide(ship,enemies,True):
                ship.decrement()
        pygame.display.flip()

def initLogger():
    logging.basicConfig(level = logging.DEBUG,
                        format = '%(levelname)s | %(module)s:%(lineno)d | %(message)s',
                        stream = sys.stderr
                        # filename = "foo.log"
                        )
                        
def initialiseGame():
    global screen,empty,clock
    screen = pygame.display.set_mode(constants.SCREENRECT.size,DOUBLEBUF | FULLSCREEN)
    empty = pygame.Surface(constants.SCREENRECT.size).convert()
    #     empty = pygame.image.load("%s/whorl.png"%constants.IMG_DIR).convert()
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        logging.info('AUDIO : Audio disabled')
    if pygame.mixer.get_init():
        sprites.Romulan.sound = pygame.mixer.Sound("%s/explosion.wav"%constants.AUDIO_DIR)
        sprites.Romulan.sound.set_volume(0.1)
    else:
        sprites.Romulan.sound = False

def main():
    initLogger()
    initialiseGame()
    disturbance = createDisturbances('%s/crackles'%constants.IMG_DIR,30)
    # displayCredits(disturbance)
    if pygame.mixer.get_init():
        # pygame.mixer.music.load("%s/phoenix.ogg"%constants.AUDIO_DIR)
        # pygame.mixer.music.load("%s/megablast.ogg"%constants.AUDIO_DIR)
        # pygame.mixer.music.set_volume(0.8)
        # pygame.mixer.music.play(-1)
        pass
    screen.blit(empty,(0,0))
    startShooter(disturbance)

if __name__ == "__main__":
    sys.exit(main())


