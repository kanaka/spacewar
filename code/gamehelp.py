"""in game help screens"""

import math
import pygame
from pygame.locals import *
import game, pref
import gfx, snd, txt
import input
import gameplay, objtext

fonts = []

def load_game_resources():
    fonts.append(txt.Font('sans', 14, italic=1))
    fonts.append(txt.Font('sans', 20, bold=1))
    snd.preload('chimein', 'chimeout')


Help = {
"introduction":"""Spacewar Tutorial Mode
The objective of Spacwar is to score points by killing your 
opponents.
-
The vital stats for each player's ship appear on the heads up 
display to the right. Below the ship image is the player's 
score. Below the score is the health of the ship and below that
is the shield strength if the ship has shield powerup.
-
You can use this mode to practice the controls for each player.
Every player's controls are bound to the single ship that is 
shown.
-
Press F1 during the tutorial or the game to show the keys that 
control each player.
""",

"keys":"""Player Control Keys
Player 1:
$
....Left:     Left Arrow
$
....Right:    Right Arrow
$
....Thrust:   Up Arrow
$
....R-Thrust: Down Arrow
$
....Fire:     Right-Ctrl
-
Player 2:
$
....Left:     a
$
....Right:    d
$
....Thrust:   w
$
....R-Thrust: s
$
....Fire:     Tab
-
Player 3:
$
....Left:     j
$
....Right:    l
$
....Thrust:   i
$
....R-Thrust: k
$
....Fire:     Space
-
Player 4:
$
....Left:     Numpad 2
$
....Right:    Numpad 8
$
....Thrust:   Numpad 4
$
....R-Thrust: Numpad 5
$
....Fire:     Numpad 0
""",

"powerups":"""Shield Power Ups
Shield powerups appear every now and then. If you run into these with 
your ship, you will receive a charge to your shields.
""",

"spikes":"""Spiked Balls
Spiked balls appear every now and then. If you run into these with 
your ship, you will die. Spiked balls are only destroyed when they
run into the Sun or into another spiked ball.
""",

"opponents":"""Your Opponents
During a real game you will have opponents.  Try and destroy the dummy
ship that will appear. If you destroy it before it falls into the sun,
you will score a point.
""",
}


QuickHelp = {
"powerup":"Grab the Powerups",
}



def help(helpname, helppos):
    ###if not game.player.help.has_key(helpname):
    ###    game.player.help[helpname] = 1
    ###    if pref.help == 0:
    ###        game.handler = GameHelp(game.handler, helpname, helppos)
    ###    elif hasattr(game.handler, "textobjs"):
    ###        t = getattr(game.handler, "textobjs")
    ###        message = QuickHelp.get(helpname, None)
    ###        if message and pref.comments >= 1:
    ###            t.append(objtext.Text(message))

    game.handler = GameHelp(game.handler, helpname, helppos)



class GameHelp:
    def __init__(self, prevhandler, helpname, helppos):
        self.prevhandler = prevhandler
        self.helpname = helpname
        self.helppos = helppos
        self.time = 0.0
        self.img = None
        self.rect = None
        self.needdraw = 1
        self.done = 0
        if snd.music:
            vol = snd.music.get_volume()
            if vol:
                snd.music.set_volume(vol * 0.6)
        snd.play('chimein')

        if hasattr(game.handler, 'player'):
            game.handler.player.cmd_turbo(0)

    def quit(self):
        snd.play('chimeout')
        if snd.music:
            snd.tweakmusicvolume()
        if self.rect:
            r = self.rect.inflate(2, 2)
            r = self.prevhandler.background(r)
            gfx.dirty(r)
        game.handler = self.prevhandler
        self.done = 1

    def input(self, i):
        if self.time > 30.0:
            self.quit()

    def event(self, e):
        pass


    def drawhelp(self, name, pos):
        if Help.has_key(name):
            text = Help[name]
            lines = text.splitlines()
            for x in range(1, len(lines)):
                if lines[x] == '$':
                    lines[x] = "\n"
                if lines[x] == '-':
                    lines[x] = "\n\n"
            title = lines[0]
            text = ' '.join(lines[1:])
        else:
            title = name
            text = "no help available"

        self.img = fonts[0].textbox((255, 240, 200), text, 260, (50, 100, 50), 30)
        r = self.img.get_rect()
        titleimg, titlepos = fonts[1].text((255, 240, 200), title, (r.width/2, 10))
        self.img.blit(titleimg, titlepos)
        r.topleft = pos
        r = r.clamp(game.arena)
        alphaimg = pygame.Surface(self.img.get_size())
        alphaimg.fill((50, 100, 50))
        alphaimg.set_alpha(192)
        gfx.surface.blit(alphaimg, r)
        self.img.set_colorkey((50, 100, 50))
        self.rect = gfx.surface.blit(self.img, r)
        gfx.dirty(self.rect)


    def run(self):
        if self.needdraw:
            self.needdraw = 0
            self.drawhelp(self.helpname, self.helppos)

        ratio = game.clockticks / 25
        speedadjust = max(ratio, 1.0)
        self.time += speedadjust

        if not self.done:
            pts = (self.rect.topleft, self.rect.topright,
                  self.rect.bottomright, self.rect.bottomleft)
            s = gfx.surface
            clr = 40, 80, 40
            gfx.dirty(pygame.draw.line(s, clr, pts[0], pts[1]))
            gfx.dirty(pygame.draw.line(s, clr, pts[1], pts[2]))
            gfx.dirty(pygame.draw.line(s, clr, pts[2], pts[3]))
            gfx.dirty(pygame.draw.line(s, clr, pts[3], pts[0]))
            off = int(self.time * 0.9)
            r = 255
            g = int(220 + math.cos(self.time * .2) * 30)
            b = int(180 + math.cos(self.time * .2) * 65)
            clr = r, g, b
            gfx.drawvertdashline(s, pts[0], pts[3], clr, 10, off)
            gfx.drawvertdashline(s, pts[1], pts[2], clr, 10, -off)
            gfx.drawhorzdashline(s, pts[0], pts[1], clr, 10, off)
            gfx.drawhorzdashline(s, pts[3], pts[2], clr, 10, -off)

        #gfx.updatestars(self.background, gfx)

    def background(self, area):
        return gfx.surface.fill((0, 0, 0), area)



