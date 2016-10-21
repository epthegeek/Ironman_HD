
import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random
import math

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
        self.fade_index = 0

    def evt_ball_starting(self):
        self.wipe_delays()

    def mode_started(self):
        self.fast_scoring_runs = self.game.getPlayerState('fast_scoring_runs')
        # play the sound and quote
#        self.game.sound.play('scoring_mode_riff')
#        duration = self.game.sound.sounds['scoring_mode_riff']['sound_list'][0].get_length()
#        self.delay(delay=duration,handler=self.voice_helper,param=['fast_scoring',procgame.sound.PLAY_FORCE])
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
        self.fade_counter = 10
        self.flash_lamps = [self.game.coils['rightRampBottomFlasher'],self.game.coils['leftRampBottomFlasher']]
        self.lamp_pulse(self.flash_lamps)

    def evt_ball_ending(self,(shoot_again,last_ball)):
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
        self.game.sound.play('fast_scoring_sfx')

    def end(self):
        self.disable_pulse()
        self.layer = None
        self.running = False
        # add up the tally for how many times FS has run
        self.game.setPlayerState('fast_scoring_runs', (self.fast_scoring_runs + 1))
        self.game.im_targets.end_target_mode()
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
        if self.timer_value <= 0:
            # it's overrrrrr
            self.delay("timer",delay = 1,handler=self.end)
        else:
            # or loop back
            self.delay("timer",delay = 1,handler=self.timer)

    def add_time(self):
        # just in case it's the last second - cancel the delay to avoid ending
        self.cancel_delayed("timer")
        # adding 20 seconds to the timer
        self.timer_value += 20
        # schedule new timer delay
        self.delay(delay=1,handler=self.timer)

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


    def lamp_pulse(self, lamps):
        fade_map = [10,10,10,10,9,9,9,8,8,7,5,3,3,2,3,3,5,7,8,8,9,9,9]
        for lamp in lamps:
            var = fade_map[self.fade_index]
            on_time = 10 - var
            off_time = var
            lamp.patter(on_time, off_time)
        self.fade_index += 1
        if self.fade_index >= len(fade_map):
            self.fade_index = 0
        self.delay("pulse", delay=0.04, handler=self.lamp_pulse,param=self.flash_lamps)

    def disable_pulse(self):
        self.cancel_delayed("pulse")
        for lamp in self.flash_lamps:
            lamp.disable()
