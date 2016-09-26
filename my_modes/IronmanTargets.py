import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *
from procgame import dmd

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
        self.letter_images = ['target_i_image','target_r_image','target_o_image','target_n1_image','target_m_image','target_a_image','target_n2_image']
        self.hit_movies = ['hit_1_movie','hit_2_movie','hit_3_movie','hit_4_movie','hit_5_movie','hit_6_movie']
        self.hit_index = 0
        i_layer = dmd.FrameLayer(frame=self.game.animations['target_i_image'].frames[0])
        i_layer.set_target_position(1,0)
        r_layer = dmd.FrameLayer(frame=self.game.animations['target_r_image'].frames[0])
        r_layer.set_target_position(321,0)
        o_layer = dmd.FrameLayer(frame=self.game.animations['target_o_image'].frames[0])
        o_layer.set_target_position(541,0)
        n1_layer = dmd.FrameLayer(frame=self.game.animations['target_n1_image'].frames[0])
        n1_layer.set_target_position(751,0)
        m_layer = dmd.FrameLayer(frame=self.game.animations['target_m_image'].frames[0])
        m_layer.set_target_position(1001,0)
        a_layer = dmd.FrameLayer(frame=self.game.animations['target_a_image'].frames[0])
        a_layer.set_target_position(1281,0)
        n2_layer = dmd.FrameLayer(frame=self.game.animations['target_n2_image'].frames[0])
        n2_layer.set_target_position(1491,0)
        self.left_layers = [i_layer,r_layer,o_layer,n1_layer]
        self.right_layers = [m_layer,a_layer,n2_layer]
        self.mode_titles = ["FAST SCORING", "DOUBLE SCORING", "IRONMAN SCORING"]
        self.left_tracking = [False,False,False,False]
        self.right_tracking = [False,False,False]


    # read the current player information
    def evt_ball_starting(self):
        # TODO: check if targets hit stay ball to ball
        self.left_tracking = self.game.getPlayerState('im_left_targets')
        self.right_tracking = self.game.getPlayerState('im_right_targets')
        self.completions = self.game.getPlayerState('im_targets_completions')
        self.mode_index = self.game.getPlayerState('im_mode_index')
        self.last_value = self.game.getPlayerState('im_last_value')
        self.scoring_mode_running = False
        self.update_lamps()

    def evt_ball_ending(self):
        self.game.setPlayerState('im_left_targets',self.left_tracking)
        self.game.setPlayerState('im_right_targets',self.right_tracking)
        self.game.setPlayerState('im_targets_completions',self.completions)
        self.game.setPlayerState('im_mode_index',self.mode_index)
        self.game.setPlayerState('im_last_value')
        self.scoring_mode_running = False

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
            for n in target_set:
                # if we find an off target, activate it
                if tracker[n] == False:
                    tracker[n] = True
                    # Check if we're done
                    data = self.check_complete()
                    #do the display - sends activated target
                    # for now play a generic sound
                    self.game.sound.play('im_target_hit')
                    # if this is the first target of a set, play the tutorial quote
                    if self.game.base.tutorials[0]:
                        self.delay(delay=0.7,handler=self.tutorial_quote)
                    if data[0]:
                        self.target_display(n,side,data[0])
                    else:
                        self.target_display_movie(n,side,data[0])
                    self.update_lamps()
                    # score points
                    self.game.score(data[1])
                    break
        else:
            # process as a unique target
            # if the target is off, turn it on
            if tracker[target] == False:
                tracker[target] = True
                # Check if we're done
                data = self.check_complete()
                # do the display
                if data[0]:
                    self.target_display(target,side,data[0])
                else:
                    self.target_display_movie(target,side,data[0])
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
        else:
            complete = False
            points = 75000
        data = [complete,points]
        return data

    # target_thunk is a default "this target is already on" handler
    def target_thunk(self):
        # score the already lit target amount
        self.game.score(10000)
        self.game.sound.play('im_target_thunk')
        # play a sound here

    def target_display_movie_helper(self,options):
        self.target_display_movie(options[0],options[1],options[2])

    def target_display_movie(self,target,side,complete = False):
        self.cancel_delayed("clear")
        if not complete:
            self.game.animations[self.hit_movies[self.hit_index]].reset()
            self.layer = self.game.animations[self.hit_movies[self.hit_index]]
            self.hit_index += 1
            if self.hit_index == 6:
                self.hit_index = 0
            self.delay(delay=2.0,handler=self.target_display_helper,param=[target,side,complete])
        else:
            self.game.animations['ironman_land_and_stand'].reset()
            self.layer = self.game.animations['ironman_land_and_stand']
            # if the player isn't done with marks, show the mark completed
            if self.game.mark.player_mark <= 6 and not self.game.mark.finished:
                self.delay(delay=4,handler=self.game.mark.completed)

            self.delay("clear",delay=4,handler=self.clear_layer)

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

        ## update the mode status
        if self.completions >= 3:
            self.game.mark.mode_completed(0)
        else:
            self.game.mark.mode_light(0)

        # load the relevant mode
        if self.completions < 3:
            if self.completions == 1:
                self.game.modes.add(self.game.fast_scoring)
            else:
                # TODO: have to add double scoring and ironman scoring yet
                # double scoring goes here
                self.end_target_mode()
        else:
            if self.completions %3 == 1:
                self.game.modes.add(self.game.fast_scoring)
            elif self.completions % 3 == 2:
                # double scoring would go here
                self.end_target_mode()
            else:
                # ironman scoring would go here
                self.end_target_mode()
                # add the completion
            # add the scoring mode and start the proper action

    def tutorial_quote(self):
        if self.completions < 3:
            if self.completions == 0:
                quote = 'tut_fast_scoring'
            elif self.completions == 1:
                # double scoring quote
                quote = 'tut_double_scoring'
            else:
                # ironman scoring quote
                quote = 'tut_ironman_scoring'
        else:
            if self.completions % 3 == 0:
                quote = 'tut_fast_scoring'
            elif self.completions % 3 == 1:
                # double scoring
                quote = 'tut_double_scoring'
            else:
                # ironman scoring
                quote = 'tut_ironman_scoring'
        duration = self.voice_helper([quote,procgame.sound.PLAY_NOTBUSY])
        #if it successfully plays, set the flag
        if duration > 0:
            self.game.base.tutorials[0] = False

    def end_target_mode(self):
        # reset the tracking for the next one
        self.left_tracking = [False,False,False,False]
        self.right_tracking = [False,False,False]
        self.scoring_mode_running = False
        # reset the tutorial flag for the next scoring mode
        self.game.base.tutorials[0] = True

    def flasher_pulse(self):
        self.game.coils['leftRampBottomFlasher'].pulse()
        self.game.coils['rightRampBottomFlasher'].pulse()

    def update_lamps(self):
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

