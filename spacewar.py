#!/usr/bin/env python
import sys, pygame
from pygame.locals import *
from math import *
from random import randint

spacewar_version = "0.1"
testmode = 0

# Initialize pygame and graphics
pygame.init()
pygame.key.set_repeat(15,15)
size = width, height = 640, 480
screen = pygame.display.set_mode(size)
black = 0, 0, 0

# Timing settings
frames_per_sec = 30
# these are proportional to frames_per_sec
fire_delay_frames = frames_per_sec / 2
compass_dirs = 36  
death_frames = 3 * frames_per_sec

# Game physics settings
thrust_power = 0.10
bullet_speed = 5.0
gravity_const = 20.0
start_clearance = 20  # distance ships start from other objects

# Objects rendered in order. Last object on top.
objects = []
# Objects not rendered, but still tracking
pending = []


# Process an image strip
def animstrip(img, width=0):
    if not width:
        width = img.get_height()
    size = width, img.get_height()
    images = []
    origalpha = img.get_alpha()
    origckey = img.get_colorkey()
    img.set_colorkey(None)
    img.set_alpha(None)
    for x in range(0, img.get_width(), width):
        i = pygame.Surface(size)
        i.blit(img, (0, 0), ((x, 0), size))
        if origalpha:
            i.set_colorkey((0,0,0))
        elif origckey:
            i.set_colorkey(origckey)
        images.append(i.convert())
    img.set_alpha(origalpha)
    img.set_colorkey(origckey)
    return images


# All rendered objects are subclass of Mass
class Mass:
    def __init__(self, x, y, vel_x=0.0, vel_y=0.0, mass=1.0, radius=0):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass
        self.radius = radius

    def delete(self, obj_list):
        for i in range(len(obj_list)):
            if obj_list[i] is self:
                del obj_list[i]
                break

    def click(self):
        self.x = (self.x + self.vel_x) % size[0]
        self.y = (self.y + self.vel_y) % size[1]

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
        if dist < 1.0: dist =  1.0
        #if dist == 0:
        #    dist = 0.00000000000001
        force = other_mass.mass/(dist*dist)
        
        rads = self.direction(other_mass)
        self.vel_x = self.vel_x - sin(rads)*force*gravity_const
        self.vel_y = self.vel_y - cos(rads)*force*gravity_const

    def clearance(self, other_mass):
        # *** TODO: this needs to account for motion
        return self.distance(other_mass) - (self.radius + other_mass.radius)
        
    def hit_by(self, other_mass):
        pass


class Bullet(Mass):
    imgs = []

    def __init__(self, image, x, y, vel_x, vel_y, owner):
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=8)
        self.phase = 0
        self.ticks_to_live = frames_per_sec * 5
        self.owner = owner

        # Loaded animated blaster sequence
        if len(Bullet.imgs) == 0:
            Bullet.imgs = animstrip(pygame.image.load(image))
            Bullet.phases = len(Bullet.imgs)

    def click(self):
        Mass.click(self)
        self.ticks_to_live = self.ticks_to_live - 1
        if self.ticks_to_live <= 0: 
            Mass.delete(self, objects)

    def draw(self):
        phase = self.phase
        cx = int(self.x) - (Bullet.imgs[phase].get_rect()[2] / 2)
        cy = int(self.y) - (Bullet.imgs[phase].get_rect()[3] / 2)
        screen.blit(Bullet.imgs[phase], (cx, cy))
        self.phase = (self.phase+1)%Bullet.phases
        if testmode:
            pygame.display.flip()

    def gravitate(self, other_mass):
        # bullets aren't effected by gravity
        # *** TODO: should be an option
        pass

    def hit_by(self, other_mass):
        # Simply remove bullet from object list
        Mass.delete(self, objects)


class Explosion(Mass):
    imgs = []

    def __init__(self, image, x, y, vel_x, vel_y):
        Mass.__init__(self, x, y, vel_x, vel_y, mass=0.0, radius=16)
        self.phase = 0.0

        # Loaded animated blaster sequence
        if len(Explosion.imgs) == 0:
            Explosion.imgs = animstrip(pygame.image.load(image))
            Explosion.phases = len(Explosion.imgs)

    def draw(self):
        phase = int(self.phase)
        cx = int(self.x) - (self.imgs[phase].get_rect()[2] / 2)
        cy = int(self.y) - (self.imgs[phase].get_rect()[3] / 2)
        screen.blit(self.imgs[phase], (cx, cy))
        self.phase = self.phase+0.5
        if self.phase >= self.phases:
            Mass.delete(self, objects)
        if testmode:
            pygame.display.flip()


