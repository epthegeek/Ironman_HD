import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class MBSwitchStop(procgame.game.Mode):
    def __init__(self,game):
        super(MBSwitchStop, self).__init__(game=game, priority=40)
        self.myID = "MBSwitchStop"
        self.valid = [True,True,True]

    def setup(self):
        # checks should be in this oder: Bogey, Whiplash, War Machine, Monger
        self.BO = self.game.bogey
        self.WL = self.game.whiplash_multiball
        self.WM = self.game.wm_multiball
        self.MO = self.game.monger_multiball

    def mode_started(self):
        self.valid = [True,True,True]

    def sw_leftSpinner_active(self, sw):
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    def sw_rightSpinner_active(self, sw):
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    def sw_leftOrbit_active(self, sw):
        noisy = True
        if self.valid[0]:
            self.make_invalid(2)
            # Check War Machine
            if self.WM.running:
                if self.WM.big5_jackpots[0]:
                    self.WM.double_jp_hit(0)
                    noisy = False
            # Check Whiplash
            if self.WL.running:
                self.WL.big5_jackpot_shot()
                noisy = False
        # if nothing hits, play the orbit noise
        if noisy:
            self.game.monger.orbit_noise()
        return procgame.game.SwitchStop

    def sw_leftRampExit_active(self, sw):
        # pass the hit to bogey if bogey is running
        if self.BO.running:
            self.game.bogey.bogey_hit()
        if self.WL.running:
            self.WL.big5_jackpot_shot()
        if self.WM.running:
            self.WM.double_jp_hit(1)
        return procgame.game.SwitchStop

    def sw_centerSpinner_active(self, sw):
        if self.valid:
            self.make_invalid(1)
            if self.WL.running:
                self.WL.big5_jackpot_shot()
            if self.WM.running:
                self.WM.double_jp_hit(2)
        return procgame.game.SwitchStop

    def sw_rightRampExit_active(self, sw):
        # pass the hit to bogey if bogey is running
        if self.BO.running:
            self.game.bogey.bogey_hit()
        if self.WL.running:
            self.WL.big5_jackpot_shot()
        if self.WM.running:
            self.WM.double_jp_hit(3)
        return procgame.game.SwitchStop

    def sw_rightOrbit_active(self, sw):
        noisy = True
        if self.valid[2]:
            self.make_invalid(0)
        # check whiplash
        if self.WL.running:
            self.WL.big5_jackpot_shot()
            noisy = False
        # Check War Machine
        if self.WM.running:
            if self.WM.big5_jackpots[4]:
                self.WM.double_jp_hit(4)
                noisy = False
        if noisy:
            self.game.monger.orbit_noise()
        return procgame.game.SwitchStop


    def make_invalid(self, orbit):
        self.valid[orbit] = False
        self.delay(delay=2, handler=self.validate,param=orbit)

    def validate(self, orbit):
        self.valid[orbit] = True

    def check_remove(self):
        if not self.MO.running \
                and not self.WM.running \
                and not self.WL.running:
            self.unload()