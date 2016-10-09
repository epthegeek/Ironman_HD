import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random
from procgame import dmd

class MongerMultiball(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(MongerMultiball, self).__init__(game=game, priority=51,mode_type=AdvancedMode.Manual)
        self.myID = "MongerMultiball"
        self.running = False
        self.loop_count = 0
        self.monger_lamps = ["Placeholder",
                             self.game.lamps['mongerM'],
                             self.game.lamps['mongerO'],
                             self.game.lamps['mongerN'],
                             self.game.lamps['mongerG'],
                             self.game.lamps['mongerE'],
                             self.game.lamps['mongerR']]
        backdrop = self.game.animations['monger_multiball_backdrop']
        title = dmd.HDTextLayer(1100,20,self.game.fonts['bebas1800'],"center",line_color=(0,0,0),line_width=3,interior_color=(146, 24, 222))
        title.set_text("IRON MONGER MULTIBALL")
        self.score_layer = dmd.HDTextLayer(1100,140,self.game.fonts['bebas300'],"center",line_color=(0,0,0),line_width=3,interior_color=(255, 255, 255))
        shoot = dmd.HDTextLayer(1100,450,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(255, 0, 0))
        shoot.set_text("SHOOT")
        self.goal_text = dmd.HDTextLayer(1100,550,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(255, 0, 0))
        self.goal_text_2 = dmd.HDTextLayer(1100,650,self.game.fonts['default'],"center",line_color=(0,0,0),line_width=3,interior_color=(255, 0, 0))
        self.main_display_layer = dmd.GroupedLayer(1920,800,[backdrop,title,self.score_layer,shoot,self.goal_text,self.goal_text_2],opaque=True)

        self.start_movies = ['monger_start_1','monger_start_2','monger_start_3','monger_start_4']
        self.start_index= 0
        self.hit_movies = ['monger_hit_1b','monger_hit_2b','monger_hit_3b','monger_hit_4b','monger_hit_5b','monger_hit_6b']
        self.monger_status = "DOWN"

        self.points_layer = dmd.HDTextLayer(1820, 550, self.game.fonts['bebas200'], "right", line_color=[0, 0, 0],line_width=4, interior_color=[146, 24, 222])
        self.points_layer.set_text("250,000")
        self.super = False

        # text layers for intro display
        self.intro_1 = dmd.HDTextLayer(1890, 650,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        self.intro_1.set_text("MULTIBALL",blink_frames=6)
        self.intro_2 = dmd.HDTextLayer(1890, 550,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        self.intro_2.set_text("MONGER",blink_frames=6)
        self.intro_3 = dmd.HDTextLayer(1890, 450,self.game.fonts['default'],"right",line_color=(0,0,0),line_width=6,interior_color=(224,224,224))
        self.intro_3.set_text("IRON",blink_frames=6)
        self.toy_valid = True

        script0 = ['immb_script0a','immb_script0b','immb_sript0c','immb_script0d','immb_script0e']
        script1 = ['immb_script1a', 'immb_script1b', 'immb_sript1c', 'immb_script1d', 'immb_script1e']
        script2 = ['immb_script2a', 'immb_script2b', 'immb_sript2c', 'immb_script2d']
        script3 = ['immb_script3a', 'immb_script3b', 'immb_sript3c', 'immb_script3d']
        self.scripts = [script0, script1, script2, script3]

    def evt_ball_starting(self):
        self.wipe_delays()

    def evt_ball_ending(self,(shoot_again,last_ball)):
        if self.running:
            self.end_multiball()

    def evt_single_ball_play(self):
        if self.running:
            self.end_multiball()

    def mode_started(self):
        self.running = True
        # add the switch filter
        if self.game.mb_switch_stop not in self.game.modes:
            self.game.modes.add(self.game.mb_switch_stop)
        # super jackpot flag
        self.super = False
        # reset the jacpot hit count
        self.jackpot_hits = 0
        self.jackpots_total = 0
        # reset to the start of MB, function used later after super as well.
        self.reset_mb()
        # start the score update
        self.update_score_layer()
        # change the music
        self.game.base.set_music()
        # make sure the toy is ready for hits
        self.toy_valid = True
        # update the mode light
        self.game.mark.mode_light(2)
        self.loop_count = 0

    def sw_mongerOptoLeft_active(self,sw):
        self.monger_opto_hit()

    def sw_mongerOptoRight_active(self,sw):
        self.monger_opto_hit()

    def sw_mongerOptoCenter_active(self,sw):
        self.monger_opto_hit()

    def monger_opto_hit(self):
        if self.toy_valid and not self.super:
            self.toy_valid = False
            self.delay(delay=0.5,handler=self.revalidate_toy)
            self.hit_toy()

    def hit_toy(self):
        if self.game.monger_toy.status == "UP" or self.game.monger_toy.status == "MOVING":
            self.cancel_delayed("display")
            # play a sound
            self.game.sound.play('monger_clank')
            # score some points?
            points = 250000
            self.game.score(points)
            anim = self.game.animations[self.hit_movies[self.jackpot_hits]]
            anim.reset()
            anim.add_frame_listener(-1, self.set_main_display)
            self.layer = dmd.GroupedLayer(1920,800,[anim,self.points_layer],opaque=True)
            # play a script quote
            self.delay(delay=2,handler=self.script_quote)
            # tick up the jackpots
            self.jackpot_hits += 1
            self.jackpots_total += 1
            # if that was the last hit, lower the monger
            if self.jackpot_hits == 6:
                self.lower_monger()

    def set_main_display(self):
        print "OOBA DOOBA"
        self.layer = self.main_display_layer

    def start_multiball(self):
        # play the clip and the audio
        self.game.sound.play('monger_big_yell')
        video = random.choice(self.start_movies)
        anim = self.game.animations[video]
        anim.reset()
        if self.game.mark.player_mark < 6:
            self.game.mark.player_mark += 1
            self.game.mark.score()
            anim.add_frame_listener(-1,self.game.mark.completed, param=self.set_main_display)
            anim.add_frame_listener(-1,self.clear_layer)
        else:
            anim.add_frame_listener(-1, self.set_main_display)
        anim.add_frame_listener(-1,self.set_main_display)
        self.layer = dmd.GroupedLayer(1920,800,[anim,self.intro_1,self.intro_2,self.intro_3],opaque=True)
        # launch the balls
       # self.game.trough.launch_and_autoplunge_balls(2)
        # lower the monger after a delay?
        self.delay(1,handler=self.game.monger_toy.fall)
        # release the ball
        self.game.monger.magnet("Release")
        # up the mark
        # do the mark here - if needed

    def center_spinner_hit(self):
        if self.super:
            # award the super jackpot
            self.super = False
            self.super_display = True
            # turn on the mode complete light
            self.game.mark.mode_completed(1)
            # score the points
            self.game.score(3000000)
            # play the animations
            anim = self.game.animations['monger_super']
            anim.reset()
            anim.add_frame_listener(-1, self.reset_mb)
            self.layer = anim
        elif self.monger_status == "DOWN":
            self.raise_monger()
        else:
            pass

    def orbit_hit(self):
        print "MONGER MB ORBIT BOOP"
        if self.monger_status == "DOWN":
            self.raise_monger()

    def raise_monger(self):
        self.monger_status = "UP"
        # play the audio call out
        # raise the toy
        self.game.monger_toy.rise()
        # set the goal text
        self.goal_text.set_text("IRON MONGER")
        self.goal_text_2.set_text("FOR JACKPOTS")
        # do the display
        anim = self.game.animations['monger_mb_raise']
        anim.reset()
        anim.add_frame_listener(-1,self.set_main_display)
        self.layer = anim
        # pick out a script
        self.selected_script = random.choice(self.scripts)
        self.script_index = 0
        # play a quote - from the 2nd raise on
        # TODO: Does it say anything on the first one?
        if self.loop_count > 0:
            self.game.play_voice('repeat_raise',action=procgame.sound.PLAY_NOTBUSY)
        self.loop_count += 1

    def lower_monger(self):
        self.monger_status = "DOWN"
        self.super = True
        self.game.monger_toy.fall()
        # reset the jackpots
        self.jackpots = 0
        # set the goal text
        self.goal_text.set_text("CENTER SPINNER")
        self.goal_text_2.set_text("FOR SUPER JACKPOT")

    def revalidate_toy(self):
        self.toy_valid = True

    def update_score_layer(self):
        p = self.game.current_player()
        self.score_layer.set_text(self.game.score_display.format_score(p.score))
        if self.running:
            self.delay(delay=0.2,handler=self.update_score_layer)

    def reset_mb(self):
        # set the goal text
        self.goal_text.set_text("THE SPINNERS")
        self.goal_text_2.set_text("TO RAISE IRON MONGER")
        # set the monger status
        self.monger_status = "DOWN"
        self.set_main_display()

    def script_quote(self):
        # play the voice clip for this players script at this players index
        # if there are quotes left in the script
        if len(self.selected_script) < (self.script_index + 1):
            duration = self.voice_helper([self.selected_script[self.script_index], procgame.sound.PLAY_NOTBUSY])
            # if the quote played, update the index
            if duration > 0:
                self.script_index += 1


    # this needs work for now it's just unloading
    def end_multiball(self):
        self.game.monger_toy.fall()
        self.running = False
        # reset the iron monger letters
        self.game.monger.letters = 0
        # check for the switch stop
        self.game.mb_switch_stop.check_remove()
        self.unload()

    def update_lamps(self):
        # the jackpot arrows
        # the letters in front of monger
        for lamp in self.monger_lamps:
            lamp.disable()
        if self.jackpot_hits > 0:
            for n in range (1,8,1):
                if n <= self.jackpot_hits and n != 0:
                    self.monger_lamps[n].enable()

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
