#!/usr/bin/env python

from pygame import transform, font, Rect, key
from pygame.locals import *
import gfx, snd, pref
from math import *
from random import randint, random

# *** TODO: make calculations use arena.left and arena.top 
#       instead of assuming 0,0
if __name__ != '__main__': 
    # We were imported normally from gameplay.py
    import game
    arena = game.arena
else:
    # We are running objs.py standalone
    arena = (0, 0, 800, 600)

# Timing settings, proportional to frames_per_sec
game_clock = None  # Set in load_game_resources or main()
frames_per_sec = 40
fire_delay_frames = frames_per_sec / 2
compass_dirs = frames_per_sec
###death_frames = 3 * frames_per_sec
fire_life = frames_per_sec * 4
fps_list = [30] * frames_per_sec

# Game physics settings
reverse_power = -0.08
thrust_power = 0.12
fire_speed = 5.0
explosion_damage = 3
bobble_power = 50.0
smoke_speed = 5.0
start_clearance = 30  # distance ships start from other objects

# Object lists:
#   - vapors for smoke and other "vapors"
#   - low for hard objects: ship and sun
#   - high for the fire and explosions
#   - virtual for help text, and non-colliding objects
#   - pend for non-rendered objects still being tracked
#   - list: rendered lists in rendering order
vapors, low, high, virtual, pend = [], [], [], [], []
list = [vapors, low, high, virtual]

# Ship images are 3D arrays [player][phase][direction]
images_ship = images_reverse = images_turbo = images_shield = None
images_explosion = images_pop = images_smoke = images_fire = None
images_box = images_spike = images_tele = images_bobble = None

