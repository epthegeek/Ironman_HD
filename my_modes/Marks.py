import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Marks(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Marks, self).__init__(game=game, priority=45, mode_type=AdvancedMode.Game)
        self.myID = "Marks"
        self.hold = False
        self.movie_index = 0
        # used to signal jericho
        self.finished = False
        # used for do or die hurry up
        self.dod = False
        # used for do or die mb
        self.dod_mb = False
        self.mark_movies = ['derp','mark_1_movie',
                            'mark_2_movie',
                            'mark_3_movie',
                            'mark_4_movie',
                            'mark_5_movie',
                            'mark_6_movie']
        self.mark_quotes = ['derp','mark_1_completed',
                            'mark_2_completed',
                            'mark_3_completed',
                            'mark_4_completed',
                            'mark_5_completed',
                            ',mark_6_completed']
        self.mark_lamps = [self.game.lamps['mark1'],
                           self.game.lamps['mark2'],
                           self.game.lamps['mark3'],
                           self.game.lamps['mark4'],
                           self.game.lamps['mark5'],
                           self.game.lamps['mark6']]
        self.mode_lamps = [self.game.lamps['progressIronMan'],
                           self.game.lamps['progressWarMachine'],
                           self.game.lamps['progressIronMonger'],
                           self.game.lamps['progressWhiplash'],
                           self.game.lamps['progressDrones']]
        self.text = dmd.HDTextLayer(1890, 640, self.game.fonts['default'], "right", line_color=(0, 0, 0), line_width=3, interior_color=(224, 224, 224))

    def evt_ball_starting(self):
        self.player_mark = self.game.getPlayerState('marks')
        self.finished = self.game.getPlayerState('marks_finished')
        self.modes_finished = self.game.getPlayerState('modes_finished')
        self.shield_flag = self.game.getPlayerState('shield_mark')
        # if ball mode count makes it to 5, then DOD is lit
        self.ball_mode_count = 0
        # modes: Ironman, War Machine, War Monger, Whiplash, Drones.
        self.modes_lit = [False,False,False,False,False]

    def evt_ball_ending(self):
        self.game.setPlayerState('marks',self.player_mark)
        self.game.setPlayerState('marks_finiahed', self.finished)
        self.game.setPlayerState('modes_finished', self.modes_finished)
        self.game.setPlayerState('shield_mark', self.shield_flag)

    def mode_light(self,number):
        # update the flag
        self.modes_lit[number] = True
        # update the lamps
        self.update_lamps()
        # check for do or die
        self.check_do_or_die()

    def mode_completed(self,number):
        # set the flag
        self.modes_finished[number] = True
        #update the lamps
        self.update_lamps()
        # see if it's done
        self.check_do_or_die()

    def check_do_or_die(self):
        if False not in self.modes_lit:
            self.light_do_or_die()
        if False not in self.modes_finished():
            self.light_do_or_die_mb()

    def light_do_or_die(self):
        print "Whoa, DOD"

    def light_do_or_die_mb(self):
        print "Whoa, DOD MB"

    def completed(self,callback=None):
        print "MARK COMPLETED"
        # If we're playing the mark 6 - set the finished flag
        if self.player_mark == 6:
            self.finished = True
        # play a quote
        print "PLAYING VOICE " + str(self.mark_quotes[self.player_mark])
        self.game.sound.play_voice(self.mark_quotes[self.player_mark],action=procgame.sound.PLAY_QUEUED)
        # play the video
        self.game.animations[self.mark_movies[self.player_mark]].reset()
        anim = self.game.animations[self.mark_movies[self.player_mark]]
        anim.add_frame_listener(-1,self.clear_layer)
        # this is so whatever called completed can do something after
        if callback:
            anim.add_frame_listener(-1, callback)
        self.text.set_text("MARK " + str(self.player_mark) + " COMPLETED")
        self.layer = dmd.GroupedLayer(1920,800,[anim,self.text],opaque=True)
        self.update_lamps()

    def score(self):
        print "MARK SCORE"
        # award points
        #TODO: assign points here
        pass

    def update_lamps(self):
        # reset
        for n in range(0,6,1):
            self.mark_lamps[n].disable()
            self.game.coils.mark6Flasher.disable()
            if n == 5:
                pass
            else:
                self.mode_lamps[n].disable()

        # and enable what should be on for marks
        for n in range(0,self.player_mark,1):
            self.mark_lamps[n].enable()
            if n == 5:
                self.game.coils.mark6Flasher.schedule(0x0F0F0F0F)

        for n in range (0,5,1):
            # Check modes finished first
            if self.modes_finished[n]:
                self.mode_lamps[n].schedule(0x0F0F0F0F)
                # status 2 means it's qualified for DOD multiball
            elif self.modes_lit[n]:
                self.mode_lamps[n].enable()
            # anything else and the light stays off
            else:
                pass
