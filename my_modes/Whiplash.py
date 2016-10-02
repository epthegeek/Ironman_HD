import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Whiplash(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Whiplash, self).__init__(game=game, priority=15, mode_type=AdvancedMode.Game)
        self.myID = "Whiplash"
        self.hold = False
        self.movie_index = 0
        hit_movies_1 = [self.game.animations['whiplash_1_movie'],
                        self.game.animations['whiplash_2_movie'],
                        self.game.animations['whiplash_3_movie'],
                        self.game.animations['whiplash_4_movie'],
                        self.game.animations['whiplash_5_movie']]
        hit_movies_2 = [self.game.animations['whiplash_1b_movie'],
                        self.game.animations['whiplash_2b_movie'],
                        self.game.animations['whiplash_3b_movie'],
                        self.game.animations['whiplash_4b_movie'],
                        self.game.animations['whiplash_5b_movie'],
                        self.game.animations['mega_whiplash_face']]
        self.progress_movies = [hit_movies_1,hit_movies_2]
        track_1 = ['whiplash_laugh','whiplash_1_3','whiplash_1_2','whiplash_1_1']
        track_2 = ['whiplash_laugh','whiplash_2_5','whiplash_2_4','whiplash_2_3','whiplash_2_2','whiplash_2_1']
        self.voice_tracks = [track_1,track_2]
        # layers for the hits left display
        self.line_1 = dmd.HDTextLayer(1600, 100, self.game.fonts['whiplash_450'], "center",line_color=(196, 255, 255), line_width=5, interior_color=(12, 117, 2))
        self.line_2 = dmd.HDTextLayer(1600, 500, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(224, 224, 224))
        self.line_3 = dmd.HDTextLayer(1600, 620, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=3,interior_color=(224, 224, 224))
        # layers for is ready display
        ready_1 = dmd.HDTextLayer(1500, 110,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=4,interior_color=(252,205,63)).set_text("WHIPLASH",blink_frames=10)
        ready_2 = dmd.HDTextLayer(1500, 280,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=4,interior_color=(252,205,63)).set_text("IS",blink_frames=10)
        ready_3 = dmd.HDTextLayer(1500, 450,self.game.fonts['bebas200'],"center",line_color=(0,0,0),line_width=4,interior_color=(252,205,63)).set_text("READY",blink_frames=10)
        # backgrounds
        bg_1 = self.game.animations['whiplash_still']
        bg_2 = self.game.animations['mega_whiplash_still']
        # hits left v1
        hits_left_v1 = dmd.GroupedLayer(1920,800,[bg_1,self.line_1,self.line_2,self.line_3],opaque=True)
        # hits left v2
        hits_left_v2 = dmd.GroupedLayer(1920,800,[bg_2,self.line_1,self.line_2,self.line_3],opaque=True)
        self.hits_left_layers = [hits_left_v1,hits_left_v2]
        # ready v1
        ready_v1 = dmd.GroupedLayer(1920,800,[bg_1,ready_1,ready_2,ready_3],opaque=True)
        # ready v2
        ready_v2 = dmd.GroupedLayer(1920,800,[bg_2,ready_1,ready_2,ready_3],opaque=True)
        self.ready_layers = [ready_v1,ready_v2]
        self.whiplash_type = 0
        self.styles = [self.game.fontstyles['whiplash_mb_0'],self.game.fontstyles['whiplash_mb_1']]

    def evt_ball_starting(self):
        self.whiplash_fights = self.game.getPlayerState('whiplash_fights')
        self.hits = self.game.getPlayerState('whiplash_hits')
        self.hits_for_mb = self.game.getPlayerState('whiplash_hits_for_mb')
        self.status = self.game.getPlayerState('whiplash_status')
        # flash the flasher if ready
        if self.status == "READY":
            self.game.coils['whiplashFlasher'].schedule(0x03030303)
        self.mb_count = self.game.getPlayerState('whiplash_mb_count')
        self.whiplash_type = self.game.getPlayerState('whiplash_type')
        self.hold = False

    def evt_ball_ending(self,(shoot_again,last_ball)):
        self.game.setPlayerState('whiplash_fights', self.whiplash_fights)
        self.game.setPlayerState('whiplash_mb_count', self.mb_count)
        self.game.setPlayerState('whiplash_hits',self.hits)
        self.game.setPlayerState('whiplash_hits_for_mb',self.hits_for_mb)
        self.game.setPlayerState('whiplash_status',self.status)
        self.game.setPlayerState('whiplash_type',self.whiplash_type)
        # disable the whiplash flasher for good measure
        self.game.coils['whiplashFlasher'].disable()

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
            # disable the whiplash flasher
            self.game.coils['whiplashFlasher'].disable()
            self.game.modes.add(self.game.whiplash_multiball)
            self.game.whiplash_multiball.start_multiball(self.whiplash_type)
        else:
            # tick down the hits to mb
            self.hits_for_mb -= 1
            # check if we're there
            if self.hits_for_mb <= 0:
                self.status = "READY"
                self.whiplash_hit_display("mb")
            else:
                self.whiplash_hit_display()

    def whiplash_hit_display(self,type="normal"):
        self.cancel_delayed("clear")
        # score some points
        if type == 'mb':
            if self.whiplash_type == 0:
                anim = self.progress_movies[0][4]
            else:
                anim = self.progress_movies[1][5]
            anim.reset()
            points = 250000
        else:
            if self.whiplash_type == 0:
                anim = self.progress_movies[0][self.movie_index]
                # tick up the index and reset if needed
                self.tick_movie_index(3)
            else:
                anim = self.progress_movies[1][self.movie_index]
                self.tick_movie_index(4)
            anim.reset()
            points = 50000

        self.game.score(points)
        anim.add_frame_listener(-1,self.whiplash_text_display_helper,param=[anim,type])
        self.layer = anim
        # play a quote
        quotes = self.voice_tracks[self.whiplash_type]
        # check if there's a quote to play
        if self.hits_for_mb <= (len(quotes) - 1):
            self.delay(delay=0.6,handler=self.voice_helper,param=[quotes[self.hits_for_mb],procgame.sound.PLAY_NOTBUSY])

    def tick_movie_index(self,n):
        self.movie_index += 1
        if self.movie_index > n:
            self.movie_index = 0

    def whiplash_text_display_helper(self,options):
        self.whiplash_text_display(options[0],options[1])

    def whiplash_text_display(self,anim,type="normal"):
        anim.frame_listeners = ()
        if type == 'mb':
            layer = self.ready_layers[self.whiplash_type]
        else:
            if self.hits_for_mb == 1:
                words = "MORE HIT"
            else:
                words = "MORE HITS TO"
            self.line_1.set_text(str(self.hits_for_mb),style=self.styles[self.whiplash_type])
            self.line_2.set_text(words)
            self.line_3.set_text("LIGHT WHIPLASH")
            layer = self.hits_left_layers[self.whiplash_type]
        # new
        self.layer = dmd.TransitionLayer(anim, layer, dmd.Transition.TYPE_CROSSFADE,dmd.Transition.PARAM_NORTH,lengthInFrames=48)
        self.delay("clear",delay=2,handler=self.clear_layer)

    def whiplash_mb_ready(self):
        self.status = "READY"
        # flash the flasher
        self.game.coils['whiplashFlasher'].schedule(0x03030303)
        self.whiplash_hit_display("mb")

    def clear_hold(self):
        self.hold = False

    def magnet(self,input):
        if input == "Throw":
            self.game.coils.whiplashMagnet.pulse()
        if input == "Hold":
            self.game.coils.whiplashMagnet.patter(on_time=2,off_time=6,original_on_time=10)

    def clear_layer(self):
        self.layer = None

    def wipe_delays(self):
        self.__delayed = []
        # simple mode shutdown

    def unload(self):
        self.wipe_delays()
        self.layer = None
        self.game.modes.remove(self)

    # delayed voice quote helper with a list input
    def voice_helper(self, options):
        duration = self.game.sound.play_voice(options[0], action=options[1])
        return duration
