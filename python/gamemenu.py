"Game main menu handler, part of SPACEWAR."

import math, os
import pygame, pygame.draw
from pygame.locals import *
import var
import gfx, snd, txt
import input
import gamecreds, gamenews, gamepref, gameplay


images = []
boximages = []
yboximages = []
rboximages = []
fame = None

class MenuItem:
    def __init__(self, imgname, handler):
        self.imgname = imgname
        self.handler = handler

    def init(self, pos):
        self.img_on = gfx.load('menu_'+self.imgname+'_on.png')
        self.img_off = gfx.load('menu_'+self.imgname+'_off.png')
        self.rect = self.img_on.get_rect().move(pos)
        self.smallrect = self.img_off.get_rect()
        self.smallrect.center = self.rect.center


def load_game_resources():
    global images, boximages, fame
    images = []
    images.append(gfx.load('menu_on_bgd.png'))
    images[0].set_colorkey(0)
    images.append(gfx.load('logo.png'))
    images.append(gfx.load('ship-big.png'))
    images[1].set_colorkey()
    images[2].set_colorkey()

    global boximages, yboximages, rboximages
    imgs = gfx.load_raw('bigboxes.png')
    origpal = imgs.get_palette()
    boximages = gfx.animstrip(imgs)
    pal = [(g,g,b) for (r,g,b) in origpal]
    imgs.set_palette(pal)
    yboximages = gfx.animstrip(imgs)
    pal = [(g,b,b) for (r,g,b) in origpal]
    imgs.set_palette(pal)
    rboximages = gfx.animstrip(imgs)

    fame = gfx.load('fame.png')

    snd.preload('select_move', 'select_choose')



