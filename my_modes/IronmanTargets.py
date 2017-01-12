import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd
import random

class IronmanTargets(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(IronmanTargets, self).__init__(game=game, priority=15, mode_type=AdvancedMode.Game)
        self.myID = "IronmanTargets"
        self.rampDoubled = "NONE"
        self.left_targets = [0,1,2,3]
        self.right_targets = [0,1,2]
        self.scoring_mode_running = False
        self.left_lamps = [self.game.lamps['leftTargetsI'],
                           self.game.lamps['leftTargetsR'],
                           self.game.lamps['leftTargetsO'],
                           self.game.lamps['leftTargetsN']]
        self.right_lamps = [self.game.lamps['rightTargetsM'],
                            self.game.lamps['rightTargetsA'],
                            self.game.lamps['rightTargetsN']]
        self.hit_movies = [self.game.animations['hit_1_movie'],
                           self.game.animations['hit_2_movie'],
                           self.game.animations['hit_3_movie'],
                           self.game.animations['hit_4_movie'],
                           self.game.animations['hit_5_movie'],
                           self.game.animations['hit_6_movie'],
                           self.game.animations['hit_7_movie'],
                           self.game.animations['hit_8_movie'],
                           self.game.animations['hit_9_movie'],
                           self.game.animations['hit_10_movie']]
        self.hit_index = 0
        self.top = dmd.HDTextLayer(15,15,self.game.fonts['bebas80'],"left",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        self.i_layer = dmd.FrameLayer(frame=self.game.animations['target_i_image'].frames[0])
        self.i_layer.set_target_position(1301,625)
        self.i_layer_d = dmd.FrameLayer(frame=self.game.animations['target_i_d'].frames[0])
        self.i_layer_d.set_target_position(1301,625)
        self.r_layer = dmd.FrameLayer(frame=self.game.animations['target_r_image'].frames[0])
        self.r_layer.set_target_position(1349,625)
        self.r_layer_d = dmd.FrameLayer(frame=self.game.animations['target_r_d'].frames[0])
        self.r_layer_d.set_target_position(1349,625)
        self.o_layer = dmd.FrameLayer(frame=self.game.animations['target_o_image'].frames[0])
        self.o_layer.set_target_position(1437,625)
        self.o_layer_d = dmd.FrameLayer(frame=self.game.animations['target_o_d'].frames[0])
        self.o_layer_d.set_target_position(1437,625)
        self.n1_layer = dmd.FrameLayer(frame=self.game.animations['target_n1_image'].frames[0])
        self.n1_layer.set_target_position(1521,625)
        self.n1_layer_d = dmd.FrameLayer(frame=self.game.animations['target_n1_d'].frames[0])
        self.n1_layer_d.set_target_position(1521,625)
        self.m_layer = dmd.FrameLayer(frame=self.game.animations['target_m_image'].frames[0])
        self.m_layer.set_target_position(1621,625)
        self.m_layer_d = dmd.FrameLayer(frame=self.game.animations['target_m_d'].frames[0])
        self.m_layer_d.set_target_position(1621,625)
        self.a_layer = dmd.FrameLayer(frame=self.game.animations['target_a_image'].frames[0])
        self.a_layer.set_target_position(1733,625)
        self.a_layer_d = dmd.FrameLayer(frame=self.game.animations['target_a_d'].frames[0])
        self.a_layer_d.set_target_position(1733,625)
        self.n2_layer = dmd.FrameLayer(frame=self.game.animations['target_n2_image'].frames[0])
        self.n2_layer.set_target_position(1817,625)
        self.n2_layer_d = dmd.FrameLayer(frame=self.game.animations['target_n2_d'].frames[0])
        self.n2_layer_d.set_target_position(1817,625)
        self.left_layers = [self.i_layer,self.r_layer,self.o_layer,self.n1_layer]
        self.right_layers = [self.m_layer,self.a_layer,self.n2_layer]
        self.mode_titles = ["FAST SCORING", "DOUBLE SCORING", "IRONMAN SCORING"]
        self.left_tracking = [False,False,False,False]
        self.right_tracking = [False,False,False]


    # read the current player information
    def evt_ball_starting(self):
        self.wipe_delays()
        # reshuffle the hit movies
        random.shuffle(self.hit_movies)

        # TODO: check if targets hit stay ball to ball
        self.left_tracking = self.game.getPlayerState('im_left_targets')
        self.right_tracking = self.game.getPlayerState('im_right_targets')
        self.completions = self.game.getPlayerState('im_targets_completions')
        self.mode_index = self.game.getPlayerState('im_mode_index')
        self.last_value = self.game.getPlayerState('im_last_value')
        self.scoring_mode_running = False
        self.update_lamps()

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('im_left_targets',self.left_tracking)
        self.game.setPlayerState('im_right_targets',self.right_tracking)
        self.game.setPlayerState('im_targets_completions',self.completions)
        self.game.setPlayerState('im_mode_index',self.mode_index)
        self.game.setPlayerState('im_last_value',self.last_value)
        self.scoring_mode_running = False
        self.disable_lamps()

    def sw_leftTargetI_active(self,sw):
        self.target_hit(0)

    def sw_leftTargetR_active(self,sw):
        self.target_hit(1)

    def sw_leftTargetO_active(self,sw):
        self.target_hit(2)

    def sw_leftTargetN_active(self,sw):
        self.target_hit(3)

    def sw_rightTargetM_active(self,sw):
        self.target_hit(4)

    def sw_rightTargetA_active(self,sw):
        self.target_hit(5)

    def sw_rightTargetN_active(self,sw):
        self.target_hit(6)

    # target_hit checks to see if mode should start - if not, passes on to activate
    def target_hit(self,target):
        # flash the IM flashers
        self.flasher_pulse()
        if self.scoring_mode_running:
            if self.game.fast_scoring.running:
                self.game.fast_scoring.increase_value()
        else:
            # if scoring mode is ready, then do that
            if False not in self.left_tracking and False not in self.right_tracking:
                self.scoring_mode_running = True
                self.start_target_mode()
            # if the targets are not ready, then we're processing it
            else:
                if target in self.left_targets:
                    self.target_activate(target,self.left_targets,self.left_tracking,"L")
                else:
                    # this is a right target
                    target -= 4
                    self.target_activate(target,self.right_targets,self.right_tracking,"R")

    # target_activate treats as either a side hit (first set) or  single target hit
    def target_activate(self,target, target_set,tracker,side):

        # if we have no completions so far, hits count differently
        if self.completions == 0:
            # process as a side hit
            if False not in tracker:
                # if this whole side is done, it's a thunk
                self.target_thunk()
            # If this side is not done, turn on the first available
            else:
                # for now play a generic sound
                self.game.sound.play('im_target_hit')

                for n in target_set:
                    # if we find an off target, activate it
                    if tracker[n] == False:
                        tracker[n] = True
                        # Check if we're done
                        data = self.check_complete()
                        #do the display - sends activated target
                        # if this is the first target of a set, play the tutorial quote
                        if self.game.base.tut_status[0]:
                            self.delay(delay=0.7,handler=self.tutorial_quote)
                        # if completed - the delays are 4 seconds
                        self.target_display_movie(n,side,data[0],data[2])
                        self.update_lamps()
                        # score points
                        self.game.score(data[1])
                        break
        else:
            # process as a unique target
            # if the target is off, turn it on
            if tracker[target] == False:
                # for now play a generic sound
                self.game.sound.play('im_target_hit')
                tracker[target] = True
                # Check if we're done
                data = self.check_complete()
                self.target_display_movie(target,side,data[0],data[2])
                # score points
                self.game.score(data[1])
            # if the target was on already, it's a thunk
            else:
                self.target_thunk()

    def check_complete(self):
        # Check if we're done
        if False not in self.left_tracking and False not in self.right_tracking:
            complete = True
            points = self.last_value
            self.last_value += 25000
            delay = 4
        else:
            complete = False
            points = 75000
            delay = 2
        data = [complete,points,delay]
        return data

    # target_thunk is a default "this target is already on" handler
    def target_thunk(self):
        # score the already lit target amount
        self.game.score(10000)
        self.game.sound.play('im_target_thunk')
        # play a sound here

    def target_display_movie_helper(self,options):
        self.target_display_movie(options[0],options[1],options[2])

    def target_display_movie(self,target,side,complete = False,delay_time = 2):
        self.cancel_delayed("clear")
        if self.mode_index == 0:
            string = "FAST SCORING"
            anim = self.game.animations['ironman_land_and_stand']
        elif self.mode_index == 1:
            string = "DOUBLE SCORING"
            anim = self.game.animations['IM_Lands_at_church']
        elif self.mode_index == 2:
            string = "IRONMAN SCORING"
            anim = self.game.animations['IM3_suit_flip']

        if not complete:
            anim = self.hit_movies[self.hit_index]
#            self.layer = self.game.animations[self.hit_movies[self.hit_index]]
            self.hit_index += 1
            if self.hit_index == 6:
                self.hit_index = 0
            self.top.set_text("COMPLETE TARGETS FOR: " + string)
        # targets complete
        else:
            # score the points for the mark complete here, in care the display gets cut off
            self.game.mark.player_mark += 1
            self.game.mark.score()
            self.top.set_text("TARGETS COMPLETED: " + string + " IS READY")
            # if the player isn't done with marks, show the mark completed
            if self.game.mark.player_mark <= 6 and not self.game.mark.finished:
                self.delay(delay=delay_time,handler=self.game.mark.completed)

        anim.reset()
        anim.opaque = True
        # the letter display
        layers = [anim,self.i_layer_d,self.r_layer_d,self.o_layer_d,self.n1_layer_d,self.m_layer_d,self.a_layer_d,self.n2_layer_d]
        for n in range(0,4,1):
            if self.left_tracking[n] == True:
                if side == "L" and target == n:
                    #on_layers.append(self.left_layers[n])
                    # This is the blinking letter
                    self.blink(["L",n,16])
                else:
                    # add the layer for that letter
                    #on_layers.append(self.left_layers[n])
                    #off_layers.append(self.left_layers[n])
                    self.left_layers[n].enabled = True
            # otherwise it's off
            else:
                self.left_layers[n].enabled = False
            layers.append(self.left_layers[n])
        for n in range(0,3,1):
            if self.right_tracking[n] == True:
                if side == "R" and target == n:
                    #on_layers.append(self.right_layers[n])
                    self.blink(["R",n,16])
                else:
                    self.right_layers[n].enabled = True
            else:
                self.right_layers[n].enabled = False
            layers.append(self.right_layers[n])

        layers.append(self.top)
        self.layer = dmd.GroupedLayer(1920, 800, layers, opaque=True)
        self.delay("clear",delay=delay_time,handler=self.clear_layer)

    def blink(self,options):
        self.cancel_delayed("blink")
        side,index,count = options
        count -= 1
        # set which side we're working with
        if side == "L":
            layer = self.left_layers[index]
        else:
            layer = self.right_layers[index]
        # toggle enabled or not
        if layer.enabled:
            layer.enabled = False
        else:
            layer.enabled = True
        # loop back until the counter is out
        if count > 0:
            self.delay("blink",delay=0.2,handler=self.blink,param=[side,index,count])


    def target_display_helper(self,options):
        self.target_display(options[0],options[1],options[2])

    def target_display(self,target,side,complete = False):
        self.cancel_delayed("clear")
        off_layers = []
        on_layers = []
        for n in range(0,4,1):
            if self.left_tracking[n] == True:
                if side == "L" and target == n:
                    on_layers.append(self.left_layers[n])
                else:
                    # add the layer for that letter
                    on_layers.append(self.left_layers[n])
                    off_layers.append(self.left_layers[n])
        for n in range(0,3,1):
            if self.right_tracking[n] == True:
                if side == "R" and target == n:
                    on_layers.append(self.right_layers[n])
                else:
                    on_layers.append(self.right_layers[n])
                    off_layers.append(self.right_layers[n])
        # top and bottom text
        top = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(96,96,86),line_width=3,interior_color=(224,224,224))
        if complete:
            # score the points for the mark complete here, in care the display gets cut off
            self.game.mark.player_mark += 1
            self.game.mark.score()
            top.set_text("TARGETS COMPLETED")
        else:
            top.set_text("COMPLETE TARGETS")
        on_layers.append(top)
        off_layers.append(top)
        bottom = dmd.HDTextLayer(1920/2,650,self.game.fonts['default'],"center",line_color=(96,96,96),line_width=3,interior_color=(224,224,224))
        if complete:
            bottom.set_text( self.mode_titles[(self.completions % 3)] + " IS READY")
        else:
            bottom.set_text("FOR " + self.mode_titles[(self.completions % 3)])
        on_layers.append(bottom)
        off_layers.append(bottom)
        # group layer without the new letter
        off = dmd.GroupedLayer(1920,800,off_layers)
        # group layer with the new letter
        on = dmd.GroupedLayer(1920,800,on_layers)
        self.layer = dmd.ScriptedLayer(1920,800,[{'seconds':0.2, 'layer':off},{'seconds':0.2,'layer':on}], opaque=True)

        if complete:
            self.delay(delay=2, handler=self.target_display_movie_helper,param=[target,side,complete])
        else:
            self.delay("clear",delay=2,handler=self.clear_layer)
        #letter = ["I","R","O","N","M","A","N"]
        #self.game.displayText(letter[target])

    def start_target_mode(self):
        # count the completion
        self.completions += 1
        self.game.sound.play('scoring_mode_riff')
        duration = self.game.sound.sounds['scoring_mode_riff']['sound_list'][0].get_length()

        ## update the mode status
        if self.completions >= 3:
            self.game.mark.mode_completed(0)
        else:
            self.game.mark.mode_light(0)

        # load the relevant mode
        if self.mode_index == 0:
            self.game.interrupt.scoring_mode_start("FAST")
            self.delay(delay=duration,handler=self.voice_helper,param=['fast_scoring',procgame.sound.PLAY_FORCE])
#            self.game.modes.add(self.game.fast_scoring)
        elif self.mode_index == 1:
            # TODO: have to add ironman scoring yet
            # double scoring goes here
            self.game.interrupt.scoring_mode_start("DOUBLE")
            self.delay(delay=duration, handler=self.voice_helper, param=['double_scoring', procgame.sound.PLAY_FORCE])
#            self.game.modes.add(self.game.double_scoring)
        else:
            # ironman scoring would go here
            self.end_target_mode()
        self.mode_index += 1
        if self.mode_index > 2:
            self.mode_index = 0

    def tutorial_quote(self):
        if self.mode_index == 0:
            quote = 'tut_fast_scoring'
        elif self.mode_index == 1:
            # double scoring quote
            quote = 'tut_double_scoring'
        # other option is ironman scoring
        else:
            quote = 'tut_ironman_scoring'

        duration = self.voice_helper([quote,procgame.sound.PLAY_NOTBUSY])
        #if it successfully plays, set the flag
        if duration > 0:
            self.game.base.tut_status[0] = False

    def end_target_mode(self):
        # reset the tracking for the next one
        self.left_tracking = [False,False,False,False]
        self.right_tracking = [False,False,False]
        self.scoring_mode_running = False
        # reset the tutorial flag for the next scoring mode
        self.game.base.tut_status[0] = True
        self.update_lamps()

    def flasher_pulse(self):
        self.game.coils['leftRampBottomFlasher'].pulse()
        self.game.coils['rightRampBottomFlasher'].pulse()

    def update_lamps(self):
        if self.game.whiplash_multiball.running or self.game.monger_multiball.running or self.game.wm_multiball.running:
            self.disable_lamps()
        else:
            # default state for unlit lamps is blinking
            for lamp in self.left_lamps:
                lamp.schedule(0x0F0F0F0F)
            for lamp in self.right_lamps:
                lamp.schedule(0x0F0F0F0F)
            # if they're done, flash slower - a nice pulse fade would be good eventually
            if False not in self.left_tracking and False not in self.right_tracking:
                for lamp in self.left_lamps:
                    lamp.schedule(0x00FF00FF)  # 0010 0010 0100 1011 1101 0010 0100 0100
                for lamp in self.right_lamps:
                    lamp.schedule(0x00FF00FF)  # 0010 0010 0100 1011 1101 0010 0100 0100
            # otherwise turn on what should be on
            else:
                for n in range (0,4,1):
                    if self.left_tracking[n]:
                        self.left_lamps[n].enable()
                for n in range (0,3,1):
                    if self.right_tracking[n]:
                        self.right_lamps[n].enable()

    def disable_lamps(self):
        for lamp in self.left_lamps:
            lamp.disable()
        for lamp in self.right_lamps:
            lamp.disable()

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
