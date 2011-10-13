import random
import pygame
import pygame.gfxdraw
from pygame.locals import *

import constants
import propulsion

import misc

class SheetSprite(pygame.sprite.Sprite):
    """
    A general class to render sprites off sheets.

    pos : Position of the sprite
    size : Size of each individual element in the sheet
    nelements : No. of elements
    sheet : The sprite sheet file
    containers : Containers to add the sprite to.
    """
    
    def __init__(self, pos, size, nelements, sheet, scale = 1, rotation = 0, colorkey = constants.BLACK):
        super(SheetSprite, self).__init__(self.containers)
        sheet = pygame.image.load(sheet).convert_alpha()
        self.images = []
        for i in range(0, size*nelements, size):
            rect = pygame.Rect((i,0, size, size))
            image = pygame.Surface(rect.size).convert()
            image.blit(sheet, (0, 0), rect)
            if colorkey is not None:
                image.set_colorkey(colorkey)
            self.images.append(pygame.transform.rotate(pygame.transform.scale(image,(scale,scale)),rotation))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.iindex = 1

    def update(self):
        self.image = self.images[int(self.iindex)]
        self.iindex += 1
        if self.iindex >= len(self.images):
            pygame.sprite.Sprite.kill(self)
    

    
class Charge(pygame.sprite.Sprite):
    def __init__(self, pos, limit, size):
        super(Charge, self).__init__(self.containers)
        x, y = size
        self.image = pygame.Surface(size).convert()
        colour = random.randrange(125, 200)
        pygame.gfxdraw.filled_circle(self.image, x/2, x/2, x/2, (colour, colour, colour))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.limit = limit
        self.counter = 10

    def update(self):
        x, y = self.rect.center
        lx, ly = self.limit
        if x > lx: x -= 2
        if x < lx: x += 2
        if y > ly: y -= 2
        if y < ly: y += 2
        self.counter -= 1
        self.rect.center = x, y
        if not self.counter:
            self.kill()


class Explosion(SheetSprite):
    def __init__(self, pos, size, typ = 1):
        if typ == 1:
            sheet = "%s/explosion-main.png"%constants.IMG_DIR
            super(Explosion, self).__init__(pos, 64, 40, sheet, scale = size * 64)
        if typ == 2:
            sheet = "%s/explosion1.png"%constants.IMG_DIR
            super(Explosion, self).__init__(pos, 64, 40, sheet, scale = size * 64)
        if typ == 3:
            sheet = "%s/explosion-mine.png"%constants.IMG_DIR
            super(Explosion, self).__init__(pos, 64, 40, sheet, scale = size * 64)
        if typ == 4:
            sheet = "%s/ship-damage.png"%constants.IMG_DIR
            super(Explosion, self).__init__(pos, 32, 12, sheet, scale = size * 32)


class Damage(SheetSprite):
    def __init__(self, pos):
        super(Damage, self).__init__(pos, 24, 16, "%s/damage.png"%constants.IMG_DIR, scale = 24)


class IonDischarge(SheetSprite):
    """Ion Canon IonDischarge"""
    def __init__(self, pos):
        super(IonDischarge, self).__init__(pos, 50, 10, "%s/ion-discharge.png"%constants.IMG_DIR, scale = 50, colorkey = False)



class Weapon(pygame.sprite.Sprite):
    def __init__(self,weapon_containers,engine = False):
        super(Weapon,self).__init__(weapon_containers)
        if not engine:
            self.engine = iter(propulsion.Engine("%s/bar.json"%constants.DATA_DIR))
        else:
            self.engine = iter(engine)
        self.coupled_update = self.update # Use the actual derived methods here
        self.decouple()
        
    def decoupled_update(self):
        x,y = self.engine.next()
        if x>1024 or y>752:
            self.kill()
        self.rect.center = (x,y)

    def couple(self):
        self.update = self.coupled_update
        self.coupled = True

    def decouple(self):
        self.update = self.decoupled_update
        self.coupled = False
        
