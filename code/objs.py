#!/usr/bin/env python
from pygame import transform, font, Rect, key
from pygame.locals import *
import gfx, snd
from math import *
from random import randint, random

import game

testmode = 0

# *** TODO: make calculations use left and top instead of assuming 0,0
left = game.arena.left
right = game.arena.right
top = game.arena.top
bottom = game.arena.bottom

# Timing settings
frames_per_sec = 40
# these are proportional to frames_per_sec
fire_delay_frames = frames_per_sec / 2
compass_dirs = 40
death_frames = 3 * frames_per_sec
spike_rate = frames_per_sec * 25

# Game physics settings
reverse_power = -0.08
turbo_power = 0.12
fire_speed = 5.0
smoke_speed = 5.0
gravity_const = 20.0
start_clearance = 25  # distance ships start from other objects
stationary_sun = 1

# Object lists:
#   - vapors for smoke and other "vapors"
#   - low for hard objects: ship and sun
#   - high for the fire and explosions
#   - virtual for help text, and non-colliding objects
#   - pend for non-rendered objects still being tracked
vapors = []
low = []
high = []
virtual = []
pend = []

# List of object lists in rendering order, top is last
list = [vapors, low, high, virtual]

# Ship images are 3D arrays [player][phase][direction]
images_ship = images_reverse = images_turbo = images_shield = None
images_explosion = images_pop = images_smoke = images_fire = None
images_box = images_spike = images_tele = None

# Load all the images
def load_game_resources():
    #load ship graphics
    global images_ship, images_reverse, images_turbo, images_shield
    global images_explosion, images_pop, images_smoke, images_fire
    global images_box, images_spike, images_tele

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

    images_shield = []
    img = gfx.load('bonus-shield.png')
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
        self.x = (self.x + self.vel_x) % right
        self.y = (self.y + self.vel_y) % bottom
        
        self.rect = Rect(int(self.x)-self.width/2, int(self.y)-self.height/2, 
                     self.width, self.height)

    def draw(self):
        phase = int(self.phase)
        dir = self.dir
        cx = int(self.x)-(self.imgs[phase][dir].get_rect()[2] /2)
        cy = int(self.y)-(self.imgs[phase][dir].get_rect()[3] /2)
        gfx.surface.blit(self.imgs[phase][dir], (cx, cy))
        gfx.dirty2(self.rect, self.lastrect)
        self.lastrect = self.rect
        if testmode:
            gfx.update()

    def erase(self, background):
        background(self.rect)
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
        self.vel_x = self.vel_x - sin(rads)*force*gravity_const
        self.vel_y = self.vel_y - cos(rads)*force*gravity_const

    def clearance(self, other_mass):
        # *** TODO: this needs to account for motion
        return self.distance(other_mass) - (self.radius + other_mass.radius)

    def find_spot(self):
        found_spot = 0
        new_dir = randint(0, compass_dirs-1)
        while not found_spot:
            self.x = randint(50, right-50)
            self.y = randint(50, bottom-50)
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
        self.ticks_to_live = frames_per_sec * 5
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
    def __init__(self, x=game.arena.width/2, y=game.arena.height/2):
        self.imgs = images_box
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x=0, vel_y=0, mass=10.0, radius=10)

    def tick(self, speedadjust):
        if not stationary_sun: 
            Mass.tick(self, speedadjust)
        self.phase = (self.phase+0.4)%self.phases

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
                snd.play('klank2', 1.0, self.rect.centerx)

    def hit_by(self, other_mass):
        if not self.dead:
            # If dead by another method, don't over-ride
            if other_mass.__class__ == Sun or other_mass.__class__ == Spike:
                self.dead = 1
                explosion = Explosion(self.x, self.y, self.vel_x, self.vel_y)
                high[0:0] = [explosion]
                # gameplay.runobjects() will remove spike

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
    PK_LEFT = [K_LEFT, K_a, K_j, K_KP2]
    PK_RIGHT = [K_RIGHT, K_d, K_l, K_KP8]
    PK_REVERSE = [K_DOWN, K_s, K_k, K_KP5]
    PK_THRUST = [K_UP, K_w, K_i, K_KP4]
    PK_FIRE = [K_RCTRL, K_TAB, K_SPACE, K_KP0]

    def __init__(self, player=0, x=50.0, y=50.0, dir=0):
        self.player=player
        self.score = 0
        self.start(x, y, dir=dir)

    def start(self, x=50.0, y=50.0, vel_x=0, vel_y=0, mass=1.0, radius=11, dir=0):
        self.imgs = images_ship[self.player]
        self.phases = len(self.imgs)
        Mass.__init__(self, x, y, vel_x, vel_y, mass, radius, dir)
       
        self.shield = 0
        self.shield_phase = 0.0
        self.shield_phases = len(images_shield)
        self.thrust = 0
        self.turbo = 0
        self.turn = 0
        self.fire_delay = 0
        self.pending_frames = 0
       
    def tick(self, speedadjust):
        if self.thrust:
            # Calculate thrust acceleration
            rads = radians(self.dir*(360/compass_dirs))
            self.vel_x = self.vel_x - sin(rads)*self.thrust
            self.vel_y = self.vel_y - cos(rads)*self.thrust
            # Smoke trails
            if gfx.surface.get_bytesize()>1:
                if self.thrust > 0: rads = (rads+pi) % (2.0*pi)
                if game.clock.get_fps() > 35.0:
                    loop = 2
                else: 
                    loop = 1
                for i in range(loop):
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
        self.shield_phase = (self.shield_phase+0.2)%self.shield_phases

        # Slow down firing rate
        if self.fire_delay > 0:
            self.fire_delay = self.fire_delay -1
        # Ship is dead, waiting to re-appear 
        if self.pending_frames > 0:
            if self.pending_frames == frames_per_sec / 2:
                snd.play('startlife', 1.0, self.rect.centerx)
            self.pending_frames = self.pending_frames -1
            # Make the ship appear again
            if self.pending_frames <= 0:
                self.dead = 0
                self.start()
                self.find_spot()

    def draw(self):
        if self.shield:
            global images_shield
            imgs = images_shield
            phase = int(self.shield_phase)
            cx = int(self.x)-(imgs[phase][0].get_rect()[2] /2)
            cy = int(self.y)-(imgs[phase][0].get_rect()[3] /2)
            gfx.surface.blit(imgs[phase][0], (cx, cy))
        Mass.draw(self)

    def do_input(self):
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
        if not self.thrust == turbo_power:
            self.thrust = turbo_power
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
        if other_mass.__class__ == Fire and other_mass.owner is not self:
            other_mass.owner.score = other_mass.owner.score + 1
        elif self.score > 0:
            self.score = self.score - 1
        self.dead = 1
        self.pending_frames = death_frames
        explosion = Explosion(self.x, self.y, self.vel_x, self.vel_y)
        high[0:0] = [explosion]
        # gameplay.runobjects() will move ship to pending


