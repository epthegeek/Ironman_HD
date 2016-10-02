import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class MongerToy(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(MongerToy, self).__init__(game=game, priority=20, mode_type=AdvancedMode.System)
        self.myID = "MongerToy"
        # specific monger toy status
#        self.status = None
        # for testing set status to down
        self.status = "INIT"
        self.target = "DOWN"

        self.monger_hit_movies = [self.game.animations['monger_hit_1'],
                                  self.game.animations['monger_hit_2'],
                                  self.game.animations['monger_hit_3'],
                                  self.game.animations['monger_hit_4']]
        self.monger_hit_idx = 0
        self.hit_score_text = dmd.HDTextLayer(1820, 550, self.game.fonts['bebas200'], "right", line_color=[0, 0, 0],line_width=4, interior_color=[146, 24, 222])
        # lower the monger
        self.reset_toy()

    def evt_ball_starting(self):
        # check if the monger should be up for the player, and if not, raise - if up and should be down - lower
        stat = self.game.getPlayerState('monger_status')
        if stat == "UP" or stat == "READY":
            # monger should be up
            if self.status == "UP":
                pass
            else:
                self.rise()
        else:
            # monger should be down
            if self.status == "DOWN":
                pass
            else:
                self.fall()

    def sw_motorSwitchTop_active(self,sw):
        if self.status == "MOVING" and self.target == "UP":
            self.game.coils.mongerMotor.disable()
            self.status = "UP"

    def sw_motorSwitchBot_active(self,sw):
        if self.status == "MOVING" and self.target == "DOWN":
            self.game.coils.mongerMotor.disable()
            self.status = "DOWN"

    # Blocking whiplash hits when the toy is up
    # TODO: check to see if sounds/points during
    def sw_whiplashLeft_active(self,sw):
        if self.status == "UP":
            return procgame.game.SwitchStop

    def sw_whiplashRight_active(self,sw):
        if self.status == "UP":
            return procgame.game.SwitchStop


    def rise(self):
        # if toy is down, lift it
        if self.status == "DOWN":
            # key that we're moving
            self.status= "MOVING"
            # set the target position we're looking for
            self.target = "UP"
            # run the motor
            self.run_motor()
        # if toy is moving, change the target to stop at
        elif self.status == "MOVING":
            self.target = "UP"
        # otherwise, it's already up and it's good
        else:
            pass

    def fall(self):
        # if the monger is up, it needs to go down
        if self.status == "UP":
            # key that we're moving
            self.status = "MOVING"
            # set the target to stop at
            self.target = "DOWN"
            # turn on the motor
            self.run_motor()
        # if already moving - reset the target
        elif self.status == "MOVING":
            self.target = "DOWN"
        # otherwise it's down and it's good
        else:
            pass

    def reset_toy(self):
        if self.status == "INIT" and self.game.switches['motorSwitchBot'].is_active():
            pass
        # if the toy is already down, fine
        elif self.status == "DOWN":
            pass
        # if not, or we don't know, cycle until it is
        else:
            self.target = "DOWN"
            self.status = "MOVING"
            self.run_motor()

    def run_motor(self):
        self.game.coils.mongerMotor.patter(on_time=6,off_time=6)


    def monger_rise_video(self):
        self.game.animations['monger_rise'].reset()
        self.layer = self.game.animations['monger_rise']
        self.delay(delay=7,handler=self.clear_layer)


    def toy_hit_display(self,points):
        # cancel any pending clear
        self.cancel_delayed("clear")
        # set up the video clip
        video = self.monger_hit_movies[self.monger_hit_idx]
        video.reset()
        # set the text for the hit display
        self.hit_score_text.set_text(str(self.game.score_display.format_score(points)))
        # make the layer
        self.layer = dmd.GroupedLayer(1920, 800, [video, self.hit_score_text], opaque=True)
        # set a clear delay
        self.delay("clear", delay=2.5, handler=self.clear_layer)
        # up the index
        self.monger_hit_idx += 1
        if self.monger_hit_idx > 3:
            self.monger_hit_idx = 0

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
