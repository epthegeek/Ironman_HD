import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random

class IronMonger(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(IronMonger, self).__init__(game=game, priority=17, mode_type=AdvancedMode.Game)
        self.myID = "IronMonger"
        self.monger_lamps = [self.game.lamps['mongerM'],
                             self.game.lamps['mongerO'],
                             self.game.lamps['mongerN'],
                             self.game.lamps['mongerG'],
                             self.game.lamps['mongerE'],
                             self.game.lamps['mongerR']]
        self.orbit_lamps = [self.game.lamps['leftOrbitMonger'],self.game.lamps['centerShotMonger'],self.game.lamps['rightOrbitMonger']]
        self.grunts = ['monger_grunt_1','monger_grunt_2','monger_grunt_3','monger_grunt_4','monger_grunt_5','monger_grunt_6']
        self.grunt_index = 0
        self.delay_names = ['leftSpinner','centerSpinner','rightSpinner','leftOrbit','rightOrbit']
        layer0 = dmd.FrameLayer(frame=self.game.animations['monger_logo_0'].frames[0])
        layer0.set_target_position(367,0)
        layer1 = dmd.FrameLayer(frame=self.game.animations['monger_logo_1'].frames[0])
        layer1.set_target_position(367,0)
        layer2 = dmd.FrameLayer(frame=self.game.animations['monger_logo_2'].frames[0])
        layer2.set_target_position(367,0)
        layer3 = dmd.FrameLayer(frame=self.game.animations['monger_logo_3'].frames[0])
        layer3.set_target_position(367,0)
        layer4 = dmd.FrameLayer(frame=self.game.animations['monger_logo_4'].frames[0])
        layer4.set_target_position(367,0)
        layer5 = dmd.FrameLayer(frame=self.game.animations['monger_logo_5'].frames[0])
        layer5.set_target_position(367,0)
        layer6 = dmd.FrameLayer(frame=self.game.animations['monger_logo_6'].frames[0])
        layer6.set_target_position(367,0)
        layer7 = dmd.FrameLayer(frame=self.game.animations['monger_logo_7'].frames[0])
        layer7.set_target_position(367,0)
        layer8 = dmd.FrameLayer(frame=self.game.animations['monger_logo_8'].frames[0])
        layer8.set_target_position(367,0)
        layer9 = dmd.FrameLayer(frame=self.game.animations['monger_logo_9'].frames[0])
        layer9.set_target_position(367,0)
        layer10 = dmd.FrameLayer(frame=self.game.animations['monger_logo_10'].frames[0])
        layer10.set_target_position(367,0)
        self.logo_layers = [layer0,layer1,layer2,layer3,layer4,layer5,layer6,layer7,layer8,layer9,layer10]
        self.points_layer = dmd.HDTextLayer(1920 / 2, 570, self.game.fonts['bebas200'], "center", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        self.monger_base_value = 100000
        self.spinner_points = [0,0,0]
        self.spinner_names = ['left','right','center']
        self.current_monger_value = 100000
        # which spinner has the live display
        self.last_spinner = 0
        self.cold = True
        self.spinner_anim = self.game.animations['monger_minigun_firing']
        self.spinner_text_layer = dmd.HDTextLayer(1870, 30, self.game.fonts['bebas200'], "right", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        self.spinner_display  = dmd.GroupedLayer(1920,800,[self.spinner_anim, self.spinner_text_layer],opaque=True)
        self.valid = [True,True,True,True,True,True]
        self.status = "OPEN"
        self.letters = 0
        self.toy_letters = 0
        # script sets for the orbit shots
        script0 = ['im_script0a','spinner_tutorial','im_script0b']
        script1 = ['im_script1a','spinner_tutorial','im_script1b']
        script2 = ['im_script2a','spinner_tutorial','im_script2b','im_script2c']
        script3 = ['im_script3a','spinner_tutorial','im_script3b','im_script3c']
        script4 = ['im_script4a','spinner_tutorial','im_script4b','im_script4c']
        script5 = ['spinner_tutorial','im_script5a','im_script5b']
        self.first_scripts = [script0, script1, script2, script3, script4, script5]
        self.first_scripts_index = 0
        script1b = ['im_script7a', 'im_script7b', 'im_script7c', 'im_script7d', 'im_script7e']
        script2b = ['im_script8a', 'im_script8b', 'im_script8c', 'im_script8d', 'im_script8e']
        script3b = ['im_script9a', 'im_script9b', 'im_script9c', 'im_script9d', 'im_script9e','im_script9f','im_script9g']
        self.second_scripts = [script1b,script2b,script3b]
        self.second_scripts_index = 0

    def evt_ball_starting(self):
        self.wipe_delays()

        # clear used to determine wait time on repeat hits to switches
        self.clear = True
        self.letters = self.game.getPlayerState('monger_letters')
        self.battles = self.game.getPlayerState('monger_battles')
        self.script_details = self.game.getPlayerState('monger_script')
        # if this player doesn't have a selected script, set one and reset
        if self.script_details[1] == 9:
            if self.battles == 0:
                options = self.first_scripts
            else:
                options = self.second_scripts
            self.script_details[0] = random.choice(options)
            self.script_details[1] = 0
        ## Status goes "OPEN" then "READY" then "UP" then "MB" then "RUNNING"
        self.status = self.game.getPlayerState('monger_status')
        self.monger_base_value = self.game.getPlayerState('monger_base_value')
        # for locking out spinners based on conditions
        self.valid = [True,True,True,True,True,True]
        self.toy_valid = True
        self.toy_letters = self.game.getPlayerState('toy_letters')
        self.orbit_quiet = False
        # set the last spinner out of scope
        self.last_spinner = 4
        # update the lamps
        self.update_lamps()

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('monger_letters', self.letters)
        self.game.setPlayerState('monger_battles', self.battles)
        self.game.setPlayerState('monger_status', self.status)
        self.game.setPlayerState('toy_letters', self.toy_letters)
        self.game.setPlayerState('monger_script', self.script_details)
        self.game.setPlayerState('monger_base_value', self.monger_base_value)
        # if we end the ball in multiball, re-set status
        if self.status == "MB" or self.status == "RUNNING":
            self.status = "OPEN"
        self.disable_lamps()

    def magnet(self,input):
        if input == "Throw":
            self.game.coils.ironMongerMagnet.pulse()
        if input == "Hold":
            self.game.coils.ironMongerMagnet.patter(on_time=2,off_time=6,original_on_time=10)
        if input == "Release":
            self.game.coils.ironMongerMagnet.disable()


    def sw_leftSpinner_active(self,sw):
        self.spinner_noise()
        if self.status == "UP":
            self.spinner(0)
        else:
            if self.valid[0]:
                self.set_valid_switches(0)
                self.letter_hit()

    def sw_centerSpinner_active(self,sw):
        self.spinner_noise()
        if self.status == "UP":
            self.spinner(1)
        else:
            if self.valid[1]:
                if self.status == "READY":
                    self.raise_monger(150000)
                    self.delay(delay=2, handler=self.raise_quote)
                else:
                    self.set_valid_switches(1)
                    self.letter_hit()

    def sw_rightSpinner_active(self,sw):
        self.spinner_noise()
        if self.status == "UP":
            self.spinner(2)
        else:
            if self.valid[2]:
                self.set_valid_switches(2)
                self.letter_hit()

    def sw_leftOrbit_active(self,sw):
        if self.valid[3]:
            if self.status == "READY":
                self.raise_monger(100000)
                self.delay(delay=2,handler=self.raise_quote)
            else:
                self.set_valid_switches(3)
                self.letter_hit()
        # play the orbit noise
        self.orbit_noise()

    def sw_rightOrbit_active(self,sw):
        if self.valid[4]:
            if self.status == "READY":
                self.raise_monger(100000)
                self.delay(delay=2, handler=self.raise_quote)
            else:
                self.set_valid_switches(4)
                self.letter_hit()
        # play the orbit noise
        self.orbit_noise()

    def sw_mongerOptoLeft_active(self,sw):
        self.monger_opto_hit()

    def sw_mongerOptoRight_active(self,sw):
        self.monger_opto_hit()

    def sw_mongerOptoCenter_active(self,sw):
        self.monger_opto_hit()

    def monger_opto_hit(self):
        if self.toy_valid:
            self.toy_valid = False
            self.delay(delay=0.5,handler=self.revalidate_toy)
            self.hit_toy()

    def letter_hit(self):
        if self.letters < 10:
            # stop any display delays
            self.cancel_delayed("display")
            self.letters += 1
            points = self.letters * 10000
            # do the display
            self.points_layer.set_text(self.game.score_display.format_score(points))
            layer1 = dmd.GroupedLayer(1920,800,[self.logo_layers[self.letters],self.points_layer])
            self.layer = dmd.ScriptedLayer(1920,800,[{'layer': layer1,'seconds': 0.2},{'layer': self.logo_layers[self.letters -1], 'seconds': 0.2}],opaque=True)
            # if complete follow up with ready message
            if self.letters == 10:
                self.delay("display",delay=1.0,handler=self.monger_ready_display)
                self.status = "READY"
            # set a clear delay
            else:
                self.delay("display",delay=1.3,handler=self.clear_layer)
            # score the points
            self.game.score(points)
            # play a delayed quote
            self.delay(delay=2,handler=self.spinner_script_quote)
        # if we're already at 10 letters raise the monger
        self.update_lamps()

    def monger_ready_display(self):
        self.points_layer.set_text("IRON MONGER READY")
        self.layer = dmd.GroupedLayer(1920, 800, [self.logo_layers[self.letters], self.points_layer],opaque=True)
        self.delay("display", delay=1.5, handler=self.clear_layer)
        # play a quote
        self.game.sound.play_voice('monger_complete',action=procgame.sound.PLAY_NOTBUSY)

    def raise_monger(self,points):
        self.cancel_delayed("display")
        self.status = "UP"
        self.monger_base_value = points
        self.reset_monger_value()
        self.game.monger_toy.rise()
        anim = self.game.animations['monger_rise']
        anim.reset()
        anim.add_frame_listener(-1,self.clear_layer)
        self.layer = anim
        # the count it
        self.battles += 1
        # set the next quote script
        self.script_details[0] = random.choice(self.second_scripts)
        self.script_details[1] = 0
        # set the music
        self.game.base.set_music()

    def raise_quote(self):
        self.game.sound.play_voice('monger_raise_quote',action=procgame.sound.PLAY_NOTBUSY)

    def reset_monger_value(self):
        self.current_monger_value = self.monger_base_value

    def spinner(self,spinner):
        # cancel any pending delay
        self.cancel_delayed("display")
        # score the points
        self.game.score(7500)
        # add the points to the temp monger hit value
        self.current_monger_value += 7500
        # if this hit is different than the last one, we're doing a spinner display
        if spinner != self.last_spinner or self.cold:
            self.cold = False
            self.spinner_anim.reset()
            self.spinner_points[spinner] += 7500
            self.update_spinner_score_text(spinner)
            self.layer = self.spinner_display
            # set a delay for clearing
            self.delay("display",delay = 1.5,handler=self.reset_spinner_display,param=spinner)
        # if it is the same spinner as the last one, just update the text
        else:
            self.spinner_points[spinner] += 7500
            self.update_spinner_score_text(spinner)
            # set a delay for clearing
            self.delay("display", delay=1.5, handler=self.reset_spinner_display, param=spinner)

        # set last spinner
        self.last_spinner = spinner

    def reset_spinner_display(self,spinner):
        self.cold = True
        self.spinner_points[spinner] = 0
        self.layer = None

    def update_spinner_score_text(self,spinner):
        text = str(self.game.score_display.format_score(self.spinner_points[spinner]))
        self.spinner_text_layer.set_text(text)

    def hit_toy(self):
        if self.game.monger_toy.status == "UP" or self.game.monger_toy.status == "MOVING":
            # play a sound
            self.game.sound.play('monger_clank')
            # play a grunt too
            self.delay(delay=0.2,handler=self.game.sound.play,param=self.grunts[self.grunt_index])
            self.grunt_index += 1
            if self.grunt_index > 5:
                self.grunt_index = 0
            # score some points?
            points = self.current_monger_value
            self.reset_monger_value()
            self.game.score(points)
            # add a letter
            if self.toy_letters < 6:
                self.toy_letters += 1
                if self.toy_letters == 6:
                    self.start_multiball()
                else:
                    self.game.monger_toy.toy_hit_display(points)
        self.update_lamps()

    def start_multiball(self):
        self.status = "MB"
        self.game.modes.add(self.game.monger_multiball)
        self.game.monger_multiball.start_multiball()

    def update_lamps(self):
        self.disable_lamps()
        if self.status == "OPEN":
            # flash the monger rectangles
            for lamp in self.orbit_lamps:
                lamp.schedule(0x00FF00FF)
            # there are no lamps for letters 1 through 4
            if self.letters <= 4:
                pass
            # if we're over 4 letters, it's time to do some shit
            else:
                local_letters = self.letters - 5
                blinker = 6
                for n in range (0, 6, 1):
                    if n < local_letters:
                        self.monger_lamps[n].enable()
                    elif n == local_letters:
                        self.monger_lamps[n].enable()
                        blinker = n + 1
                    elif n == blinker:
                        self.monger_lamps[n].schedule(0x0F0F0F0F)
                    else:
                        pass
        if self.status == "READY":
            for lamp in self.monger_lamps:
                lamp.schedule(0x0F0F0F0F)
            for lamp in self.orbit_lamps:
                lamp.schedule(0x0F0F0F0F)
        if self.status == "UP":
            if self.toy_letters == 5:
                for lamp in self.monger_lamps:
                    lamp.schedule(0x0F0F0F0F)
            else:
                for n in range(0, 6, 1):
                    if n <= self.toy_letters:
                        self.monger_lamps[n].enable()
                    else:
                        pass

    def disable_lamps(self):
        for lamp in self.monger_lamps:
            lamp.disable()
        for lamp in self.orbit_lamps:
            lamp.disable()

    def set_valid_switches(self,switch):
        # left spinner
        if switch == 0:
            # affects left spinner and left orbit
            self.process_validation([0, 3])
            # immediately validates right spinner
            self.validate(2)
        # center spinner
        elif switch == 1:
            self.process_validation([1])

        # right spinner
        elif switch == 2:
            # affects right spinner and right orbit
            self.process_validation([2, 4])
            # immediately validates left spinner
            self.validate(0)
        # left orbit
        elif switch == 3:
            # affect the left spinner and the right orbit
            self.process_validation([0, 4])
            # forces re-validation of the right spinner in case of a repeat fast loop
            self.validate(2)
        # right orbit
        elif switch == 4:
            # affects the left orbit and the right spinner
            self.process_validation([3, 2])
            # forces re-validation of the left spinner in case of a repeat fast loop
            self.validate(0)

    def process_validation(self,list):
        self.stop_valid_reset(list)
        self.delay(delay=0.1,handler=self.invalidate_switches,param=list)
        self.delay(delay=0.2,handler=self.revalidate,param=list)

    def invalidate_switches(self,list):
        for item in list:
            self.valid[item] = False

    def stop_valid_reset(self,list):
        for item in list:
            self.cancel_delayed(self.delay_names[item])

    def revalidate(self,list):
        for item in list:
            self.delay(name=self.delay_names[item], delay=2, handler=self.validate,param=item)

    def validate(self,spinner):
        self.valid[spinner] = True

    def reset_center(self):
        self.valid[1] = True

    def orbit_noise(self):
        if not self.orbit_quiet:
            self.orbit_quiet = True
            self.game.sound.play('helicopter')
            self.delay(delay=5, handler=self.orbit_noise_reset)

    def spinner_noise(self):
        if self.game.monger_toy.status == "UP" or self.game.monger_multiball.running:
            self.game.sound.play('spinner_monger')
        else:
            self.game.sound.play('spinner_normal')

    def revalidate_toy(self):
        self.toy_valid = True

    def orbit_noise_reset(self):
        self.orbit_quiet = False

    def spinner_script_quote(self):
        print "SPINNER SCRIPT"
        print str(len(self.script_details[0]))
        print str(self.script_details[1] + 1)
        # play the voice clip for this players script at this players index
        # if there are quotes left in the script
        if len(self.script_details[0]) > (self.script_details[1] + 1):
            duration = self.voice_helper([self.script_details[0][self.script_details[1]], procgame.sound.PLAY_NOTBUSY])
            # if the quote played, update the index
            if duration > 0:
                self.script_details[1] += 1

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
