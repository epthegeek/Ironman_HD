
import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class FastScoring(procgame.game.Mode):

    def __init__(self,game):
        super(FastScoring, self).__init__(game=game, priority=9)
        self.myID = "FastScoring"
        self.running = False
        backdrop = dmd.FrameLayer(frame=self.game.animations['metal_bg'].frames[0])
        banner = dmd.PanningLayer(3840,800,self.game.animations['fast_scoring_banner'].frames[0],(0,0),(20,0),bounce=False,wrap=True)
        self.display = dmd.GroupedLayer(1920,800,[backdrop,banner],opaque=True)

    def mode_started(self):
        # play the sound and quote
        # set up the display
        self.layer = self.display
        self.running = True

    def evt_ball_drained(self):
        self.end()

    def switch_hit(self):
        # should do something to the display
        pass

    def end(self):
        self.layer = None
        self.game.ironman_targets.end_scoring_mode()
        self.running = False
        self.unload()

