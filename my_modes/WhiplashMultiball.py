import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class WhiplashMultiball(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(WhiplashMultiball, self).__init__(game=game, priority=49,mode_type=AdvancedMode.Manual)
        self.myID = "WhiplashMultiball"
        self.running = False
        start_movie_1 = self.game.animations['whiplash_start']
        start_movie_1.opaque = True
        start_movie_2 = self.game.animations['mega_whiplash_start']
        start_movie_2.opaque = True
        self.start_movies = [start_movie_1, start_movie_2]
        jp_movies_1 = [self.game.animations['whiplash_jp_1'],
                       self.game.animations['whiplash_jp_2'],
                       self.game.animations['whiplash_jp_3'],
                       self.game.animations['whiplash_jp_4'],
                       self.game.animations['whiplash_jp_5']]
        jp_movies_2 = [self.game.animations['whiplash_jp_1b'],
                       self.game.animations['whiplash_jp_2b'],
                       self.game.animations['whiplash_jp_3b'],
                       self.game.animations['whiplash_jp_4b'],
                       self.game.animations['whiplash_jp_5b'],
                       self.game.animations['whiplash_jp_6b']]
        self.jackpot_movies = [jp_movies_1, jp_movies_2]
        super_1 = [self.game.animations['whiplash_super'],
                   self.game.animations['whiplash_super_2']]
        super_2 = [self.game.animations['mega_whiplash_super'],
                   self.game.animations['mega_whiplash_super_2']]
        self.super_movies = [super_1, super_2]
        self.type = 0
        bg = self.game.animations['whiplash_mb_bg']
        bg.opaque = True
        bg_mk2 = self.game.animations['whiplash_mk2_mb_bg']
        bg_mk2.opaque = True
        self.line_1 = dmd.HDTextLayer(1920/2, 300, self.game.fonts['whiplash_300'], "center",line_color=(203,197,55), line_width=5, interior_color=(169,42,0))
        self.line_2 = dmd.HDTextLayer(1920/2, 200, self.game.fonts['default'], "center", line_color=(96,96,86), line_width=3,interior_color=(224,224,224))
        jp_text_1 = dmd.GroupedLayer(1920,800,[bg,self.line_1,self.line_2],opaque=True)
        jp_text_2 = dmd.GroupedLayer(1920,800,[bg_mk2,self.line_1,self.line_2],opaque=True)
        self.jackpot_text = [jp_text_1,jp_text_2]
        self.jackpot_count = [5,10]
        title = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(224,224,224))
        title.set_text("WHIPLASH MULTIBALL")
        self.info_line = dmd.HDTextLayer(1920 / 2, 650, self.game.fonts['default'], "center", line_color=(0,0,0), line_width=5,interior_color=(224, 224, 224))
        self.score_line = dmd.HDTextLayer(1920 / 2, 200, self.game.fonts['main_score'], "center", line_color=(0,0,0), line_width=5,interior_color=(224, 0, 0))
        main_1 = dmd.GroupedLayer(1920,800,[bg,title,self.score_line,self.info_line],opaque=True)
        main_2 = dmd.GroupedLayer(1920,800,[bg_mk2,title,self.score_line,self.info_line],opaque=True)
        self.main_display = [main_1,main_2]
        self.styles = [self.game.fontstyles['whiplash_mb_0'],self.game.fontstyles['whiplash_mb_1']]
        self.jp_hit_sounds = ['whiplash_jp_hit_1','whiplash_jp_hit_2','whiplash_jp_hit_3','whiplash_jp_hit_4']
        self.jp_sound_index = 0
        self.points = 0
        self.orbit_inactive = False
        self.hold = True
        self.arrows = False
        self.ball_added = False

    def evt_ball_starting(self):
        self.wipe_delays()

    def mode_started(self):
        self.hold = True
        self.jackpot_index = 0
        # default value for jackpots is 250k
        self.jackpot_value = 250000
        # flag the super as off just to be sure
        self.super = False
        # to toggle between score/count behavior
        self.round = 0
        # starts with 5 jackpots
        self.jackpots_left = 5
        self.super_count = 0
        # update the info line
        self.update_info_layer(str(self.jackpots_left))

    def evt_ball_ending(self,(shoot_again,last_ball)):
        if self.running:
            self.end_multiball()

    def evt_single_ball_play(self):
        if self.running:
            self.end_multiball()

    def sw_whiplashLeft_active(self,sw):
        if not self.hold:
            self.target_hit()
        return procgame.game.SwitchStop

    def sw_whiplashRight_active(self,sw):
        if not self.hold:
            self.target_hit()
        return procgame.game.SwitchStop

    def target_hit(self):
        self.hold = True
        self.cancel_delayed("hold")
        self.delay("hold", delay=0.5, handler=self.clear_hold)
        self.jackpot_shot()

    def start_multiball(self,type):
        # start a ball save
        #self.game.enable_ball_saver(allow_multiple_saves=True,num_balls_to_save=8)

        self.type = type
        # set the colors?
        if type == 0:
            self.line_1.interior_color = (169.42,0)
            self.line_1.line_color = (203,197,55)
        else:
            self.line_1.interior_color = (40,109,204)
            self.line_2.line_color = (160,156,201)
        self.running = True
        # set a flag for if ball add has been used
        self.ball_added = False
        # update all the lamps
        self.game.update_lamps()
        # bring in the switch blocker
        if self.game.mb_switch_stop not in self.game.modes:
            self.game.modes.add(self.game.mb_switch_stop)
        # fire off the score update
        self.update_score_layer()
        # play some music
        self.game.base.set_music()
        # do the display
        anim = self.start_movies[self.type]
        anim.reset()
        anim.opaque = True
        anim.frame_listeners = []
        if self.game.mark.player_mark < 6:
            self.game.mark.player_mark += 1
            self.game.mark.score()
            # add a listener to do the completed with a callback to the main display here.
            anim.add_frame_listener(-1,self.game.mark.completed,param=self.do_main_display)
            anim.add_frame_listener(-1,self.clear_layer)
        else:
            anim.add_frame_listener(-1,self.do_main_display)
        self.layer = anim
        # set the total score to zero
        self.total_points = 0
        # launch another ball
        self.game.trough.launch_and_autoplunge_balls(1)
        # light the mode light
        self.game.mark.mode_light(3)
        # Turn on the jackpot arrows
        self.arrows = True
        self.update_lamps()
        # Turn off the hold
        self.hold = False

    def do_main_display(self):
        self.layer = self.main_display[self.type]

    def big5_jackpot_shot(self):
        if not self.super:
            self.jackpot_shot()

    def jackpot_shot(self,):
        self.cancel_delayed("clear")
        # set the points to score to the current JP value
        points = self.jackpot_value
        # if we're at the 3 million jackpot - complete the mode
        if self.points == 3000000:
            self.game.mark.mode_completed(3)
        # play the movie - if we're on super jackpot set it to that
        if self.super:
            text = "SUPER JACKPOT"
            self.super_count += 1
            if self.round == 0 and self.super_count == 2:
                # 2 supers in the first round
                self.super = False
                # turn off the flasher
                self.game.coils.whiplashFlasher.disable()
                # turn on the arrows
                self.arrows = True
                self.update_lamps()
                toggle = True
                anim = self.super_movies[self.type][1]
                self.jackpot_value = 500000
            # if we're only at one super in phase 1, don't toggle to phase 2
            elif self.round == 0:
                anim = self.super_movies[self.type][0]
                toggle = False
                self.jackpot_value = 1000000
            else:
                anim = self.super_movies[self.type][1]
                self.super = False
                # turn off the flasher
                self.game.coils.whiplashFlasher.disable()
                # turn on the arrows
                self.arrows = True
                self.update_lamps()
                toggle = True
                self.jackpot_value = 250000
        else:
            text = "JACKPOT"
            anim = self.jackpot_movies[self.type][self.jackpot_index]
            toggle = False

        anim.reset()
        anim.opaque = True
        anim.frame_listeners = []
        anim.add_frame_listener(-1,self.show_jp_value_helper,param=[text,points])
        self.layer = anim
        self.tick_jackpot_index()
        # award the points
        self.game.score(points)
        # play a hit noise
        self.game.sound.play(self.jp_hit_sounds[self.jp_sound_index])
        self.jp_sound_index += 1
        if self.jp_sound_index == 4:
            self.jp_sound_index = 0
        # are we toggling to the next phase?
        if toggle:
            # if we're in the 0 round, there are 2 shots
            # flip the round
            if self.round == 0:
                self.round = 1
            else:
                self.round = 0
            self.jackpots_left = self.jackpot_count[self.round]
            self.update_info_layer(str(self.jackpots_left))
        else:
            if not self.super:
                self.jackpots_left -= 1
            if self.jackpots_left == 0:
                self.update_info_layer()
                self.super = True
                # turn off the arrows
                self.arrows = False
                self.update_lamps()
                # turn on the flasher
                self.game.coils.whiplashFlasher.schedule(0x03030303)
                if self.round == 0:
                    self.jackpot_value = 500000
                else:
                    self.jackpot_value = 3000000
            else:
                self.update_info_layer(str(self.jackpots_left))

    def tick_jackpot_index(self):
        self.jackpot_index += 1
        if self.type == 0:
            if self.jackpot_index > 4:
                self.jackpot_index = 0
        else:
            if self.jackpot_index > 5:
                self.jackpot_index = 0

    def show_jp_value_helper(self,options):
        self.show_jp_value(options[0],options[1])

    def show_jp_value(self,text,value):
        self.line_2.set_text(text)
        self.line_1.set_text(self.game.score_display.format_score(value),style=self.styles[self.type])
        self.layer = self.jackpot_text[self.type]
        self.delay("clear",delay=2,handler=self.do_main_display)

    def update_score_layer(self):
        p = self.game.current_player()
        self.score_line.set_text(self.game.score_display.format_score(p.score))
        if self.running:
            self.delay(delay=0.2,handler=self.update_score_layer)

    def update_info_layer(self,string="SUPER JACKPOT IS LIT"):
        if string != "SUPER JACKPOT IS LIT":
            if self.jackpots_left == 1:
                string = str(self.jackpots_left) + " JACKPOT REMAINING"
            else:
                string = str(self.jackpots_left) + " JACKPOTS REMAINING"

        self.info_line.set_text(string)

    def end_multiball(self):
        # turn off the flasher just in case
        self.game.coils.whiplashFlasher.disable()
        # turn off the ramp arrows
        self.arrows = False
        self.update_lamps()
        # remove the run flag
        self.running = False
        # set the whiplash status off of ready
        self.game.whiplash.status = "OPEN"
        # set the hits for the next MB at base value + 5 per previous multiball
        self.game.whiplash.whiplash_fights += 1
        self.game.whiplash.hits_for_mb = (self.game.base.whiplash_hits_base + (self.game.whiplash.whiplash_fights * 5))
        # if we just finished regular whiplash, set the type to mega for next run
        if self.game.whiplash.whiplash_type == 0:
            self.game.whiplash.whiplash_type = 1
        else:
            self.game.whiplash.whiplash_type = 0
        # check the switch block
        self.game.mb_switch_stop.check_remove()
        # set the music back
        self.game.base.set_music()
        # update the recon info
        self.game.score_display.update_recon_whiplash()
        self.unload()

    def add_ball(self):
        # Only do this if all 4 aren't already in play
        if self.game.trough.num_ball_in_play < 4:
            self.ball_added = True
            self.game.trough.launch_and_autoplunge_balls(1)

    def clear_hold(self):
        self.hold = False

    def update_lamps(self):
        self.game.mb_switch_stop.update_lamps()

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
