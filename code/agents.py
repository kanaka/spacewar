from pygame import key
from pygame.locals import *
import random
import pref
import ai

class Agent:
    def __init__(self, playernum, ship):
        self.playernum = playernum
        self.ship = ship
        self.ship.player = self
        self.score = 0
        self.deaths = 0
        
        self.complement = 0
        self.insult = 0

    def do_action(self):
        pass

class HumanAgent(Agent):
    PK_LEFT = (K_LEFT, K_a, K_j, K_KP2)
    PK_RIGHT = (K_RIGHT, K_d, K_l, K_KP8)
    PK_REVERSE = (K_DOWN, K_s, K_k, K_KP5)
    PK_THRUST = (K_UP, K_w, K_i, K_KP4)
    PK_FIRE = (K_RCTRL, K_TAB, K_SPACE, K_KP0)

    def do_action(self, keyset=None):
        if keyset == None:
            keyset = self.ship.shipnum
        if self.ship.dead: 
            self.ship.cmd_turn_off()
            self.ship.cmd_thrust_off()
            return
        if key.get_pressed()[self.PK_LEFT[keyset]]:
            self.ship.cmd_left()
        elif key.get_pressed()[self.PK_RIGHT[keyset]]:
            self.ship.cmd_right()
        else:
            self.ship.cmd_turn_off()
        if key.get_pressed()[self.PK_REVERSE[keyset]]:
            self.ship.cmd_reverse()
        elif key.get_pressed()[self.PK_THRUST[keyset]]:
            self.ship.cmd_turbo()
        else:
            self.ship.cmd_thrust_off()
        if key.get_pressed()[self.PK_FIRE[keyset]]:
            self.ship.cmd_fire()


#class AIAgent(Agent):
#    def __init__(self, playernum, ship):
#        Agent.__init__(self, playernum, ship)
#        self.start()
#
#    def start(self):
#        self.ticks = 0
#        self.turn_to = -1
#        self.turbo_for = -1
#
#    def do_action(self):
#        if self.ship.dead:
#            self.start()
#            return
#        self.ticks +=1
#        if self.turbo_for > -1:
#            self.turbo_for -=1
#            if self.turbo_for < 0:
#                self.ship.cmd_thrust_off()
#            else:
#                self.ship.cmd_turbo()
#        if self.turn_to > -1:
#            dirdiff = self.ship.dir - self.turn_to
#            if abs(dirdiff > 20): dirdiff = -dirdiff
#            if dirdiff == 0:
#                self.ship.cmd_turn_off()
#                self.turn_to = -1
#            elif dirdiff > 0:
#                self.ship.cmd_right()
#            else:
#                self.ship.cmd_left()
#
#class AIAgent_Docile(AIAgent):
#    def do_action(self):
#        AIAgent.do_action(self)
#        if self.turbo_for < 0 and random.randint(0, 40) == 0:
#            self.turbo_for = random.randint(5, pref.frames_per_sec/2)
#        if self.turn_to < 0 and random.randint(0, 20) == 0:
#            self.turn_to = random.randint(0, pref.compass_dirs-1)
#
#class AIAgent_Dumb(AIAgent):
#    def do_action(self):
#        AIAgent.do_action(self)
#        if self.turbo_for < 0 and random.randint(0, 40) == 0:
#            self.turbo_for = random.randint(5, pref.frames_per_sec/2)
#        if self.turn_to < 0 and random.randint(0, 20) == 0:
#            self.turn_to = random.randint(0, pref.compass_dirs-1)
#        if random.randint(0, 40) == 0:
#            self.ship.cmd_fire()

class DNAAgent(Agent):
    def __init__(self, playernum, ship, dna, objs=[]):
        Agent.__init__(self, playernum, ship)
        ###self.dna = random.choice(ai.dna_pool)
        ###print "dna_pool: ", ai.dna_pool
        ###print "dna selected: ", self.dna
        self.dna = dna
        self.obj_list = objs
        self.start()
    
    def start(self):
        self.last_gene = None
        self.cur_action = 0

    def choose_gene(self):
        found = 0
        for gene in self.dna.gene:
            for object in self.obj_list[0] + self.obj_list[1]:
                if object != self.ship and gene.test(self.ship, object):
                    found = 1
                    break
            if found: break
        if not found:
            gene = ai.null_gene
        return gene

    def do_action(self):
        gene = self.choose_gene()
        if gene != self.last_gene:
            self.last_gene = gene
            self.cur_action = 0
        if gene.action[self.cur_action] == "left":
            self.ship.cmd_left()
        elif gene.action[self.cur_action] == "right":
            self.ship.cmd_right()
        else:
            self.ship.cmd_turn_off()
        if gene.action[self.cur_action] == "thrust":
            self.ship.cmd_turbo()
        elif gene.action[self.cur_action] == "rthrust":
            self.ship.cmd_reverse()
        else:
            self.ship.cmd_thrust_off()
        if gene.action[self.cur_action] == "fire":
            self.ship.cmd_fire()
        actions = len(gene.action)
        self.cur_action = (self.cur_action + 1) % actions
