"gameplay handler. for the main part of the game"

import pygame
from pygame.locals import *
import random

import game, gfx, input, snd
import gamehelp, gamepause
import objs, objtext, hud


Songs = [('arg.xm', 1.0), ('h2.ogg', 0.6)]

def load_game_resources():
    snd.preload('gameover', 'startlife', 'levelskip', 'explode')
    snd.preload('boxhot', 'levelfinish', 'shoot', 'whip', 'klank2')
    snd.preload('spring', 'flop')


class GamePlay:
    def __init__(self, prevhandler):
        self.prevhandler = prevhandler
        self.ship = []
        self.ship.append(objs.Ship(x=game.arena.right-50, 
                                   y=game.arena.bottom-50, player=0))
        #self.ship[0].shield = 1
        self.ship.append(objs.Ship(x=game.arena.left+50, 
                                   y=game.arena.top+50, player=1))
        if game.player_cnt > 2:
            self.ship.append(objs.Ship(x=game.arena.right-50, 
                                       y=game.arena.top+50, player=2))
        if game.player_cnt > 3:
            self.ship.append(objs.Ship(x=game.arena.left+50, 
                                       y=game.arena.bottom-50, player=3))

        self.hud = hud.HUD(self.ship)

        self.state = ''
        self.statetick = self.dummyfunc

        self.lasttick = pygame.time.get_ticks()
        self.start_player = 0
        self.speedadjust = 1.0
        self.startmusic = 1
        self.song = ''
        self.songtime = 0

        self.changestate('gamestart')

        self.bgfill = gfx.surface.fill

    def starting(self):
        if self.startmusic:
            self.startmusic = 0
            self.song = random.choice(Songs)
            snd.playmusic(*self.song)
            self.songtime = pygame.time.get_ticks()
        gfx.dirty(self.background(gfx.rect))

    def changestate(self, state):
        getattr(self, self.state+'_end', self.dummyfunc)()
        self.state = state
        getattr(self, state+'_start', self.dummyfunc)()
        self.statetick = getattr(self, state+'_tick')

    def dummyfunc(self): pass

    def userquit(self):
        if self.state == 'gameover': return
        self.changestate('gameover')

    def input(self, i):
        if i.release:
            pass
        else:
            if i.translated == input.ABORT:
                self.userquit()

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            #What are you doing? Looking for Cheats?
            #shame shame
            if input.Cheatstring == "joel":
                snd.play('gameover')
                snd.play('delete')
                game.player.cheater = 1
                objs.virtual.append(objtext.Text('"joel" Cheat: <desc>'))
                # *** TODO: implement cheat
            if e.key == pygame.K_PAUSE or e.key == pygame.K_p:
                if game.handler is self: #just in case some "help" gets in first?
                    game.handler = gamepause.GamePause(self)

    def run(self):
        if game.handler is not self: #help or pause is taking over
            return
        ratio = game.clockticks / 25
        self.speedadjust = max(ratio, 1.0)
        if game.speedmult >= 2:
            self.speedadjust *= 0.5
        elif game.speedmult: #if true must be 1
            self.speedadjust *= 0.75

        # Do input for each player/ship
        for i in range(game.player_cnt):
            self.ship[i].do_input()

        self.statetick()

        self.runobjects()
        
        if self.state == 'normal':
            self.hud.draw()

    def gotfocus(self):
        pass
    def lostfocus(self):
        if game.handler is self:
            game.handler = gamepause.GamePause(self)


    def runobjects(self):
        B, S = self.background, self.speedadjust
        gfx.updatestars(B, gfx)
        
        # Gravitate
        for o1 in objs.vapors + objs.low + objs.high:
            for o2 in objs.low + objs.high:
                if o1 is not o2:
                    o1.gravitate(o2)

        # Erase and tick visible objects
        for l in objs.list:
            for o in l[:]:
                o.erase(B)
                o.tick(S)

        # Tick pending objects
        for o in objs.pend:
            o.tick(S)
            if not o.dead:
                if o.__class__ == objs.Ship:
                    objs.pend.remove(o)
                    objs.low.append(o)
                if o.__class__ == objs.Spike:
                    objs.pend.remove(o)
                    objs.low.append(o)
       
        # Check for collisions, skip virtual and pending objects
        for o1 in objs.low + objs.high:
            for o2 in objs.low + objs.high:
                if o1 is not o2:
                    if o1.clearance(o2) < 0:
                        o1.hit_by(o2)
                        o2.hit_by(o1)

        # Check all objects for death
        for l in objs.list:
            for o in l[:]:
                if o.dead:
                    o.erase(B)
                    l.remove(o)
                    # Put ships on pending list
                    if o.__class__ == objs.Ship:
                        objs.pend.append(o)
                    # Replace fires with pops
                    if o.__class__ == objs.Fire and o.dead != 2:
                        vel_x = o.vel_x
                        vel_y = o.vel_y
                        if o.dead_by_hit:
                            vel_x = vel_x / 5
                            vel_y = vel_y / 5
                            snd.play('shoot', 1.0, o.rect.centerx)
                        objs.vapors.append(objs.Pop(o.x, o.y, vel_x, vel_y))

        for l in objs.list:
            for o in l[:]:
                o.draw()

    def background(self, area):
        return self.bgfill(0, area)
        #return self.bgfill((70,70,70), area)


