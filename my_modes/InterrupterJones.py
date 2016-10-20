import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from collections import deque
from procgame import dmd

class InterrupterJones(procgame.game.AdvancedMode):
    def __init__(self, game):
        super(InterrupterJones, self).__init__(game=game, priority=61, mode_type=AdvancedMode.Game)
        self.myID = "InterrupterJones"

    ## This mode is just for putting high priority junk on the display - sledgehammer style
    def display(self,layer,time):
        self.cancel_delayed("display")
        self.layer = layer
        self.delay("display",delay=time,handler=self.clear_layer)

    def clear_layer(self):
        self.layer = None

    def wipe_delays(self):
        self.__delayed = []

    # simple mode shutdown
    def unload(self):
        print "Unloading: " + self.myID
        self.wipe_delays()
        self.layer = None
        self.game.modes.remove(self)

    # delayed voice quote helper with a list input
    def voice_helper(self, options):
        duration = self.game.sound.play_voice(options[0], action=options[1])
        return duration
