import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class MBSwitchStop(procgame.game.AdvancedMode):
    def __init__(self,game):
        super(MBSwitchStop, self).__init__(game=game, priority=40,mode_type=AdvancedMode.Manual)
        self.myID = "MBSwitchStop"
        self.valid = [True,True,True]
        self.target_lights = ['leftTargetsI','leftTargetsR','leftTargetsO','leftTargetsN','rightTargetsM','rightTargetsA','rightTargetsN']
        self.orbits_inactive = False

        ## Shared arrow inserts from oribts/ramps

        self.jp_arrow_lamps = [self.game.lamps['leftOrbitArrow'],
                               self.game.lamps['leftRampArrow'],
                               self.game.lamps['centerShotArrow'],
                               self.game.lamps['rightRampArrow'],
                               self.game.lamps['rightOrbitArrow']]

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
        return procgame.game.SwitchStop

    def sw_leftTargetR_active(self,sw):
        self.target_hit(1)
        return procgame.game.SwitchStop

    def sw_leftTargetO_active(self,sw):
        self.target_hit(2)
        return procgame.game.SwitchStop

    def sw_leftTargetN_active(self,sw):
        self.target_hit(3)
        return procgame.game.SwitchStop

    def sw_rightTargetM_active(self,sw):
        self.target_hit(4)
        return procgame.game.SwitchStop

    def sw_rightTargetA_active(self,sw):
        self.target_hit(5)
        return procgame.game.SwitchStop

    def sw_rightTargetN_active(self,sw):
        self.target_hit(6)
        return procgame.game.SwitchStop

    def sw_droneTarget0_active(self,sw):
        return procgame.game.SwitchStop

    def sw_droneTarget1_active(self,sw):
        return procgame.game.SwitchStop

    def sw_droneTarget2_active(self,sw):
        return procgame.game.SwitchStop

    def sw_droneTarget3_active(self,sw):
        return procgame.game.SwitchStop

    def sw_leftOrbit_active(self, sw):
        noisy = True
        if self.valid[0] and not self.orbits_inactive:
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
            # check iron monger
            if self.MO.running:
                self.MO.orbit_hit()
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
            if self.MO.running:
                self.MO.center_spinner_hit()
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
        if self.valid[2] and not self.orbits_inactive:
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
            # check iron monger
            if self.MO.running:
                self.MO.orbit_hit()
        if noisy:
            self.game.monger.orbit_noise()
        return procgame.game.SwitchStop

    def sw_shooterLane_inactive(self,sw):
        self.orbits_inactive = True
        self.delay(delay=2,handler=self.reactivate_orbits)

    def reactivate_orbits(self):
        self.orbits_inactive = False

    def target_hit(self,number):
        self.game.lamps[self.target_lights[number]].pulse(128)

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

    def clear_layer(self):
        self.layer = None

    def wipe_delays(self):
        self.__delayed = []

        # simple mode shutdown

    def unload(self):
        self.wipe_delays()
        self.layer = None
        self.game.modes.remove(self)

    # delayed voice quote helper with a list input
    if __name__ == '__main__':
        def voice_helper(self, options):
            duration = self.game.sound.play_voice(options[0], action=options[1])
            return duration


    ## Also doing shared insert lamp control for multiballs & modes here as well
    def disable_lamps(self):
        for lamp in self.jp_arrow_lamps:
            lamp.disable()

    def update_lamps(self):
        self.disable_lamps()
        for x in range (0,5,1):
            count = 0
            # for each lamp - should the insert flash for any of the 3 multiballs?
            if self.game.whiplash_multiball.running and self.game.whiplash_multiball.arrows:
                count += 1
            if self.game.wm_multiball.running and self.game.wm_multiball.big5_jackpots[x]:
                count += 1
            # all arrows but the center are affected by bogey
            if x != 2:
                if self.game.bogey.running:
                    count += 1

            # flash the lamp accordingly
            if count == 0:
                pass
            elif count == 1:
                self.jp_arrow_lamps[x].schedule(0x00FF00FF)
            elif count == 2:
                self.jp_arrow_lamps[x].schedule(0x0F0F0F0F)
            elif count == 3:
                self.jp_arrow_lamps[x].schedule(0x33333333)
            elif count > 3:
                self.jp_arrow_lamps[x].schedule(0x55555555)