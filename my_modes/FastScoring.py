
import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random

class FastScoring(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(FastScoring, self).__init__(game=game, priority=9,mode_type=AdvancedMode.Manual)
        self.myID = "FastScoring"
        self.running = False
        backdrop = dmd.FrameLayer(frame=self.game.animations['metal_bg'].frames[0])
        banner = dmd.PanningLayer(3840,800,self.game.animations['fast_scoring_banner'].frames[0],(0,0),(20,0),bounce=False,wrap=True)
        #self.explosion = self.game.animations['fast_scoring_explosion']
        #self.explosion.composite_op = "blacksrc"
        #self.explosion.enabled = False
        #self.display = dmd.GroupedLayer(1920, 800, [backdrop, banner, self.explosion], opaque=True)
        self.score1 = dmd.HDTextLayer(250, 100, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score2 = dmd.HDTextLayer(300, 250, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score3 = dmd.HDTextLayer(250, 450, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score4 = dmd.HDTextLayer(1700, 100, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score5 = dmd.HDTextLayer(1600, 250, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score6 = dmd.HDTextLayer(1700, 450, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(255, 255, 0))
        self.score_layers = [self.score1, self.score2, self.score3, self.score4, self.score5, self.score6]
        self.timer_layer = dmd.HDTextLayer(1920/2, 120, self.game.fonts['bebas500'], "center", line_color=(0,0,0), line_width=8,interior_color=(255, 0, 0))
        timer_box = self.game.animations['timer_box']
        timer_box.set_target_position(731,164)
        title = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        title.set_text("FAST SCORING")
        bottom1 = dmd.HDTextLayer(1920/2,650,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        bottom1.set_text("IRONMAN TARGETS RAISE VALUE")
        self.bottom2 = dmd.HDTextLayer(1920/2,650,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        self.bottom2.set_text("ALL SWITCHES SCORE 10,000 POINTS")
        info_line = dmd.ScriptedLayer(1920,800,[{'layer':bottom1,'seconds':2},{'layer':self.bottom2,'seconds':2}])
        self.display = dmd.GroupedLayer(1920, 800, [backdrop,
                                                    banner,
                                                    title,
                                                    info_line,
                                                    timer_box,
                                                    self.timer_layer,
                                                    self.score1,
                                                    self.score2,
                                                    self.score3,
                                                    self.score4,
                                                    self.score5,
                                                    self.score6], opaque=True)
        self.names = ['fast5','fast4','fast3','fast2','fast1','fast0']
        self.timer_start_value = 41


    def mode_started(self):
        self.fast_scoring_runs = self.game.getPlayerState('fast_scoring_runs')
        # play the sound and quote
        self.game.sound.play('scoring_mode_riff')
        duration = self.game.sound.sounds['scoring_mode_riff']['sound_list'][0].get_length()
        self.delay(delay=duration,handler=self.voice_helper,param=['fast_scoring',procgame.sound.PLAY_FORCE])
        self.running = True
        # set the starting value
        self.switch_value = 10000 + (5000 * self.fast_scoring_runs)

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
        # and score points
        self.game.score(self.switch_value)
        # randomly select a layer
        score_number = self.get_random_layer()
        # cancel any pending delay
        self.cancel_delayed(self.names[score_number])
        self.reset_layer(self.score_layers[score_number],self.game.score_display.format_score(self.switch_value))
        self.delay(name=self.names[score_number],delay=1,handler=self.disable_layer,param=self.score_layers[score_number])
        # play the fast scoring sound effect - just jumble that crap with the other sounds for now
        self.game.sound.play('fast_scoring')

    def end(self):
        self.layer = None
        self.game.im_targets.end_target_mode()
        self.running = False
        # add up the tally for how many times FS has run
        self.game.setPlayerState('fast_scoring_runs', (self.fast_scoring_runs + 1))
        self.unload()

    # updates the score layers and triggers the update to the info line
    def set_layer_points(self):
        for layer in self.score_layers:
            layer.set_text(self.game.score_display.format_score(self.switch_value))
        self.update_info_line()

    # increases the switch value 1000 points and updates the score layers
    def increase_value(self):
        # maximum value is 50k
        if self.switch_value < 50000:
            self.switch_value += 1000
        self.set_layer_points()

    # updates the info line that contains points
    def update_info_line(self):
        string = "ALL SWITCHES SCORE " + self.game.score_display.format_score(self.switch_value) + " POINTS"
        self.bottom2.set_text(string)

    # chooses and returns a random layer from the available layers for score display
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