"gameplay handler. for the main part of the game"

import pygame
from pygame.locals import *
import random

import game, pref, gfx, input, snd
import gamehelp, gamepause
import ai, objs, agents, objtext, hud


Songs = [('arg.xm', 1.0), ('h2.ogg', 0.6)]

def load_game_resources():
    snd.preload('gameover', 'startlife', 'levelskip', 'explode')
    snd.preload('boxhot', 'levelfinish', 'shoot', 'whip', 'klank2')
    snd.preload('spring', 'flop')


class GamePlay:
    def __init__(self, prevhandler):
        self.prevhandler = prevhandler
        left = game.arena.left
        top = game.arena.top
        right = game.arena.right
        bottom = game.arena.bottom
        self.players = []
        for num,ppref,x,y in ((0, pref.player_1, right-50, bottom-50),
                              (1, pref.player_2, left+50, top+50),
                              (2, pref.player_3, right-50, top+50),
                              (3, pref.player_4, left+50, bottom-50)):
            if ppref == 1 or pref.game_mode == 2:
                ship = objs.Ship(num, x, y)
                self.players.append(agents.HumanAgent(num, ship))
                if pref.game_mode == 2: break
            elif ppref == 2:
                ship = objs.Ship(num, x, y)
                dna = random.choice(ai.dna_pool)
                ###self.players.append(agents.AIAgent_Dumb(num, ship))
                self.players.append(agents.DNAAgent(num, ship, 
                    dna=dna, objs=[objs.low, objs.high]))
        #self.players[0].ship.shield = 100.0
        #self.players[0].ship.bullet = pref.bbobble_charge

        self.hud = hud.HUD(self.players)

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

    def non_key(self):
        keys = list(pygame.key.get_pressed())
        for i in range(4):
            keys[agents.HumanAgent.PK_LEFT[i]] = 0
            keys[agents.HumanAgent.PK_RIGHT[i]] = 0
            keys[agents.HumanAgent.PK_REVERSE[i]] = 0
            keys[agents.HumanAgent.PK_THRUST[i]] = 0
            keys[agents.HumanAgent.PK_FIRE[i]] = 0
        keys[K_F1] = 0
        keys[K_p] = 0
        if 1 in keys:
            return 1
        else:
            return 0

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            #What are you doing? Looking for Cheats?
            #shame shame
            if input.Cheatstring == "joel":
                snd.play('gameover')
                snd.play('delete')
                objs.virtual.append(objtext.Text('"joel" Cheat: <desc>'))
                # *** TODO: implement cheat
            if e.key == pygame.K_PAUSE or e.key == pygame.K_p:
                if game.handler is self: # in case some "help" gets in first
                    game.handler = gamepause.GamePause(self)

    def gotfocus(self):
        pass
    def lostfocus(self):
        if game.handler is self:
            game.handler = gamepause.GamePause(self)

    def background(self, area):
        return gfx.surface.fill(0, area)
        #return self.bgfill((70,70,70), area)

    def run(self):
        if game.handler is not self: #help or pause is taking over
            return
        ratio = game.clockticks / 25
        self.speedadjust = max(ratio, 1.0)
        if game.speedmult >= 2:
            self.speedadjust *= 0.5
        elif game.speedmult: #if true must be 1
            self.speedadjust *= 0.75

        self.statetick()

        if pref.graphics == 2:
            gfx.updatestars(self.background, gfx)
        
        objs.runobjects(self.speedadjust)
        
        if self.state == 'normal':
            self.hud.draw()

