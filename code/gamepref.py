"""Game Settings Control for Spacewar."""
import string, math
import pygame
from pygame.locals import *
import game, pref
import gfx, snd, txt
import input
import gameplay

# Values must be integers
Prefs = {
0: ("game_mode", (("Normal", 1), ("1 Player Tutorial", 2))),
1: ("player_1", (("Human", 1), ("Computer", 2))),
2: ("player_2", (("Human", 1), ("Computer", 2), ("Off", 0))),
3: ("player_3", (("Human", 1), ("Computer", 2), ("Off", 0))),
4: ("player_4", (("Human", 1), ("Computer", 2), ("Off", 0))),
5: ("win_score", (("1", 1), ("5", 5), ("7", 7), ("10", 10), ("21", 21))),
6: ("scoring", (("Death Subtract", 0), ("Never Subtract", 1))),
7: ("sun", (("None", 0), ("Tethered", 1), ("Floating", 2), ("Black Hole", 3))),
8: ("fire_damage", (("Low", 20), ("Medium", 50), ("Normal", 80), ("Super", 120))),
9: ("gravity_const", (("Weak", 10), ("Normal", 20), ("Strong", 40))),
10: ("spike_rate", (("Infrequent", 60), ("Normal", 30), ("Frequent", 10))),
11: ("shield_powerup_rate", (("Infrequent", 40), ("Normal", 20), ("Frequent", 12))),
12: ("bullet_powerup_rate", (("Infrequent", 70), ("Normal", 40), ("Frequent", 20))),
13: ("heal_rate", (("Slow", 1), ("Normal", 3), ("Fast", 10))),
14: ("death_time", (("Quick", 3), ("Normal", 5), ("Slow", 10))),
15: ("graphics", (("Minimal", 0), ("Smoke", 1), ("Smoke and Stars", 2))),
16: ("display", (("Window", 0), ("Fullscreen", 1))),
17: ("music", (("Off", 0), ("Low", 1), ("Normal", 2))),
18: ("volume", (("Off", 0), ("Low", 1), ("Normal", 2))),
}

linesize = 20
fontsize1 = 25
fontsize2 = 22

def load_prefs():
    try:
        filename = game.make_dataname('prefs')
        for line in open(filename).readlines():
            name, val = [s.strip() for s in line.split('=')]
            setattr(pref, name, int(val))
    except (IOError, OSError, KeyError):
        #print 'ERROR OPENING PREFS FILE'
        pass


def save_prefs():
    try:
        filename = game.make_dataname('prefs')
        f = open(filename, 'w')
        for key in Prefs.keys():
            p = Prefs[key][0]
            val = getattr(pref, p)
            f.write("%s = %d\n" % (p, int(val)))
        f.close()
    except (IOError, OSError), msg:
        #print 'ERROR SAVING PREFS FILE'
        pass


images = []
namefont = None
valuefont = None


def load_game_resources():
    global images, namefont, valuefont

    timg = pygame.transform.rotate(gfx.load('ship-mini-boost2.png'), -90)
    img = pygame.transform.scale(timg, (20, 20))
    images.append((img, img.get_rect()))

    img = gfx.load('menu_setup_on.png')
    images.append((img, img.get_rect().move(20, 20)))

    namefont = txt.Font(None, fontsize1)
    valuefont = txt.Font(None, fontsize2)

    snd.preload('select_choose', 'select_move', 'delete')



