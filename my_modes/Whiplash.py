import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Whiplash(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Whiplash, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Game)
        self.myID = "Whiplash"
        self.hold = False
        self.movie_index = 0
        self.hit_movies = ['whiplash_1_movie','whiplash_2_movie','whiplash_3_movie','whiplash_4_movie','whiplash_5_movie']
        self.track_1 = ['whiplash_laugh','whiplash_laugh','whiplash_1_3','whiplash_1_2','whiplash_1_1']
        self.track_2 = ['whiplash_laugh','whiplash_laugh','whiplash_2_5','whiplash_2_4','whiplash_2_3','whiplash_2_2','whiplash_2_1']

    def evt_ball_starting(self):
        self.hits = self.game.getPlayerState('whiplash_hits')
        self.hits_for_mb = self.game.getPlayerState('whiplash_hits_for_mb')
        self.status = self.game.getPlayerState('whiplash_status')
        self.mb_count = self.game.getPlayerState('whiplash_mb_count')
        self.hold = False

    def evt_ball_ending(self):
        self.game.setPlayerState('whiplash_mb_count', self.mb_count)
        self.game.setPlayerState('whiplash_hits',self.hits)
        self.game.setPlayerState('whiplash_hits_for_mb',self.hits_for_mb)
        self.game.setPlayerState('whiplash_status',self.status)

    def sw_whiplashLeft_active(self,sw):
        if not self.hold:
            self.hold = True
            self.cancel_delayed("hold")
            self.target_hit(0)

    def sw_whiplashRight_active(self,sw):
        if not self.hold:
            self.hold = True
            self.cancel_delayed("hold")
            self.target_hit(1)

    def target_hit(self,side):
        # flash the flasher
        self.game.coils.whiplashFlasher.pulse()
        self.delay("hold",delay=0.5,handler=self.clear_hold)
        # play a sound for the hit
        self.game.sound.play('electric_buzz_1')
        # count the hit
        self.hits += 1
        if self.status == "READY":
            # do the multiball start thing
            print "START MULTIBALL"
        else:
            # tick down the hits to mb
            self.hits_for_mb -= 1
            print "HITS FOR MB : " + str(self.hits_for_mb)
            # check if we're there
            if self.hits_for_mb <= 0:
                print "DO MB READY"
                self.status = "READY"
                self.whiplash_hit_display("mb")
            else:
                self.whiplash_hit_display()

    def whiplash_hit_display(self,type="normal"):
        print "WHIPLASH HIT TYPE " + type
        self.cancel_delayed("clear")
        # score some points
        if type == 'mb':
            self.game.animations['whiplash_ready_movie'].reset()
            self.animation_layer = self.game.animations['whiplash_ready_movie']
            points = 100000
        else:
            self.game.animations[self.hit_movies[self.movie_index]].reset()
            self.animation_layer = self.game.animations[self.hit_movies[self.movie_index]]
            points = 50000
            # tick up the index and reset if needed
            self.movie_index += 1
            if self.movie_index > 4:
                self.movie_index = 0

        self.game.score(points)
        self.animation_layer.add_frame_listener(-1,lambda: self.whiplash_text_display(type))
        self.layer = self.animation_layer
        # play a quote
        if self.mb_count == 0:
            quotes = self.track_1
        else:
            quotes = self.track_2
        if quotes[self.hits_for_mb]:
            self.game.sound.play_voice(quotes[self.hits_for_mb])

    def whiplash_text_display(self,type="normal"):
        print "TEXT DISPLAY TYPE " + type
        self.animation_layer.frame_listeners = ()
        top = dmd.HDTextLayer(1920 / 2, 20, self.game.fonts['default'], "center", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        middle = dmd.HDTextLayer(1920 / 2, 200, self.game.fonts['whiplash_large'], "center", line_color=(196,255,255), line_width=12,interior_color=(12,117,2))
        middle.set_text("WHIPLASH")
        bottom = dmd.HDTextLayer(1920 / 2, 620, self.game.fonts['default'], "center", line_color=(96, 96, 86), line_width=3,interior_color=(224, 224, 224))
        if type == 'mb':
            bottom.set_text("MULTIBALL IS READY")
        else:
            if self.hits_for_mb == 1:
                word = "HIT"
            else:
                word = "HITS"
            top.set_text(str(self.hits_for_mb) + " MORE " + word + " FOR")
            bottom.set_text("MULTIBALL")
        # new
        display = dmd.GroupedLayer(1920,800,[self.game.base_game_mode.black,top,middle,bottom],opaque=True)
        self.layer = dmd.TransitionLayer(self.animation_layer, display, dmd.Transition.TYPE_CROSSFADE,dmd.Transition.PARAM_NORTH,lengthInFrames=48)
        self.delay("clear",delay=2,handler=self.clear_layer)

    def whiplash_mb_ready(self):
        print "MULTIBALL READY"
        self.status = "READY"
        self.whiplash_hit_display("mb")

    def clear_hold(self):
        self.hold = False

    def whiplash_mb_ready(self):
        self.status = "READY"
        # flash the flasher
        # play some sound or whatever

    def magnet(self,input):
        if input == "Throw":
            self.game.coils.whiplashMagnet.pulse()
        if input == "Hold":
            self.game.coils.whiplashMagnet.patter(on_time=2,off_time=6,original_on_time=10)