#normal play
    def normal_start(self):
        self.clocks = 0
        self.non_key_cnt = 0.0

    def normal_tick(self):
        self.clocks += 1

        # Handle player input
        if pref.game_mode == 1:
            # Normal: do input for each player
            for player in self.players:
                player.do_action()
        else: # pref.game_mode == 2
            # Tutorial: everything controls player 1
            player = 0
            keys = pygame.key.get_pressed()
            for i in range(4):
                if (keys[agents.HumanAgent.PK_LEFT[i]] or
                    keys[agents.HumanAgent.PK_RIGHT[i]] or
                    keys[agents.HumanAgent.PK_REVERSE[i]] or
                    keys[agents.HumanAgent.PK_THRUST[i]] or
                    keys[agents.HumanAgent.PK_FIRE[i]]):
                    player = i
            self.players[0].do_action(keyset=player)
            # Any AI tutorial players 
            for i in range(1,len(self.players)):
                self.players[i].do_action()
      
        # Give help if player is guessing at keys
        self.non_key_cnt = max (0, self.non_key_cnt - 0.02)
        if self.non_key():
            self.non_key_cnt += 1.0
            if self.non_key_cnt >= 15.0:
                self.non_key_cnt = 0.0
                message = "Press F1 for key list"
                objs.virtual.append(objtext.Text(message))

        # If tutorial mode, show periodic messages
        if pref.game_mode == 2:
            if self.clocks == pref.frames_per_sec*2:
                gamehelp.help("introduction", (250, 100))
            if self.clocks == pref.frames_per_sec*10:
                gamehelp.help("powerups", (250, 100))
                sbobble = objs.ShieldBobble(0,0,0,0)
                sbobble.dead = 1
                sbobble.pending_frames = pref.frames_per_sec
                objs.pend.append(sbobble)
            if self.clocks == pref.frames_per_sec*20:
                gamehelp.help("spikes", (250, 100))
                spike = objs.Spike(0,0,0,0)
                spike.dead = 1
                spike.pending_frames = pref.frames_per_sec
                objs.pend.append(spike)
            if self.clocks == pref.frames_per_sec*3:
                gamehelp.help("opponents", (250, 100))
                ship = objs.Ship(shipnum=1, x=50, y=50)
                objs.low.append(ship)
                ###self.players.append(agents.AIAgent_Docile(1, ship))
                self.players.append(agents.DNAAgent(1, ship))

        # Control key help
        if pygame.key.get_pressed()[K_F1]:
            gamehelp.help("keys", (250, 100))

        # Check for winner, complements and insults
        for player in self.players:
            if pref.game_mode == 1 and player.score >= pref.win_score:
                self.changestate('gameover')
                break
            if player.complement:
                player.complement = 0
                complement = random.randint(0, len(game.Complements)-1)
                objs.virtual.append(objtext.Text(game.Complements[complement]))
            if player.insult:
                player.insult = 0
                insult = random.randint(0, len(game.Insults)-1)
                objs.virtual.append(objtext.Text(game.Insults[insult]))

#appear
    def appear_start(self):
        snd.play('startlife', 1.0, gfx.rect[2] / 2)
        players = pref.player_cnt()
        self.hud.drawships(players)
        for player in self.players:
            teleport = objs.Tele(player.ship.x, player.ship.y)
            objs.virtual.append(teleport)
        self.lastteleport = teleport

        if pref.sun:
            objs.low.append(objs.Sun())

    def appear_tick(self):
        #when animations done
        if self.lastteleport.dead:
            self.changestate('normal')
            for player in self.players:
                objs.low.append(player.ship)

    def appear_end(self):
        input.resetexclusive()
        input.postactive()

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
            players = pref.player_cnt()
            if not self.ticks % 3:
                self.hud.drawstats()
            if not self.ticks % 30 and self.start_player < players:
                self.start_player += 1
                self.hud.drawships(self.start_player)
                snd.play('shoot')
            if self.start_player == players:
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
        for player in self.players:
            if player.score >= pref.win_score:
                text = "Player %d wins!" % (player.playernum+1)
                length = game.text_length * 2
                objs.virtual.append(objtext.Text(text, text_length=length))
            else:
                ship = player.ship
                if not ship.dead:
                    ship.dead = 1
                    explosion = objs.Explosion(ship.x,ship.y,ship.vx,ship.vy)
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
