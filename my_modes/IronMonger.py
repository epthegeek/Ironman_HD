import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class IronMonger(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(IronMonger, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "IronMonger"
        self.monger_lamps = [self.game.lamps['mongerM'],
                             self.game.lamps['mongerO'],
                             self.game.lamps['mongerN'],
                             self.game.lamps['mongerG'],
                             self.game.lamps['mongerE'],
                             self.game.lamps['mongerR']]


    def evt_ball_starting(self):
        # clear used to determine wait time on repeat hits to switches
        self.clear = True
        self.letters = self.game.getPlayerState('monger_letters')
        self.battles = self.game.getPlayerState('monger_battles')
        self.status = self.game.getPlayerState('monger_status')
        # for locking out spinners based on conditions
        self.valid = [True,True,True]
        self.toy_valid = True
        self.toy_letters = self.game.getPlayerState('toy_letters')

    def evt_ball_ending(self):
        self.game.setPlayerState('monger_letters', self.letters)
        self.game.setPlayerState('monger_battles', self.battles)
        self.game.setPlayerState('monger_status', self.status)
        self.game.setPlayerState('toy_letters', self.toy_letters)

    def magnet(self,input):
        if input == "Throw":
            self.game.coils.ironmongerMagnet.pulse()
        if input == "Hold":
            self.game.coils.ironmongerMagnet.patter(on_time=2,off_time=6,original_on_time=10)


    def sw_leftSpinner_active(self,sw):
        if self.valid[0]:
            self.valid[0] = False
            self.spinner_hit(0)

    def sw_centerSpinner_active(self,sw):
        if self.valid[1]:
            self.valid[1] = False
            self.spinner_hit(1)

    def sw_rightSpinner_active(self,sw):
        if self.valid[2]:
            self.valid[2] = False
            self.spinner_hit(2)

    def sw_mongerOptoLeft_active(self,sw):
        if self.toy_valid:
            self.toy_valid = False
            self.hit_toy()

    def sw_mongerOptoRight_active(self,sw):
        if self.toy_valid:
            self.toy_valid = False
            self.hit_toy()

    def sw_mongerOptoCenter_active(self,sw):
        if self.toy_valid:
            self.toy_valid = False
            self.hit_toy()

    def spinner_hit(self,spinner):
        # reset the valid in a bit
        self.delay(delay=2,handler=lambda:self.validate(spinner))
        if self.letters < 10:
            self.letters += 1
            if self.letters == 10:
                self.rise()

    def hit_toy(self):
        if self.status == "UP":
            # play a sound
            # score some points?
            # add a letter
            if self.toy_letters < 6:
                self.toy_letters += 1
                if self.toy_letters == 6:
                    self.start_multiball()

    def rise(self):
        if self.game.switches['motorSwitchBot'].is_active() and not self.game.switches['motorSwitchTop'].is_active():
            # raise the monger
            self.status= "MOVING"
            self.game.coils.mongerMotor.patter(on_time=6, off_time=6)

    def lower(self):
        if self.game.switches['motorSwitchTop'].is_active() and not self.game.switches['motorSwitchBot'].is_active():
            self.status = "MOVING"
            self.game.coils.mongerMotor.patter(on_time=6,off_time=6)

    def sw_motorSwitchTop_active(self,sw):
        self.game.coils.mongerMotor.disable()
        self.status == "UP"

    def sw_motorSwitchBot_active(self,sw):
        self.game.coilsmongerMotor.disable()

    def start_multiball(self):
        print "START MULTIBALL"
        pass

    def validate(self,spinner):
        self.valid[spinner] = True

    def update_lamps(self):
        for lamp in self.monger_lamps:
            lamp.disable()
        if self.status == "OPEN":
            if self.letters < 4:
                pass
            else:
                blinker = 11
                for n in range (0,11,1):
                    if n < 4:
                        pass
                    if n < self.letters:
                        self.monger_lamps[n].enable()
                    if n == self.letters:
                        self.monger_lamps[n].enable()
                        blinker = n + 1
                    if n == blinker:
                        self.monger_lamps[n].schedule(0x00FF00FF)
                    else:
                        pass
        if self.status == "UP":
            for n in range(0,7,1):
                if n <= self.toy_letters:
                    self.monger_lamps[n].enable()
                else:
                    pass