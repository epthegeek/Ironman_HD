import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
import random
from procgame import dmd

class Drones(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Drones, self).__init__(game=game, priority=15, mode_type=AdvancedMode.Game)
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
        self.text = dmd.HDTextLayer(1920 / 2, 620, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(224, 224, 224))
        self.score_text = dmd.HDTextLayer(1920 / 2, 620, self.game.fonts['bebas200'], "center", line_color=(0, 0, 0), line_width=6, interior_color=(64, 64, 224))
        self.text_positions = [300,750,1180,1620]
        self.drone_tracking = [True,True,True,True]

    def evt_ball_starting(self):
        self.wipe_delays()

        self.drone_tracking = self.game.getPlayerState('drone_targets')
        self.drone_total = self.game.getPlayerState('drone_hits')
        self.war_machine_battles = self.game.getPlayerState('war_machine_battles')
        self.drones_for_mb = self.game.getPlayerState('drones_for_mb')
        self.drone_value = self.game.getPlayerState('drone_value')
        self.drone_jp_value = self.game.getPlayerState('drone_jp_value')
        self.update_lamps()

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('drone_targets', self.drone_tracking)
        self.game.setPlayerState('drone_hits',self.drone_total)
        self.game.setPlayerState('war_machine_battles', self.war_machine_battles)
        self.game.setPlayerState('drones_for_mb', self.drones_for_mb)
        self.game.setPlayerState('drone_value', self.drone_value)
        self.game.setPlayerState('drone_jp_value', self.drone_jp_value)
        self.disable_lamps()

    def sw_droneTarget0_active(self,sw):
        self.drone_hit(0)

    def sw_droneTarget1_active(self,sw):
        self.drone_hit(1)

    def sw_droneTarget2_active(self,sw):
        self.drone_hit(2)

    def sw_droneTarget3_active(self,sw):
        self.drone_hit(3)

    def drone_hit(self,target):
        if self.game.wm_multiball.running:
            pass
        else:
            # is the target lit?
            if self.drone_tracking[target] == True:
                self.drone_tracking[target] = False
                # then we've got a hit
                # count the hit
                self.drone_total += 1

                # if we're at 8, light the mode, if we're at 16, complete it
                if self.drone_total == 8:
                    self.game.mark.mode_light(4)
                elif self.drone_total == 16:
                    self.game.mark.mode_completed(4)

                self.drones_for_mb -= 1
                # play the sound effect
                self.game.sound.play('drone_hit')
                # if that was enough, it's time for war machine multiball
                if self.drones_for_mb <= 0:
                    # time to do WM Multiball
                    self.game.warmachine.light_multiball()
                    # Turn all the drones off
                    for n in range (0,4,1):
                        self.drone_tracking[n] = False
                    # bail on the rest of this junk
                    return
                # If not, do the normal display
                else:
                    self.drone_hit_display(target,self.drone_value)
                # score some points
                self.game.score(self.drone_value * 1000)
                self.drone_value += 5
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
                # update the lamps
                self.update_lamps()
            else:
                # otherwise, it's a thunk
                self.drone_thunk(target)

    def add(self,target=5,display=False):
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
        if display:
            self.drone_added_display(drone)

    def drone_added_display(self,drone):
        # layer without the new drone
        layers_off = []
        layers_on = []
        for n in range(0,4,1):
            # if the drone is lit
            if self.drone_tracking[n]:
                # if it matches the one that just got added, its in the on list
                if n == drone:
                    layers_on.append(self.drone_layers[n])
                # otherwise it's in both
                else:
                    layers_on.append(self.drone_layers[n])
                    layers_off.append(self.drone_layers[n])
        self.text.set_text("DRONE ADDED")
        layers_off.append(self.text)
        layers_on.append(self.text)
        off = dmd.GroupedLayer(1920,800,layers_off)
        on = dmd.GroupedLayer(1920,800,layers_on)
        self.layer = dmd.ScriptedLayer(1920,800,[{'layer':off,'seconds':0.2},{'layer':on,'seconds':0.2}], opaque=True)
        self.delay("clear",delay=2,handler=self.clear_layer)
        # play the quote for adding the drone
        self.game.sound.play_voice('drone_added',action=procgame.sound.PLAY_FORCE)

    def drone_thunk(self,target):
        self.game.sound.play('drone_thunk')
        self.game.score(5000)

    def drone_hit_display(self,target,value):
        self.cancel_delayed("clear")
        # play a delayed quote for the drone
        self.delay(delay=self.quote_delay,handler=self.drone_hit_quote,param=target)
        self.set_explosion_position(target)
        self.score_text.set_text(str(value) + "K",blink_frames = 8)
        self.score_text.set_target_position(self.text_positions[target],170)
        count = self.drones_for_mb
        if count == 1:
            word = "DRONE"
        else:
            word = "DRONES"
        self.text.set_text(str(count) + " MORE " + word + " REMAINING")
        list = []
        list.append(self.score_text)
        for n in range (0,4,1):
            if self.drone_tracking[n]:
                list.append(self.drone_layers[n])
        list.append(self.explosion_layer)
        list.append(self.text)
        self.layer = dmd.GroupedLayer(1920,800,list,opaque=True)

        self.delay("clear",delay=3,handler=self.clear_layer)

    def drone_hit_quote(self,target):
        if self.game.base.tut_status[1]:
            clip = 'drone_tutorial'
        else:
            clip = self.drone_quotes[target]
        duration = self.voice_helper([clip,procgame.sound.PLAY_NOTBUSY])
        # if the tutorial clip played, set the flag
        if duration > 0 and self.game.base.tut_status[1]:
            self.game.base.tut_status[1] = False

    def update_lamps(self):
        # war machine multiball controls the drone target lamps - do nothing if that is running
        if self.game.wm_multiball.running:
            pass
        else:
            # if WM MB is not running, disable first
            self.disable_lamps()
            # if either of the other 2 multiballs are running - stop there
            if self.game.whiplash_multiball.running or self.game.monger_multiball.running:
                pass
            else:
                # otherwise, activate as normal
                for n in range (0,4,1):
                    if self.drone_tracking[n] == True:
                        self.drone_lamps[n].schedule(0x0F0F0F0F)

    def disable_lamps(self):
        for lamp in self.drone_lamps:
            lamp.disable()

    def set_explosion_position(self,target):
        self.explosion_layer.reset()
        self.explosion_layer.composite_op = 'blacksrc'
        self.explosion_layer.set_target_position(self.explosion_positions[target],84)

    def reset_value(self):
        self.drone_value = 10

    def raise_jackpot(self):
        self.drone_jp_value += 25000

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
