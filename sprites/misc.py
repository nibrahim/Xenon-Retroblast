import random

import pygame

import constants

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, vx, vy, ax, ay, size, colorstructure):
        super(Particle,self).__init__(self.containers)
        self.vx, self.vy, self.ax, self.ay = vx, vy, ax, ay
        self.images = []
        for x in colorstructure:
            start, end, duration = x
            startr, startg, startb = start
            endr, endg, endb = end
            def f(s, e, t):
                val = s + int((e - s)*(t/float(duration)))
                return val
            for t in range(duration):
                image = pygame.Surface((size, size)).convert()
                image.fill((f(startr, endr, t),
                            f(startg, endg, t),
                            f(startb, endb, t)))
                self.images.append(image)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
    def update(self):
        self.rect.move_ip(self.vx, self.vy)
        self.vx = self.vx + self.ax
        self.vy = self.vy + self.ay
        if not self.images:
            self.kill()
        else:
            self.image = self.images.pop(0)
            
class EnergyBar(pygame.sprite.Sprite):
    def __init__(self,ship):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.max_width = 500
        self.image = pygame.Surface((500,10)).convert_alpha()
        self.ship = ship
        self.width = int((self.ship.energy/100) * self.max_width) 
        pygame.draw.rect(self.image, (0,0,0), (1,1,self.width,8,),0)
        pygame.draw.rect(self.image, (150,150,150), (1,1,self.width,8,),0)
        self.rect = self.image.get_rect()
        self.rect.topleft = (12,748)
        self.last_energy = 0
        self.glowcounter = 150

    def update(self):
        self.width = int((self.ship.energy/100.0) * self.max_width)
        self.image.fill((0,0,0,0))
        #         pygame.draw.rect(self.image, (0,0,0,0), (0,0,self.max_width,10,),0)
        pygame.draw.rect(self.image, (150,150,150), (1,1,self.width,8,),0)
        if self.ship.energy != self.last_energy:
            self.glowcounter = 0
        if self.glowcounter != 150:
            self.glowcounter += 10
            pygame.draw.rect(self.image, (self.glowcounter,self.glowcounter,self.glowcounter), (1,1,self.width,8,),0)
        else:
            pygame.draw.rect(self.image, (150,150,150), (1,1,self.width,8,),0)
        self.last_energy = self.ship.energy

class ScoreBar(pygame.sprite.Sprite):
    def __init__(self,ship):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.Font('%s/jGara2.ttf'%constants.DATA_DIR,20)
        self.image = pygame.Surface((200,25)).convert_alpha()
        self.image.fill((100,100,100,0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (550,740)
        self.ship = ship
        score = self.font.render("score  %010d"%self.ship.score,True,(20,20,20))
        self.image.fill((100,100,100,0))
        self.image.blit(score,(0,0))
    def update(self):
        score = self.font.render("score  %010d"%self.ship.score,True,(20,20,20))
        self.image.fill((100,100,100,0))
        self.image.blit(score,(0,0))
                        
class StatusPanel(pygame.sprite.Sprite):
    def __init__(self,ship):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.image.load("%s/cpanel.png"%constants.IMG_DIR).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (512,752,)
        EnergyBar.containers = self.containers
        self.energy_bar = EnergyBar(ship)
        ScoreBar.containers = self.containers
        self.score_bar = ScoreBar(ship)

            
class DisturbanceSprite(pygame.sprite.Sprite):
    def __init__(self,image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image).convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect()

    def update(self):
        dist_pos = (random.randrange(1024),
                    random.randrange(752))
        dist_rot = random.randrange(180)
        self.image = pygame.transform.rotate(self.image, dist_rot).convert_alpha()
        self.rect.center = dist_pos

class CrackSprite(pygame.sprite.Sprite):
    def __init__(self,image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image).convert_alpha()
        self.orig_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (0,384)
        self.visible = False

    def update(self):
        if self.visible:
            self.visible = False
            crack = 0 + random.randrange(1024)
            self.rect.center = (crack,384)
        else:
            self.visible = True

class StarSprite(pygame.sprite.Sprite):
    def __init__(self, position, brightness, velocity, min_velocity, acceleration):
        pygame.sprite.Sprite.__init__(self)
        self.brightness = brightness
        color = (255*brightness,255*brightness,255*brightness)
        self.image = pygame.Surface((3,3)).convert()
        pygame.draw.circle(self.image,color,(0,0),3,0)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.acceleration = acceleration
        self.velocity = velocity
        self.min_velocity = min_velocity

    def update(self):
        if self.velocity != 0:
            c = random.randrange(0,int(255*self.brightness))
            pygame.draw.circle(self.image,(c,c,c),(0,0),1,0)
        if self.velocity <= self.min_velocity:
            self.velocity = self.min_velocity
        else:
            self.velocity = self.velocity + self.acceleration
        self.rect.center = (self.rect.center[0],self.rect.center[1]+self.velocity)
        if self.rect.center[1] >= 768:
            self.rect.center = ((random.randrange(1024),0))
