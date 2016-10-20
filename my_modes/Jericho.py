import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class Jericho(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Jericho, self).__init__(game=game, priority=52,mode_type=AdvancedMode.Manual)
        self.myID = "Jericho"
        self.running = False
        ## Main display bits
        title = dmd.HDTextLayer(1920/2,10,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        title.set_text("JERICHO")
        shoot = dmd.HDTextLayer(1920/2,200,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        shoot.set_text("SHOOT")
        self.im_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.im_text_layer.set_text("IRONMAN TARGETS")
        self.wl_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.wl_text_layer.set_text("WHIPLASH")
        self.m_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.m_text_layer.set_text("IRON MONGER")
        self.wm_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.wm_text_layer.set_text("WAR MACHINE")
        self.b_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.b_text_layer.set_text("BOGEY RAMPS")
        self.s_text_layer = dmd.HDTextLayer(1920/2,400,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.s_text_layer.set_text("SHIELD LANES")
        self.info_lines = [self.im_text_layer,self.wl_text_layer,self.m_text_layer,self.wm_text_layer,self.b_text_layer,self.s_text_layer]
        script = [{'layer':self.im_text_layer,'seconds':2},
                  {'layer':self.wl_text_layer,'seconds':2},
                  {'layer':self.m_text_layer,'seconds':2},
                  {'layer':self.wm_text_layer,'seconds':2},
                  {'layer':self.b_text_layer,'seconds':2},
                  {'layer':self.s_text_layer, 'seconds':2}]
        self.info_line_layer = dmd.ScriptedLayer(1920,800,script)
        self.shot_value_layer = dmd.HDTextLayer(1920/2,600,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=4,interior_color=(192,192,192))
        self.main_display = dmd.GroupedLayer(1920,800,[title,shoot,self.info_line,self.shot_value_layer],opaque = True)
        # Intro display bits
        start_title = dmd.HDTextLayer(1920 / 2, 10, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        start_title.set_text("COMPLETE")
        start_for = dmd.HDTextLayer(1920 / 2, 400, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        start_for.set_text("FOR")
        start_points = dmd.HDTextLayer(1920 / 2, 600, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        start_points.set.text("1,000,000 + ")
        self.start_info = dmd.HDTextLayer(1920 / 2, 200, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        self.start_layer = dmd.GroupedLayer(1920,800,[start_title,start_for,start_points,self.start_info],opaque = True)
        start_strings = ["IRONMAN TARGETS", "WAR MACHINE", "WHIPLASH", "IRON MONGER", "BOGEY RAMPS", "SHIELD LANES"]
        # title display
        card_top = dmd.HDTextLayer(1920 / 2, 10, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        card_top.set_text("JERICHO")
        card_bottom = dmd.HDTextLayer(1920 / 2, 400, self.game.fonts['bebas200'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(192, 192, 192))
        card_bottom.set_text("MISSILE MAYHEM")
        self.title_card = dmd.GroupedLayer(1920,800,[card_top, card_bottom],opaque = True)
        # various hit displays - each needs a background?
        self.hit_score_layer = dmd.HDTextLayer(1920/2,200,self.game.fonts['main_score'],"center",line_color=(0,0,0),line_width=6,interior_color=(224,224,0))
        self.im_hit_layer = dmd.GroupedLayer(1920,800,[self.hit_score_layer],opaque = True)
        # im target lamps? or use from IM targets mode?

    # spinners and jets increase shot value - and still award their own points - no stop
    def sw_leftSpinner_active(self,sw):
        self.increase_shot_value()
    def sw_rightSpinner_active(self,sw):
        self.increase_shot_value()
    def sw_centerSpinner_active(self,sw):
        self.increase_shot_value()
    def sw_leftJetBumper_active(self,sw):
        self.increase_shot_value()
    def sw_rightJetBumper_active(self,sw):
        self.increase_shot_value()
    def sw_bottomJetBumper_active(self,sw):
        self.increase_shot_value()
    # iron man targets are locked in to this mode, register individually
    def sw_leftTargetI_active(self,sw):
        self.im_targets_hit(0)
        return procgame.game.SwitchStop
    def sw_leftTargetR_active(self,sw):
        self.im_targets_hit(1)
        return procgame.game.SwitchStop
    def sw_leftTargetO_active(self,sw):
        self.im_targets_hit(2)
        return procgame.game.SwitchStop
    def sw_leftTargetN_active(self,sw):
        self.im_targets_hit(3)
        return procgame.game.SwitchStop
    def sw_rightTargetM_active(self,sw):
        self.im_targets_hit(4)
        return procgame.game.SwitchStop
    def sw_rightTargetA_active(self,sw):
        self.im_targets_hit(5)
        return procgame.game.SwitchStop
    def sw_rightTargetN_active(self,sw):
        self.im_targets_hit(6)
        return procgame.game.SwitchStop

    def mode_started(self):
        # scores 1 mil right off the bat
        self.game.score(1000000)
        # shot value starts at 250k
        self.shot_value = 250000
        self.shot_value_layer.set_text("SHOTS = 250,000")
        # six items total to complete
        self.completed_items = 0
        # set up all the tracking bits for progress
        self.im_targets = [False,False,False,False,False,False,False]
        self.left_ramp = [False,False,False,False]
        self.right_ramp = [False,False,False,False]
        self.shields = [False,False,False,False,False,False]
        self.warmachine_hits = 0
        self.whiplash_hits = 0
        self.monger_hits = 0
        # show the intro card
        self.layer = self.title_card
        # delay 2 seconds to the intro loop
        self.delay(delay=2,handler=self.intro_loop)

    def intro_loop(self,phase = 0):
        # set the layer on first run
        if phase == 0:
            self.layer = self.start_layer
        # set the text for the info line
        self.start_info.set_text(self.start_strings[phase])
        # up the phase count
        phase += 1
        # if we're done, get on with it
        if self.phase == 6:
            self.delay(delay=1.5,handler=self.get_going)
        # if not, loop back for the next page
        else:
            self.delay(delay=1.5,handler=self.intro_loop,param=phase)

    def get_going(self):
        # drop the post
        self.game.coils['centerShotPost'].disable()
        # put the display up
        self.layer = self.main_display

    def im_targets_hit(self,target):
        if self.im_targets[target] == True:
            # play some noise?
            pass
        else:
            # play some noise?
            self.im_targets[target] = True
            # check if we're done
            if False not in self.im_targets:
                self.completed_items += 1
                # score the million
                points = 100000
                # remove the layer from the list
                self.remove_info_line(self.im_text_layer)
            else:
                points = self.shot_value
            self.game.score(points)
            # update the lamps
            self.update_lamps()
            # do the display
            self.hit_display(self.im_hit_layer,points)

    def hit_display(self,layer,points):
        self.cancel_delayed("display")
        self.hit_score_layer.set_text(str(self.game.score_display.format_score(points)),blink_frames=8)
        self.layer = layer
        self.delay("display",delay = 2,handler=self.clear_layer)

    def increase_shot_value(self):
        if self.shot_value < 500000:
            self.shot_value += 1000
        # update the shot value layer
        self.shot_value_layer.set_text("SHOTS = " + str(self.game.score_display.format_score(self.shot_value)))

    def remove_info_line(self,layer):
        self.info_lines.remove(layer)
        script = []
        for item in self.info_lines:
            script.append({'layer': item, 'seconds': 2})
        # update the scripted layer
        self.info_line_layer.script = script

    def evt_ball_ending(self):
        if self.running:
            self.end()

    def end(self):
        self.running = False

    def clear_layer(self):
        self.layer = None

    def wipe_delays(self):
        self.__delayed = []

    # simple mode shutdown
    def unload(self):
        self.wipe_delays()
        self.layer = None
        self.game.modes.remove(self)

    # delayed voice quote helper with a list input
    def voice_helper(self, options):
        duration = self.game.sound.play_voice(options[0], action=options[1])
        return duration
