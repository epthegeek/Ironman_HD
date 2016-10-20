
import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random
import math

class DoubleScoring(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(DoubleScoring, self).__init__(game=game, priority=9,mode_type=AdvancedMode.Manual)
        self.myID = "DoubleScoring"
        self.running = False
        backdrop = dmd.FrameLayer(frame=self.game.animations['metal_bg'].frames[0])
        banner = dmd.PanningLayer(3840,800,self.game.animations['double_scoring_banner'].frames[0],(0,0),(20,0),bounce=False,wrap=True)
        self.timer_layer = dmd.HDTextLayer(1920/2, 120, self.game.fonts['bebas500'], "center", line_color=(0,0,0), line_width=8,interior_color=(255, 0, 0))
        timer_box = self.game.animations['timer_box']
        timer_box.set_target_position(731,164)
        title = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        title.set_text("DOUBLE SCORING")
        # score goes on bottom 2 for double scoring
        self.bottom2 = dmd.HDTextLayer(1920/2,650,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        self.display = dmd.GroupedLayer(1920, 800, [backdrop,
                                                    banner,
                                                    title,
                                                    self.bottom2,
                                                    timer_box,
                                                    self.timer_layer], opaque=True)
        self.names = ['fast5','fast4','fast3','fast2','fast1','fast0']
        self.timer_start_value = 41
        self.fade_index = 0

    def evt_ball_starting(self):
        self.wipe_delays()

    def mode_started(self):
        # set the multiplier to 2
        self.game.multiplier = 2
        # update the score layer
        self.update_score_layer()
        self.double_scoring_runs = self.game.getPlayerState('double_scoring_runs')
        # play the sound and quote
        self.game.sound.play('scoring_mode_riff')
        duration = self.game.sound.sounds['scoring_mode_riff']['sound_list'][0].get_length()
        self.delay(delay=duration,handler=self.voice_helper,param=['double_scoring',procgame.sound.PLAY_FORCE])
        self.running = True

        # set up the display
        self.timer_value = self.timer_start_value
        self.timer()
        self.layer = self.display
        self.flash_lamps = [self.game.coils['rightRampBottomFlasher'],self.game.coils['leftRampBottomFlasher']]
        self.lamp_pulse(self.flash_lamps)

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.multiplier = 1
        self.end()

    def end(self):
        self.disable_pulse()
        self.layer = None
        self.running = False
        # add up the tally for how many times FS has run
        self.game.setPlayerState('double_scoring_runs', (self.double_scoring_runs + 1))
        self.game.im_targets.end_target_mode()
        self.unload()

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

    def update_score_layer(self):
        p = self.game.current_player()
        self.bottom2.set_text(self.game.score_display.format_score(p.score))
        if self.running:
            self.delay(delay=0.2,handler=self.update_score_layer)

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
