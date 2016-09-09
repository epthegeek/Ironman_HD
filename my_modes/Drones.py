import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
import random
from procgame import dmd

class Drones(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Drones, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "Drones"
        self.drone_lamps = [self.game.lamps['droneTarget0'],
                            self.game.lamps['droneTarget1'],
                            self.game.lamps['droneTarget2'],
                            self.game.lamps['droneTarget3']]
        self.drone_0_layer = self.game.animations['drone_0_image']
        self.drone_0_layer.set_target_position(113,0)
        self.drone_1_layer = self.game.animations['drone_1_image']
        self.drone_1_layer.set_target_position(560,0)
        self.drone_2_layer = self.game.animations['drone_2_image']
        self.drone_2_layer.set_target_position(1007,0)
        self.drone_3_layer = self.game.animations['drone_3_image']
        self.drone_3_layer.set_target_position(1426,0)
        self.explosion_layer = self.game.animations['explosion']
        self.explosion_positions = [53,500,933,1386]
        self.drone_layers = [self.drone_0_layer,self.drone_1_layer,self.drone_2_layer,self.drone_3_layer]
        self.drone_quotes = ['ga_drone','aa_drone','ta_drone','sa_drone']
        self.quote_delay = self.game.sound.sounds['drone_hit']['sound_list'][0].get_length()

    def evt_ball_starting(self):
        self.drone_tracking = self.game.getPlayerState('drone_targets')
        self.drone_total = self.game.getPlayerState('drone_hits')
        self.war_machine_battles = self.game.getPlayerState('war_machine_battles')
        self.drones_for_mb = self.game.getPlayerState('drones_for_mb')

    def evt_ball_ending(self):
        self.game.setPlayerState('drone_targets', self.drone_tracking)
        self.game.setPlayerState('drone_hits',self.drone_total)
        self.game.setPlayerState('war_machine_battles', self.war_machine_battles)
        self.game.setPlayerState('drones_for_mb', self.drones_for_mb)

    def sw_droneTarget0_active(self,sw):
        self.drone_hit(0)

    def sw_droneTarget1_active(self,sw):
        self.drone_hit(1)

    def sw_droneTarget2_active(self,sw):
        self.drone_hit(2)

    def sw_droneTarget3_active(self,sw):
        self.drone_hit(3)

    def drone_hit(self,target):
        # is the target lit?
        if self.drone_tracking[target] == True:
            self.drone_tracking[target] = False
            # then we've got a hit
            # count the hit
            self.drone_total += 1
            self.drones_for_mb -= 1
            # play the sound effect
            self.game.sound.play('drone_hit')
            # if that was enough, it's time for war machine multiball
            if self.drones_for_mb <= 0:
                self.warmachine.light_multiball()
            # If not, do the normal display
            else:
                self.drone_hit_display(target)
            # score some points
            self.game.score(10000)
            # Then balance the drones if needed
            # if WM multiball hasn't run yet, always a minimum of three
            if self.war_machine_battles <= 0:
                # if less than three are lit
                if sum(self.drone_tracking) < 3:
                    #step through them
                    for x in range(0,4,1):
                        # for the target that just went out, skip that one
                        if x == target:
                            pass
                        # for the others, turn on the False one to get back to three
                        else:
                            if self.drone_tracking[x] == False:
                                self.drone_tracking[x] = True
            # for any time after one multiball, the minimum is 2
            else:
                # if the sum is only one
                if sum(self.drone_tracking) <= 1:
                    # add another drone
                    self.add(target)
        else:
            # otherwise, it's a thunk
            self.drone_thunk(target)

    def add(self,target):
        candidates = []
        # step through the values
        for x in range(0, 4, 1):
            # if the target that just got hit comes up pass
            if x == target:
                pass
            # For the others, store the false values
            else:
                if self.drone_tracking[x] == False:
                    candidates.append(x)
        # now we know which ones are out - randomly turn one back on
        drone = random.choice(candidates)
        self.drone_tracking[drone] = True
        self.update_lamps()

    def drone_thunk(self,target):
        self.game.displayText("THUNK")
        self.game.score(5000)

    def drone_hit_display(self,target):
        self.cancel_delayed("clear")
        # play a delayed quote for the drone
        self.delay(delay=self.quote_delay,handler=lambda: self.game.sound.play_voice(self.drone_quotes[target]))
        self.set_explosion_position(target)
        list = []
        for n in range (0,4,1):
            if self.drone_tracking[n]:
                list.append(self.drone_layers[n])
        list.append(self.explosion_layer)
        self.layer = dmd.GroupedLayer(1920,800,list,opaque=True)

        #self.delay("clear",delay=2,handler=self.clear_layer)

    def update_lamps(self):
        for lamp in self.drone_lamps:
            lamp.disable()
        for n in range (0,4,1):
            if self.drone_tracking[n] == True:
                self.drone_lamps[n].enable()

    def set_explosion_position(self,target):
        self.explosion_layer.reset()
        self.explosion_layer.composite_op = 'blacksrc'
        self.explosion_layer.add_frame_listener(-1,self.clear_layer)
        self.explosion_layer.set_target_position(self.explosion_positions[target],84)

