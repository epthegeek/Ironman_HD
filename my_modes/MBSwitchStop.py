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
        self.target_lights = ['leftTargetI','leftTargetR','leftTargetO','leftTargetN','rightTargetM','rightTargetA','rightTargetN']

    def setup(self):
        # checks should be in this oder: Bogey, Whiplash, War Machine, Monger
        self.BO = self.game.bogey
        self.WL = self.game.whiplash_multiball
        self.WM = self.game.wm_multiball
        self.MO = self.game.monger_multiball

    def mode_started(self):
        self.valid = [True,True,True]

    def sw_leftSpinner_active(self, sw):
        # TODO: Check what spinners soundlike in other multiballs... default?
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    def sw_rightSpinner_active(self, sw):
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    # Ironman targets do nothing, just blink during MB
    def sw_leftTargetI_active(self,sw):
        self.target_hit(0)

    def sw_leftTargetR_active(self,sw):
        self.target_hit(1)

    def sw_leftTargetO_active(self,sw):
        self.target_hit(2)

    def sw_leftTargetN_active(self,sw):
        self.target_hit(3)

    def sw_rightTargetM_active(self,sw):
        self.target_hit(4)

    def sw_rightTargetA_active(self,sw):
        self.target_hit(5)

    def sw_rightTargetN_active(self,sw):
        self.target_hit(6)


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

    def target_hit(self,number):
        self.game.lamps[self.target_lights[number]].pulse()

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