class GamePref:
    def __init__(self, prevhandler):
        self.prevhandler = prevhandler
        self.images = images
        self.prefs = []
        items = Prefs.items()
        sort = lambda x,y: (x[0] < y[0] and -1) or (x[0] > y[0] and 1) or 0
        items.sort(sort)
        for p in items:
            n = p[1][0]
            v = p[1][1]
            self.prefs.append((n,v))
        self.prefs.append(("", (("Return To Menu",),)))

        self.done = 0
        self.aborted = 0
        self.gamelist = []
        self.buildlabels()
        self.buildlist()
        self.current = [0, 0]
        self.shipmovex = 40
        self.shipmovey = 16

        step = 0

        self.moveto(self.gamelist[0][0][1])


    def starting(self):
        #snd.playmusic('gamestart.wav')
        pass


    def moveto(self, pos):
        self.shippos = pos[0], pos[1]


    def input(self, i):
        if self.done:
            return
        if i.release:
            return
        if i.translated == input.ABORT:
            self.aborted = 1
            self.done = 1
            self.current[0] = -1
            self.clearlist()
            self.moveto((2, 2))
            snd.play('select_choose')
        if i.translated == input.PRESS:
            return self.pressed()

        if i.translated in (input.DOWN, input.UP, input.LEFT, input.RIGHT):
            if i.translated == input.DOWN:
                self.current[0] = (self.current[0]+1) % len(self.gamelist)
                self.current[1] = min(self.current[1], len(self.gamelist[self.current[0]])-1)
            elif i.translated == input.UP:
                self.current[0] = (self.current[0]-1) % len(self.gamelist)
                self.current[1] = min(self.current[1], len(self.gamelist[self.current[0]])-1)
            elif i.translated == input.LEFT:
                self.current[1] = (self.current[1]-1) % len(self.gamelist[self.current[0]])
            else:
                self.current[1] = (self.current[1]+1) % len(self.gamelist[self.current[0]])
            snd.play('select_move')
            x = self.gamelist[self.current[0]][self.current[1]][1].left
            y = self.gamelist[self.current[0]][self.current[1]][1].top
            self.moveto((x, y))

    def event(self, e):
        pass

    def run(self):
        r = self.background(self.images[0][1])
        gfx.dirty(r)

        self.moveship()
        gfx.updatestars(self.background, gfx)

        if not self.done:
            self.drawlist()
            for img in self.images:
                r = gfx.surface.blit(img[0], img[1])
                gfx.dirty(r)
        else:
            game.handler = self.prevhandler
            self.clearlist()
            for img in self.images[1:]:
                r = self.background(img[1])
                gfx.dirty(r)


    def background(self, area):
        return gfx.surface.fill((0, 0, 0), area)


    def buildlabels(self):
        clr = 160, 200, 250
        x, y = 245, 140
        for p, vals in self.prefs:
            p = p.replace("_", " ")
            p = p.capitalize()
            imgpos = namefont.text(clr, p, (x,y), "midright")
            images.append(imgpos)
            y += linesize

    def buildlist(self):
        clr = 220, 230, 240
        clr2 = 140, 150, 160
        offsetx, offsety = 290, 140
        self.clearlist()
        self.gamelist = []
        for p, vals in self.prefs:
            x = offsetx
            y = offsety
            if not p:
                y += 30
            allvals = []
            valpos = -1
            if p:
                realval = getattr(pref, p)
                for pnum in Prefs.keys():
                    if Prefs[pnum][0] == p:
                        for i in range(len(Prefs[pnum][1])):
                            if realval == Prefs[pnum][1][i][1]:
                                valpos = i
                        break
            i = 0
            for val in vals:
                if i == valpos:
                    c = clr
                else:
                    c = clr2
                imgpos = valuefont.text(c, val[0], (x,y), "midleft")
                allvals.append(imgpos)
                x = imgpos[1].right + 60
                i += 1
            self.gamelist.append(allvals)
            offsety += linesize


    def clearlist(self):
        for vals in self.gamelist:
            for v in vals:
                gfx.dirty(self.background(v[1]))

    def drawlist(self):
        for vals in self.gamelist:
            for v in vals:
                gfx.dirty(gfx.surface.blit(*v))

    def moveship(self):
        pos = list(self.images[0][1].topright)
        if pos[0] + self.shipmovex < self.shippos[0]:
            pos[0] += self.shipmovex
        elif pos[0] < self.shippos[0]:
            pos[0] = self.shippos[0]

        if pos[0] - self.shipmovex > self.shippos[0]:
            pos[0] -= self.shipmovex
        elif pos[0] > self.shippos[0]:
            pos[0] = self.shippos[0]

        if pos[1] + self.shipmovey < self.shippos[1]:
            pos[1] += self.shipmovey
        elif pos[1] < self.shippos[1]:
            pos[1] = self.shippos[1]

        if pos[1] - self.shipmovey > self.shippos[1]:
            pos[1] -= self.shipmovey
        elif pos[1] > self.shippos[1]:
            pos[1] = self.shippos[1]

        self.images[0][1].topright = pos


    def pressed(self):
        p, vals = self.prefs[self.current[0]]
        if not p:
            snd.play('select_choose')
            self.done = 1
        else:
            val = vals[self.current[1]][1]
            oldval = getattr(pref, p)
            if oldval == val:
                return
            setattr(pref, p, val)
            self.buildlist()
            #some of these need callbacks, music/volume/display
            if hasattr(self, "do_" + p):
                getattr(self, "do_" + p)()
            snd.play('select_choose')


    def do_music(self):
        snd.tweakmusicvolume()

    def do_display(self):
        gfx.switchfullscreen()

