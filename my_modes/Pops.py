import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Pops(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Pops, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "Pops"
        self.pop_lamps = [self.game.lamps['leftJetBumper'],self.game.lamps['bottomJetBumper'],self.game.lamps['rightJetBumper']]


    def evt_ball_starting(self):
        # set all the pops as unlit
        self.pop_state = [0,0,0]
        self.pop_lit_hits = 0
        # need to check the logic on this - once they're all lit, how many hits?
        self.pop_hits_for_level = 30
        self.level = 0

    def sw_leftJetBumper_active(self,sw):
        self.pop_hit(0)
    def sw_bottomJetBumper_active(self,sw):
        self.pop_hit(1)
    def sw_rightJetBumper_active(self,sw):
        self.pop_hit(2)

    # orbits enable the pops
    def sw_leftOrbit_active(self,sw):
        self.light_pop(0)
    def sw_centerSpinner_active(self,sw):
        self.light_pop(1)
    def sw_rightOrbit_active(self,sw):
        self.light_pop(2)

    def pop_hit(self,number):
        # are they all lit?
        if 0 not in self.pop_state:
            self.super_pop_hit(number)
        else:
            # flash the light
            self.pop_lamps[number].pulse()
            # check if pop is lit
            lit = self.pop_state[number]
            if lit:
                points = 25000
                # sound = some sound
            else:
                points = 5000
                # sound = some other sound
            self.game.score(points)
            # play the sound

    def light_pop(self,number):
        if not self.pop_state[number] == 0:
            self.pop_state[number] = 1
            self.update_lamps()

    def super_pop_hit(self,number):
        self.pop_hits_for_level -= 1
        if self.pop_hits_for_level <= 0:
            # score points
            self.game.score(100000 + (25000 * self.level))
            # count the level
            self.level += 1
            self.pop_hits_for_level = (self.level + 30)

    def update_lamps(self):
        for n in range (0,3,1):
            if self.pop_state[n] == 1:
                self.pop_lamps[n].enable()
            else:
                self.pop_lamps[n].disable()