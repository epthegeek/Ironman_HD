import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class WhiplashMultiball(procgame.game.Mode):

    def __init__(self,game):
        super(WhiplashMultiball, self).__init__(game=game, priority=50)
        self.myID = "WhiplashMultiball"
        self.running = False
        self.jackpot_movies = [self.game.animations['whiplash_jp_1'],
                               self.game.animations['whiplash_jp_2'],
                               self.game.animations['whiplash_jp_3'],
                               self.game.animations['whiplash_jp_4'],
                               self.game.animations['whiplash_jp_5']]

    def mode_started(self):
        self.jackpot_index = 0
        # have to check on how jackpot values work in Whiplash
        self.jackpot_value = 500000

    def evt_ball_ending(self):
        if self.running:
            self.end_multiball()

    def evt_single_ball_play(self):
        if self.running:
            self.end_multiball()

    def sw_whiplashLeft_active(self,sw):
        self.jackpot_shot()
        return procgame.game.SwitchStop

    def sw_whiplashRight_active(self,sw):
        self.jackpot_shot()
        return procgame.game.SwitchStop


    def start_multiball(self):
        # do the display
        # set the total score to zero
        self.total_points = 0

    def jackpot_shot(self):
        # play the movie
        self.jackpot_movies[self.jackpot_index].reset()
        self.jackpot_movies[self.jackpot_index].add_frame_listener(-1,self.show_jp_value)
        # award the points
        self.score(self.jackpot_value)

    def show_jp_value(self):
        self.game.displayText(self.game.score_display.format_score(self.jackpot_value))

    def end_multiball(self):
        self.running = False
        self.unload()