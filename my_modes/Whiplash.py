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
        self.line_1 = dmd.HDTextLayer(1870, 450, self.game.fonts['whiplash_200'], "right",line_color=(196, 255, 255), line_width=5, interior_color=(12, 117, 2))
        self.line_2 = dmd.HDTextLayer(1870, 625, self.game.fonts['bebas80'], "right", line_color=(0,0,0), line_width=3,interior_color=(224, 224, 224))
        self.line_4 = dmd.HDTextLayer(1920/2, 660, self.game.fonts['default'], "center", line_color=(0,0,0,), line_width=3, interior_color=(252,205,63))
        self.line_3 = dmd.HDTextLayer(1870, 700, self.game.fonts['bebas80'], "right", line_color=(0,0,0), line_width=3,interior_color=(224, 224, 224))
        self.whiplash_type = 0
        self.styles = [self.game.fontstyles['whiplash_mb_0'],self.game.fontstyles['whiplash_mb_1']]

    def evt_ball_starting(self):
        self.wipe_delays()

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
            self.line_4.set_text("WHIPLASH IS READY", style=self.styles[self.whiplash_type])
            layers = [anim, self.line_4]
        else:
            # set up the animation
            if self.whiplash_type == 0:
                anim = self.progress_movies[0][self.movie_index]
                # tick up the index and reset if needed
                self.tick_movie_index(3)
            else:
                anim = self.progress_movies[1][self.movie_index]
                self.tick_movie_index(4)
            if self.hits_for_mb == 1:
                words = "MORE HIT TO"
            else:
                words = "MORE HITS TO"
            self.line_1.set_text(str(self.hits_for_mb),style=self.styles[self.whiplash_type],blink_frames = 8)
            self.line_2.set_text(words, style=self.game.fontstyles['grey'])
            self.line_3.set_text("LIGHT WHIPLASH", style=self.game.fontstyles['grey'])
            layers = [anim, self.line_1, self.line_2, self.line_3]

            anim.reset()
            points = 50000

        self.game.score(points)
#        anim.add_frame_listener(-1,self.whiplash_text_display_helper,param=[anim,type])
        anim.add_frame_listener(-1,self.delayed_clear,param=0.5)
#        self.layer = anim
        self.layer = dmd.GroupedLayer(1920,800,layers,opaque=True)
        # play a quote
        quotes = self.voice_tracks[self.whiplash_type]
        # check if there's a quote to play
        if self.hits_for_mb <= (len(quotes) - 1):
            self.delay(delay=0.5,handler=self.voice_helper,param=[quotes[self.hits_for_mb],procgame.sound.PLAY_NOTBUSY])

    def delayed_clear(self,time):
        self.delay("clear",delay=time, handler=self.clear_layer)

    def tick_movie_index(self,n):
        self.movie_index += 1
        if self.movie_index > n:
            self.movie_index = 0

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