###def main():
###    clock = pygame.time.Clock()
###
###    # Load the main game objects
###    ship1 = Ship("ship1.png", "ship2.png", 100, 100, 270)
###    objects.append(ship1)
###    ship2 = Ship("ship1.png", "ship3.png", 540, 380, 90)
###    objects.append(ship2)
###    sun = Sun("spikeball.png")
###    objects.append(sun)
###
###    # Setup scoring
###    score = Score(ship1, ship2)
###
###    # Main game event loop
###    while 1:
###        # Set the max frame rate
###        clock.tick(frames_per_sec)
###
###        # Handle keyboard events
###        if pygame.key.get_pressed()[K_LEFT]:
###            ship1.rotate_left()
###        if pygame.key.get_pressed()[K_RIGHT]:
###            ship1.rotate_right()
###        if pygame.key.get_pressed()[K_DOWN]:
###            ship1.fire()
###        if pygame.key.get_pressed()[K_UP]:
###            ship1.thrust_on()
###        else:
###            ship1.thrust_off()
###        if pygame.key.get_pressed()[K_a]:
###            ship2.rotate_left()
###        if pygame.key.get_pressed()[K_d]:
###            ship2.rotate_right()
###        if pygame.key.get_pressed()[K_s]:
###            ship2.fire()
###        if pygame.key.get_pressed()[K_w]:
###            ship2.thrust_on()
###        else:
###            ship2.thrust_off()
###
###        for event in pygame.event.get():
###            if event.type == QUIT:
###                sys.exit()
###            elif event.type == KEYDOWN and event.key == K_ESCAPE:
###                sys.exit()
###      
###        # For each object against every other object:
###        # - determine gravitational effect
###        # - determine whether they have collided
###        for object1 in objects:
###            for object2 in objects:
###                if object1 is not object2:
###                    object1.gravitate(object2)
###        for object1 in objects:
###            for object2 in objects:
###                if object1 is not object2:
###                    if object1.clearance(object2) < 0:
###                        object1.hit_by(object2)
###                        object2.hit_by(object1)
###
###        # Tell objects to update (position, etc)
###        for object in objects:
###            object.tick()
###        for object in pending:
###            object.tick()
###
###        # Update the screen and draw all objects
###        screen.fill(black)
###        for object in objects:
###            object.draw()
###        score.draw()
###
###        pygame.display.flip()


###if __name__ == '__main__': 
###    main()
###else:
###    global testmode
###    testmode = 1
###    ship1 = Ship("ship1.png", "ship2.png", 100, 100, 270)
###    ship2 = Ship("ship1.png", "ship3.png", 150, 100, 90)
###    ship1.draw()
###    ship2.draw()
###    print "Test mode"
