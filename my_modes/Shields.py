import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from collections import deque
from procgame import dmd

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
        self.top_text = dmd.HDTextLayer(1920 / 2, 230, self.game.fonts['bebas200'], "center", line_color=(0,0,0), line_width=6,interior_color=(224, 224, 224))
        self.bot_text = dmd.HDTextLayer(1920 / 2, 450, self.game.fonts['bebas200'], "center", line_color=(0,0,0), line_width=6,interior_color=(0, 192, 0))
        self.top_text.set_text("SHIELD IS LIT")
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
        self.layer = dmd.GroupedLayer(1920,1080,[self.shield_bg,self.top_text,self.bot_text],opaque=True)
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
            self.game.score(10)
            self.shield_awards_pending -= 1
            self.game.displayText("SHIELDS COLLECTED")

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

    def increase_bonus_x(self):
        # bonus x maxes at 25x
        if self.game.base.bonus_x < 25:
            self.game.base.bonus_x += 1


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
