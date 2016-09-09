import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class MongerToy(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(MongerToy, self).__init__(game=game, priority=20, mode_type=AdvancedMode.Game)
        self.myID = "MongerToy"
        # specific monger toy status
        self.status = None
        self.target = "DOWN"

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
            self.game.coilsmongerMotor.disable()
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
        # if the toy is already down, fine
        if self.status == "DOWN":
            pass
        # if not, or we don't know, cycle until it is
        else:
            self.target = "DOWN"
            self.status = "MOVING"
            self.run_motor()

    def run_motor(self):
        self.game.coils.mongerMotor.patter(on_time=6,off_time=6)