import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
import random

class Drones(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Drones, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "Drones"
        self.drone_hit_movies = ['drone_hit_1','drone_hit_2','drone_hit_3','drone_hit_4','drone_hit_5']
        self.drone_movie_index = 0
        self.drone_lamps = [self.game.lamps['droneTarget0'],
                            self.game.lamps['droneTarget1'],
                            self.game.lamps['droneTarget2'],
                            self.game.lamps['droneTarget3']]

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
                    self.add()
        else:
            # otherwise, it's a thunk
            self.drone_thunk(target)

    def add(self):
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
        self.game.animations[self.drone_hit_movies[self.drone_movie_index]].reset()
        self.layer = self.game.animations[self.drone_hit_movies[self.drone_movie_index]]
        self.drone_movie_index += 1
        if self.drone_movie_index > 4:
            self.drone_movie_index = 0

        self.delay("clear",delay=2,handler=self.clear_layer)

    def update_lamps(self):
        for lamp in self.drone_lamps:
            lamp.disable()
        for n in range (0,4,1):
            if self.drone_tracking[n] == True:
                self.drone_lamps[n].enable()

