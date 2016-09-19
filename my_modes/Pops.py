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
        self.backdrop = self.game.animations['pops_back']
        self.left_pop_image = self.game.animations['pop_left']
        self.right_pop_image = self.game.animations['pop_right']
        self.right_pop_image.set_target_position(1325,0)
        self.bottom_pop_image = self.game.animations['pop_bottom']
        self.bottom_pop_image.set_target_position(330,365)
        self.title = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        self.title.set_text("SUPER POPS")
        self.p_value_text = dmd.HDTextLayer(1920/2,120,self.game.fonts['bebas200'],"center",line_color=(96,96,86),line_width=3,interior_color=(0,0,255))
        self.info_line = dmd.HDTextLayer(1920/2,350,self.game.fonts['default'],"center",line_color=(96,96,86),line_width=3,interior_color=(224,224,224))
        self.pop_layers = [self.left_pop_image, self.bottom_pop_image, self.right_pop_image]
        layer_list = [self.backdrop,self.left_pop_image,self.right_pop_image,self.bottom_pop_image,self.title,self.p_value_text,self.info_line]
        self.main_display = dmd.GroupedLayer(1920,800,layer_list,opaque= True)

    def evt_ball_starting(self):
        # set all the pops as unlit
        self.pop_state = [False,False,False]
        self.hits = 0
        # need to check the logic on this - once they're all lit, how many hits?
        self.level = self.game.getPlayerState('pops_level')
        self.pop_hits_for_level = ((self.level * 5) + 25)
        self.jackpot = self.game.getPlayerState('pops_jackpot')
        self.value = self.game.getPlayerState('pops_value')
        self.super = False
        self.super_value = 0
        self.title.enabled = False
        # reset the pop images
        for layer in self.pop_layers:
            layer.enabled = False

    def evt_ball_ending(self):
        self.game.setPlayerState('pops_level', self.level)
        self.game.setPlayerState('pops_jackpot', self.jackpot)
        self.game.setPlayerState('pops_value', self.value)

    def sw_leftJetBumper_active(self,sw):
        self.pop_hit(0)
    def sw_bottomJetBumper_active(self,sw):
        self.pop_hit(1)
    def sw_rightJetBumper_active(self,sw):
        self.pop_hit(2)

    # orbits enable the pops
    def sw_leftOrbit_active(self,sw):
        self.light_pop(0)
    def sw_centerSpinner_active(self,sw):
        self.light_pop(1)
    def sw_rightOrbit_active(self,sw):
        self.light_pop(2)

    def pop_hit(self,number):
        # are they all lit?
        if False not in self.pop_state:
            self.super_pop_hit(number)
        else:
            # flash the light
            self.pop_lamps[number].pulse()
            # check if pop is lit
            lit = self.pop_state[number]
            if lit:
                points = 25000
                # sound = some sound
            else:
                points = 5000
                # sound = some other sound
            self.game.score(points)
            # play the sound
            # do the display
            self.do_main_display(points)
            # add the points to the jackpot
            self.jackpot += points
            # add the hit
            self.hits += 1

    def light_pop(self,number):
        if self.pop_state[number] == False:
            self.pop_state[number] = True
            # turn on that layer
            self.pop_layers[number].enabled = True
            # if that's the last one, turn on super
            if False not in self.pop_state:
                self.super = True
                self.super_value = (self.hits * 1000)
                self.title.enabled = True
            self.update_lamps()

    def super_pop_hit(self,number):
        self.pop_hits_for_level -= 1
        # if we're done, there's stuff to do.
        if self.pop_hits_for_level <= 0:
            # score points
            self.game.score(self.jackpot)
            self.complete_display()
            # turn off the super layer
            self.title.enabled = False
        else:
            self.game.score(self.super_value)
            self.do_main_display(self.super_value)

    def do_main_display(self,points):
        self.cancel_delayed("clear")
        # display during super
        if self.super:
            self.p_value_text.set_text(self.game.score_display.format_score(self.super_value))
            if self.pop_hits_for_level == 1:
                string = "1 HIT REMAINING"
            else:
                string = str(self.pop_hits_for_level) + " HITS REMAINING"
            self.info_line.set_text(string)
        else:
            self.p_value_text.set_text(self.game.score_display.format_score(points))
            self.info_line.set_text("JACKPOT VALUE: " + self.game.score_display.format_score(self.jackpot))
        self.layer = self.main_display
        # set the clear delay
        self.delay("clear",delay=2,handler=self.clear_layer)

    def complete_display(self):
        layers = []
        layers.append(self.backdrop)
        layers.append(self.left_pop_image)
        layers.append(self.right_pop_image)
        layers.append(self.bottom_pop_image)
        line_1 = dmd.HDTextLayer(1920/2,150,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        line_1.set_text("SUPER POPS")
        line_2 = dmd.HDTextLayer(1920/2,300,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        line_2.set_text("COMPLETED")
        layers.append(line_1)
        layers.append(line_2)
        self.layer = dmd.GroupedLayer(1920,1080,layers,opaque=True)
        # reset all the things
        self.delay(delay=2,handler=self.reset_pops)
        self.delay("clear",delay=2,handler=self.clear_layer)

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
        # TODO: does the jackpot value reset?
        # TODO: or the super value?
        self.update_lamps()

    def update_lamps(self):
        for n in range (0,3,1):
            if self.pop_state[n] == 1:
                self.pop_lamps[n].enable()
            else:
                self.pop_lamps[n].disable()