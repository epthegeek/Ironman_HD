import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Ramps(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Ramps, self).__init__(game=game, priority=11, mode_type=AdvancedMode.Game)
        self.myID = "Ramps"
        self.pointValues = [100000, 200000, 300000, 400000]
        self.rampMadeAnimations = ['bogey_1_movie', 'bogey_2_movie', 'bogey_3_movie', 'bogey_4_movie']
        self.left_ramp_lamps = [self.game.lamps['leftRamp100k'],
                                self.game.lamps['leftRamp200k'],
                                self.game.lamps['leftRamp300k'],
                                self.game.lamps['leftRamp400k'],]
        self.right_ramp_lamps = [self.game.lamps['rightRamp100k'],
                                 self.game.lamps['rightRamp200k'],
                                 self.game.lamps['rightRamp300k'],
                                 self.game.lamps['rightRamp400k']]
        self.callouts = {'100000': 'one_hundred_th',
                         '200000': 'two_hundred_th',
                         '300000': 'three_hundred_th',
                         '400000': 'four_hundred_th',
                         '600000': 'six_hundred_th',
                         '800000': 'eight_hundred_th'}
        self.ramp_stage = [0,0]

    def evt_ball_starting(self):
        self.wipe_delays()

        # set the ramp doubler back to none
        self.rampDoubled = 9
        self.ramp_stage = self.game.getPlayerState('ramp_stage')
        self.ramp_shots = self.game.getPlayerState('ramp_shots')
        self.bogey_rounds = self.game.getPlayerState('bogey_rounds')
        self.bogey_status = self.game.getPlayerState('bogey_status')
        self.update_lamps()

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('ramp_stage',self.ramp_stage)
        self.game.setPlayerState('ramp_shots',self.ramp_shots)
        self.game.setPlayerState('bogey_rounds', self.bogey_rounds)
        self.game.setPlayerState('bogey_status',self.bogey_status)
        self.disable_lamps()

    def sw_leftRampEnter_active(self, sw):
        self.rampEnter()

    def sw_leftRampExit_active(self, sw):
        ramp = 0
        otherRamp = 1
        self.ramp_made(ramp, otherRamp)

    def sw_rightRampEnter_active(self, sw):
        self.rampEnter()

    def rampEnter(self):
        # score points
        self.game.score(5000)
        # make noise
        self.game.sound.play('ramp_enter')

    def sw_rightRampExit_active(self, sw):
        ramp = 1
        otherRamp = 0
        self.ramp_made(ramp, otherRamp)

    def ramp_made(self, ramp, otherRamp):
        # cancel the ramp double timer if any
        self.cancel_delayed("End Ramp Double")
        # Count the ramp shot
        self.ramp_shots[ramp] += 1

        ## If bogey is ready, start that
        if self.bogey_status == 'READY':
            self.bogey_status == 'RUNNING'
            # start bogey chase here
            if self.game.bogey.running == False:
                self.game.modes.add(self.game.bogey)

        ## If bogey chase is not ready, then process normally
        else:
            # play sound

            # if at stage 3, the ramp is completed points are minimal
            if self.ramp_stage[ramp] == 4:
                points = 1170
            # otherwise, they're a set value
            else:
                points = self.pointValues[self.ramp_stage[ramp]]
            # and possibly doubled - but not if maxed
            if self.rampDoubled == ramp and self.ramp_stage[ramp] <= 3:
                points *= 2
            # score the points
            self.game.score(points)
            # play the callout
            self.game.sound.play(self.callouts[str(points)])

            # update stage if not already at 3
            if self.ramp_stage[ramp] < 4:
                # do display
                self.ramp_made_display(self.ramp_stage[ramp], points)
                # update the tracking
                self.ramp_stage[ramp] += 1
                # Check the first hard bogey ramp setting and update accordingly - if not yet to first hard, both update
                if self.game.user_settings['Ironman']['02 1st Hard Bogey Ramp'] > self.bogey_rounds:
                    self.ramp_stage[otherRamp] += 1
                else:
                #  update the lamps?
                    pass

            # if the opposite ramp isn't done, turn on the doubler for that side
            if self.ramp_stage[otherRamp] < 4:
                self.start_ramp_double(otherRamp)

            # check bogey status
            if self.ramp_stage[ramp] == 4 and self.ramp_stage[otherRamp] == 4:
                self.bogey_status = "READY"

            # start the clear double timer
            self.delay("End Ramp Double", delay=4, handler=self.end_ramp_double)
            self.update_lamps()


    def ramp_made_display(self, stage, points):
        self.cancel_delayed("Ramp Display")
        # video clip
        video = self.game.animations[self.rampMadeAnimations[stage]]
        video.reset()
        text = dmd.HDTextLayer(1820,550,self.game.fonts['bebas200'],"right",line_color=[2,2,2],line_width=4,interior_color=[224,128,0])
        text.set_text(self.game.score_display.format_score(points))
        text.blink_frames = 8
        text.blink_frames_counter = 8
        self.layer = dmd.GroupedLayer(1920,800,[video,text],opaque=True)
        # clear layer after x
        self.delay("Ramp Display", delay=3,handler=self.clear_layer)


    def start_ramp_double(self, ramp):
        self.rampDoubled = ramp
        # turn on the lamp

    def end_ramp_double(self):
        self.rampDoubled = 9
        # turn off the lamp


    def update_lamps(self):
        if self.game.bogey.running:
            pass
        else:
            self.disable_lamps()
            # if both ramps add up to 8, we're ready for bogey and they should all flash
            if (self.ramp_stage[0] + self.ramp_stage[1]) == 8:
                for n in range(0,4,1):
                    self.left_ramp_lamps[n].schedule(0x00FF00FF)
                    self.right_ramp_lamps[n].schedule(0x00FF00FF)
            # otherwise step through and make the right lamps solid & blink
            else:
                blinker = False
                for n in range (0,4,1):
                    if self.ramp_stage[0] == n:
                        blinker = True
                        self.left_ramp_lamps[n].schedule(0x0F0F0F0F)
                    elif not blinker:
                        self.left_ramp_lamps[n].enable()
                    else:
                        pass
                blinker = False
                for n in range (0,4,1):
                    if self.ramp_stage[1] == n:
                        blinker = True
                        self.right_ramp_lamps[n].schedule(0x0F0F0F0F)
                    elif not blinker:
                        self.right_ramp_lamps[n].enable()
                    else:
                        pass

    def disable_lamps(self):
        for lamp in self.left_ramp_lamps:
            lamp.disable()
        for lamp in self.right_ramp_lamps:
            lamp.disable()

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
