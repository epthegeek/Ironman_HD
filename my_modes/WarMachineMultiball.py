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
        self.jp_delays = [1.8,1.8,1.8,1.8,1.8]
        self.d_jp_movies = ['war_machine_d_jp_1','war_machine_d_jp_2','war_machine_d_jp_3']
        self.d_jp_delays = [3.5,3.5,3.5]
        self.top = dmd.HDTextLayer(1920 / 2, 50, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(64, 64, 224))
        self.bottom = dmd.HDTextLayer(1920 / 2, 400, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(255,255,0))
        self.text_display = dmd.GroupedLayer(1920,800,[self.top,self.bottom],opaque=True)
        self.main_text_info = dmd.HDTextLayer(1920 / 2, 620, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(224, 224, 224))
        # group layers for the main display
        self.super_main = dmd.GroupedLayer(1920,800,[self.main_text_info],opaque=True)
        drones_main_layers = []
        for layer in self.game.drones.drone_layers:
            drones_main_layers.append(layer)
        drones_main_layers.append(self.main_text_info)
        self.drones_main = dmd.GroupedLayer(1920,800,drones_main_layers,opaque=True)
        self.valid = [True,True]
        self.left_arrow = self.game.animations['left_arrow']
        self.left_mid_arrow = self.game.animations['left_mid_arrow']
        self.left_mid_arrow.set_target_position(384,0)
        self.center_arrow = self.game.animations['center_arrow']
        self.center_arrow.set_target_position(768,0)
        self.right_mid_arrow = self.game.animations['right_mid_arrow']
        self.right_mid_arrow.set_target_position(1152,0)
        self.right_arrow = self.game.animations['right_arrow']
        self.right_arrow.set_target_position(1536,0)
        self.arrows = [self.left_arrow, self.left_mid_arrow,self.center_arrow,self.right_mid_arrow,self.right_arrow]
        big5_list = []
        for layer in self.arrows:
            big5_list.append(layer)
        big5_list.append(self.main_text_info)
        self.big5_main = dmd.GroupedLayer(1920, 800, big5_list, opaque=True)
        #
        # text layers for intro display
        intro_1 = dmd.HDTextLayer(1850, 650,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224)).set_text("MULTIBALL")
        intro_2 = dmd.HDTextLayer(1850, 550,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224)).set_text("MACHINE")
        intro_3 = dmd.HDTextLayer(1850, 450,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224)).set_text("WAR")
        self.intro_movie = self.game.animations['war_machine_start']
        self.intro = dmd.GroupedLayer(1920,800,[self.intro_movie,intro_1,intro_2,intro_3],opaque = True)

    def mode_started(self):
        self.valid = [True, True]
        self.display_type = "drones"
        self.start_multiball()
        self.jp_idx = 0
        self.d_jp_idx = 0

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
        self.intro_movie.reset()
        self.layer = self.intro
        self.delay(delay=3,handler=self.set_main_display)
        # audio callout?
        self.game.sound.play_voice('war_machine_multiball')
        # change the music
        self.game.sound.play_music('war_machine_mb',loops=-1)
        # launch balls
       # self.game.trough.launch_and_autoplunge_balls(1)
        # reset the drone jackpots
        self.jackpots_init('drone',True)
        self.jackpots_init('big5',False)

    def jackpot_display(self,type,points):
        self.cancel_delayed("display")
        if type == 'Super':
            choice = 'war_machine_super'
            text = "SUPER JACKPOT"
            delay = 3
            voice = 'super_jackpot'
        elif type == self.d_jp_movies:
            text = "DOUBLE JACKPOT"
            choice = self.d_jp_movies[self.d_jp_idx]
            delay = self.d_jp_delays[self.d_jp_idx]
            self.d_jp_idx += 1
            if self.d_jp_idx > 2:
                self.d_jp_idx = 0
            voice = 'double_jackpot'
        else:
            text = "JACKPOT"
            choice = self.jp_movies[self.jp_idx]
            delay = self.jp_delays[self.jp_idx]
            self.jp_idx += 1
            if self.jp_idx > 4:
                self.jp_idx = 0
            voice = 'jackpot'
        self.game.animations[choice].reset()
        self.layer = self.game.animations[choice]
        self.game.sound.play_voice(voice)
        self.delay("display",delay=delay,handler=lambda:self.text_portion(text,points))

    def text_portion(self,string,points):
        self.top.set_text(string)
        self.bottom.set_text(self.game.score_display.format_score(points))
        self.layer = self.text_display
        self.delay("display",delay=1,handler=self.set_main_display)

    def set_main_display(self):
        # if that was the last drone jackpot - shift to the big5
        if True not in self.drone_jackpots and self.display_type == 'drones':
            self.jackpots_init('big5', True)
            self.display_type = 'big5'
        elif True not in self.big5_jackpots and self.display_type == 'big5':
            self.display_type = 'super'
            self.light_super()
        elif self.display_type == 'super':
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
                self.game.drones.drone_layers[x].enabled = True
            else:
                self.game.drones.drone_layers[x].enabled = False
        for x in range (0,5,1):
            if self.big5_jackpots[x]:
                self.arrows[x].enabled = True
            else:
                self.arrows[x].enabled = False

    def jackpots_init(self,set,value):
        if set == 'drone':
            for jp in range (0,4,1):
                self.drone_jackpots[jp] = value
        elif set == 'big5':
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

    def validate(self,orbit):
        self.valid[orbit] = True
