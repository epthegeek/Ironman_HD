import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

class Pops(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Pops, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "Pops"
        self.pop_lamps = [self.game.lamps['leftJetBumper'],self.game.lamps['bottomJetBumper'],self.game.lamps['rightJetBumper']]
        self.orbit_lamps = [self.game.lamps['leftOrbitWeaponAdvance'],
                            self.game.lamps['centerShotWeaponAdvance'],
                            self.game.lamps['rightOrbitWeaponAdvance']]
        self.backdrop = self.game.animations['pops_back']
        self.left_pop_image = self.game.animations['pop_left']
        self.right_pop_image = self.game.animations['pop_right']
        self.right_pop_image.set_target_position(1325,0)
        self.bottom_pop_image = self.game.animations['pop_bottom']
        self.bottom_pop_image.set_target_position(330,365)
        self.top_line = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        self.super_line = dmd.HDTextLayer(1920/2,120,self.game.fonts['bebas200'],"center",line_color=(96,96,86),line_width=3,interior_color=(0,0,255))
        self.super_line.set_text("SUPER POPS")
        self.p_1_points = dmd.HDTextLayer(120,480,self.game.fonts['bebas80'],"center",line_color=(0,0,0),line_width=3,interior_color=(128,128,255))
        self.p_2_points = dmd.HDTextLayer(1780,480,self.game.fonts['bebas80'],"center",line_color=(0,0,0),line_width=3,interior_color=(128,128,255))
        self.p_3_points = dmd.HDTextLayer(1920/2,310,self.game.fonts['bebas80'],"center",line_color=(0,0,0),line_width=3,interior_color=(128,128,255))
        self.pop_layers = [self.left_pop_image, self.bottom_pop_image, self.right_pop_image]
        self.pop_text = [self.p_1_points,self.p_2_points,self.p_3_points]
        # pop names used for delays
        self.pop_names = ['left','bottom','right']
        # pop sound names based on level
        self.pop_sounds = ['pops_0','pops_1','pops_1']
        # set the values for the various levels
        self.pop_values = [5000,7500,10000]
        layer_list = [self.backdrop,
                      self.left_pop_image,
                      self.right_pop_image,
                      self.bottom_pop_image,
                      self.top_line,
                      self.super_line,
                      self.p_1_points,
                      self.p_2_points,
                      self.p_3_points]
        self.main_display = dmd.GroupedLayer(1920,800,layer_list,opaque= True)
        # default pop state
        self.pop_state = [False,False,False]
        # TODO: maybe do the same for sounds? -- are sounds during super specific?
        self.super_boom = True

    def evt_ball_starting(self):
        # set all the pops as unlit
        self.pop_state = [False,False,False]
        # pops have 3 levels - 5k, 7.5k and 10k
        self.pop_level = [0,0,0]
        self.hits = 0
        self.level = self.game.getPlayerState('pops_level')
        # base hits for pops jackpot is 25 + 5each time
        self.pop_hits_for_level = ((self.level * 5) + 25)
        # TODO: Check if the jackpot carries over ball to ball
        self.jackpot = self.game.getPlayerState('pops_jackpot')
        self.super = False
        # TODO: Check if super value carries over from ball to ball if not started
        self.super_value = self.game.getPlayerState('pops_super_value')
        self.super_line.enabled = False
        # reset the pop images
        for layer in self.pop_layers:
            layer.enabled = False
        # the flag for halting the increase in super pops points
        self.super_lock = False
        self.super_boom = True
        self.update_lamps()


    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('pops_level', self.level)
        self.game.setPlayerState('pops_jackpot', self.jackpot)
        self.game.setPlayerState('pops_super_value',self.super_value)

    def sw_leftJetBumper_active(self,sw):
        self.pop_hit(0)
    def sw_bottomJetBumper_active(self,sw):
        self.pop_hit(1)
    def sw_rightJetBumper_active(self,sw):
        self.pop_hit(2)

    # orbits and center spinner enable the pops
    def sw_leftOrbit_active(self,sw):
        self.light_pop(0)

    def sw_centerSpinner_active(self,sw):
        self.increase_jackpot_value(1)
        self.light_pop(1)

    def sw_rightOrbit_active(self,sw):
        self.light_pop(2)

   # left and right spinner increase the value of the super
    def sw_leftSpinner(self,sw):
        self.increase_jackpot_value(0)

    def sw_rightSpinner(self,sw):
        self.increase_jackpot_value(2)

    def pop_hit(self,number):
        # are they all lit?
        if False not in self.pop_state:
            self.super_pop_hit(number)
        else:
            # flash the light
            self.game.coils['popsFlasher'].pulse()
            # score points based on level
            points = self.pop_values[self.pop_level[number]]
            self.game.score(points)
            # play the sound
            # do the display
            # show the pop hit points
            self.pop_points_display(number)
            self.do_main_display(points)
            # add the points to the jackpot
            self.jackpot += points
            # add the hit
            self.hits += 1
        # play a sound - pop sounds play WITH the super explosion
        self.game.sound.play(self.pop_sounds[self.pop_level[number]])

    def light_pop(self,number):
        if self.pop_state[number] == False:
            self.pop_state[number] = True
            # turn on that layer
            self.pop_layers[number].enabled = True
            # increase the pop level - max is 2
            if self.pop_level < 2:
                self.pop_level[number] += 1
            # if that's the last one, turn on super
            if False not in self.pop_state:
                self.super = True
                self.super_line.enabled = True
            self.update_lamps()

    def super_pop_hit(self,number):
        # lock the pop value increase with the first super pop hit
        if not self.super_lock:
            self.super_lock = True
        self.pop_hits_for_level -= 1
        # if we're done, there's stuff to do.
        if self.pop_hits_for_level <= 0:
            # score points
            self.game.score(self.super_value)
            self.game.score(self.jackpot)
            self.complete_display()
            # turn off the super layer
            self.super_line.enabled = False
        else:
            self.game.score(self.super_value)
            # show the pop hit points
            self.pop_points_display(number)
            self.do_main_display(self.super_value)
        # if it's ok to play the super explosion, do that
        if self.super_boom:
            self.super_boom = False
            self.game.sound.play('pop_super')
            # set a delay for the next allowed super boom
            self.delay(delay=4.5,handler=self.reset_super_boom)

    def reset_super_boom(self):
        self.super_boom = True

    def pop_points_display(self,number):
        self.cancel_delayed(self.pop_names[number])
        if self.super_lock:
            points = self.super_value
        else:
            points = self.pop_values[self.pop_level[number]]
        self.pop_text[number].set_text(self.game.score_display.format_score(points))
        # set the clear
        self.delay(self.pop_names[number],delay=0.5,handler=self.clear_pop_text,param=number)

    def clear_pop_text(self,number):
        self.pop_text[number].set_text("")

    def do_main_display(self,points):
        self.cancel_delayed("clear")
        # display during super
        if self.super:
            if self.pop_hits_for_level == 1:
                string = "1 HIT REMAINING"
            else:
                string = str(self.pop_hits_for_level) + " HITS REMAINING"
            self.top_line.set_text(string)
            self.super_line.set_text("SUPER POPS")
        else:
            self.top_line.set_text("JACKPOT VALUE: " + self.game.score_display.format_score(self.jackpot))
            # set the super pops layer to the player score
            p = self.game.current_player()
            self.super_line.set_text(self.game.score_display.format_score(p.score))
        self.layer = self.main_display
        # set the clear delay
        self.delay("clear",delay=2,handler=self.clear_layer)

    def complete_display(self):
        layers = []
        layers.append(self.backdrop)
        layers.append(self.left_pop_image)
        layers.append(self.right_pop_image)
        layers.append(self.bottom_pop_image)
        line_1 = dmd.HDTextLayer(1920/2,20,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=3,interior_color=(0,224,0))
        line_1.set_text("SUPER POPS")
        line_2 = dmd.HDTextLayer(1920/2,170,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=3,interior_color=(0,224,0))
        line_2.set_text("COMPLETED")
        line_3 = dmd.HDTextLayer(1920/2,360,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,0))
        line_3.set_text("JACKPOT = " + self.game.score_display.format_score(self.jackpot),blink_frames=8)
        layers.append(line_1)
        layers.append(line_2)
        layers.append(line_3)
        self.layer = dmd.GroupedLayer(1920,1080,layers,opaque=True)
        # reset all the things
        self.delay(delay=3,handler=self.reset_pops)
        self.delay("clear",delay=3,handler=self.clear_layer)

    def reset_pops(self):
        # turn off the super flag
        self.super = False
        # turn off the lit layers
        for layer in self.pop_layers:
            layer.enabled = False
        # reset the pop states
        for n in range (0,3,1):
            self.pop_state[n] = False
        # count the level
        self.level += 1
        # set the hits for the next level
        self.pop_hits_for_level = ((self.level * 5) + 25)
        # Jackpot value resets + 100k base
        self.jackpot = 500000 + (100000 * self.level)
        # The super value resets to the base 20k
        self.super_value = 20000
        self.update_lamps()
        self.super_lock = False

    def increase_jackpot_value(self,pop):
        self.jackpot += self.pop_values[self.pop_level[pop]]

    def update_lamps(self):
        for n in range (0,3,1):
            if self.pop_state[n] == 1:
                self.pop_lamps[n].enable()
                self.orbit_lamps[n].disable()
            else:
                self.pop_lamps[n].disable()
                self.orbit_lamps[n].enable()

    def disable_lamps(self):
        for n in range (0,3,1):
            self.pop_lamps[n].disable()
            self.orbit_lamps[n].disable()