import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class IronMonger(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(IronMonger, self).__init__(game=game, priority=17, mode_type=AdvancedMode.Game)
        self.myID = "IronMonger"
        self.monger_lamps = ["Placeholder",
                             self.game.lamps['mongerM'],
                             self.game.lamps['mongerO'],
                             self.game.lamps['mongerN'],
                             self.game.lamps['mongerG'],
                             self.game.lamps['mongerE'],
                             self.game.lamps['mongerR']]
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
        self.spinner_text_layer = dmd.HDTextLayer(1920 / 2, 570, self.game.fonts['bebas200'], "center", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        self.spinner_display  = dmd.GroupedLayer(1920,800,[self.spinner_anim, self.spinner_text_layer],opaque=True)

    def evt_ball_starting(self):
        # clear used to determine wait time on repeat hits to switches
        self.clear = True
        self.letters = self.game.getPlayerState('monger_letters')
        self.battles = self.game.getPlayerState('monger_battles')
        ## Status goes "OPEN" then "READY" then "UP" then "MB"
        self.status = self.game.getPlayerState('monger_status')
        # for locking out spinners based on conditions
        self.valid = [True,True,True,True,True]
        self.toy_valid = True
        self.toy_letters = self.game.getPlayerState('toy_letters')
        self.orbit_quiet = False
        # set the last spinner out of scope
        self.last_spinner = 4

    def evt_ball_ending(self):
        self.game.setPlayerState('monger_letters', self.letters)
        self.game.setPlayerState('monger_battles', self.battles)
        self.game.setPlayerState('monger_status', self.status)
        self.game.setPlayerState('toy_letters', self.toy_letters)

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
            else:
                self.set_valid_switches(3)
                self.letter_hit()
        # play the orbit noise
        self.orbit_noise()

    def sw_rightOrbit_active(self,sw):
        if self.valid[4]:
            if self.status == "READY":
                self.raise_monger(100000)
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
        # stop any display delays
        self.cancel_delayed("display")
        if self.letters < 10:
            self.letters += 1
            points = self.letters * 10000
            # do the display
            self.points_layer.set_text(self.game.score_display.format_score(points))
            layer1 = dmd.GroupedLayer(1920,800,[self.logo_layers[self.letters],self.points_layer])
            self.layer = dmd.ScriptedLayer(1920,800,[{'layer': layer1,'seconds': 0.2},{'layer': self.logo_layers[self.letters -1], 'seconds': 0.2}],opaque=True)
            # if complete follow up with ready message
            if self.letters == 10:
                self.delay("display",delay=1.4,handler=self.monger_ready_display)
                self.status = "READY"
            # set a clear delay
            else:
                self.delay("display",delay=1.8,handler=self.clear_layer)
            # score the points
            self.game.score(points)
        # if we're already at 10 letters raise the monger
        else:
            self.layer = None
            self.game.monger_toy.rise()
            self.game.monger_toy.monger_rise_video()

    def monger_ready_display(self):
        self.points_layer.set_text("IRON MONGER READY")
        self.layer = dmd.GroupedLayer(1920, 800, [self.logo_layers[self.letters], self.points_layer],opaque=True)
        self.delay("display", delay=1.5, handler=self.clear_layer)

    def raise_monger(self,points):
        self.status = "UP"
        self.monger_base_value = points
        self.reset_monger_value()
        self.game.monger_toy.rise()
        anim = self.game.animations['monger_rise']
        anim.reset()
        anim.add_frame_listener(-1,self.clear_layer)
        self.layer = anim

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
            self.delay("display",delay = 2,handler=self.reset_spinner_display,param=spinner)
        # if it is the same spinner as the last one, just update the text
        else:
            self.spinner_points[spinner] += 7500
            self.update_spinner_score_text(spinner)
            # set a delay for clearing
            self.delay("display", delay=2, handler=self.reset_spinner_display, param=spinner)

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
        print "TRYING TO HIT TOY - STATUS " + str(self.game.monger_toy.status)
        if self.game.monger_toy.status == "UP" or self.game.monger_toy.status == "MOVING":
            # play a sound
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

    def start_multiball(self):
        self.game.modes.add(self.game.monger_multiball)
        self.game.monger_multiball.start_multiball()

    def update_lamps(self):
        for lamp in self.monger_lamps:
            lamp.disable()
        if self.status == "OPEN":
            if self.letters < 4:
                pass
            else:
                blinker = 12
                for n in range (1, 12, 1):
                    if n < 5:
                        pass
                    if n < self.letters and n > 4:
                        self.monger_lamps[n].enable()
                    if n == self.letters:
                        self.monger_lamps[n].enable()
                        blinker = n + 1
                    if n == blinker:
                        self.monger_lamps[n].schedule(0x00FF00FF)
                    else:
                        pass
        if self.status == "UP":
            for n in range(1, 8, 1):
                if n <= self.toy_letters:
                    self.monger_lamps[n].enable()
                else:
                    pass

    def set_valid_switches(self,switch):
        print "SET VALID SWITCHES"
        # left spinner
        if switch == 0:
            # affects left spinner and left orbit
            self.process_validation([0, 3])
            # immediately validates right spinner
            self.validate(2)
        # center spinner
        elif switch == 1:
            print "FOUND POWER ONE"
            # affects only itself
            self.cancel_delayed(self.delay_names[1])
            self.valid[1] = False
            self.delay(name=self.delay_names[1], delay=1, handler=self.validate, param=1)
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
        self.invalidate_switches(list)
        self.revalidate(list)

    def invalidate_switches(self,list):
        for item in list:
            print "set invalid on " + str(item)
            self.valid[item] = False

    def stop_valid_reset(self,list):
        for item in list:
            print "CANCEL DELAY NAMED " + self.delay_names[item]
            self.cancel_delayed(self.delay_names[item])


    def revalidate(self,list):
        for item in list:
            print "SETTING REVALIDATE DELAY ON " + str(item)
            self.delay(name=self.delay_names[item], delay=1, handler=self.validate,param=item)

    def validate(self,spinner):
        print "MAKING TRUE NUMBER " + str(spinner)
        self.valid[spinner] = True

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
