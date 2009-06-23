import random
import pygame
import logging
from pygame.locals import *

import constants
import propulsion
    

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, vx, vy, ax, ay, size, colorstructure):
        pygame.sprite.Sprite.__init__(self, self.containers)
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
            
class Explosion(pygame.sprite.Sprite):
    def _getExplosionImages(self,spritefile,scale,size=48,colorkey = constants.BLACK):
        "Extract an array of images from the given sprite sheet."
        sheet = pygame.image.load(spritefile).convert_alpha()
        images = []
        rotation = random.randrange(0,180)
        for i in range(0,768,size):
            rect = pygame.Rect((i,0,size,size))
            image = pygame.Surface(rect.size).convert()
            image.blit(sheet, (0, 0), rect)
            if colorkey is not None:
                image.set_colorkey(colorkey)
            images.append(pygame.transform.rotate(pygame.transform.scale(image,(scale,scale)),rotation))
        return images
    def __init__(self,pos,size,fr,colour = False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        if colour:
            self.images = self._getExplosionImages("%s/colour-explosion.png"%constants.IMG_DIR,size*48)
        else:
            self.images = self._getExplosionImages("%s/explosion.png"%constants.IMG_DIR,size*48)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.iindex = 1
        self.rate = fr
    def update(self):
        self.image = self.images[int(self.iindex)]
        self.iindex += self.rate
        if self.iindex >= len(self.images):
            pygame.sprite.Sprite.kill(self)

class Romulan(pygame.sprite.Sprite):
    def __init__(self,ship,egroup,path="%s/bar.path"%constants.DATA_DIR):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("%s/enemy1.png"%constants.IMG_DIR).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        x,y = random.randrange(1024),0
        self.rect.center = (x,y)
        self.vx = random.randrange(1,20)
        self.vy = random.randrange(1,20)
        self.ship = ship
        self.alive = True
        self.direction_counter = 0
        self.group = egroup
        ship_pos = lambda : self.ship.rect.center
        self.engine = iter(propulsion.Engine("%s/bar.path"%constants.DATA_DIR,ship_pos))

    def update(self):
        x,y = self.engine.next()
        if x>1024 or y>752:
            pygame.sprite.Sprite.kill(self)
        self.rect.center = (x,y)

    def kill(self):
        Explosion(self.rect.center,2,2)
        self.ship.score += 5
#         for i in range(20):
#             c = random.randrange(0, 128)
#             Particle(self.rect.center, random.randrange(-3, 3), random.randrange(-3, 0), random.randrange(-2,2), random.randrange(-2,2), random.randrange(4),
#                      [((c, 0, 0), (c, 0, 0), 3),
#                       ((128, 128, 0), (0, 0, 0), 7)
#                       ])

        if self.sound:
            self.sound.play(0)
        pygame.sprite.Sprite.kill(self)
        
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

class ShipSprite(pygame.sprite.Sprite):
    def __init__(self,image,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image).convert_alpha()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.firing = False # Are we firing?
        self.energy = 100 # Energy
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
    def decrement(self):
        self.energy -= 10
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
#         pygame.draw.rect(self.image,(255,0,255),self.image.get_rect(),2)#bounding_rect,2)
        if weapon.position == constants.TOP:
            weapon.rect.bottom = bounding_rect.top
        elif weapon.position == constants.BOTTOM:
            weapon.rect.top = bounding_rect.bottom
        elif weapon.position == constants.LEFT:
            weapon.rect.right = bounding_rect.left - 10
        elif weapon.position == constants.RIGHT:
            weapon.rect.left = bounding_rect.right + 10
        logging.debug("ATTACH : Weapon attached at %s with center %s"%(str(weapon.rect),str(weapon.rect.center)))
        if weapon.coupled:
            self.weapons.append(weapon)
        weapon.offset = (weapon.rect.center[0] - self.rect.center[0] ,
                         weapon.rect.center[1] - self.rect.center[1] )
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        x0,y0,x1,y1 = self.rect
        for i in self.weapons:
            i.kill()
        for i in range(1,15):
            Explosion((random.randrange(x0,x0+x1),random.randrange(y0,y0+y1)),random.randrange(1,5),1,True)


class StarSprite(pygame.sprite.Sprite):
    def __init__(self,position,brightness,velocity,min_velocity,acceleration):
        pygame.sprite.Sprite.__init__(self)
        self.brightness = brightness
        color = (255*brightness,255*brightness,255*brightness)
        self.image = pygame.Surface((2,2)).convert()
        pygame.draw.circle(self.image,color,(0,0),1,0)
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

            
# ---------------------- Weapons -----------------------


class Weapon(pygame.sprite.Sprite):
    def __init__(self,weapon_containers):
        pygame.sprite.Sprite.__init__(self, *weapon_containers)
        
    def update(self):
        raise NotImplemented()

    
    

class Laser(Weapon):
    name = "Laser"
    class LaserFire(pygame.sprite.Sprite):
        def _laserimage(self,pos):
            image = pygame.Surface((3,768)).convert()
            image.fill((128,128,128))
            return image
        def __init__(self,canon):
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.image = self._laserimage(canon.rect.midtop)
            self.rect = self.image.get_rect()
            self.canon = canon
            self.rect.midbottom = self.canon.rect.midtop
        def update(self):
            self.rect.midbottom = self.canon.rect.midtop
            c = random.randrange(128,255)
            t = Rect(self.rect[0]+1,self.rect[1],self.rect[2]-1,self.rect[3])
            #             pygame.draw.rect(self.image,(c,c,0),self.rect,0)
            self.image.fill((c,c,c))
    def __init__(self,position,weapon_containers,fire_containers):
        Weapon.__init__(self, weapon_containers)
        self.LaserFire.containers = fire_containers
        if pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound("%s/laser1.wav"%constants.AUDIO_DIR)
            self.sound.set_volume(0.1)
        else:
            self.sound = False
        self.image = pygame.image.load("%s/canon1.png"%constants.IMG_DIR).convert_alpha()
#         pygame.draw.rect(self.image,(255,0,0),self.image.get_rect(),2)
        self.coupled = True
        self.cold = self.image
        self.hot = pygame.image.load("%s/canon1-hot.png"%constants.IMG_DIR).convert_alpha()
        self.rect = self.image.get_rect()
        self.position = position
        self.fire = False
        self.temp = 0
        self.overheat = False
        self.maxtemp = random.randrange(100,200)
    def update(self):
        if self.ship.firing and not self.fire and not self.overheat:
            # Start firing if the ship is firing and we're not and we're cool enough
            self.fire = self.LaserFire(self)
            if self.sound:
                self.sound.play(-1)
        if not self.ship.firing and self.fire:
            # Stop firing if the ship has stopped and we still are
            if self.sound:
                self.sound.stop()
            self.fire.kill()
            self.fire = False
        if self.fire:
            # If we are firing, increase temperature.
            self.temp += 2
        if self.temp >= self.maxtemp:
            # If we overheat, mark it so.
            self.overheat = True
            self.image = self.hot
        if self.overheat:
            # If overheated, turn off laser
            if self.fire:
                if self.sound:
                    self.sound.stop()
                self.fire.kill()
                self.fire = False
            for i in range(10):
                c = random.randrange(0, 128)
                x,y = random.randrange(-5,5),random.randrange(-5,5)
                Particle((self.rect.center[0]+x,self.rect.center[1]+y),
                         random.randrange(-2, 2), random.randrange(-1,2),0,0,random.randrange(3),
                         [((100, 100, 100), (c, c, c), 6),
                          ((c, c, c), (50, 50, 50), 12)
                          ])
            if self.image == self.hot:
                self.image = self.cold
            else:
                self.image = self.hot
        if self.temp <= 0:
            # If cooled down, unset overheat
            self.overheat = False
            self.image = self.cold
        if not self.fire and self.temp > 0:
            # Cool down to minimum if not firing
            self.temp -= 3

class SteamGun(pygame.sprite.Sprite):
    name = "Steam gun"
    class SteamJet(pygame.sprite.Sprite):
        def __init__(self,images,gun):
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.gun = gun
            self.images = images
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.midbottom = self.gun.rect.midtop
            self.index = 0
        def update(self):
            self.index += 1
            self.index %= len(self.images) - 1
            try:
                self.image = self.images[int(self.index)]
            except IndexError:
                print self.index
                raise
            self.rect = self.image.get_rect()
            self.rect.midbottom = self.gun.rect.midtop
    def _getShotImages(self,spritefile,colorkey = constants.BLACK):
        "Extract an array of images from the given sprite sheet."
        sheet = pygame.image.load(spritefile).convert_alpha()
        images = []
        for i in range(0,705,78):
            rect = pygame.Rect((i,0,68,255))
            image = pygame.Surface(rect.size).convert_alpha()
            image.blit(sheet, (0, 0), rect)
            if colorkey is not None:
                image.set_colorkey(colorkey)
            images.append(image)
        return images
    def __init__(self,position,weapon_containers,fire_containers):
        pygame.sprite.Sprite.__init__(self, *weapon_containers)
        self.SteamJet.containers = fire_containers
        self.fc = fire_containers
        self.fire_images = self._getShotImages("%s/steamsprites.png"%constants.IMG_DIR)
        self.image = pygame.image.load("%s/steamgun.png"%constants.IMG_DIR).convert_alpha()
#         pygame.draw.rect(self.image,(255,0,0),self.image.get_rect(),2)
        self.rect = self.image.get_rect()
        if pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound("%s/steam1.wav"%constants.AUDIO_DIR)
            self.sound.set_volume(0.5)
        self.position = position
        self.coupled = True
        self.firing = False
    def update(self):
        if self.ship.firing and not self.firing:
            # Activate weapon if we're not shooting but the ship is
#             for i in range(50):
#                 c = random.randrange(0, 128)
#                 x = random.randrange(-5,5)
#                 t=Particle((self.rect.midtop[0]+x,self.rect.midtop[1]),
#                            random.randrange(-4, 4), random.randrange(-30,0),0,0,random.randrange(3),
#                            [((100, 100, 100), (c, c, c), 4),
#                             ((c, c, c), (50, 50, 50), 2)
#                             ])
#                 t.add(*self.fc)
                self.firing = self.SteamJet(self.fire_images,self)
        if self.firing and not self.ship.firing:
            # Deactivate weapon if we're shooting and the ship stops
            self.firing.kill()
            self.firing = False


class MineGun(pygame.sprite.Sprite):
    name = "Mine gun"
    class Mine(pygame.sprite.Sprite):
        def __init__(self,images,cannon,fc):
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.images = images
            self.image = self.images[0]
            self.rect = self.image.get_rect()
            self.rect.midbottom = cannon.rect.midtop
            self.index = 0
            self.moving = 20
            self.lifetime = random.randrange(30)
            self.fc = fc
        def update(self):
            x,y = self.rect.center
            if self.moving:
                y-=10
                self.moving-=1
            else:
                self.lifetime-=1
            self.rect.center = (x,y)
            self.index += 1
            self.index %= len(self.images) - 1
            try:
                self.image = self.images[int(self.index)]
            except IndexError:
                print self.index
                raise
        def kill(self):
            f = Explosion(self.rect.center,3,1)
            f.add(*self.fc)
            pygame.sprite.Sprite.kill(self)
    def _getMineImages(self,spritefile,colorkey = constants.BLUE):
        "Extract an array of images from the given sprite sheet."
        sheet = pygame.image.load(spritefile).convert()
        images = []
        for i in range(0,911,46):
            rect = pygame.Rect((i,0,30,30))
            image = pygame.Surface(rect.size).convert()
            image.blit(sheet, (0, 0), rect)
            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey)
            images.append(image)
        return images            
    def __init__(self,position,weapon_containers,fire_containers):
        pygame.sprite.Sprite.__init__(self, *weapon_containers)
        self.Mine.containers = weapon_containers
        self.image = pygame.image.load("%s/minegun.png"%constants.IMG_DIR).convert_alpha()
        self.mine_images = self._getMineImages("%s/minesheet.png"%constants.IMG_DIR,-1)
        self.rect = self.image.get_rect()
        self.position = position
        self.coupled = True
        self.firing = False
        self.fc = fire_containers
    def update(self):
        if not self.firing:
            if self.ship.firing:
                self.firing = self.Mine(self.mine_images,self,self.fc)
        else:
            if self.firing.lifetime == 0:
                self.firing.kill()
                self.firing = False

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

            
    
    