class Sun(Mass):
    imgs = []

    def __init__(self, image, x=width/2, y=height/2):
        Mass.__init__(self, x, y, vel_x=0, vel_y=0, mass=10.0, radius=10)
        self.phase = 0.0

        # Load animated "sun" sequence
        if len(Sun.imgs) == 0:
            Sun.imgs = animstrip(pygame.image.load(image))
            Sun.phases = len(Sun.imgs)

    def click(self):
        # Remain stationary, no other updates
        pass

    def draw(self):
        phase = int(self.phase)
        cx = int(self.x) - (self.imgs[phase].get_rect()[2] / 2)
        cy = int(self.y) - (self.imgs[phase].get_rect()[3] / 2)
        screen.blit(self.imgs[phase], (cx, cy))
        self.phase = (self.phase+0.5) % Sun.phases
        if testmode:
            pygame.display.flip()


class Ship(Mass):
    def __init__(self, image1, image2, x=50.0, y=50.0, dir=0):
        Mass.__init__(self, x, y, vel_x=0, vel_y=0, mass=1.0, radius=10)
        self.dir = dir*compass_dirs/360
        self.thrusting = 0
        self.phase = 0
        self.fire_delay = 0
        self.pending_frames = 0

        # These items should only be initialized once
        if self.__dict__.has_key('score'):
            return

        self.score = 0

        # Load non-thruster version
        img = pygame.image.load(image1).convert()
        self.imgs1 = []
        for i in range(0, 361, 360/compass_dirs):
            self.imgs1.append(pygame.transform.rotate(img, i))
       
        # Load animated thruster version
        img_anim = animstrip(pygame.image.load(image2))
        self.phases = len(img_anim)
        self.imgs2 = [[] for i in range(self.phases)]
        for p in range(self.phases):
            for i in range(0, 361, 360/compass_dirs):
                self.imgs2[p].append(pygame.transform.rotate(img_anim[p],i))

    def click(self):
        Mass.click(self)
        if self.fire_delay > 0:
            self.fire_delay = self.fire_delay -1
        if self.pending_frames > 0:
            self.pending_frames = self.pending_frames -1
            # Make the ship appear again
            if self.pending_frames <= 0:
                Mass.delete(self, pending)
                objects.append(self)
                found_spot = 0
                new_dir = randint(0, compass_dirs-1)
                while not found_spot:
                    new_x = randint(50, width-50)
                    new_y = randint(50, height-50)
                    Ship.__init__(self, None, None, new_x, new_y, new_dir)
                    found_spot = 1
                    for object in objects:
                        if object is not self:
                            if self.clearance(object) < start_clearance:
                                found_spot = 0
                    if found_spot == 0:
                        print "DEBUG: Finding alternate spot"


    def draw(self):
        phase = self.phase
        dir = self.dir
        if not self.thrusting:
            cx = int(self.x) - (self.imgs1[dir].get_rect()[2] / 2)
            cy = int(self.y) - (self.imgs1[dir].get_rect()[3] / 2)
            screen.blit(self.imgs1[dir], (cx, cy))
        else:
            cx = int(self.x) - (self.imgs2[phase][dir].get_rect()[2] / 2)
            cy = int(self.y) - (self.imgs2[phase][dir].get_rect()[3] / 2)
            screen.blit(self.imgs2[phase][dir], (cx, cy))
            self.phase = (self.phase+1)%self.phases
        if testmode:
            pygame.display.flip()

    def rotate_left(self):
        self.dir = (self.dir+1)%compass_dirs
    
    def rotate_right(self):
        self.dir = (self.dir-1)%compass_dirs
    
    def thrust_on(self):
        self.thrusting = 1
        rads = radians(self.dir*(360/compass_dirs))
        self.vel_x = self.vel_x - sin(rads)*thrust_power
        self.vel_y = self.vel_y - cos(rads)*thrust_power
    
    def thrust_off(self):
        self.thrusting = 0

    def fire(self):
        if not self.fire_delay and not self.pending_frames:
            rads = radians(self.dir*(360/compass_dirs))
            vel_x = self.vel_x - sin(rads)*bullet_speed
            vel_y = self.vel_y - cos(rads)*bullet_speed
            bullet = Bullet("fire.png", 0.0, 0.0, vel_x, vel_y, self)
            bullet.x = self.x - sin(rads)*(self.radius+bullet.radius+1)
            bullet.y = self.y - cos(rads)*(self.radius+bullet.radius+1)
            self.fire_delay = fire_delay_frames
            objects[0:0] = [bullet]

    def hit_by(self, other_mass):
        if other_mass.__class__ == Bullet and other_mass.owner is not self:
            other_mass.owner.score = other_mass.owner.score + 1
        elif self.score > 0:
            self.score = self.score - 1
        explosion = Explosion("explosion.png", self.x, self.y, 
            self.vel_x, self.vel_y)
        Mass.delete(self, objects)
        objects[0:0] = [explosion]
        pending.append(self)
        self.pending_frames = death_frames
        pass

