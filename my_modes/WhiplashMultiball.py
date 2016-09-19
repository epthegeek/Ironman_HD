import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class WhiplashMultiball(procgame.game.Mode):

    def __init__(self,game):
        super(WhiplashMultiball, self).__init__(game=game, priority=49)
        self.myID = "WhiplashMultiball"
        self.running = False
        start_movie_1 = self.game.animations['whiplash_start']
        start_movie_2 = self.game.animations['mega_whiplash_start']
        self.start_movies = [start_movie_1, start_movie_2]
        jp_movies_1 = [self.game.animations['whiplash_jp_1'],
                       self.game.animations['whiplash_jp_2'],
                       self.game.animations['whiplash_jp_3'],
                       self.game.animations['whiplash_jp_4'],
                       self.game.animations['whiplash_jp_5']]
        jp_movies_2 = [self.game.animations['whiplash_jp_1b'],
                       self.game.animations['whiplash_jp_2b'],
                       self.game.animations['whiplash_jp_3b'],
                       self.game.animations['whiplash_jp_4b'],
                       self.game.animations['whiplash_jp_5b'],
                       self.game.animations['whiplash_jp_6b']]
        self.jackpot_movies = [jp_movies_1, jp_movies_2]
        super_1 = [self.game.animations['whiplash_super'],
                   self.game.animations['whiplash_super_2']]
        super_2 = [self.game.animations['mega_whiplash_super'],
                   self.game.animations['mega_whiplash_super_2']]
        self.super_movies = [super_1, super_2]
        self.type = 0
        self.line_1 = dmd.HDTextLayer(1920/2, 200, self.game.fonts['whiplash_300'], "center",line_color=(196, 255, 255), line_width=5, interior_color=(12, 117, 2))
        self.line_2 = dmd.HDTextLayer(1920/2, 100, self.game.fonts['default'], "center", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        self.jackpot_text = dmd.GroupedLayer(1920,800,[self.line_1,self.line_2],opaque=True)
        self.jackpot_count = [5,10]
        title = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(96,96,86),line_width=3,interior_color=(224,224,224))
        title.set_text("WHIPLASH MULTIBALL")
        self.info_line = dmd.HDTextLayer(1920 / 2, 650, self.game.fonts['default'], "center", line_color=(96, 96, 96), line_width=3,interior_color=(224, 224, 224))
        self.score_line = dmd.HDTextLayer(1920 / 2, 200, self.game.fonts['main_score'], "center", line_color=(96, 96, 96), line_width=3,interior_color=(224, 0, 0))
        self.main_display = dmd.GroupedLayer(1920,800,[title,self.score_line,self.info_line],opaque=True)

    def mode_started(self):
        self.jackpot_index = 0
        # default value for jackpots is 250k
        self.jackpot_value = 250000
        # flag the super as off just to be sure
        self.super = False
        # to toggle between score/count behavior
        self.round = 0
        # starts with 5 jackpots
        self.jackpots_left = 5
        self.super_count = 0
        # update the info line
        self.update_info_layer(self.jackpots_left)

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


    def start_multiball(self,type):
        self.type = type
        self.running = True
        # fire off the score update
        self.update_score_layer()
        # play some music
        self.game.sound.play_music('whiplash_mb',loops=-1)
        # do the display
        self.start_movies[self.type].reset()
        self.start_movies[self.type].add_frame_listener(-1,self.do_main_display)
        self.layer = self.start_movies[self.type]
        # set the total score to zero
        self.total_points = 0

    def do_main_display(self):
        self.layer = self.main_display

    def jackpot_shot(self):
        self.cancel_delayed("clear")
        # set the points to score to the current JP value
        points = self.jackpot_value
        # play the movie - if we're on super jackpot set it to that
        if self.super:
            text = "SUPER JACKPOT"
            self.super_count += 1
            if self.round == 0 and self.super_count == 2:
                # 2 supers in the first round
                self.super = False
                toggle = True
                anim = self.super_movies[self.type][1]
                self.jackpot_value = 500000
            # if we're only at one super in phase 1, don't toggle to phase 2
            elif self.round == 0:
                anim = self.super_movies[self.type][0]
                toggle = False
                self.jackpot_value = 1000000
            else:
                anim = self.super_movies[self.type][1]
                self.super = False
                toggle = True
                self.jackpot_value = 250000
        else:

            text = "JACKPOT"
            anim = self.jackpot_movies[self.type][self.jackpot_index]
            toggle = False
        anim.reset()
        anim.add_frame_listener(-1,lambda: self.show_jp_value(text,points))
        self.layer = anim
        self.tick_jackpot_index()
        # award the points
        self.game.score(points)
        # are we toggling to the next phase?
        if toggle:
            # if we're in the 0 round, there are 2 shots
            # flip the round
            if self.round == 0:
                self.round = 1
            else:
                self.round = 0
            self.jackpots_left = self.jackpot_count[self.round]
            self.update_info_layer(self.jackpots_left)
        else:
            if not self.super:
                self.jackpots_left -= 1
            if self.jackpots_left == 0:
                self.update_info_layer()
                self.super = True
                if self.round == 0:
                    self.jackpot_value = 500000
                else:
                    self.jackpot_value = 3000000
            else:
                self.update_info_layer(self.jackpots_left)

    def tick_jackpot_index(self):
        self.jackpot_index += 1
        if self.type == 0:
            if self.jackpot_index > 4:
                self.jackpot_index = 0
        else:
            if self.jackpot_index > 5:
                self.jackpot_index = 0

    def show_jp_value(self,text,value):
        self.line_2.set_text(text)
        self.line_1.set_text(self.game.score_display.format_score(value))
        self.layer = self.jackpot_text
        self.delay("clear",delay=2,handler=self.do_main_display)

    def update_score_layer(self):
        p = self.game.current_player()
        self.score_line.set_text(self.game.score_display.format_score(p.score))
        if self.running:
            self.delay(delay=0.2,handler=self.update_score_layer)

    def update_info_layer(self,string="SUPER JACKPOT IS LIT"):
        if string != "SUPER JACKPOT IS LIT":
            if self.jackpots_left == 1:
                string = str(self.jackpots_left) + " JACKPOT REMAINING"
            else:
                string = str(self.jackpots_left) + " JACKPOTS REMAINING"

        self.info_line.set_text(string)

    def end_multiball(self):
        self.running = False
        # if we just finished regular whiplash, set the type to mega for next run
        if self.game.whiplash.whiplash_type == 0:
            self.game.whiplash.whiplash_type = 1
        else:
            self.game.whiplash.whiplash.type = 0
        self.unload()