# Load all the images
def load_game_resources():
    global game_clock 
    global images_ship, images_reverse, images_turbo, images_shield
    global images_explosion, images_pop, images_smoke, images_fire
    global images_box, images_spike, images_tele, images_bobble

    if not game_clock:
        # objs.py is imported, not standalone
        game_clock = game.clock

    # Load normal ship image
    images_ship   = [[],[],[],[]]
    for ship, file in [(0, "ship1-up.png"), (1, "ship2-up.png"),
                       (2, "ship3-up.png"), (3, "ship4-up.png")]:
        img = gfx.load(file)
        #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
        img_anim = gfx.animstrip(img)
        phases = len(img_anim)
        for p in range(phases):
            images_ship[ship].append([])
            for i in range(0, 361, 360/compass_dirs):
                images_ship[ship][p].append(transform.rotate(img_anim[p],i))
    
    # Load animated reverse version
    images_reverse = [[],[],[],[]]
    for ship, file in [(0, "ship1-up-boost1.png"), (1, "ship2-up-boost1.png"),
                       (2, "ship3-up-boost1.png"), (3, "ship4-up-boost1.png")]:
        img = gfx.load(file)
        #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
        img_anim = gfx.animstrip(img)
        phases = len(img_anim)
        for p in range(phases):
            images_reverse[ship].append([])
            for i in range(0, 361, 360/compass_dirs):
                images_reverse[ship][p].append(transform.rotate(img_anim[p],i))

    images_turbo  = [[],[],[],[]]
    for ship, file in [(0, "ship1-up-boost2.png"), (1, "ship2-up-boost2.png"),
                       (2, "ship3-up-boost2.png"), (3, "ship4-up-boost2.png")]:
        img = gfx.load(file)
        #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
        img_anim = gfx.animstrip(img)
        phases = len(img_anim)
        for p in range(phases):
            images_turbo[ship].append([])
            for i in range(0, 361, 360/compass_dirs):
                images_turbo[ship][p].append(transform.rotate(img_anim[p],i))

    images_smoke = []
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
        images_smoke.append([])
        images_smoke[p].append(img_anim[p])

    images_shield = []
    img = gfx.load('bonus-shield.png')
    #img.set_alpha(128)
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_shield.append([])
        images_shield[p].append(img_anim[p])

    images_explosion = []
    img = gfx.load('explosion.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_explosion.append([])
        images_explosion[p].append(img_anim[p])

    images_tele = []
    img = gfx.load('ship-teleport.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_tele.append([])
        images_tele[p].append(img_anim[p])

    images_fire = []
    img = gfx.load('fire.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_fire.append([])
        images_fire[p].append(img_anim[p])

    images_pop = []
    img = gfx.load('popshot.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img, 18)
    phases = len(img_anim)
    for p in range(phases):
        images_pop.append([])
        images_pop[p].append(img_anim[p])

    images_box = []
    img = gfx.load('boxes.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_box.append([])
        images_box[p].append(img_anim[p])

    images_spike = []
    img = gfx.load('spikeball.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_spike.append([])
        images_spike[p].append(img_anim[p])

    images_bobble = []
    img = gfx.load('powerup.png')
    #img = transform.scale(img, (img.get_width()*2/3, img.get_height()*2/3))
    img_anim = gfx.animstrip(img)
    phases = len(img_anim)
    for p in range(phases):
        images_bobble.append([])
        images_bobble[p].append(img_anim[p])


# All game play objects are a subclass of Mass
#   - Mass itself cannot be instantiated
#   - self.imgs must exist before calling Mass.__init__()
class Mass:
    def __init__(self, x, y, vel_x=0.0, vel_y=0.0, mass=1.0, radius=0, dir=0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass
        self.radius = radius
        self.dir = dir*compass_dirs/360

        self.width = self.imgs[0][self.dir].get_width()
        self.height = self.imgs[0][self.dir].get_height()
        self.rect = Rect(int(self.x)-self.width/2, int(self.y)-self.height/2, 
                     self.width, self.height)
        self.lastrect = self.rect
        self.dead = 0
        self.phase = 0.0

    def tick(self, speedadjust):
        self.x = (self.x + self.vel_x) % arena[2]
        self.y = (self.y + self.vel_y) % arena[3]
        
        self.rect = Rect(int(self.x)-self.width/2, int(self.y)-self.height/2, 
                     self.width, self.height)

    def draw(self):
        phase = int(self.phase)
        dir = self.dir
        ###cx = int(self.x)-(self.imgs[phase][dir].get_rect()[2] /2)
        ###cy = int(self.y)-(self.imgs[phase][dir].get_rect()[3] /2)
        ###gfx.surface.blit(self.imgs[phase][dir], (cx, cy))
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

    def gravitate(self, other_mass):
        dist = self.distance(other_mass)
        if dist < 4.0: dist = 4.0
        force = other_mass.mass/(dist*dist)
        
        rads = self.direction(other_mass)
        self.vel_x = self.vel_x - sin(rads)*force*pref.gravity_const
        self.vel_y = self.vel_y - cos(rads)*force*pref.gravity_const

    def clearance(self, other_mass):
        # *** TODO: this needs to account for motion
        return self.distance(other_mass) - (self.radius + other_mass.radius)

    def find_spot(self):
        found_spot = 0
        new_dir = randint(0, compass_dirs-1)
        while not found_spot:
            self.x = randint(50, arena[2]-50)
            self.y = randint(50, arena[3]-50)
            found_spot = 1
            for object in low + high:
                if object is not self:
                    if self.clearance(object) < start_clearance:
                        found_spot = 0
        
    def hit_by(self, other_mass):
        pass


class Smoke(Mass):
    def __init__(self, x, y, vel_x, vel_y):
        self.imgs = images_smoke
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=8)
        self.ticks_to_live = randint(12, 20)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)
        if self.ticks_to_live: self.ticks_to_live -= 1
        self.phase = int(self.phases * (self.ticks_to_live / 20.0))
        if self.ticks_to_live <= 0:
            self.dead = 1

class Fire(Mass):
    def __init__(self, x, y, vel_x, vel_y, owner):
        self.imgs = images_fire
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=8)
        self.ticks_to_live = fire_life
        self.owner = owner
        self.dead_by_hit = 0
        

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)
        self.phase = (self.phase+0.3)%self.phases
        self.ticks_to_live = self.ticks_to_live - 1
        if self.ticks_to_live <= 0 and not self.dead: 
            self.dead = 1

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            self.dead_by_hit = 1
            self.dead = 1

class Pop(Mass):
    def __init__(self, x, y, vel_x, vel_y):
        self.imgs = images_pop
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=8)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)
        self.phase = self.phase+0.2
        if self.phase >= self.phases: 
            self.dead = 1

    def gravitate(self, other_mass):
        # No effect from gravity
        pass

class Explosion(Mass):
    def __init__(self, x, y, vel_x, vel_y):
        self.imgs = images_explosion
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=16)
        snd.play('explode', 1.0, self.rect.centerx)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)
        self.phase = self.phase+0.5
        if self.phase >= self.phases:
            self.dead = 1

    def gravitate(self, other_mass):
        pass

