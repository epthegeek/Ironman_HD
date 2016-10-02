import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class WarMachineMultiball(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(WarMachineMultiball, self).__init__(game=game, priority=50,mode_type=AdvancedMode.Manual)
        self.myID = "WarMachineMultiball"
        self.running = False
        self.drone_jackpots = [False,False,False,False]
        self.big5_jackpots = [False,False,False,False,False]
        self.super = False
        self.jp_movies = ['war_machine_jp_1','war_machine_jp_2','war_machine_jp_3','war_machine_jp_4','war_machine_jp_5']
        self.jp_delays = [1.8,1.8,1.8,1.8,1.8]
        self.jp_audio_clips = ['wm_jp_1','wm_jp_2','wm_jp_3','wm_jp_4']
        self.d_jp_movies = ['war_machine_d_jp_1','war_machine_d_jp_2','war_machine_d_jp_3']
        self.d_jp_delays = [2.8,2.7,2.3]
        self.d_jp_audio_clips = ['wm_djp_1','wm_djp_2','wm_djp_3','wm_djp_4','wm_djp_5']
        metal_backdrop = self.game.animations['war_machine_bg_blank']
        self.top = dmd.HDTextLayer(1920 / 2, 100, self.game.fonts['bebas300'], "center", line_color=(0, 0, 0), line_width=9,interior_color=(64, 64, 255))
        self.bottom = dmd.HDTextLayer(1920 / 2, 350, self.game.fonts['bebas300'], "center", line_color=(0, 0, 0), line_width=9,interior_color=(255,255,0))
        self.text_display = dmd.GroupedLayer(1920,800,[metal_backdrop,self.top,self.bottom],opaque=True)
        self.main_text_info = dmd.HDTextLayer(1920 / 2, 565, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(224, 224, 224))
        # group layers for the main display
        super_1 = dmd.HDTextLayer(1130, 110,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=9,interior_color=(224,0,0)).set_text("SHOOT",blink_frames=10)
        super_2 = dmd.HDTextLayer(1130, 280,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=9,interior_color=(224,0,0)).set_text("WAR",blink_frames=10)
        super_3 = dmd.HDTextLayer(1130, 450,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=9,interior_color=(224,0,0)).set_text("MACHINE",blink_frames=10)
        wm_backdrop = self.game.animations['war_machine_bg']
        self.super_main = dmd.GroupedLayer(1920,800,[wm_backdrop,super_3,super_2,super_1],opaque=True)
        # drones
        self.drone_0_layer = self.game.animations['drone_0_sm']
        self.drone_0_layer.set_target_position(183,75)
        self.drone_1_layer = self.game.animations['drone_1_sm']
        self.drone_1_layer.set_target_position(585,75)
        self.drone_2_layer = self.game.animations['drone_2_sm']
        self.drone_2_layer.set_target_position(997,75)
        self.drone_3_layer = self.game.animations['drone_3_sm']
        self.drone_3_layer.set_target_position(1366,75)
        self.drone_layers = [self.drone_0_layer, self.drone_1_layer, self.drone_2_layer,self.drone_3_layer]
        drones_main_layers = []
        drones_main_layers.append(metal_backdrop)
        for layer in self.drone_layers:
            drones_main_layers.append(layer)
        drones_main_layers.append(self.main_text_info)
        self.drones_main = dmd.GroupedLayer(1920,800,drones_main_layers,opaque=True)
        self.left_arrow = self.game.animations['left_arrow']
        self.left_arrow.set_target_position(220,140)
        self.left_mid_arrow = self.game.animations['left_mid_arrow']
        self.left_mid_arrow.set_target_position(520,140)
        self.center_arrow = self.game.animations['center_arrow']
        self.center_arrow.set_target_position(823,140)
        self.right_mid_arrow = self.game.animations['right_mid_arrow']
        self.right_mid_arrow.set_target_position(1122,140)
        self.right_arrow = self.game.animations['right_arrow']
        self.right_arrow.set_target_position(1420,140)
        self.arrows = [self.left_arrow, self.left_mid_arrow,self.center_arrow,self.right_mid_arrow,self.right_arrow]
        big5_list = []
        big5_list.append(metal_backdrop)
        for layer in self.arrows:
            big5_list.append(layer)
        big5_list.append(self.main_text_info)
        self.big5_main = dmd.GroupedLayer(1920, 800, big5_list, opaque=True)

        #
        # text layers for intro display
        intro_1 = dmd.HDTextLayer(70, 650,self.game.fonts['default'],"left",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        intro_1.set_text("MULTIBALL",blink_frames=6)
        intro_2 = dmd.HDTextLayer(70, 550,self.game.fonts['default'],"left",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        intro_2.set_text("MACHINE",blink_frames=6)
        intro_3 = dmd.HDTextLayer(70, 450,self.game.fonts['default'],"left",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        intro_3.set_text("WAR",blink_frames=6)
        self.intro_movie = self.game.animations['war_machine_ready']
        self.intro = dmd.GroupedLayer(1920,800,[self.intro_movie,intro_1,intro_2,intro_3],opaque = True)

    def mode_started(self):
        self.valid = [True, True]
        self.display_type = "drones"
        self.start_multiball()
        self.jp_idx = 0
        self.d_jp_idx = 0
        self.super_jp_value = 0
        # add the switch filter
        if self.game.mb_switch_stop not in self.game.modes:
            self.game.modes.add(self.game.mb_switch_stop)
        # add the mode light
        self.game.mark.mode_light(1)

    def evt_ball_ending(self,(shoot_again,last_ball)):
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

    def sw_warMachineOpto_active(self,sw):
        # TODO: for the first 20 seconds, any shot to war machine should add a ball
        self.game.coils.warMachineKicker.pulse()
        # always make the noise
        self.game.sound.play('wm_explosion')
        # if the ball goes up into the war machine
        if self.super == True:
            points = self.super_jp_value
            self.game.score(points)
            self.jackpot_display('super',points)
            # Turn the super back off
            self.super = False
            # reset the super for the next round
            self.super_jp_value = 0
            # up the jackpot value by 100k
            self.game.drones.drone_jp_value += 100000
        else:
            pass
        return procgame.game.SwitchStop

    def drone_hit(self,target):
        if self.drone_jackpots[target]:
            self.drone_jackpots[target] = False
            # score the jp value
            points = self.game.drones.drone_jp_value
            self.game.score(points)
            # add the points to the super
            self.super_jp_value += points
            # do the display
            self.jackpot_display(self.jp_movies,points)
            # play the sound
            self.game.sound.play(self.jp_audio_clips[self.jp_audio_idx])
            self.jp_audio_idx += 1
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
            # double the current jackpot value
            points = self.game.drones.drone_jp_value * 2
            self.game.score(points)
            # add the jackpot to the super value
            self.super_jp_value += points
            self.jackpot_display(self.d_jp_movies,points)
            # turn on the super jackpot
            self.super = True
            # play the sound
            self.game.sound.play(self.d_jp_audio_clips[self.d_jp_audio_idx])
            self.d_jp_audio_idx += 1
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
        # do the mark here - if needed
        if self.game.mark.player_mark < 6:
            self.game.mark.player_mark += 1
            self.game.mark.score()
            self.delay(delay=3,handler=self.game.mark.completed,param=self.set_main_display)
            self.delay(delay=3,handler=self.clear_layer)
        else:
            self.delay(delay=3,handler=self.set_main_display)
        # change the music
        self.game.base.set_music()
        # audio callout
        self.game.sound.play_voice('war_machine_multiball',action=procgame.sound.PLAY_FORCE)

        # launch balls
        self.game.trough.launch_and_autoplunge_balls(1)
        # reset the drone jackpots
        self.jackpots_init('drone',True)
        self.jackpots_init('big5',False)

    def jackpot_display(self,type,points):
        self.cancel_delayed("display")
        if type == 'super':
            choice = 'war_machine_super'
            text = "SUPER JACKPOT"
            voice = 'super_jackpot'
            delay = 3
            # reset the drone jackpots
            self.jackpots_init('drone',True)
            # complete the mode light
            self.game.mark.mode_completed(1)

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
        # reset the video clip
        self.game.animations[choice].reset()
        # play the video clip
        self.layer = self.game.animations[choice]
        # delay the jackpot callout
        self.delay(delay=0.5,handler=self.voice_helper,param=[voice,procgame.sound.PLAY_NOTBUSY])
        # go to the text display after a delay
        self.delay("display",delay=delay,handler=self.text_portion_helper,param=[text,points])

    def text_portion_helper(self,options):
        self.text_portion(options[0],options[1])

    def text_portion(self,string,points):
        self.top.set_text(string)
        self.bottom.set_text(self.game.score_display.format_score(points),blink_frames=10)
        self.layer = self.text_display
        self.delay("display",delay=1.5,handler=self.set_main_display)

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
                self.drone_layers[x].enabled = True
            else:
                self.drone_layers[x].enabled = False
        for x in range (0,5,1):
            if self.big5_jackpots[x]:
                self.arrows[x].enabled = True
            else:
                self.arrows[x].enabled = False

    def jackpots_init(self,set,value):
        if set == 'drone':
            for jp in range (0,4,1):
                self.drone_jackpots[jp] = value
            # reset the audio index
            self.jp_audio_idx = 0
        elif set == 'big5':
            for jp in range (0,5,1):
                self.big5_jackpots[jp] = value
            # reset the audio index
            self.d_jp_audio_idx = 0
        self.update_main_layers()

    def end_multiball(self):
        self.running = False
        # reset the drone targets
        for n in range (0,4,1):
            self.game.drones.drone_tracking[n] = True
        # check for the switch stop
        self.game.mb_switch_stop.check_remove()
        self.unload()

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
