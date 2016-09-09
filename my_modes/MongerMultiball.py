import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class MongerMultiball(procgame.game.Mode):

    def __init__(self,game):
        super(MongerMultiball, self).__init__(game=game, priority=50)
        self.myID = "MongerMultiball"
        self.toy_status = None
        self.running = False

    def evt_ball_ending(self):
        if self.running:
            self.end_multiball()

    def evt_single_ball_play(self):
        if self.running:
            self.end_multiball()


    def mode_started(self):
        self.running = True
        if self.game.monger_toy.status == "UP":
            self.toy_status = "UP"
        # reset the jacpot hit count
        self.jackpot_hits = 0
        self.jackpots_total = 0


    def start_multiball(self):
        # play the clip and the audio
        # launch the balls
        self.game.trough.launch_and_autoplunge_balls(2)
        # lower the monger after a delay?
        self.delay(2,handler=self.game.monger_toy.fall)
        # release the ball
        self.game.monger.magnet("Release")

    # this needs work for now it's just unloading
    def end_multiball(self):
        self.game.monger_toy.fall()
        self.unload()