"gameplay handler. for the main part of the game"

import pygame
from pygame.locals import *
import random

import game, pref, gfx, input, snd
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
        self.ships = []
        self.ships.append(objs.Ship(x=game.arena.right-50, 
                                   y=game.arena.bottom-50, player=0))
        #self.ships[0].shield = 100.0
        #self.ships[0].score = 9
        if pref.players > 1:
            self.ships.append(objs.Ship(x=game.arena.left+50, 
                                       y=game.arena.top+50, player=1))
        if pref.players > 2:
            self.ships.append(objs.Ship(x=game.arena.right-50, 
                                       y=game.arena.top+50, player=2))
        if pref.players > 3:
            self.ships.append(objs.Ship(x=game.arena.left+50, 
                                       y=game.arena.bottom-50, player=3))

        self.hud = hud.HUD(self.ships)

        self.state = ''
        self.statetick = self.dummyfunc

        self.lasttick = pygame.time.get_ticks()
        self.start_player = 0
        self.speedadjust = 1.0
        self.startmusic = 1
        self.song = ''
        self.songtime = 0

        self.changestate('gamestart')

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
                if game.handler is self: # in case some "help" gets in first
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

        if pref.players > 1:
            # Normal: do input for each player
            for ship in self.ships:
                ship.do_input() # Do input for each player/ship
        else:
            # Tutorial: everything controls player 1
            player = 0
            for i in range(4):
                if (pygame.key.get_pressed()[objs.Ship.PK_LEFT[i]] or
                    pygame.key.get_pressed()[objs.Ship.PK_RIGHT[i]] or
                    pygame.key.get_pressed()[objs.Ship.PK_REVERSE[i]] or
                    pygame.key.get_pressed()[objs.Ship.PK_THRUST[i]] or
                    pygame.key.get_pressed()[objs.Ship.PK_FIRE[i]]):
                    player = i
            self.ships[0].do_input(player=player)

        self.statetick()

        if pref.graphics == 2:
            gfx.updatestars(self.background, gfx)
        
        objs.runobjects(self.speedadjust)
        
        if self.state == 'normal':
            self.hud.draw()

    def gotfocus(self):
        pass
    def lostfocus(self):
        if game.handler is self:
            game.handler = gamepause.GamePause(self)

    def background(self, area):
        return gfx.surface.fill(0, area)
        #return self.bgfill((70,70,70), area)


#normal play
    def normal_start(self):
        if pref.players == 1:
            gamehelp.help("introduction", (250, 100))

    def normal_tick(self):
        self.clocks += 1

        # Check for tutorial stuff
        if pref.players == 1 and pygame.key.get_pressed()[K_F1]:
            gamehelp.help("keys", (250, 100))
        if pref.players == 1 and self.clocks == objs.frames_per_sec*7:
            gamehelp.help("powerups", (250, 100))
            bobble = objs.Bobble(0,0,0,0)
            bobble.dead = 1
            bobble.pending_frames = objs.frames_per_sec
            objs.pend.append(bobble)
        if pref.players == 1 and self.clocks == objs.frames_per_sec*15:
            gamehelp.help("spikes", (250, 100))
            spike = objs.Spike(0,0,0,0)
            spike.dead = 1
            spike.pending_frames = objs.frames_per_sec
            objs.pend.append(spike)
        if pref.players == 1 and self.clocks == objs.frames_per_sec*3:
            gamehelp.help("opponents", (250, 100))
            ship = objs.Ship(x=game.arena.right-50, 
                                       y=game.arena.top+50, player=2)
            self.ships.append(ship)
            objs.low.append(ship)


        # Check for winner, complements and insults
        for ship in self.ships:
            if ship.score >= pref.win_score:
                self.changestate('gameover')
                break
            if ship.complement:
                ship.complement = 0
                complement = random.randint(0, len(game.Complements)-1)
                objs.virtual.append(objtext.Text(game.Complements[complement]))
            if ship.insult:
                ship.insult = 0
                insult = random.randint(0, len(game.Insults)-1)
                objs.virtual.append(objtext.Text(game.Insults[insult]))

#appear
    def appear_start(self):
        snd.play('startlife', 1.0, gfx.rect[2] / 2)
        self.hud.drawships(pref.players)
        for ship in self.ships:
            teleport = objs.Tele(ship.x, ship.y)
            objs.virtual.append(teleport)
        self.lastteleport = teleport

        if pref.sun:
            objs.low.append(objs.Sun())

    def appear_tick(self):
        #when animations done
        if self.lastteleport.dead:
            self.changestate('normal')
            for ship in self.ships:
                objs.low.append(ship)

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
            if not self.ticks % 30 and self.start_player < pref.players:
                self.start_player += 1
                self.hud.drawships(self.start_player)
                snd.play('shoot')
            if self.start_player == pref.players:
                self.changestate('appear')

    def gamestart_end(self):
        if pref.comments >= 1:
            objs.virtual.append(objtext.Text('Begin'))
        del self.ticks
        
        self.hud.drawstats()
        if pref.comments >= 2:
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
        for ship in self.ships:
            if ship.score >= pref.win_score:
                text = "Player %d wins!" % (ship.player+1)
                length = game.text_length * 2
                objs.virtual.append(objtext.Text(text, text_length=length))
            else:
                if not ship.dead:
                    ship.dead = 1
                    explosion = objs.Explosion(ship.x,ship.y,
                                               ship.vel_x,ship.vel_y)
                    explosion.mass = ship.mass
                    objs.high[0:0] = [explosion]
                ship.erase()
                try:
                    objs.low.remove(ship)
                except:
                    pass

    def gameover_tick(self):
        objs.pend = []
        if self.ticks:
            self.ticks -= 1
        self.hud.setwidth(self.ticks * 20)
        if not self.ticks and not objs.virtual and not objs.vapors:
            for x in objs.vapors + objs.low + objs.high: x.dead = 2
            game.handler = self.prevhandler

        for l in objs.list:
            for o in l:
                o.erase()
