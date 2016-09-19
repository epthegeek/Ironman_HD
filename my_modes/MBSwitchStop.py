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
        self.WM = self.game.wm_multiball
        self.MO = self.game.monger_multiball
        self.WL = self.game.whiplash_multiball

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
        if self.WM.running:
            self.WM.double_jp_hit(1)
        if self.WL.running:
            self.WL.big5_jackpot_shot()
        return procgame.game.SwitchStop

    def sw_centerSpinner_active(self, sw):
        if self.valid:
            self.make_invalid(1)
            if self.WM.running:
                self.WM.double_jp_hit(2)
            if self.WL.running:
                self.WL.big5_jackpot_shot()
        return procgame.game.SwitchStop

    def sw_rightRampExit_active(self, sw):
        if self.WM.running:
            self.WM.double_jp_hit(3)
        if self.WL.running:
            self.WL.big5_jackpot_shot()
        return procgame.game.SwitchStop

    def sw_rightOrbit_active(self, sw):
        noisy = True
        if self.valid[2]:
            self.make_invalid(0)
        # Check War Machine
        if self.WM.running:
            if self.WM.big5_jackpots[4]:
                self.WM.double_jp_hit(4)
                noisy = False
        if self.WL.running:
            self.WL.big5_jackpot_shot()
            noisy = False
        if noisy:
            self.game.monger.orbit_noise()
        return procgame.game.SwitchStop


    def make_invalid(self, orbit):
        self.valid[orbit] = False
        self.delay(delay=2, handler=lambda: self.validate(orbit))

    def validate(self, orbit):
        self.valid[orbit] = True

    def check_remove(self):
        if not self.MO.running \
                and not self.WM.running \
                and not self.WL.running:
            self.unload()