class Sun(Mass):
    def __init__(self, x=arena[2]/2, y=arena[3]/2):
        self.imgs = images_box
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x=0, vel_y=0, mass=10.0, radius=10)

    def tick(self, speedadjust):
        if pref.sun >= 2: 
            Mass.tick(self, speedadjust)
        self.phase = (self.phase+0.4)%self.phases

    def draw(self):
        if pref.sun != 3:
            Mass.draw(self)

class Spike(Mass):
    def __init__(self, x, y, vel_x, vel_y):
        self.imgs = images_spike
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=4.0, radius=10)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)

        self.phase = (self.phase+0.4)%self.phases

        if self.pending_frames > 0:
            if self.pending_frames == frames_per_sec / 2:
                snd.play('flop', 1.0, self.rect.centerx)
            self.pending_frames = self.pending_frames -1
            # Make the spike appear again
            if self.pending_frames <= 0:
                self.dead = 0
                self.find_spot()
                self.vel_x = (random()-0.5) * 4
                self.vel_y = (random()-0.5) * 4
                snd.play('klank2', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            if other_mass.__class__ == Sun or other_mass.__class__ == Spike:
                self.dead = 1
                explosion = Explosion(self.x, self.y, self.vel_x, self.vel_y)
                explosion.mass = self.mass
                high[0:0] = [explosion]
                # gameplay.runobjects() will remove spike

class Bobble(Mass):
    def __init__(self, x, y, vel_x, vel_y):
        self.imgs = images_bobble
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.5, radius=10)

    def tick(self, speedadjust):
        Mass.tick(self, speedadjust)

        self.phase = (self.phase+0.2)%self.phases

        if self.pending_frames > 0:
            self.pending_frames = self.pending_frames -1
            # Make the spike appear again
            if self.pending_frames <= 0:
                self.dead = 0
                self.find_spot()
                self.vel_x = (random()-0.5) * 6
                self.vel_y = (random()-0.5) * 6
                snd.play('chimeout', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            self.dead = 1
            vel_x = self.vel_x / 5
            vel_y = self.vel_y / 5
            if not other_mass.__class__ == Ship:
                snd.play('boxhit', 1.0, other_mass.rect.centerx)
                vapors.append(Pop(other_mass.x, other_mass.y, vel_x, vel_y))

class Tele(Mass):
    def __init__(self, x, y):
        self.imgs = images_tele
        self.phases = len(self.imgs)
        self.phase = 0.0
        Mass.__init__(self, x=x, y=y)

    def tick(self, speedadjust):
        self.phase += speedadjust * .6
        if self.phase >= self.phases:
            self.dead = 1

class Ship(Mass):
    PK_LEFT = (K_LEFT, K_a, K_j, K_KP2)
    PK_RIGHT = (K_RIGHT, K_d, K_l, K_KP8)
    PK_REVERSE = (K_DOWN, K_s, K_k, K_KP5)
    PK_THRUST = (K_UP, K_w, K_i, K_KP4)
    PK_FIRE = (K_RCTRL, K_TAB, K_SPACE, K_KP0)

    BASE_COLOR = ((75, 0, 0), (0, 75, 0), (0, 0, 75), (75, 75, 0))

    def __init__(self, player=0, x=50.0, y=50.0, dir=0):
        self.player=player
        self.mycolor = self.BASE_COLOR[player]
        self.score = 0
        self.max_health = 100.0
        self.max_shield = 100.0
        self.start(x, y, dir=dir)

    def start(self, x=50.0, y=50.0, vel_x=0, vel_y=0, mass=1.0, radius=11, dir=0):
        self.imgs = images_ship[self.player]
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass, radius, dir)
      
        self.health = 100.0
        self.shield = 0.0
        self.shield_phases = len(images_shield)
        self.thrust = 0
        self.turn = 0
        self.fire_delay = 0
        self.smoke_rate = 0.0
        self.pending_frames = 0
        self.complement = 0
        self.insult = 0
       
    def tick(self, speedadjust):
        # Ship is dead, waiting to re-appear 
        if self.pending_frames > 0:
            if self.pending_frames == frames_per_sec / 2:
                snd.play('startlife', 1.0, self.rect.centerx)
            self.pending_frames = self.pending_frames -1
            self.health = (self.max_health * 
                (pref.death_time * frames_per_sec - self.pending_frames) / 
                (pref.death_time * frames_per_sec))
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
            rads = radians(self.dir*(360/compass_dirs))
            self.vel_x = self.vel_x - sin(rads)*self.thrust
            self.vel_y = self.vel_y - cos(rads)*self.thrust
            # Smoke trails, don't overload frame rate
            if pref.graphics > 0 and gfx.surface.get_bytesize()>1:
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
                    vel_x = (self.vel_x - sin(rads)*smoke_speed + random()/3)
                    vel_y = (self.vel_y - cos(rads)*smoke_speed + random()/3)
                    vapors.append(Smoke(x, y, vel_x, vel_y))

        # Perform turns
        if self.turn:
            self.dir = (self.dir+self.turn)%compass_dirs
            self.width = self.imgs[0][self.dir].get_width()
            self.height = self.imgs[0][self.dir].get_height()

        # Perform standard movement
        Mass.tick(self, speedadjust)
        
        # Next phase from animation
        self.phase = (self.phase+1.0)%self.phases
        if self.health < self.max_health:
            self.health = min (self.max_health, 
                               self.health + pref.heal_rate/100.0)

        # Slow down firing rate
        if self.fire_delay > 0:
            self.fire_delay = self.fire_delay -1

    def draw(self):
        Mass.draw(self)
        if self.shield:
            phases = self.shield_phases-1
            phase = phases - int((phases+0.99) * self.shield / self.max_shield)
            imgs = images_shield[phase][0]
            cx = int(self.x)-(imgs.get_rect()[2] /2)
            cy = int(self.y)-(imgs.get_rect()[3] /2)
            gfx.surface.blit(imgs, (cx, cy))

    def do_input(self, player=None):
        if not player:
            player = self.player
        if self.dead: 
            self.cmd_turn_off()
            self.cmd_thrust_off()
            return
        if key.get_pressed()[self.PK_LEFT[player]]:
            self.cmd_left()
        elif key.get_pressed()[self.PK_RIGHT[player]]:
            self.cmd_right()
        else:
            self.cmd_turn_off()
        if key.get_pressed()[self.PK_REVERSE[player]]:
            self.cmd_reverse()
        elif key.get_pressed()[self.PK_THRUST[player]]:
            self.cmd_turbo()
        else:
            self.cmd_thrust_off()
        if key.get_pressed()[self.PK_FIRE[player]]:
            self.cmd_fire()

    def cmd_left(self):
        self.turn = 1
    
    def cmd_right(self):
        self.turn = -1
    
    def cmd_turn_off(self):
        self.turn = 0
    
    def cmd_reverse(self):
        if not self.thrust == reverse_power:
            self.thrust = reverse_power
            self.imgs = images_reverse[self.player]
            self.phases = len(self.imgs)
            self.phase = 0.0
    
    def cmd_turbo(self):
        if not self.thrust == thrust_power:
            self.thrust = thrust_power
            self.imgs = images_turbo[self.player]
            self.phases = len(self.imgs)
            self.phase = 0.0
    
    def cmd_thrust_off(self):
        if self.thrust:
            self.thrust = 0
            self.imgs = images_ship[self.player]
            self.phases = len(self.imgs)
            self.phase = 0.0

    def cmd_fire(self):
        if not self.fire_delay and not self.pending_frames:
            rads = radians(self.dir*(360/compass_dirs))
            vel_x = self.vel_x - sin(rads)*fire_speed
            vel_y = self.vel_y - cos(rads)*fire_speed
            fire = Fire(0.0, 0.0, vel_x, vel_y, self)
            fire.x = self.x - sin(rads)*(self.radius+fire.radius+1)
            fire.y = self.y - cos(rads)*(self.radius+fire.radius+1)
            self.fire_delay = fire_delay_frames
            high.append(fire)
            snd.play('select_choose', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        global high
        if self.dead: return
        if other_mass.__class__ == Fire:
            damage = ((pref.fire_damage-10) * 
                      other_mass.ticks_to_live/fire_life + 10)
            self.shield -= damage
            if self.shield < 0.0:
                self.health += self.shield
                self.shield = 0.0
            if self.health <= 0.0:
                if other_mass.owner is not self:
                    other_mass.owner.score = other_mass.owner.score + 1
                    other_mass.owner.complement = 1
        elif other_mass.__class__ == Explosion:
            if not self.shield:
                self.health -= explosion_damage
        elif other_mass.__class__ == Bobble:
            self.shield = min (self.max_shield, self.shield + bobble_power)
            snd.play('chimein', 1.0, other_mass.rect.centerx)
        else:
            self.health = 0.0
            if self.score > 0:
                if pref.scoring == 0:
                    self.score = self.score - 1
                self.insult = 1
        if self.health <= 0.0: 
            self.health = 0.0
            self.dead = 1
            self.pending_frames = pref.death_time * frames_per_sec
            explosion = Explosion(self.x, self.y, self.vel_x, self.vel_y)
            explosion.mass = self.mass
            high[0:0] = [explosion]
            # gameplay.runobjects() will move ship to pending


# Standalone execution only
class Score:
    def __init__(self, ships):
        self.font = font.SysFont("sans", 25)
        self.ships = ships
        self.render()
        self.dead = 0

    def render(self):
        self.imgs = []
        self.scores = []
        for ship in self.ships:
            self.scores.append(ship.score)
            self.imgs.append(self.font.render(
                "Player %d: %d" % (ship.player+1, ship.score), 1, (0,128,255)))

    def tick(self, speedadjust):
        realscores = [x.score for x in self.ships]
        if self.scores != realscores:
            self.render()
        pass

    def erase(self):
        self.draw(erase=1)

    def draw(self, erase=0):
        for i in range(len(self.scores)):
            width = self.imgs[i].get_width()
            height = self.imgs[i].get_height()
            cx = arena[2] - width - 20
            cy = 20 + i*30
            if not erase:
                r = gfx.surface.blit(self.imgs[i], (cx, cy))
                gfx.dirty(r)
            else:
                gfx.surface.fill(0, (cx, cy, width+15, height))


def fps_update():
    global fps_list
    fps_list.append(game_clock.get_fps())
    fps_list = fps_list[1:]


def runobjects(speedadjust):
    # Miscellaneous housekeeping
    fps_update()

    # Make spikes appear
    if randint(0,pref.spike_rate * frames_per_sec) == 1:
        spike = Spike(0,0,0,0)
        spike.dead = 1
        spike.pending_frames = frames_per_sec
        pend.append(spike)

    # Make shield powerups appear
    if randint(0,pref.shield_powerup_rate * frames_per_sec) == 1:
        bobble = Bobble(0,0,0,0)
        bobble.dead = 1
        bobble.pending_frames = frames_per_sec
        pend.append(bobble)

    # Gravitate
    for o1 in vapors + low + high:
        for o2 in low + high:
            if o1 is not o2:
                o1.gravitate(o2)

    # Tick pending objects
    for o in pend:
        o.tick(speedadjust)
        if not o.dead:
            if o.__class__ == Ship:
                pend.remove(o)
                low.append(o)
            if o.__class__ == Spike:
                pend.remove(o)
                low.append(o)
            if o.__class__ == Bobble:
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
                if o.__class__ == Fire and o.dead != 2:
                    vel_x = o.vel_x
                    vel_y = o.vel_y
                    if o.dead_by_hit:
                        vel_x = vel_x / 5
                        vel_y = vel_y / 5
                        snd.play('shoot', 1.0, o.rect.centerx)
                    vapors.append(Pop(o.x, o.y, vel_x, vel_y))

    for l in list:
        for o in l[:]:
            o.draw()



def main():
    global game_clock

    import pygame, sys

    pygame.init()
    game_clock = pygame.time.Clock()

    full=1
    if '-window' in sys.argv:
        full = 0

    gfx.initialize((800,600), full)
    pygame.display.set_caption('Spacewar')

    load_game_resources()

    if not '-nosound' in sys.argv:
        snd.initialize()

    # Load the main game objects
    ships = []
    ships.append( Ship(player=0, x=100, y=100))
    low.append(ships[0])
    ships.append(Ship(player=1, x=540, y=380))
    low.append(ships[1])
    sun = Sun()
    low.append(sun)
    virtual.append(Score(ships))

    # Main game event loop
    while 1:
        game_clock.tick(frames_per_sec)  # max frame rate

        for ship in ships: ship.do_input()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()
        
        runobjects(1.0)

        gfx.update()

if __name__ == '__main__': 
    main()