class Score:
    def __init__(self, ship1, ship2):
        self.font = pygame.font.SysFont("sans", 18)
        self.ship1 = ship1
        self.ship2 = ship2
        self.render(self.ship1.score, self.ship2.score)

    def render(self, score1, score2):
        self.score1 = score1
        self.score2 = score2
        self.img1 = self.font.render("Player 1: %d" % score1, 1, (0,128,255))
        self.img2 = self.font.render("Player 2: %d" % score2, 1, (255,128,0))

    def draw(self):
        if self.ship1.score != self.score1 or self.ship2.score != self.score2:
            self.render(self.ship1.score, self.ship2.score)
        cx = 20
        cy = height - self.img1.get_height() - 10
        screen.blit(self.img1, (cx, cy))
        cx = width - self.img2.get_width() - 20
        cy = height - self.img2.get_height() - 10
        screen.blit(self.img2, (cx, cy))

def show_logo():
    logo = pygame.image.load("logo.png")
    cx = int(width/2) - (logo.get_rect()[2] / 2)
    cy = int(height/2) - (logo.get_rect()[3] / 2)
    screen.blit(logo, (cx, cy))
    pygame.display.flip()

def show_logo_msg():
    font = pygame.font.SysFont("sans", 18)
    img = font.render("Press <SPACE> to start", 1, (127, 127, 0))
    cx = int(width/2) - (img.get_rect()[2] / 2)
    cy = int(height) - (img.get_rect()[3]) - 20
    screen.blit(img, (cx, cy))
    pygame.display.flip()

    while 1:
        pygame.time.wait(200)
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()
            if event.type == KEYDOWN and event.key == K_SPACE:
                return

def main():
    clock = pygame.time.Clock()

    show_logo()

    # Load the main game objects
    ship1 = Ship("ship1.png", "ship2.png", 100, 100, 270)
    objects.append(ship1)
    ship2 = Ship("ship1.png", "ship3.png", 540, 380, 90)
    objects.append(ship2)
    sun = Sun("spikeball.png")
    objects.append(sun)

    # Setup scoring
    score = Score(ship1, ship2)

    # Show the continue message
    show_logo_msg()

    # Main game event loop
    while 1:
        # Set the max frame rate
        clock.tick(frames_per_sec)

        # Handle keyboard events
        if pygame.key.get_pressed()[K_LEFT]:
            ship1.rotate_left()
        if pygame.key.get_pressed()[K_RIGHT]:
            ship1.rotate_right()
        if pygame.key.get_pressed()[K_DOWN]:
            ship1.fire()
        if pygame.key.get_pressed()[K_UP]:
            ship1.thrust_on()
        else:
            ship1.thrust_off()
        if pygame.key.get_pressed()[K_a]:
            ship2.rotate_left()
        if pygame.key.get_pressed()[K_d]:
            ship2.rotate_right()
        if pygame.key.get_pressed()[K_s]:
            ship2.fire()
        if pygame.key.get_pressed()[K_w]:
            ship2.thrust_on()
        else:
            ship2.thrust_off()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                sys.exit()
      
        # For each object against every other object:
        # - determine gravitational effect
        # - determine whether they have collided
        for object1 in objects:
            for object2 in objects:
                if object1 is not object2:
                    object1.gravitate(object2)
        for object1 in objects:
            for object2 in objects:
                if object1 is not object2:
                    if object1.clearance(object2) < 0:
                        object1.hit_by(object2)
                        object2.hit_by(object1)

        # Tell objects to update (position, etc)
        for object in objects:
            object.click()
        for object in pending:
            object.click()

        # Update the screen and draw all objects
        screen.fill(black)
        for object in objects:
            object.draw()
        score.draw()

        pygame.display.flip()


if __name__ == '__main__': 
    main()
else:
    global testmode
    testmode = 1
    ship1 = Ship("ship1.png", "ship2.png", 100, 100, 270)
    ship2 = Ship("ship1.png", "ship3.png", 150, 100, 90)
    ship1.draw()
    ship2.draw()
    print "Test mode"
