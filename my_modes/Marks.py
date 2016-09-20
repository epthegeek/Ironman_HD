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
        self.mark_movies = ['derp','mark_1_movie','mark_2_movie','mark_3_movie','mark_4_movie','mark_5_movie','mark_6_movie']
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
        self.text = dmd.HDTextLayer(1890, 640, self.game.fonts['default'], "right", line_color=(0,0,0), line_width=3,interior_color=(224, 224, 224))

    def evt_ball_starting(self):
        self.player_mark = self.game.getPlayerState('marks')
        self.finished = self.game.getPlayerState('marks_finished')
        self.mode_master_status = self.game.getPlayerState('mode_master_status')
        self.shield_flag = self.game.getPlayerState('shield_mark')
        # if ball mode count makes it to 5, then DOD is lit
        self.ball_mode_count = 0

    def evt_ball_ending(self):
        self.game.setPlayerState('marks',self.player_mark)
        self.game.setPlayerState('marks_finiahed', self.finished)
        self.game.setPlayerState('mode_master_status', self.mode_master_status)
        self.game.setPlayerState('shield_mark', self.shield_flag)

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
        # and enable what should be on
        for n in range(0,self.player_mark,1):
            self.mark_lamps[n].enable()
            if n == 5:
                self.game.coils.mark6Flasher.schedule(0x0F0F0F0F)
            # update the mode lamps on lower numbers
            else:
                # status 1 means it ran
                if self.mode_master_status[n] == 1:
                    self.mode_lamps[n].enable()
                # status 2 means it's qualified for DOD multiball
                elif self.mode_master_status[n] == 2:
                    self.mode_lamps[n].schedule(0x0F0F0F0F)
                # anything else and the light stays off
                else:
                    pass