class GameMenu:
    def __init__(self, prevhandler):
        self.prevhandler = prevhandler
        self.current = 0
        self.glow = 0.0
        self.switchhandler = None
        self.switchclock = 0
        self.startclock = 5
        self.logo = images[1]
        self.logorect = self.logo.get_rect().move(100, 25)
        self.logorectsmall = self.logorect.inflate(-2,-2)
        self.boxtick = 0
        self.boximages = boximages
        self.boxrect = self.boximages[0].get_rect().move(580, 80)
        self.bigship = images[2]
        self.bigshiprect = self.bigship.get_rect().move(450, 250)

        if var.ai_train:
            print "ai_train"
            Player = gameplay.AIPlay
        else:
            print "not ai_train"
            Player = gameplay.GamePlay

        self.menu = [
            MenuItem('start', Player),
            MenuItem('news', gamenews.GameNews),
            MenuItem('creds', gamecreds.GameCreds),
            MenuItem('setup', gamepref.GamePref),
            MenuItem('quit', None),
        ]

        pos = [20, 380] #[100, 420]
        odd = 0
        for m in self.menu:
            m.init(pos)
            pos[0] += 150
            odd = (odd+1)%2
            if odd:
                pos[1] += 20
            else:
                pos[1] -= 20


    def starting(self):
        snd.playmusic('aster2_sw.xm')

        gfx.dirty(gfx.surface.blit(self.logo, self.logorect))
        gfx.dirty(gfx.surface.blit(self.bigship, self.bigshiprect))

        fnt = txt.Font(None, 18)
        self.version = fnt.text((200, 120, 100), 
                'Spacewar Version ' + var.version, (10, 580), 'topleft')

        fnt = txt.Font(None, 22)
        if var.ai_train:
            self.players = fnt.text((200, 175, 120), 
                'AI Training', (115, 500), 'center')
        else:
                if var.game_mode == 2:
                    self.players = fnt.text((200, 175, 120), 
                        '1 player tutorial', (115, 500), 'center')
                else:
                    players = var.player_cnt()
                    self.players = fnt.text((200, 175, 120), 
                        'with %d players' % (players), (115, 500), 'center')

    def quit(self):
        self.current = len(self.menu)-1
        self.workbutton()


    def workbutton(self):
        button = self.menu[self.current]
        if not button.handler:
            self.switchhandler = self.prevhandler
        else:
            self.switchhandler = button.handler
        self.switchclock = 10


    def clearitem(self, item, dirty=0):
        r = self.background(item.rect)
        if dirty:
            gfx.dirty(r)


    def setalphas(self, alpha, extras=[]):
        imgs = []
        menu = self.menu
        selected = menu[self.current]
        imgs.extend([x.img_off for x in menu if x is not selected])
        imgs.extend(extras)
        if gfx.surface.get_bytesize()==1:
            return
        if alpha < 255:
            for i in imgs:
                i.set_alpha(alpha)
        else:
            for i in imgs:
                i.set_alpha()
                c = i.get_colorkey()
                if c:
                    i.set_colorkey(c, RLEACCEL)


    def drawitem(self, item, lit):
        if not lit:
            gfx.surface.blit(item.img_off, item.smallrect)
        else:
            lite = images[0]
            glowval = (math.sin(self.glow) + 2.5) * 50.0
            if self.switchclock == 2:
                glowval /= 2
            if gfx.surface.get_bytesize()>1:
                lite.set_alpha(glowval)
            gfx.surface.blit(lite, item.rect)
            gfx.surface.blit(item.img_on, item.rect)
        gfx.dirty(item.rect)


    def input(self, i):
        if i.release:
            return
        if self.switchclock:
            return
        if i.translated == input.LEFT:
            self.current = (self.current - 1)%len(self.menu)
            snd.play('select_move')
        elif i.translated == input.RIGHT:
            self.current = (self.current + 1)%len(self.menu)
            snd.play('select_move')
        elif i.translated == input.PRESS:
            self.workbutton()
            snd.play('select_choose')
        elif i.translated == input.ABORT:
            snd.play('select_choose')
            self.quit()

    def event(self, e):
        pass


    def run(self):
        menu = self.menu
        self.glow += .35
        self.boxtick = (self.boxtick + 1)%15
        boximg = self.boximages[self.boxtick]

        if self.startclock:
            alpha = (6-self.startclock)*40
            self.setalphas(alpha, [menu[self.current].img_on, boximg])
            self.background(self.boxrect)
        elif self.switchclock:
            alpha = (self.switchclock-1)*20
            self.setalphas(alpha, [boximg])
            self.background(self.boxrect)
            if self.switchclock == 2 and gfx.surface.get_bytesize()>1:
                menu[self.current].img_on.set_alpha(128)

        for m in menu:
            self.clearitem(m)

        gfx.updatestars(self.background, gfx)

        gfx.dirty(gfx.surface.blit(*self.version))
        gfx.dirty(gfx.surface.blit(*self.players))

        if self.startclock == 1 or self.switchclock == 1:
            self.setalphas(255, [menu[self.current].img_on] + self.boximages)

        if self.switchclock != 1:
            r = gfx.surface.blit(boximg, self.boxrect)
            gfx.dirty(r)

            select = menu[self.current]
            for m in [m for m in menu if m is not select]:
                self.drawitem(m, 0)
            self.drawitem(select, 1)

        else:
            for m in menu:
                gfx.dirty(m.rect)
            if self.switchhandler == self.prevhandler:
                var.handler = self.prevhandler
            else:
                var.handler = self.switchhandler(self)
                self.switchclock = 0
                self.switchhandler = None
                self.startclock = 5
            gfx.dirty(self.background(self.version[1]))
            gfx.dirty(self.background(self.players[1]))
            gfx.dirty(gfx.surface.fill((0, 0, 0), self.logorect))
            gfx.dirty(gfx.surface.fill((0, 0, 0), self.bigshiprect))

        if self.startclock:
            self.startclock -= 1
        elif self.switchclock:
            self.switchclock -= 1



    def background(self, area):
        fullr = gfx.surface.fill((0, 0, 0), area)
        if self.switchclock != 1:
            if area.colliderect(self.bigshiprect):
                    r = area.move(-self.bigshiprect.left, -self.bigshiprect.top)
                    return gfx.surface.blit(self.bigship, area, r)
            elif self.switchclock != 1:
                if area.colliderect(self.logorectsmall):
                    r = area.move(-self.logorect.left, -self.logorect.top)
                    return gfx.surface.blit(self.logo, area, r)
        return fullr

