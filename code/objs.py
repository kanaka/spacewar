#!/usr/bin/env python

from pygame import transform, font, Rect
from pygame.locals import *
import var, gfx, snd, agents, ai
from math import *
from random import randint, random 

# *** TODO: make calculations use arena.left and arena.top 
#       instead of assuming 0,0
if __name__ != '__main__': 
    # We were imported normally from gameplay.py
    arena = var.arena
else:
    # We are running objs.py standalone
    arena = Rect(0, 0, 800, 600)

fps_list = [30] * var.frames_per_sec

# Object lists:
#   - vapors for smoke and other "vapors"
#   - low for hard objects: ship and sun
#   - high for the fire and explosions
#   - virtual for help text, and non-colliding objects
#   - pend for non-rendered objects still being tracked
#   - list: rendered lists in rendering order
vapors, low, high, virtual, pend = [], [], [], [], []
list = [vapors, low, high, virtual]

images = {}

# Load all the images
def load_game_resources():
    global images

    # Ship images are 3D arrays [shipnum][phase][direction]
    for name,files in (
        ('ship',   ((0, "ship1-up.png"), (1, "ship2-up.png"),
                    (2, "ship3-up.png"), (3, "ship4-up.png"))),
        ('reverse',((0, "ship1-up-boost1.png"), (1, "ship2-up-boost1.png"),
                    (2, "ship3-up-boost1.png"), (3, "ship4-up-boost1.png"))),
        ('turbo',  ((0, "ship1-up-boost2.png"), (1, "ship2-up-boost2.png"),
                    (2, "ship3-up-boost2.png"), (3, "ship4-up-boost2.png")))):
        images[name]   = [[],[],[],[]]
        for ship, file in files:
            img = gfx.load(file)
            #img=transform.scale(img,(img.get_width()*2/3,img.get_height()*2/3))
            img_anim = gfx.animstrip(img)
            phases = len(img_anim)
            for p in range(phases):
                target = images[name]
                target[ship].append([])
                for i in range(0, 361, 360/var.compass_dirs):
                    target[ship][p].append(transform.rotate(img_anim[p],i))

    images['shield']  = []
    img = gfx.load('bonus-shield.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    alphas = [160,145,130,115,100,85,70,55,40,55,70,85,100,115,130,145]
    for p in range(len(alphas)):
        images['shield'].append([])
        for img in img_anim:
            newimg = img.convert()
            newimg.set_alpha(alphas[p], RLEACCEL)
            images['shield'][p].append(newimg)

    images['bullet']  = []
    img = gfx.load('bonus-bullet.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    alphas = [255,239,223,207,191,175,159,143,127,111,95,79,63]
    for p in range(len(img_anim)):
    #for p in range(len(alphas)):
        images['bullet'].append([])
        for alpha in alphas:
            newimg = img_anim[p].convert()
            newimg.set_alpha(alpha, RLEACCEL)
            images['bullet'][p].append(newimg)

    images['smoke'] = []
    img = gfx.load('smoke.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    if gfx.surface.get_bytesize()>1: #16 or 32bit
        i = 1
        for img in img_anim:
            img.set_alpha((1.8-log(i))*40, RLEACCEL)
            i += 1
    phases = len(img_anim)
    for p in range(phases):
        images['smoke'].append([])
        images['smoke'][p].append(img_anim[p])

    images['pop'] = []
    img = gfx.load('popshot.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img, 18)
    phases = len(img_anim)
    for p in range(phases):
        images['pop'].append([])
        images['pop'][p].append(img_anim[p])

    # Images with no special needs
    for name,file in (('explosion', 'explosion.png'), 
                      ('tele', 'ship-teleport.png'), 
                      ('fire', 'fire.png'),
                      ('fire2', 'fire2.png'),
                      ('box', 'boxes.png'),
                      ('spike', 'spikeball.png'),
                      ('asteroid', 'asteroid.png'),
                      ('bobble', 'powerup.png')):
        images[name] = []
        img = gfx.load(file)
        #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
        img_anim = gfx.animstrip(img)
        phases = len(img_anim)
        for p in range(phases):
            images[name].append([])
            images[name][p].append(img_anim[p])


# All game play objects are a subclass of Mass
#   - Mass itself cannot be instantiated because
#     image_name must be defined
class Mass:
    phase_rate = 0.0
    phase_death = 0
    radius = 0
    taxonomy = ()

    def __init__(self, x, y, vx=0.0, vy=0.0, mass=1.0, dir=0, imgs=''):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.dir = dir*var.compass_dirs/360

        if imgs:
            self.imgs = imgs
        else:
            self.imgs = images[self.image_name]
        self.phases = len(self.imgs)
        self.phase = 0.0
        self.ticks_to_live = -1
        self.width = self.imgs[0][self.dir].get_width()
        self.height = self.imgs[0][self.dir].get_height()
        self.rect = Rect(int(self.x)-self.width/2, int(self.y)-self.height/2, 
                     self.width, self.height)
        self.lastrect = self.rect
        self.dead = 0

    def tick(self, speedadjust):
        self.x = (self.x + self.vx) % arena.right
        self.y = (self.y + self.vy) % arena.bottom
        
        self.rect = Rect(int(self.x)-self.width/2, int(self.y)-self.height/2, 
                     self.width, self.height)
        if self.phase_death:
            self.phase = self.phase + self.phase_rate
            if not self.dead and self.phase >= self.phases:
                self.dead = 1
        else:
            self.phase = (self.phase+self.phase_rate)%self.phases
        if self.ticks_to_live > 0:
            self.ticks_to_live = self.ticks_to_live - 1
            if not self.dead and self.ticks_to_live == 0:
                self.dead = 1

    def draw(self):
        phase = int(self.phase)
        dir = self.dir
        gfx.surface.blit(self.imgs[phase][dir], self.rect)
        gfx.dirty2(self.rect, self.lastrect)
        self.lastrect = self.rect

    def erase(self):
        gfx.surface.fill(0, self.rect)
        if self.dead:
            gfx.dirty2(self.rect, self.lastrect)

    def distance(self, other_mass):
        xdist = self.x - other_mass.x
        ydist = self.y - other_mass.y
        return sqrt(xdist*xdist + ydist*ydist)

    # Return radian direction to other mass
    def direction(self, other_mass):
        xdist = self.x - other_mass.x
        ydist = self.y - other_mass.y
        if ydist == 0:
            ydist = 0.00000000000001
        rads = atan(xdist/ydist)
        # Adjust atan depending on direction quadrant
        # upper left stays the same
        # upper right
        if xdist < 0 and ydist > 0:
            rads = rads + 2.0*pi
        # lower left and lower right
        if ydist < 0:
            rads = rads + pi
        return rads

    # Return relative radian direction to other mass
    def rel_direction(self, other_mass):
        abs_rads = Mass.direction(self, other_mass)
        self_rads = self.dir*2*pi/var.compass_dirs
        rel_rads = (abs_rads-self_rads) % (2*pi)
        if rel_rads > pi: 
            rel_rads -= 2*pi
        elif rel_rads < -pi: 
            rel_rads += 2*pi
        return rel_rads

    def gravitate(self, other_mass):
        dist = self.distance(other_mass)
        if dist < 4.0: dist = 4.0
        force = other_mass.mass/(dist*dist)
        
        rads = self.direction(other_mass)
        self.vx = self.vx - sin(rads)*force*var.gravity_const
        self.vy = self.vy - cos(rads)*force*var.gravity_const

    def clearance(self, other_mass):
        # *** TODO: this needs to account for motion
        return self.distance(other_mass) - (self.radius + other_mass.radius)

    def check_spot(self):
        for object in low + high:
            if object is not self:
                if self.clearance(object) < var.start_clearance:
                    return 0
        return 1

    def find_spot(self):
        new_dir = randint(0, var.compass_dirs-1)
        while 1:
            self.x = randint(50, arena.right-50)
            self.y = randint(50, arena.bottom-50)
            if self.check_spot(): return
            ###found_spot = 1
            ###for object in low + high:
            ###    if object is not self:
            ###        if self.clearance(object) < var.start_clearance:
            ###            found_spot = 0
        
    def hit_by(self, other_mass):
        pass


class Smoke(Mass):
    image_name = 'smoke'
    taxonomy = ()
    radius = 5.0

    def __init__(self, x, y, vx, vy):
        Mass.__init__(self, x, y, vx, vy, mass=0.0)
        self.ticks_to_live = randint(12, 20)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)
        self.phase = int(self.phases * (self.ticks_to_live / 20.0))

class Fire(Mass):
    image_name = 'fire'
    taxonomy = ('fire', 'damage', 'significant')
    radius = 8.0
    phase_rate = 0.20
    damage = var.fire_damage

    def __init__(self, x, y, vx, vy, owner):
        Mass.__init__(self, x, y, vx, vy, mass=0.0)
        self.ticks_to_live = var.fire_life
        self.owner = owner
        self.dead_by_hit = 0

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            self.dead_by_hit = 1
            self.dead = 1

class SuperFire(Fire):
    image_name = 'fire2'
    taxonomy = ('fire', 'damage', 'significant') 
    radius = 8.0
    phase_rate = 0.3
    damage = int(var.fire_damage * 1.5)

    def __init__(self, x, y, vx, vy, owner):
        Mass.__init__(self, x, y, vx, vy, mass=0.0)
        self.ticks_to_live = int(var.fire_life * 1.5)
        self.owner = owner
        self.dead_by_hit = 0

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            self.dead_by_hit = 1
            self.dead = 1

class Pop(Mass):
    image_name = 'pop'
    radius = 8.0
    phase_rate = 0.2
    phase_death = 1

    def __init__(self, x, y, vx, vy):
        Mass.__init__(self, x, y, vx, vy, mass=0.0)

    def gravitate(self, other_mass):
        # No effect from gravity
        pass

class Explosion(Mass):
    image_name = 'explosion'
    taxonomy = ('explosion', 'damage', 'significant') 
    radius = 18.0
    phase_rate = 0.5
    phase_death = 1    

    def __init__(self, x, y, vx, vy):
        Mass.__init__(self, x, y, vx, vy, mass=0.0)
        snd.play('explode', 1.0, self.rect.centerx)

    def gravitate(self, other_mass):
        # No effect from gravity
        pass

class Sun(Mass):
    image_name = 'box'
    taxonomy = ('sun', 'hard', 'significant') 
    radius = 10.0
    phase_rate = 0.4

    def __init__(self, x=arena.centerx, y=arena.centery):
        Mass.__init__(self, x, y, vx=0, vy=0, mass=10.0)

    def draw(self):
        if var.sun != 3:
            Mass.draw(self)

    def gravitate(self, other_mass):
        if var.sun >= 2:
            Mass.gravitate(self)

# Spike and Asteroid superclass. Don't instantiate
class Hard(Mass):
    def __init__(self, x, y, vx, vy):
        Mass.__init__(self, x, y, vx, vy, mass=4.0)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)

        if self.pending_frames > 0:
            if self.pending_frames == var.frames_per_sec / 2:
                if self.snd1: snd.play('flop', 1.0, self.rect.centerx)
            self.pending_frames = self.pending_frames -1
            # Make the spike appear
            if self.pending_frames <= 0:
                self.dead = 0
                self.find_spot()
                self.vx = (random()-0.5) * 4
                self.vy = (random()-0.5) * 4
                if self.snd2: snd.play('klank2', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            if other_mass.__class__ in (Sun, Spike, Asteroid):
                self.dead = 1
                explosion = Explosion(self.x, self.y, self.vx, self.vy)
                explosion.mass = self.mass
                high[0:0] = [explosion]
                # gameplay.runobjects() will remove spike


class Spike(Hard):
    image_name = 'spike'
    taxonomy = ('spike', 'hard', 'significant') 
    radius = 10.0
    phase_rate = 0.4
    snd1 = 'flop'
    snd2 = 'klank2'

class Asteroid(Hard):
    image_name = 'asteroid'
    taxonomy = ('asteroid', 'hard', 'significant') 
    radius = 15.0
    phase_rate = 0.2
    snd1 = ''
    snd2 = ''

    def find_spot(self):
        new_dir = randint(0, var.compass_dirs-1)
        edge = randint(0, 1) # what edge
        while 1:
            if edge == 0:
                if edge == 0: self.x = 0
                self.y = randint(0, arena.bottom-1)
            else:
                if edge == 2: self.y = 0
                self.x = randint(0, arena.right-1)
            if self.check_spot(): return
        

# Superclass for "Bobbles". Don't instantiate
class Bobble(Mass):
    def __init__(self, x, y, vx, vy):
        Mass.__init__(self, x, y, vx, vy, mass=0.5)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)

        if self.pending_frames > 0:
            self.pending_frames = self.pending_frames -1
            # Make the bobble appear
            if self.pending_frames <= 0:
                self.dead = 0
                self.find_spot()
                self.vx = (random()-0.5) * 6
                self.vy = (random()-0.5) * 6
                snd.play('chimeout', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            self.dead = 1
            vx = self.vx / 5
            vy = self.vy / 5
            if not other_mass.__class__ == Ship:
                snd.play('boxhit', 1.0, other_mass.rect.centerx)
                vapors.append(Pop(other_mass.x, other_mass.y, vx, vy))

class ShieldBobble(Bobble):
    image_name = 'bobble'
    taxonomy = ('shield', 'powerup', 'significant') 
    radius = 10.0
    phase_rate = 0.2

class BulletBobble(Bobble):
    image_name = 'bobble'
    taxonomy = ('bullet', 'powerup', 'significant') 
    radius = 10.0
    phase_rate = 0.1

class Tele(Mass):
    image_name = 'tele'
    radius = 11.0
    phase_rate = 0.6
    phase_death = 1

class Ship(Mass):
    BASE_COLOR = ((75, 0, 0), (0, 75, 0), (0, 0, 75), (75, 75, 0))

    image_name = 'ship'
    taxonomy = ('ship', 'damage', 'significant') 
    radius = 11.0
    phase_rate = 1.0

    def __init__(self, shipnum, x=50.0, y=50.0, dir=0):
        self.shipnum=shipnum
        self.player = None
        self.mycolor = self.BASE_COLOR[shipnum]
        self.max_health = 100.0
        self.max_shield = 100.0
        self.max_bullet = var.bbobble_charge
        self.start(x, y, dir=dir)

    def start(self, x=50.0, y=50.0, vx=0, vy=0, mass=1.0, dir=0):
        imgs = images['ship'][self.shipnum]
        Mass.__init__(self, x, y, vx, vy, mass, dir, imgs)
     
        self.health = 100.0
        self.shield = 0.0
        self.shield_phase = 0
        self.shield_phases = len(images['shield'])
        self.bullet = 0.0
        self.bullet_phase = 0
        self.bullet_phases = len(images['bullet'])
        self.thrust = 0
        self.turn = 0
        self.fire_delay = 0
        self.smoke_rate = 0.0
        self.pending_frames = 0
       
    def tick(self, speedadjust):
        # Ship is dead, waiting to re-appear 
        if self.pending_frames > 0:
            if self.pending_frames == var.frames_per_sec / 2:
                snd.play('startlife', 1.0, self.rect.centerx)
            self.pending_frames = self.pending_frames -1
            self.health = (self.max_health * 
                (var.death_time * var.frames_per_sec - self.pending_frames) / 
                (var.death_time * var.frames_per_sec))
            # Make the ship appear again
            if self.pending_frames <= 0:
                self.dead = 0
                dir = randint(0, 359)
                self.start(dir=dir)
                self.find_spot()
            # Since we're dead, no more to do
            return

        if self.thrust:
            # Calculate thrust acceleration
            rads = radians(self.dir*(360/var.compass_dirs))
            self.vx = self.vx - sin(rads)*self.thrust
            self.vy = self.vy - cos(rads)*self.thrust
            # Smoke trails, don't overload frame rate
            if (not var.ai_train and 
                    var.graphics > 0 and 
                    gfx.surface.get_bytesize()>1):
                if self.thrust > 0: rads = (rads+pi) % (2.0*pi)
                fps = min(fps_list)
                if fps > 40.0:
                    self.smoke_rate += 2.0
                if fps > 35.0:
                    self.smoke_rate += 1.0
                elif fps > 30.0:
                    self.smoke_rate += 0.4
                elif fps > 25.0:
                    self.smoke_rate += 0.2
                elif fps > 20.0:
                    self.smoke_rate += 0.1
                else:
                    self.smoke_rate += 0.05
                for i in range(int(self.smoke_rate)):
                    self.smoke_rate -= 1.0
                    x = (self.x - sin(rads)*(self.radius+5) + randint(-7,7))
                    y = (self.y - cos(rads)*(self.radius+5) + randint(-7,7))
                    vx = (self.vx - sin(rads)*var.smoke_speed + random()/3)
                    vy = (self.vy - cos(rads)*var.smoke_speed + random()/3)
                    vapors.append(Smoke(x, y, vx, vy))

        # Perform turns
        if self.turn:
            self.dir = (self.dir+self.turn)%var.compass_dirs
            self.width = self.imgs[0][self.dir].get_width()
            self.height = self.imgs[0][self.dir].get_height()

        # Perform standard movement
        Mass.tick(self, speedadjust)
        
        # Shield and health housekeeping
        self.shield_phase = (self.shield_phase+0.4)%self.shield_phases
        self.bullet_phase = (self.bullet_phase+0.4)%self.bullet_phases
        if self.bullet > 0:
            self.bullet -= 1
        if self.health < self.max_health:
            self.health = min (self.max_health, 
                               self.health + var.heal_rate/100.0)

        # Slow down firing rate
        if self.fire_delay > 0:
            self.fire_delay = self.fire_delay -1

    def draw(self):
        Mass.draw(self)
        if self.bullet:
            levels = len(images['bullet'][0])-1
            level = levels - int((levels+0.99) * self.bullet / self.max_bullet)
            phase = int(self.bullet_phase)
            img = images['bullet'][phase][level]
            cx = int(self.x)-(img.get_rect()[2] /2)
            cy = int(self.y)-(img.get_rect()[3] /2)
            gfx.surface.blit(img, (cx, cy))
        if self.shield:
            levels = len(images['shield'][0])-1
            level = levels - int((levels+0.99) * self.shield / self.max_shield)
            phase = int(self.shield_phase)
            img = images['shield'][phase][level]
            cx = int(self.x)-(img.get_rect()[2] /2)
            cy = int(self.y)-(img.get_rect()[3] /2)
            gfx.surface.blit(img, (cx, cy))

    def cmd_left(self):
        self.turn = 1
    
    def cmd_right(self):
        self.turn = -1
    
    def cmd_turn_off(self):
        self.turn = 0
    
    def cmd_reverse(self):
        if not self.thrust == var.reverse_power:
            self.thrust = var.reverse_power
            self.imgs = images['reverse'][self.shipnum]
            self.phases = len(self.imgs)
            self.phase = 0.0
    
    def cmd_turbo(self):
        if not self.thrust == var.thrust_power:
            self.thrust = var.thrust_power
            self.imgs = images['turbo'][self.shipnum]
            self.phases = len(self.imgs)
            self.phase = 0.0
    
    def cmd_thrust_off(self):
        if self.thrust:
            self.thrust = 0
            self.imgs = images['ship'][self.shipnum]
            self.phases = len(self.imgs)
            self.phase = 0.0

    def cmd_fire(self):
        if not self.fire_delay and not self.pending_frames:
            rads = radians(self.dir*(360/var.compass_dirs))
            vx = self.vx - sin(rads)*var.fire_speed
            vy = self.vy - cos(rads)*var.fire_speed
            x = self.x - sin(rads)*(self.radius+Fire.radius+1)
            y = self.y - cos(rads)*(self.radius+Fire.radius+1)
            if self.bullet:
                self.fire_delay = int(var.fire_delay_frames * 0.75)
                vx *= 1.2
                vy *= 1.2
                fire = SuperFire(x, y, vx, vy, self)
            else:
                self.fire_delay = var.fire_delay_frames
                fire = Fire(x, y, vx, vy, self)
            high.append(fire)
            snd.play('select_choose', 1.0, self.rect.centerx)

    def damage(self, damage):
        self.shield -= damage
        if self.shield < 0.0:
            self.health += self.shield
            self.shield = 0.0
        if self.health <= 0.0: 
            self.health = 0.0
            self.dead = 1
            self.player.deaths += 1
            self.pending_frames = var.death_time * var.frames_per_sec
            explosion = Explosion(self.x, self.y, self.vx, self.vy)
            explosion.mass = self.mass
            high[0:0] = [explosion]
            # gameplay.runobjects() will move ship to pending
            return 1  # Ship is dead
        return 0  # Ship still alive
        

    def hit_by(self, other_mass):
        global high
        if self.dead: return
        if other_mass.__class__ in (Fire, SuperFire):
            damage = ((other_mass.damage-10) * 
                      other_mass.ticks_to_live/var.fire_life + 10)
            dead = self.damage(damage)
            if dead and other_mass.owner is not self:
                other_mass.owner.player.score += 1
                other_mass.owner.player.complement = 1
        elif other_mass.__class__ == Explosion:
            if not self.shield:
                self.damage(var.explosion_damage)
        elif other_mass.__class__ == Ship:
            my_damage = other_mass.health + other_mass.shield
            other_damage = self.health + self.shield
            self.damage(my_damage)
            other_mass.damage(other_damage)
        elif other_mass.__class__ == ShieldBobble:
            self.shield = min(self.max_shield, self.shield + var.sbobble_power)
            snd.play('chimein', 1.0, other_mass.rect.centerx)
        elif other_mass.__class__ == BulletBobble:
            self.bullet = min(self.max_bullet, self.bullet+var.bbobble_charge)
            snd.play('chimein', 1.0, other_mass.rect.centerx)
        else:
            dead = self.damage(1000)
            if dead and self.player.score > 0:
                if var.scoring == 0:
                    self.player.score -= 1
                self.player.insult = 1


# Standalone execution only
class Score:
    def __init__(self, players):
        self.font = font.SysFont("sans", 25)
        self.players = players
        self.render()
        self.dead = 0

    def render(self):
        self.imgs = []
        self.scores = []
        for player in self.players:
            self.scores.append(player.score)
            self.imgs.append(self.font.render(
                "Player %d: %d" % (player.playernum+1, player.score), 1, (0,128,255)))

    def tick(self, speedadjust):
        realscores = [x.score for x in self.players]
        if self.scores != realscores:
            self.render()
        pass

    def erase(self):
        self.draw(erase=1)

    def draw(self, erase=0):
        for i in range(len(self.scores)):
            width = self.imgs[i].get_width()
            height = self.imgs[i].get_height()
            cx = arena.right - width - 20
            cy = 20 + i*30
            if not erase:
                r = gfx.surface.blit(self.imgs[i], (cx, cy))
                gfx.dirty(r)
            else:
                gfx.surface.fill(0, (cx, cy, width+15, height))


def fps_update():
    global fps_list
    fps_list.append(var.clock.get_fps())
    fps_list = fps_list[1:]


def runobjects(speedadjust):
    # Miscellaneous housekeeping
    fps_update()

    # Make spikes appear
    if randint(0,var.spike_rate * var.frames_per_sec) == 1:
        spike = Spike(0,0,0,0)
        spike.dead = 1
        spike.pending_frames = var.frames_per_sec
        pend.append(spike)

    # Make asteroids appear
    if randint(0,var.spike_rate * var.frames_per_sec) == 1:
        asteroid = Asteroid(0,0,0,0)
        asteroid.dead = 1
        asteroid.pending_frames = var.frames_per_sec
        pend.append(asteroid)

    # Make shield powerups appear
    if randint(0,var.shield_powerup_rate * var.frames_per_sec) == 1:
        sbobble = ShieldBobble(0,0,0,0)
        sbobble.dead = 1
        sbobble.pending_frames = var.frames_per_sec
        pend.append(sbobble)

    # Make bullet powerups appear
    if randint(0,var.bullet_powerup_rate * var.frames_per_sec) == 1:
        bbobble = BulletBobble(0,0,0,0)
        bbobble.dead = 1
        bbobble.pending_frames = var.frames_per_sec
        pend.append(bbobble)

    # Gravitate
    for o1 in vapors + low + high:
        for o2 in low + high:
            if o1 is not o2:
                o1.gravitate(o2)

    # Tick pending objects
    for o in pend:
        o.tick(speedadjust)
        if not o.dead:
            if o.__class__ in [Ship, Spike, ShieldBobble, BulletBobble]:
                pend.remove(o)
                low.append(o)

    # Erase and tick visible objects
    for l in list:
        for o in l[:]:
            o.erase()
            o.tick(speedadjust)

    # Check for collisions, skip virtual and pending objects
    for o1 in low + high:
        for o2 in low + high:
            if o1 is not o2 and not o1.dead:
                if o1.clearance(o2) < 0:
                    o1.hit_by(o2)

    # Check all objects for death
    for l in list:
        for o in l[:]:
            if o.dead:
                o.erase()
                l.remove(o)
                # Put ships on pending list
                if o.__class__ == Ship:
                    pend.append(o)
                # Replace fires with pops
                if o.__class__ in (Fire, SuperFire) and o.dead != 2:
                    vx = o.vx
                    vy = o.vy
                    if o.dead_by_hit:
                        vx = vx / 5
                        vy = vy / 5
                        snd.play('shoot', 1.0, o.rect.centerx)
                    vapors.append(Pop(o.x, o.y, vx, vy))

    for l in list:
        for o in l[:]:
            o.draw()



def main():

    import pygame, sys

    pygame.init()
    var.clock = pygame.time.Clock()

    full=1
    if '-window' in sys.argv:
        full = 0

    gfx.initialize((800,600), full)
    pygame.display.set_caption('Spacewar')

    load_game_resources()

    if len(ai.dna_pool) == 0:
        ai.load_dna_pool()

    if not '-nosound' in sys.argv:
        snd.initialize()

    # Load the main game objects
    players = []
    ship = Ship(shipnum=0, x=100, y=100)
    ship.shield = 100.0
    ship.bullet = var.bbobble_charge
    low.append(ship)
    players.append(agents.HumanAgent(playernum=0, ship=ship))
    
    #ship = Ship(shipnum=1, x=540, y=380)
    #low.append(ship)
    ####players.append(agents.AIAgent_Docile(playernum=1, ship=ship))
    #dna = random.choice(ai.dna_pool)
    #players.append(agents.DNAAgent(1,ship,dna,[low,high]))

    ship = Ship(shipnum=2, x=540, y=100)
    low.append(ship)
    #dna = random.choice(ai.dna_pool)
    dna = ai.DNA()
    dna.random()
    print dna
    players.append(agents.DNAAgent(2,ship,dna,[low,high]))

    #sun = Sun()
    #low.append(sun)
    #virtual.append(Score(players))

    # Main game event loop
    while 1:
        for player in players: player.do_action()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()
        
        runobjects(1.0)

        gfx.update()
        
        var.clock.tick(standalone_frame_rate)  # max frame rate

if __name__ == '__main__': 
    standalone_frame_rate = var.frames_per_sec  
    main()
