#hud class

import pygame
from pygame.locals import *
import game, gfx, txt


hudimage = None
livesfont = None
gamefont = None
shipimg = []

def load_game_resources():
    global livesfont, gamefont, shipimg
    shipimg.append(gfx.load('ship1-up.png'))
    shipimg.append(gfx.load('ship2-up.png'))
    shipimg.append(gfx.load('ship3-up.png'))
    shipimg.append(gfx.load('ship4-up.png'))
    livesfont = txt.Font(None, 30)
    gamefont = txt.Font(None, 28)

class HUD:
    def __init__(self, ship_array):
        self.imghud1 = gfx.load('hud.png')
        self.imghud2 = gfx.load('hud2.gif')
        self.ship = ship_array
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

        self.drawsurface.blit(self.imghud1, (0, 0))

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
        txt = 'Spacewar'
        pos = 50, 20
        txt,pos = gamefont.text((150,150,200), txt, pos, 'center')
        r1 = dest.blit(txt, pos).move(offset)
        gfx.dirty(r1)

    def drawships(self, player):
        dest = self.drawsurface
        offset = self.drawoffset
        space_each = (600-140)/game.player_cnt
        self.last_player = player
        for i in range(player):
            # Draw the player's ship
            poslevel = Rect(50-16, 120+(i*space_each), 1, 1)
            r1 = dest.blit(shipimg[i], poslevel).move(offset)
            gfx.dirty(r1)
           
            # Draw ship scores
            txt = '%d' % self.ship[i].score
            pos = 10, 160+(i*space_each)
            txt,pos = gamefont.text((200,200,150), txt, pos, 'topleft')
            r = Rect(pos[0], pos[1], txt.get_width(), txt.get_height())
            redraw = (r[0], r[1], 80, r[3])
            r2 = dest.blit(self.imghud1, redraw, redraw).move(offset)
            r1 = dest.blit(txt, pos).move(offset)
            gfx.dirty2(r1,r2)


    def draw(self):
        self.ticks +=1
        if not self.ticks % 10:
            self.drawships(game.player_cnt)
        