#normal play
    def normal_tick(self):
        self.clocks += 1
        if random.randint(0,objs.spike_rate) == 1:
            pass
            spike = objs.Spike(0,0,0,0)
            spike.dead = 1
            spike.pending_frames = objs.frames_per_sec
            objs.pend.append(spike)

#appear
    def appear_start(self):
        snd.play('startlife', 1.0, gfx.rect[2] / 2)
        self.hud.drawships(game.player_cnt)
        for i in range(game.player_cnt):
            teleport = objs.Tele(self.ship[i].x, self.ship[i].y)
            objs.virtual.append(teleport)
        self.lastteleport = teleport

        objs.low.append(objs.Sun())

    def appear_tick(self):
        #when animations done
        if self.lastteleport.dead:
            self.changestate('normal')
            for i in range(game.player_cnt):
                objs.high.append(self.ship[i])

    def appear_end(self):
        input.resetexclusive()
        input.postactive()
        
        self.clocks = 0
        # *** TODO: should a help message appear
        #gamehelp.help("player", (250, 100))

#game start
    def gamestart_start(self):
        self.ticks = 0
        self.donehud = 0
        sound = snd.fetch('whip')
        self.whip = None
        if sound:
            self.whip = sound.play(-1)


    def gamestart_tick(self):
        self.ticks += 1
        if not self.donehud:
            self.hud.setwidth(self.ticks * 10)
            if self.ticks == 10:
                self.donehud = 1
                self.ticks = 0
        else:
            if not self.ticks % 3:
                self.hud.drawstats()
            #if not self.ticks % 16 and self.start_player < game.player_cnt:
            if not self.ticks % 16 and self.start_player < game.player_cnt:
                self.start_player += 1
                self.hud.drawships(self.start_player)
            if self.start_player == game.player_cnt:
                self.changestate('appear')

    def gamestart_end(self):
        if game.comments >= 1:
            objs.virtual.append(objtext.Text('Begin'))
        if self.whip:
            self.whip.stop()
        del self.ticks
        del self.whip
        
        self.hud.drawstats()
        if game.comments >= 2:
            objs.virtual.append(objtext.Text(msg))

        #rotate music
        if pygame.time.get_ticks() - self.songtime > game.musictime:
            songs = list(Songs)
            songs.remove(self.song)
            self.song = random.choice(songs)
            snd.playmusic(*self.song)
            self.songtime = pygame.time.get_ticks()

#game over
    def gameover_start(self):
        snd.play('gameover')
        self.ticks = 5
        objs.virtual.append(objtext.Text('Game Over'))

        # Clean-up the ships
        for i in range(game.player_cnt):
            self.ship[i].dead = 1
            self.ship[i].erase(self.background)
            try:
                objs.high.remove(self.ship[i])
            except:
                pass
        objs.pend = []

    def gameover_tick(self):
        if self.ticks:
            self.ticks -= 1
        self.hud.setwidth(self.ticks * 20)
        if not self.ticks and not objs.virtual and not objs.vapors:
            for x in objs.vapors + objs.low + objs.high: x.dead = 2
            game.handler = self.prevhandler

        B = self.background
        for l in objs.list:
            for o in l:
                o.erase(B)
