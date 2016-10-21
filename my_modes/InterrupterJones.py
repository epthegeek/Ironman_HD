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
        # Scoring mode screens
        bg = dmd.FrameLayer(frame=self.game.animations['gold_bg'].frames[0])
        self.score_title_top = dmd.HDTextLayer(1920/2,80,self.game.fonts['IM370'],"center", line_color=(0,0,0),line_width=8, interior_color=(255,0,0))
        title_bot = dmd.HDTextLayer(1920 / 2, 420, self.game.fonts['IM370'], "center", line_color=(0, 0, 0),line_width=8, interior_color=(255, 0, 0))
        title_bot.set_text("SCORING")
        self.score_page2_top = dmd.HDTextLayer(1920/2,30,self.game.fonts['IM160'],"center", line_color=(0,0,0,), line_width=4, interior_color=(192,192,192))
        self.score_page2_mid = dmd.HDTextLayer(1920/2,220,self.game.fonts['IM370'],"center", line_color=(0,0,0),line_width=8, interior_color=(255,0,0))
        self.score_page2_bot = dmd.HDTextLayer(1920/2,590,self.game.fonts['IM160'],"center", line_color=(0,0,0,), line_width=4, interior_color=(192,192,192))
        self.score_page1 = dmd.GroupedLayer(1920,800,[bg,self.score_title_top, title_bot],opaque = True)
        self.score_page2 = dmd.GroupedLayer(1920,800,[bg,self.score_page2_top, self.score_page2_mid, self.score_page2_bot], opaque = True)


    ## This mode is just for putting high priority junk on the display - sledgehammer style
    def display(self,layer,time):
        print "INTERRUPTER JONES DISPLAY"
        self.cancel_delayed("display")
        self.layer = layer
        self.delay("display",delay=time,handler=self.clear_layer)

    # 2 part intro demo for the scoring modes
    def scoring_mode_start(self,title):
        self.score_title_top.set_text(title)
        self.layer = self.score_page1
        self.delay(delay=2,handler=self.scoring_mode_start_2,param=title)

    def scoring_mode_start_2(self,title):
        if title == "FAST":
            top_string = "ALL TARGETS"
            mid_string = "SCORE"
            bot_string = "10,000 POINTS"
            mode = self.game.fast_scoring
        elif title == "DOUBLE":
            top_string = "ALL SCORES"
            mid_string = "DOUBLED"
            bot_string = "FOR 40 SECONDS"
            mode = self.game.double_scoring
        else:
            top_string = "SHOOT THE"
            mid_string = "RED"
            bot_string =  "TARGETS"
            mode = self.game.ironman_scoring
        self.score_page2_top.set_text(top_string)
        self.score_page2_mid.set_text(mid_string)
        self.score_page2_bot.set_text(bot_string)
        self.layer = self.score_page2
        self.delay(delay=2,handler=self.clear_layer)
        self.delay(delay=2,handler=self.game.modes.add,param=mode)

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
