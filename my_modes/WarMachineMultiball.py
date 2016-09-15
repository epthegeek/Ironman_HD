import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class WarMachineMultiball(procgame.game.Mode):

    def __init__(self,game):
        super(WarMachineMultiball, self).__init__(game=game, priority=50)
        self.myID = "WarMachineMultiball"
        self.running = False
        self.drone_jackpots = [False,False,False,False]
        self.big5_jackpots = [False,False,False,False,False]
        self.super = False
        self.jp_movies = ['war_machine_jp_1','war_machine_jp_2','war_machine_jp_3','war_machine_jp_4','war_machine_jp_5']
        self.d_jp_movies = ['war_machine_d_jp_1','war_machine_d_jp_2','war_machine_d_jp_3']
        self.top = dmd.HDTextLayer(1920 / 2, 50, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(64, 64, 224))
        self.bottom = dmd.HDTextLayer(1920 / 2, 400, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(255,255,0))
        self.text_display = dmd.GroupedLayer(1920,800,[self.top,self.bottom],opaque=True)
        self.main_text_info = dmd.HDTextLayer(1920 / 2, 620, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(224, 224, 224))
        # group layers for the main display
        self.super_main = dmd.GroupedLayer(1920,800,[self.main_text_info],opaque=True)
        self.big5_main = dmd.GroupedLayer(1920,800,[self.main_text_info],opaque=True)
        drones_main_layers = []
        for layer in self.game.drones.drone_layers:
            drones_main_layers.append(layer)
        drones_main_layers.append(self.main_text_info)
        self.drones_main = dmd.GroupedLayer(1920,800,drones_main_layers,opaque=True)
        self.valid = [True,True]

    def mode_started(self):
        self.valid = [True, True]
        self.display_type = "drones"
        self.start_multiball()

    def evt_ball_ending(self):
        if self.running:
            self.end_multiball()

    def evt_single_ball_play(self):
        if self.running:
            self.end_multiball()

    def sw_droneTarget0_active(self,sw):
        self.drone_hit(0)
        return procgame.game.SwitchStop

    def sw_droneTarget1_active(self,sw):
        self.drone_hit(1)
        return procgame.game.SwitchStop

    def sw_droneTarget2_active(self,sw):
        self.drone_hit(2)
        return procgame.game.SwitchStop

    def sw_droneTarget3_active(self,sw):
        self.drone_hit(3)
        return procgame.game.SwitchStop

    def sw_leftSpinner_active(self,sw):
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    def sw_rightSpinner_active(self,sw):
        self.game.monger.spinner_noise()
        return procgame.game.SwitchStop

    def sw_leftOrbit_active(self,sw):
        if self.valid[0]:
            self.make_invalid(1)
            self.double_jp_hit(0)
        return procgame.game.SwitchStop

    def sw_leftRampExit_active(self,sw):
        self.double_jp_hit(1)

    def sw_centerSpinner_active(self,sw):
        self.double_jp_hit(2)
        return procgame.game.SwitchStop

    def sw_rightRampExit_active(self,sw):
        self.double_jp_hit(3)

    def sw_rightOrbit_active(self,sw):
        if self.valid[1]:
            self.make_invalid(0)
            self.double_jp_hit(4)

    def sw_warMachineOpto_active(self,sw):
        self.game.coils.warMachineKicker.pulse()
        # if the ball goes up into the war machine
        if self.display_type == 'super':
            # TODO: need to make this adjust to what it should really do points wise
            points = 1000000
            self.game.score(points)
            self.game.jackpot_display('SUPER',points)
        else:
            pass
        return procgame.game.SwitchStop

    def drone_hit(self,target):
        if self.drone_jackpots[target]:
            self.drone_jackpots[target] = False
            # score the jp value
            points = self.game.drones.drone_jp_value
            self.game.score(points)
            # do the display
            self.jackpot_display(self.jp_movies,points)
        else:
            self.drone_thunk()

    def drone_thunk(self):
        # TODO: Check on the specifics of these
        # score some points
        self.game.score(10000)
        # play a noise ?

    def double_jp_hit(self,target):
        if self.big5_jackpots[target]:
            self.big5_jackpots[target] = False
            points = self.game.drones.drone_jp_value * 2
            self.game.score(points)
            self.jackpot_display(self.d_jp_movies,points)
        else:
            self.double_jp_thunk()

    def double_jp_thunk(self):
        # TODO: not sure what to do with this, have to check
        self.game.score(10000)

    def start_multiball(self):
        self.running = True
        # display
        self.game.animations['war_machine_start'].reset()
        self.layer = self.game.animations['war_machine_start']
        self.delay(delay=3,handler=self.set_main_display)
        # audio callout?
        self.game.sound.play_voice('war_machine_multiball')
        # change the music
        # launch balls
        self.game.trough.launch_and_autoplunge_balls(1)
        # reset the drone jackpots
        self.jackpots_init('drone',True)
        self.jackpots_init('big5',False)

    def jackpot_display(self,type,points):
        self.cancel_delayed("display")
        if type == 'Super':
            choice = 'war_machine_super'
            text = "SUPER JACKPOT"
        elif type == self.d_jp_movies:
            text = "DOUBLE JACKPOT"
            choice = random.choice(type)
        else:
            text = "JACKPOT"
            choice = random.choice(type)
        self.game.animations[choice].reset()
        self.layer = self.game.animations[choice]
        self.delay("display",delay=1.5,handler=lambda:self.text_portion(text,points))

    def text_portion(self,string,points):
        self.top.set_text(string)
        self.bottom.set_text(self.game.score_display.format_score(points))
        self.layer = self.text_display
        self.delay("display",delay=1,handler=self.set_main_display)

    def set_main_display(self):
        # if that was the last drone jackpot - shift to the big5
        if True not in self.drone_jackpots and self.display_type == 'drone':
            self.jackpots_init('big5', True)
            self.display_type = 'big5'
        if True not in self.big5_jackpots and self.display_type == 'big5':
            self.display_type = 'super'
            self.light_super()
        if self.display_type == 'super':
            self.jackpots_init('drones',True)
            self.display_type = 'drones'

        self.update_main_layers()
        if self.display_type == 'super':
            self.main_text_info.set_text("SHOOT FOR WAR MACHINE")
            self.layer = self.super_main
        elif self.display_type == 'big5':
            self.main_text_info.set_text("SHOOT THE FLASHING ARROWS")
            self.layer = self.big5_main
        else:
            self.main_text_info.set_text("SHOOT THE DRONE TARGETS")
            self.layer = self.drones_main

    def light_super(self):
        # this should turn on light so rsomething - or maybe update_lamps can handle it
        pass

    def update_main_layers(self):
        for x in range (0,4,1):
            if self.drone_jackpots[x]:
                print str(x) + " IS VALID"
                self.game.drones.drone_layers[x].enabled = True
            else:
                self.game.drones.drone_layers[x].enabled = False
        # TODO: need to add arrow layers

    def jackpots_init(self,set,value):
        if set == 'drone':
            for jp in range (0,4,1):
                self.drone_jackpots[jp] = value
        if set == 'big5':
            for jp in range (0,5,1):
                self.big5_jackpots[jp] = value

    def end_multiball(self):
        self.running = False
        # reset the drone layers for use outside of MB
        for layer in self.game.drones.drone_layers:
            layer.enabled = True
        self.unload()

    def make_invalid(self,orbit):
        self.valid[orbit] = False
        self.delay(delay=1,handler=lambda: self.validate(orbit))

    def validate(self,oribt):
        self.valid[orbit] = True
