#hud class

import pygame
from pygame.locals import *
import game, pref, gfx, txt


hudimage = None
livesfont = None
gamefont = None
smallfont = None
shipimg = []

def load_game_resources():
    global livesfont, gamefont, smallfont, shipimg
    shipimg.append(gfx.load('ship1-up.png'))
    shipimg.append(gfx.load('ship2-up.png'))
    shipimg.append(gfx.load('ship3-up.png'))
    shipimg.append(gfx.load('ship4-up.png'))
    livesfont = txt.Font(None, 30)
    gamefont = txt.Font(None, 28)
    smallfont = txt.Font(None, 20)

class HUD:
    def __init__(self, player_array):
        self.imghud = gfx.load('hud.png')
        self.imghealth = gfx.load('health_back.png')
        self.players = player_array
        self.ticks = 0
        self.drawsurface = gfx.surface
        self.drawoffset = 800, 0
        self.lastplayer = 0

    def setwidth(self, width):
        width = max(min(width, 100), 0)
        oldwidth = 800 - self.drawoffset[0]
        if width == oldwidth:
            return
        self.drawsurface = gfx.surface.subsurface(800-width, 0, width, 600)
        self.drawoffset = 800-width, 0

        self.drawsurface.blit(self.imghud, (0, 0))

        gfx.surface.set_clip(0, 0, 800-width, 600)
        if oldwidth > width:
            r = game.handler.background((800-oldwidth, 0, oldwidth-width, 600))
            gfx.dirty(r)

        self.drawships(self.lastplayer)
        self.drawstats()

        gfx.dirty((800-width, 0, width, 600))

    # 20 margin at the bottomm and top
    # 100 at top for game stats
    # So below each ship is at most 83 pixels
    def drawstats(self):
        dest = self.drawsurface
        offset = self.drawoffset
        # Game Title
        txt = 'Spacewar'
        pos = 50, 20
        txt,pos = gamefont.text((150,170,200), txt, pos, 'center')
        r1 = dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)
       
        # Game time title
        txt = 'Time:'
        pos = 10, 40
        txt,pos = smallfont.text((150,150,150), txt, pos, 'topleft')
        r1 = dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)

        # Game deaths title
        txt = 'Deaths:'
        pos = 10, 60
        txt,pos = smallfont.text((150,150,150), txt, pos, 'topleft')
        r1 = dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)

        # Game kills title
        txt = 'Kills:'
        pos = 10, 80
        txt,pos = smallfont.text((150,150,150), txt, pos, 'topleft')
        r1 = dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)

        self.drawtime()
        self.drawkills_deaths()

    def drawtime(self):
        dest = self.drawsurface
        offset = self.drawoffset
        # Game Time
        redraw = (50, 40, 40, 20)
        r1 = dest.blit(self.imghud, redraw, redraw).move(offset)
        secs = int(self.ticks / pref.frames_per_sec)
        txt1 = '%d' % secs
        pos = 90, 40
        txt,pos = smallfont.text((150,150,150), txt1, pos, 'topright')
        dest.blit(txt, pos).move(offset)

        gfx.dirty(r1)

    def drawkills_deaths(self):
        dest = self.drawsurface
        offset = self.drawoffset
        # Game Deaths
        deaths = 0
        for player in self.players:
            deaths += player.deaths
        redraw = (50, 60, 40, 20)
        r1 = dest.blit(self.imghud, redraw, redraw).move(offset)
        txt1 = '%d' % deaths
        pos = 90, 60
        txt,pos = smallfont.text((150,150,150), txt1, pos, 'topright')
        dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)
        
        # Game Kills
        kills = 0
        for player in self.players:
            kills += player.score
        redraw = (50, 80, 40, 20)
        r1 = dest.blit(self.imghud, redraw, redraw).move(offset)
        txt1 = '%d' % kills
        pos = 90, 80
        txt,pos = smallfont.text((150,150,150), txt1, pos, 'topright')
        dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)


    def drawships(self, player):
        dest = self.drawsurface
        offset = self.drawoffset
        players = pref.player_cnt()
        space_each = (600-140)/players
        self.last_player = player
        for i in range(player):
            ship = self.players[i].ship

            # Player ship image
            poslevel = Rect(50-16, 120+(i*space_each), 1, 1)
            r1 = dest.blit(shipimg[ship.shipnum], poslevel).move(offset)
            gfx.dirty(r1)
           
            # Player scores
            txt = '%d' % self.players[i].score
            pos = 10, 145+(i*space_each)
            txt,pos = gamefont.text((200,200,150), txt, pos, 'topleft')
            r = Rect(pos[0], pos[1], txt.get_width(), txt.get_height())
            redraw = (r[0], r[1], 80, r[3])
            r2 = dest.blit(self.imghud, redraw, redraw).move(offset)
            r1 = dest.blit(txt, pos).move(offset)
            gfx.dirty2(r1,r2)

            # Health and shield background
            area = 6, 171+(i*space_each), 88, 39
            r1 = dest.blit(self.imghealth, area).move(offset)
            # Health bar
            width = int(80 * ship.health / ship.max_health)
            area = 10, 175+(i*space_each), width, 15
            c = ship.mycolor
            color = (c[0] + 50, c[1] + 50, c[2] + 50)
            dest.fill(color, area).move(offset)
            # Shield bar
            width = int(80 * ship.shield / ship.max_shield)
            area = 10, 198+(i*space_each), width, 8
            color = (255, 200, 0)
            dest.fill(color, area).move(offset)
            gfx.dirty(r1)


    def draw(self):
        self.ticks +=1
        self.drawtime()
        if not self.ticks % 5:
            players = pref.player_cnt()
            self.drawships(players)
            self.drawkills_deaths()

