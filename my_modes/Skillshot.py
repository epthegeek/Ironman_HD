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

    def mode_started(self):
        self.leaving = False
        self.ss_value = self.game.getPlayerState('ss_value')
        self.light = 0
        self.hit = False
        self.right_orbit_count = 0
        self.update_lamps()

    def sw_flipperLwL_active(self,sw):
        self.change_lane()

    def sw_flipperLwR_active(self,sw):
        self.change_lane()

    def sw_topLeftLane_active(self,sw):
        self.check_ss(0)

    def sw_topRightLane_active(self,sw):
        self.check_ss(1)

    def sw_rightOrbit_active(self,sw):
        self.right_orbit_count +=1
        # this is to unload on a short plunge
        if self.right_orbit_count >= 2:
            if not self.hit:
                self.unload()
        return procgame.game.SwitchStop

    def sw_shooterLane_active(self,sw):
        self.cancel_delayed("unload")

    def sw_shooterLane_inactive(self,sw):
        # and fire the orbit post
        self.game.coils['orbitPost'].patter(on_time=4,off_time=4,original_on_time=20)
        # drop the post in 2 seconds
        self.delay(delay=2,handler=self.game.coils['orbitPost'].disable)
        # trying merged lampshow
        self.game.lampctrl.play_show('bottom-to-top', repeat=False,merge=True)

    def check_ss(self,lane):
        self.cancel_delayed("unload")
        self.game.shields.update_lamps()
        if self.light == lane:
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
        print "SKILLSHOT LAMP UPDATE"
        self.game.lamps['topLeftLane'].disable()
        self.game.lamps['topRightLane'].disable()
        other_shields = [self.game.lamps['leftOutlane'],self.game.lamps['leftReturnLane'],self.game.lamps['rightReturnLane'],self.game.lamps['rightOutlane']]
        for lamp in other_shields:
            lamp.disable()
        if self.light == 0:
            print "SS: TURN ON LEFT LIGHT"
            self.game.lamps['topLeftLane'].enable()
        else:
            print "SS: TURN ON RIGHT LIGHT"
            self.game.lamps['topRightLane'].enable()

    def unload(self):
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