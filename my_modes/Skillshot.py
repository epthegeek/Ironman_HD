import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class Skillshot(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Skillshot, self).__init__(game=game, priority=60, mode_type=AdvancedMode.Manual)
        self.myID = "Skillshot"
        self.running = False
        bg = self.game.animations['shield_logo']
        bar = self.game.animations['gold_bar']
        bar.set_target_position(0,200)
        title = dmd.HDTextLayer(1920/2, 45, self.game.fonts['default'], "center", interior_color=(255, 255, 255),
                                line_color=(0, 0, 1), line_width=4).set_text("SKILLSHOT", blink_frames=6)
        self.score_text = dmd.HDTextLayer(1920/2, 185, self.game.fonts['main_score'], "center", interior_color=(200, 15, 15),
                                line_color=(0, 0, 1), line_width=8)
        self.display = dmd.GroupedLayer(1920, 800, [bg, bar, title, self.score_text],opaque=True)
        self.light = 0
        self.hit = False
        self.saver = False

    def evt_ball_starting(self):
        self.wipe_delays()
        self.saver = False

    def mode_started(self):
        self.leaving = False
        self.ss_value = self.game.getPlayerState('ss_value')
        self.light = 0
        self.hit = False
        self.right_orbit_count = 0
        self.update_lamps()
        self.saver = False

    def sw_flipperLwL_active(self,sw):
        self.change_lane()

    def sw_flipperLwR_active(self,sw):
        self.change_lane()

    def sw_topLeftLane_active(self,sw):
        self.check_ss(0)

    def sw_topRightLane_active(self,sw):
        self.check_ss(1)

    def sw_rightOrbit_active(self,sw):
        if not self.saver:
            self.start_save()
        self.right_orbit_count +=1
        # this is to unload on a short plunge
        if self.right_orbit_count >= 2:
            if not self.hit:
                self.unload()
        return procgame.game.SwitchStop

    def sw_shooterLane_active(self,sw):
        self.cancel_delayed("unload")

    def sw_shooterLane_inactive(self,sw):
        # trying merged lampshow
        self.game.lampctrl.play_show('bottom-to-top', repeat=False,merge=True)

    def sw_shooterLane_inactive_for_2s(self,sw):
        if not self.saver:
            self.start_save()

    def check_ss(self,lane):
        if not self.saver:
            self.start_save()
        self.cancel_delayed("unload")
        self.game.shields.update_lamps()
        if self.light == lane and not self.hit:
            self.hit = True
            self.collect_skillshot()
        else:
            self.unload()

    def collect_skillshot(self):
        # play the sfx
        # score the points
        points = self.ss_value
        self.game.score(points)
        # do the display
        self.skillshot_display(points)
        # raise the value for next time
        self.ss_value += 25000

    def skillshot_display(self,points):
        # play the sound
        self.game.sound.play('skillshot_collect')
        # do the display part
        self.score_text.set_text(self.game.score_display.format_score(points))
        self.layer = self.display
        self.delay(delay=3, handler=self.unload)

    def change_lane(self):
        if self.light == 0:
            self.light = 1
        else:
            self.light= 0
        self.update_lamps()

    def update_lamps(self):
        self.game.lamps['topLeftLane'].disable()
        self.game.lamps['topRightLane'].disable()
        other_shields = [self.game.lamps['leftOutlane'],self.game.lamps['leftReturnLane'],self.game.lamps['rightReturnLane'],self.game.lamps['rightOutlane']]
        for lamp in other_shields:
            lamp.disable()
        if self.light == 0:
            self.game.lamps['topLeftLane'].schedule(0x0F0F0F0F)
        else:
            self.game.lamps['topRightLane'].schedule(0x0F0F0F0F)

    def unload(self):
        print "Unloading: " + self.myID
        # switch to the general gameplay music
        self.game.base.set_music()
        # drop the post just to be safe
        self.game.coils['orbitPost'].disable()
        self.wipe_delays()
        self.game.setPlayerState('ss_value',self.ss_value)
        self.clear_layer()
        self.game.modes.remove(self)
        self.game.shields.update_lamps(force=True)

    ## Kill Switch list
    def sw_rightSpinner_active(self,sw):
        self.shut_it_down_now()
    def sw_leftSpinner_active(self,sw):
        self.shut_it_down_now()
    def sw_centerSpinner_active(self,sw):
        self.shut_it_down_now()
    def sw_leftSlingshot_active(self,sw):
        self.shut_it_down_now()
    def sw_rightSlingshot_active(self,sw):
        self.shut_it_down_now()
    def sw_droneTarget0_active(self,sw):
        self.shut_it_down_now()
    def sw_droneTarget1_active(self,sw):
        self.shut_it_down_now()
    def sw_droneTarget2_active(self,sw):
        self.shut_it_down_now()
    def sw_droneTarget3_active(self,sw):
        self.shut_it_down_now()
    def sw_leftTargetI_active(self,sw):
        self.shut_it_down_now()
    def sw_leftTargetR_active(self,sw):
        self.shut_it_down_now()
    def sw_leftTargetO_active(self,sw):
        self.shut_it_down_now()
    def sw_leftTargetN_active(self,sw):
        self.shut_it_down_now()
    def sw_rightTargetM_active(self,sw):
        self.shut_it_down_now()
    def sw_rightTargetA_active(self,sw):
        self.shut_it_down_now()
    def sw_rightTargetN_active(self,sw):
        self.shut_it_down_now()
    def sw_whiplashLeft_active(self,sw):
        self.shut_it_down_now()
    def sw_whiplashRight_active(self,sw):
        self.shut_it_down_now()
    def sw_rightRampEnter_active(self,sw):
        self.shut_it_down_now()
    def sw_leftRampEnter_active(self,sw):
        self.shut_it_down_now()

    def shut_it_down_now(self):
        if not self.leaving:
            self.leaving = True
            self.unload()

    def clear_layer(self):
        self.layer = None

    def wipe_delays(self):
        self.__delayed = []

        # simple mode shutdown

    # delayed voice quote helper with a list input
    def voice_helper(self, options):
        duration = self.game.sound.play_voice(options[0], action=options[1])
        return duration

    def start_save(self):
        self.saver = True
        self.game.enable_ball_saver()