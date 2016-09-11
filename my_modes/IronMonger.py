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
        self.delay_names = {0,'leftSpinner',
                            1, 'centerSpinner',
                            2, 'rightSpinner',
                            3, 'leftOrbit',
                            4, 'rightOrbit'}


    def evt_ball_starting(self):
        # clear used to determine wait time on repeat hits to switches
        self.clear = True
        self.letters = self.game.getPlayerState('monger_letters')
        self.battles = self.game.getPlayerState('monger_battles')
        self.status = self.game.getPlayerState('monger_status')
        # for locking out spinners based on conditions
        self.valid = [True,True,True,True,True]
        self.toy_valid = True
        self.toy_letters = self.game.getPlayerState('toy_letters')
        self.orbit_quiet = False

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
        if input == "Release":
            self.game.coils.ironmongerMagnet.disable()


    def sw_leftSpinner_active(self,sw):
        if self.valid[0]:
            self.set_valid_switches(0)
            self.letter_hit(0)

    def sw_centerSpinner_active(self,sw):
        if self.valid[1]:
            self.set_valid_switches(1)
            self.letter_hit(1)

    def sw_rightSpinner_active(self,sw):
        if self.valid[2]:
            self.set_valid_switches(2)
            self.letter_hit(2)

    def sw_leftOrbit_active(self,sw):
        if self.valid[3]:
            self.set_valid_switches(3)
            self.letter_hit(3)
        # play the orbit noise
        self.orbit_noise()

    def sw_rightOrbit_active(self,sw):
        if self.valid[4]:
            self.set_valid_switches(4)
            self.letter_hit(4)
        # play the orbit noise
        self.orbit_noise()

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

    def letter_hit(self):
        if self.letters < 10:
            self.letters += 1
            if self.letters == 10:
                self.game.monger_toy.rise()

    def hit_toy(self):
        if self.game.monger_toy.status == "UP":
            # play a sound
            # score some points?
            # add a letter
            if self.toy_letters < 6:
                self.toy_letters += 1
                if self.toy_letters == 6:
                    self.start_multiball()

    def start_multiball(self):
        self.game.modes.add(self.game.monger_multiball)
        self.game.monger_multiball.start_multiball()

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

    def set_valid_switches(self,switch):
        # left spinner
        if switch == 0:
            # affects left spinner and left orbit
            self.process_validation([0,3])
        # center spinner
        elif switch == 1:
            # affects only itself
            self.process_validation([1])
        # right spinner
        elif switch == 2:
            # affects right spinner and right orbit
            self.process_validation([2,4])
        # left orbit
        elif switch == 3:
            # affect the left spinner and the right orbit
            self.process_validation([0,4])
            # forces re-validation of the right spinner in case of a repeat fast loop
            self.validate(2)
        # right orbit
        elif switch == 4:
            # affects the left orbit and the right spinner
            self.process_validation([3,2])
            # forces re-validation of the left spinner in case of a repeat fast loop
            self.validate(0)

    def process_validation(self,list):
        self.stop_valid_reset(list)
        self.invalidate_switches(list)
        self.revalidate(list)

    def invalidate_switches(self,list):
        for item in list:
            self.valid[item] = False

    def stop_valid_reset(self,list):
        for item in list:
            self.cancel_delayed(self.delay_names[item])

    def revalidate(self,list):
        for item in list:
            self.delay(self.delay_names[item],delay=2,handler=lambda: self.validate(item))

    def orbit_noise(self):
        if not self.orbit_quiet:
            self.orbit_quiet = True
            self.game.sound.play('helicopter')
            self.delay(delay=1,handler=self.orbit_noise_reset)

    def orbit_noise_reset(self):
        self.orbit_quiet = False