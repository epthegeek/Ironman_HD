import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class WarMachine(procgame.game.AdvancedMode):
    def __init__(self, game):
        super(WarMachine, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "WarMachine"


    def evt_ball_starting(self):
        self.valid = True
        self.multiball_status = self.game.getPlayerState('wm_multiball_status')

    def evt_ball_ending(self):
        self.game.setPlayerState('wm_multiball_status',self.multiball_status)

    def sw_warMachineOpto_active(self,sw):
        # if the ball goes up into the war machine
        self.valid = False
        self.delay(delay=0.5,handler=self.make_valid)
        # fire the kicker
        self.game.coils.warMachineKicker.pulse()
        self.process_hit()

    def process_hit(self):
        # if there are shield awards waiting, do that
        if self.game.shields.shield_awards_pending > 0:
            self.game.shields.collect_award()
        if self.multiball_status == "READY":
            # if war machine multiball is ready, do that
            pass
        # last option is add a drone
        else:
            self.game.drones.add()


    def light_multiball(self):
        self.multiball_status == "READY"
        # do a display?
        # update the lamps?

    def make_valid(self):
        self.valid = True