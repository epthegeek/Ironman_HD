import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class SwitchFilter(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(SwitchFilter, self).__init__(game=game, priority=900, mode_type=AdvancedMode.Game)
        self.myID = "SwitchFilter"

        # add the rules for any switch tagged bonus
        for sw in self.game.switches.items_tagged('Bonus'):
            self.add_switch_handler(name=sw.name, event_type="active", delay=None,handler=self.register)

    # at ball start, set the last switch and total switches to blanks
    def evt_ball_starting(self):
        self.last_switch = None
        self.total = 0

    def register(self,sw):
        # count the switch
        self.total += 1
        # set the last hit switch
        self.last_switch = sw.name
