import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class Skillshot(procgame.game.Mode):

    def __init__(self,game):
        super(Skillshot, self).__init__(game=game, priority=60)
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
        self.ss_value = self.game.getPlayerState('ss_value')
        self.light = 0
        self.hit = False
        self.right_orbit_count = 0

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

    def sw_shooterLane_active(self,sw):
        self.cancel_delayed("unload")

    def sw_shooterLane_inactive(self,sw):
        # start a timer to unload if nothing else happens
        self.delay("unload",delay=15,handler=self.unload)

    def check_ss(self,lane):
        self.cancel_delayed("unload")
        if self.light == lane:
            self.hit = True
            self.collect_skillshot()
        else:
            self.unload()

    def collect_skillshot(self):
        # play the sfx
        # score the points
        self.game.score(self.ss_value)
        # do the display
        self.skillshot_display(self.ss_value)

    def skillshot_display(self,points):
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
        if self.light == 0:
            self.game.lamps['topLeftLane'].enable()
        else:
            self.game.lamps['topRightLane'].enable()

    def unload(self):
        self.wipe_delays()
        self.game.setPlayerState('ss_value')
        self.clear_layer()
        self.game.modes.remove(self)