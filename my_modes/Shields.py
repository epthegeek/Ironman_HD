import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from collections import deque
from procgame import dmd
import random

class Shields(procgame.game.AdvancedMode):
    def __init__(self, game):
        super(Shields, self).__init__(game=game, priority=11, mode_type=AdvancedMode.Game)
        self.myID = "Shields"
        self.shield_lamps = [self.game.lamps.topLeftLane,
                             self.game.lamps.topRightLane,
                             self.game.lamps.rightOutlane,
                             self.game.lamps.rightReturnLane,
                             self.game.lamps.leftReturnLane,
                             self.game.lamps.leftOutlane]
        self.shield_bg = dmd.FrameLayer(frame=self.game.animations['shield_logo'].frames[0])
        self.title = dmd.HDTextLayer(980,-40,self.game.fonts['main_score'],"center",line_color=(0,0,0),line_width=8,interior_color=(192,192,0))
        self.title.set_text("S.H.I.E.L.D.")
        self.top_text = dmd.HDTextLayer(980, 280, self.game.fonts['bebas200'], "center", line_color=(0,0,0), line_width=6,interior_color=(192, 192, 0))

        self.bot_text = dmd.HDTextLayer(980, 490, self.game.fonts['bebas200'], "center", line_color=(0,0,0), line_width=6,interior_color=(0, 192, 0))
        self.top_text.set_text("IS LIT")
        self.twolineA = dmd.HDTextLayer(980,380, self.game.fonts['bebas200'],"center", line_color=(0,0,0), line_width=6, interior_color=(0,192,0))
        self.twolineB = dmd.HDTextLayer(980,550, self.game.fonts['bebas200'],"center", line_color=(0,0,0), line_width=6, interior_color=(0,192,0))
        self.valid = True
        self.shield_tracking = [False,False,False,False,False,False]

    def evt_ball_starting(self):
        self.wipe_delays()

        self.shield_tracking = self.game.getPlayerState('shields')
        self.shield_awards_pending = self.game.getPlayerState('shield_awards_pending')
        self.shield_awards_collected = self.game.getPlayerState('shield_awards_collected')
        self.shield_mark = self.game.getPlayerState('shield_mark')
        self.valid = True

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('shields',self.shield_tracking)
        self.game.setPlayerState('shield_awards_pending',self.shield_awards_pending)
        self.game.setPlayerState('shield_awards_collected', self.shield_awards_collected)
        self.game.setPlayerState('shield_mark', self.shield_mark)
        self.disable_lamps()

    ####
    ### Shields
    ####

    def sw_topLeftLane_active(self, sw):
        self.shield_hit(0)

    def sw_topRightLane_active(self, sw):
        self.shield_hit(1)

    def sw_rightOutlane_active(self, sw):
        self.shield_hit(2)

    def sw_rightReturnLane_active(self, sw):
        self.shield_hit(3)

    def sw_leftReturnLane_active(self, sw):
        self.shield_hit(4)

    def sw_leftOutlane_active(self, sw):
        self.shield_hit(5)

    def sw_flipperLwL_active(self,sw):
        if self.valid:
            self.rotate_shields(1)

    def sw_flipperLwR_active(self,sw):
        if self.valid:
            self.rotate_shields(-1)

    def sw_warMachineKicker_active(self,sw):
        if self.shield_awards_pending > 0:
            self.collect_award()

    def shield_hit(self,switch):
        if self.valid:
            # is this switch already on?
            if self.shield_tracking[switch] == True:
                # already lit
                points = 0
                #sound = "miss"
                self.game.sound.play('shield_already_lit')
            else:
                self.shield_tracking[switch] = True
                points = 3000
                #sound = "hit"
                if sum(self.shield_tracking) == 6:
                    self.game.sound.play('last_shield')
                else:
                    self.game.sound.play('shield_unlit')
                self.update_lamps()

            #Did we finish the set?
            if False not in self.shield_tracking:
                self.valid = False
                self.game.score(10000)
                self.light_shield_collect()
            else:
                #play the selected sound
                self.game.score(points)

    def light_shield_collect(self):
        # add the bonus multiplier
        self.increase_bonus_x()
        # play a sound
        #self.game.sound.play('shields_collected')
        duration = self.game.sound.sounds['shields_collected']['sound_list'][0].get_length()
        # play a quote
        self.delay(delay=(duration -1) ,handler=self.voice_helper,param=['shields_completed',procgame.sound.PLAY_NOTBUSY])
        self.shield_awards_pending += 1
        # flash the lights a bit
        self.flash_lights()
        # do the display
        if self.game.base.bonus_x == 25:
            self.bot_text.set_text("BONUS X MAXED AT 25X")
        else:
            self.bot_text.set_text(str(self.game.base.bonus_x) + "X BONUS")
        self.layer = dmd.GroupedLayer(1920,1080,[self.shield_bg,self.title,self.top_text,self.bot_text],opaque=True)
        self.delay(delay=3,handler=self.clear_layer)
        # if this player hasn't gotten a mark level from shields, add one
        if not self.shield_mark:
            self.game.mark.player_mark += 1
            self.game.mark.score()
            self.delay(delay=3,handler=self.game.mark.completed)
            self.shield_mark = True
        # reset
        self.delay(delay=2,handler=self.reset_shields)

    def collect_award(self):
        if self.shield_awards_pending > 0:
            self.shield_awards_pending -= 1
            # TODO: during scoring modes add time, during MB add a ball
            choices = []
            # Basic Awards 2 = 200,00, 3 = POPs Jackpot 100,000, 4 = Bonus multiplier +10x, 5 = EB, 6 = Special
            choices.append([2,2,2,2,2])
            choices.append([3,3,3,3,3])
            # Only add bonus x if they're below 20 already
            if self.game.base.bonus_x < 20:
                choices.append([4,4,4,4])
            # Oly add extra balls if they're below max extra balls
            if self.game.getPlayerState('extra_balls_total') < self.game.settings['Machine (Standard)']['Maximum Extra Balls']:
                choices.append([5,5])
            choices.append([6])
            # shuffle that shit up
            for n in range (0,9,1):
                random.shuffle(choices)
                print choices
            # then pick one
            selected = random.choice(choices)
            # and do a thing
            layers = [self.shield_bg,self.title]
            if selected == 2:
                self.bot_text = "200,000"
                layers.append(self.bot_text)
                self.game.score(200000)
            elif selected == 3:
                self.twolineA.set_text("POPS JACKPOT GROWS")
                self.twolineB.set_text("100,000")
                self.game.pops.increase_jackpot_value(9)
                layers.append([self.twolineA,self.twolineB])
            elif selected == 4:
                self.twolineA.set_text("10 X BONUS")
                self.twolineB.set_text("MULTIPLIER")
                self.increase_bonus_x(10)
                layers.append([self.twolineA, self.twolineB])
            elif selected == 5:
                self.twolineA.set_text("EXTRA BALL")
                self.twolineB.set_text("IS LIT")
                self.game.base.light_extra_ball()
                layers.append([self.twolineA, self.twolineB])
            elif selected == 6:
                self.twolineA.set_text("SPECIAL")
                self.twolineB.set_text("IS LIT")
                self.game.base.light_special()
                layers.append([self.twolineA,self.twolineB])
            # set up the display
            display = dmd.GroupedLayer(1920,1080,layers,opaque = True)
            # have interrupted show it
            self.game.interrupt.display(display,3)

    def reset_shields(self):
        self.shield_tracking = [False,False,False,False,False,False]
        self.valid = True
        self.update_lamps()

    def rotate_shields(self,direction):
        if self.valid:
            items = deque(self.shield_tracking)
            items.rotate(direction)
            self.shield_tracking = items
            self.update_lamps()

    def update_lamps(self,force=False):
        # if the skillshot is in the mode stack, don't do this
        if self.game.skillshot in self.game.modes and not force:
            pass
        else:
            if self.valid:
                for i in range (0,6,1):
                    if self.shield_tracking[i] == True:
                        self.shield_lamps[i].enable()
                    else:
                        self.shield_lamps[i].disable()

    def disable_lamps(self):
        for lamp in self.shield_lamps:
            lamp.disable()

    def flash_lights(self):
        for i in range (0,6,1):
            self.shield_lamps[i].schedule(0x00FF00FF)

    def increase_bonus_x(self,amount = 1):
        # bonus x maxes at 25x
        self.game.base.bonus_x += amount
        if self.game.base.bonus_x > 25:
            self.game.base.bonus_x = 25


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
