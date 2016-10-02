import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class WarMachine(procgame.game.AdvancedMode):
    def __init__(self, game):
        super(WarMachine, self).__init__(game=game, priority=16, mode_type=AdvancedMode.Game)
        self.myID = "WarMachine"
        metal_backdrop = self.game.animations['war_machine_bg_blank']
        top = dmd.HDTextLayer(1920 / 2, 100, self.game.fonts['bebas300'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(64, 64, 255))
        top.set_text("JACKPOT NOW")
        self.jp_now_text = dmd.HDTextLayer(1920 / 2, 350, self.game.fonts['bebas300'], "center", line_color=(0, 0, 0), line_width=4,interior_color=(255,255,0))
        self.jp_now_display = dmd.GroupedLayer(1920,800,[metal_backdrop,top,self.jp_now_text],opaque=True)


    def evt_ball_starting(self):
        self.valid = True
        self.multiball_status = self.game.getPlayerState('wm_multiball_status')

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('wm_multiball_status',self.multiball_status)

    def sw_warMachineOpto_active(self,sw):
        # always make the noise
        self.game.sound.play('wm_explosion')
        # if the ball goes up into the war machine
        self.valid = False
        self.delay(delay=0.5,handler=self.make_valid)
        # fire the kicker
        self.game.coils.warMachineKicker.pulse()
        self.process_hit()

    def process_hit(self):
        # the start multiball shot doesn't raise JP value - all others do.
        if self.multiball_status != "READY":
            # raise the drone jackpot by some amount - every time
            self.game.drones.raise_jackpot()

        # if there are shield awards waiting, do that
        if self.game.shields.shield_awards_pending > 0:
            self.game.shields.collect_award()
        if self.multiball_status == "READY":
            # if war machine multiball is ready, do that
            self.game.modes.add(self.game.wm_multiball)
        # this option is add a drone if needed
        elif sum(self.game.drones.drone_tracking) < 4:
            self.game.drones.add(display=True)
        else:
            self.jp_now_text.set_text(self.game.score_display.format_score(self.game.drones.drone_jp_value),blink_frames=10)
            self.layer = self.jp_now_display
            self.delay(delay=5,handler=self.clear_layer)
            pass


    def light_multiball(self):
        self.multiball_status = "READY"
        # do a display?
        self.layer = self.game.animations['war_machine_start']
        # change the music
        self.game.base.set_music()
        self.delay(delay=0.5,handler=self.voice_helper,param=['war_machine_ready',procgame.sound.PLAY_QUEUED])
        self.delay(delay=3.6,handler=self.clear_layer)
        # update the lamps?

    def make_valid(self):
        self.valid = True


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