class Laser(Weapon):
    name = "Laser"

    class LaserFire(pygame.sprite.Sprite):
        power = 10
        name = "Laser fire"
        def _laserimage(self,pos):
            image = pygame.Surface((3,768)).convert()
            image.fill((128,128,128))
            return image

        def __init__(self,canon):
            super(Laser.LaserFire,self).__init__(self.containers)
            self.image = self._laserimage(canon.rect.midtop)
            self.rect = self.image.get_rect()
            self.canon = canon
            self.rect.midbottom = self.canon.rect.midtop

        def update(self):
            self.rect.midbottom = self.canon.rect.midtop
            c = random.randrange(128,255)
            t = Rect(self.rect[0]+1,self.rect[1],self.rect[2]-1,self.rect[3])
            self.image.fill((c,c,c))

    def __init__(self,position,weapon_containers,fire_containers,engine = False):
        super(Laser,self).__init__(weapon_containers,engine = engine)
        self.LaserFire.containers = fire_containers
        if pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound("%s/laser1.wav"%constants.AUDIO_DIR)
            self.sound.set_volume(0.1)
        else:
            self.sound = False
        self.image = pygame.image.load("%s/canon1.png"%constants.IMG_DIR).convert_alpha()
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
            for i in range(10): # Blow off steam. Particle effects. :)
                c = random.randrange(0, 128)
                x,y = random.randrange(-5,5),random.randrange(-5,5)
                misc.Particle((self.rect.center[0]+x,self.rect.center[1]+y),
                              random.randrange(-2, 2), random.randrange(-1,2),0,0,random.randrange(3),
                              [((100, 100, 100), (c, c, c), 12),
                               ((c, c, c), (50, 50, 50), 24)
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
            self.temp -= 1

class SteamGun(Weapon):
    name = "Steam gun"

    class SteamJet(pygame.sprite.Sprite):
        power = 5
        name = "Steam fire"
        def __init__(self,images,gun):
            super(SteamGun.SteamJet,self).__init__()
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

    def __init__(self, position, weapon_containers, fire_containers, engine = False):
        super(SteamGun,self).__init__(weapon_containers,engine = engine)
        self.fc = fire_containers
        self.fire_images = self._getShotImages("%s/steamsprites.png"%constants.IMG_DIR)
        self.image = pygame.image.load("%s/steamgun.png"%constants.IMG_DIR).convert_alpha()
        # pygame.draw.rect(self.image,(255,0,0),self.image.get_rect(),2)
        self.rect = self.image.get_rect()
        if pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound("%s/steam1.wav"%constants.AUDIO_DIR)
            self.sound.set_volume(0.5)
        self.position = position
        self.firing = False

    def update(self):
        if self.ship.firing and not self.firing:
            # Activate weapon if we're not shooting but the ship is
            self.firing = self.SteamJet(self.fire_images, self)
            for i in self.fc:
                self.firing.add(i)
        if self.firing and not self.ship.firing:
            # Deactivate weapon if we're shooting and the ship stops
            self.firing.kill()
            self.firing = False

class IonCanon(Weapon):
    name = "Ion canon"

    class IonFire(pygame.sprite.Sprite):
        """Ion canon beam"""
        power = 20
        name = "Ion beam"
        def _laserimage(self, pos, colour, width):
            image = pygame.Surface((width,768), flags = SRCALPHA).convert()
            image.fill(colour)
            self.counter = 20
            return image

        def __init__(self, canon, width, offset, colour, volatile = False):
            super(IonCanon.IonFire, self).__init__(self.containers)
            self.canon = canon
            x, y = self.canon.rect.midtop
            x += offset[0]
            y += offset[1]
            self.image = self._laserimage((x, y), colour, width)
            self.rect = self.image.get_rect()
            self.colour = colour
            self.offset = offset
            self.rect.midbottom = x, y
            self.volatile = volatile

        def update(self):
            x, y = self.canon.rect.midtop
            x += self.offset[0]
            y += self.offset[1]
            self.rect.midbottom = x, y
            self.image.fill(self.colour)

            self.counter -= 1

            if self.volatile:
                r, g, b = (x/4 for x in self.colour)
                self.image.fill((r, g, b))
                self.colour = (r, g, b)
                if self.counter == 17:
                    self.kill()

            if not self.volatile and not self.counter:
                self.kill()



    def __init__(self, position, weapon_containers, fire_containers, engine = False):
        super(IonCanon,self).__init__(weapon_containers, engine = engine)
        self.IonFire.containers = fire_containers
        self.image = pygame.image.load("%s/ion-canon.png"%constants.IMG_DIR).convert_alpha()
        self.rect = self.image.get_rect()
        self.position = position
        self.firing = False
        self.recharging = False
        self.charge_time = 0
        self.fc = fire_containers
        self.sound_playing = False
        if pygame.mixer.get_init():
            self.sound = pygame.mixer.Sound("%s/ion-canon2.wav"%constants.AUDIO_DIR)
            self.sound.set_volume(0.1)
        else:
            self.sound = False


    def update(self):
        if self.ship.firing and not self.firing and not self.recharging:
            # Start charging weapon
            self.charge_time += 1
            x0, y0 = self.rect.midtop
            x1, y1 = self.rect.midbottom
            size = random.randrange(7, 14)
            if self.sound:
                self.sound_playing = True
                self.sound.play(0)
            Charge((x0 + random.randrange(-20,20), y0 - random.randrange(15,25)),
                   (x0, y0),
                   (size, size))
            Charge((x1 + random.randrange(-20,20), y1 + random.randrange(15,25)),
                   (x1, y1),
                   (size, size))

            if self.charge_time == 18:
                # Charged. Fire it!
                for i in range(10, 1, -2):
                    offset = i/2
                    colour = 255 - (i/10.0 * 255)
                    self.IonFire(self, i, (-offset, offset - 5), (colour, colour, colour))
                    self.IonFire(self, i, (offset, offset - 5), (colour, colour, colour))
                self.IonFire(self, 50, (0,0), (255, 255, 255), True)
                x, y = self.rect.midtop
                # IonDischarge((x, y-10))
                # Explosion(self.rect.midtop, 2,  True)
                self.charge_time = -50
                self.firing = False
                self.recharging = True
                
        if self.charge_time < 0:
            # Recharge
            self.charge_time += 1

        if self.charge_time == 0:
            # Recharged
            self.recharging = False

        if not self.ship.firing and not self.recharging:
            # Charging interrupted
            self.charge_time = 0
            if self.sound_playing:
                self.sound.stop()
        


class MineGun(Weapon):
    name = "Mine gun"

    class Mine(pygame.sprite.Sprite):
        power = 10
        name = "Mine"
        def __init__(self, images, cannon, fc):
            super(MineGun.Mine,self).__init__(*self.containers)
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
                raise

        def kill(self):
            f = Explosion(self.rect.center, 3, 3)
            f.add(*self.fc)
            f.power = 50
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

    def __init__(self,position,weapon_containers,fire_containers,engine = False):
        super(MineGun,self).__init__(weapon_containers,engine = engine)
        self.Mine.containers = fire_containers
        self.image = pygame.image.load("%s/minegun.png"%constants.IMG_DIR).convert_alpha()
        self.mine_images = self._getMineImages("%s/minesheet.png"%constants.IMG_DIR,-1)
        self.rect = self.image.get_rect()
        self.position = position
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
