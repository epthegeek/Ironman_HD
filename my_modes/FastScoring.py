
import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random

class FastScoring(procgame.game.Mode):

    def __init__(self,game):
        super(FastScoring, self).__init__(game=game, priority=9)
        self.myID = "FastScoring"
        self.running = False
        backdrop = dmd.FrameLayer(frame=self.game.animations['metal_bg'].frames[0])
        banner = dmd.PanningLayer(3840,800,self.game.animations['fast_scoring_banner'].frames[0],(0,0),(20,0),bounce=False,wrap=True)
        #self.explosion = self.game.animations['fast_scoring_explosion']
        #self.explosion.composite_op = "blacksrc"
        #self.explosion.enabled = False
        #self.display = dmd.GroupedLayer(1920, 800, [backdrop, banner, self.explosion], opaque=True)
        self.score1 = dmd.HDTextLayer(200, 100, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score2 = dmd.HDTextLayer(250, 250, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score3 = dmd.HDTextLayer(200, 500, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score4 = dmd.HDTextLayer(1700, 100, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score5 = dmd.HDTextLayer(1650, 250, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score6 = dmd.HDTextLayer(1700, 500, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score_layers = [self.score1, self.score2, self.score3, self.score4, self.score5, self.score6]
        self.timer_layer = dmd.HDTextLayer(1920/2, 120, self.game.fonts['bebas500'], "center", line_color=(0,0,0), line_width=8,interior_color=(255, 0, 0))
        timer_box = self.game.animations['timer_box']
        timer_box.set_target_position(731,164)
        self.display = dmd.GroupedLayer(1920, 800, [backdrop, banner,timer_box,self.timer_layer,self.score1,self.score2,self.score3,self.score4,self.score5,self.score6], opaque=True)
        self.names = ['fast5','fast4','fast3','fast2','fast1','fast0']
        self.timer_start_value = 41

    def mode_started(self):
        # play the sound and quote
        self.running = True
        # set the starting value
        self.switch_value = 15000

        for layer in self.score_layers:
            layer.enabled = False
            self.set_layer_points()
        # set up the display
        self.timer_value = self.timer_start_value
        self.timer()
        self.layer = self.display
        self.last_score = 0


    def evt_ball_drained(self):
        self.end()

    def switch_hit(self):
        # should do something to the display
        #self.explosion.reset()
        #self.explosion.enabled = True
        #self.explosion.add_frame_listener(-1,self.disable_explosion)
        # and score points
        self.game.score(self.switch_value)
        # randomly select a layer
        score_number = self.get_random_layer()
        # cancel any pending delay
        self.cancel_delayed(self.names[score_number])
        self.reset_layer(self.score_layers[score_number],self.game.score_display.format_score(self.switch_value))
        self.delay(name=self.names[score_number],delay=1,handler=lambda: self.disable_layer(self.score_layers[score_number]))

   # def disable_explosion(self):
   #     self.explosion.enabled = False

    def end(self):
        self.layer = None
        self.game.im_targets.end_scoring_mode()
        self.running = False
        self.unload()

    def set_layer_points(self):
        for layer in self.score_layers:
            layer.set_text(self.game.score_display.format_score(self.switch_value))

    def get_random_layer(self):
        choices = []
        for n in range (0,6,1):
            if n == self.last_score:
                pass
            else:
                choices.append(n)
        selected = random.choice(choices)
        return selected

    def reset_layer(self,target,value):
        target.enabled = True

    def disable_layer(self,target,):
        target.enabled = False

    def timer(self):
        self.timer_value -= 1
        if self.timer_value < 10:
            text = "0" + str(self.timer_value)
        else:
            text = str(self.timer_value)
        self.timer_layer.set_text(text)
        if self.timer_value == 0:
            # it's overrrrrr
            self.delay(delay = 1,handler=self.end)
        else:
            # or loop back
            self.delay(delay = 1,handler=self.timer)