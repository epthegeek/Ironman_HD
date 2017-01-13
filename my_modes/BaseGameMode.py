import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class BaseGameMode(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(BaseGameMode, self).__init__(game=game, priority=5, mode_type=AdvancedMode.Game)
        self.black = self.game.animations['black']
        self.extra_balls_lit = 0
        self.extra_balls_pending = 0
        self.specials_lit = 0

    def evt_game_starting(self):
        self.game.mb_switch_stop.setup()

    # player added event
    def evt_player_added(self, player):
        # Stores/sets data for the player for the game
        # bonus multiplier
        #player.setState('bonus_x', 0)
        # ironman targets start blank
        player.setState('im_left_targets', [False,False,False,False])
        player.setState('im_right_targets', [False,False,False])
        # set the completion total to 0
        player.setState('im_targets_completions',0)
        player.setState('fast_scoring_runs',0)
        player.setState('double_scoring_runs', 0)
        # tutorial quotes: 0 = IM Targets, 1 = Drones, 2 = Spinners
        player.setState('tutorials', [True,True,True])
        player.setState('im_mode_index',0)
        player.setState('im_last_value',125000)
        # shields stat blank
        player.setState('shields', [False,False,False,False,False,False])
        player.setState('shield_awards_pending',0)
        player.setState('shield_awards_collected',0)
        # monger letters starting amount - apply setting
        if self.game.user_settings['Ironman']['06 Monger Letter Difficulty'] == 'Easy':
            value = 5
        else:
            value = 0
        player.setState('monger_letters', value)
        # add a counter for times monger has been battled
        player.setState('monger_battles',0)
        # tracker for the quote scripts for spinners and monger MB
        player.setState('monger_script',[None, 9, None, 9])
        player.setState('monger_status', "OPEN")
        # slot to hold the base value of moner shots in case it spreads across more than one ball
        player.setState('monger_base_value', 100000)
        player.setState('toy_letters', 0)
        # bogey ramps progress
        player.setState('ramp_stage',[0,0])
        player.setState('ramp_shots',[0,0])
        player.setState('bogey_status', "OPEN")
        player.setState('bogey_rounds',0)
        # whiplash hits
        player.setState('whiplash_hits',0)
        # and a counter for total whiplash battles
        player.setState('whiplash_battles',0)
        # set the drone targets lit
        player.setState('drone_targets', [True,True,True,True])
        # set the drone count for the player
        player.setState('drone_hits', 0)
        player.setState('drone_value', 10)
        player.setState('drone_jp_value', 150000)
        # set a count for war machine battles
        player.setState('war_machine_battles',0)
        # TODO: need to apply config to this
        player.setState('drones_for_mb',8)
        player.setState('wm_multiball_status', "OPEN")
        player.setState('whiplash_hits',0)
        # TODO: need to apply config to this
        self.whiplash_hits_base = 4
        player.setState('whiplash_hits_for_mb',self.whiplash_hits_base)
        player.setState('whiplash_mb_count',0)
        player.setState('whiplash_status', "OPEN")
        player.setState('whiplash_fights', 0)
        # used to toggle between whiplash and mk2
        player.setState('whiplash_type', 0)
        player.setState('marks',0)
        player.setState('marks_finished', False)
        # for tracking not done/started/done on the 5 main mode lights
        player.setState('modes_finished', [False,False,False,False,False])
        # for tracking if player has a mark level from shields
        player.setState('shield_mark',False)
        player.setState('ss_value',250000)
        # pops junk
        # first pops jackpot starts at 500,000
        player.setState('pops_jackpot', 500000)
        # pops super value starts at 20,000
        player.setState('pops_super_value',20000)
        player.setState('pops_level', 0)
        # track extra ball stuff
        player.setState('extra_balls_earned', 0)
        player.setState('extra_balls_pending', 0)
        player.setState('extra_balls_lit', 0)
        player.setState('specials_earned', 0)
        player.setState('specials_lit', 0)
        # and so on
        self.game.sound.play('start_button')
        # call a lamp update?
        self.game.update_lamps()

    def evt_ball_starting(self):
        self.wipe_delays()

        # get some tracking info for the player
        self.extra_balls_lit = self.game.getPlayerState('extra_balls_lit')
        self.extra_balls_pending = self.game.getPlayerState('extra_balls_pending')
        self.specials_lit = self.game.getPlayerState('specials_lit')
        self.update_lamps()

        # Shooter lane music selection
        if self.game.monger.status == "UP":
            song = 'monger_ready_shooter_lane'
        elif self.game.warmachine.multiball_status == "READY":
            song = 'wm_ready_shooter_lane'
        else:
            song = 'main_shooter_lane'
        # start the music
        self.game.sound.play_music(song,loops=-1)
        # ball saver?
        #self.game.ball_saver_enable(num_balls_to_save=1, time=5, now=True, allow_multiple_saves=False,callback=self.ballsaved)
        # reset bonus x
        self.bonus_x = 1
        # load the skill shot
        self.game.modes.add(self.game.skillshot)
        self.modes_this_ball = [0,0,0,0,0]
        self.tut_status = self.game.getPlayerState('tutorials')

    def evt_ball_saved(self):
        """ this event is fired to notify us that a ball has been saved
        """
        self.game.log("BaseGameMode: BALL SAVED from Trough callback")
        self.game.sound.play('ball_saved')
        self.game.displayText('Ball Saved!')
        # Do NOT tell the trough to launch balls!  It's handled automatically!
        # self.game.trough.launch_balls(1)

    def ballsaved(self):
        self.game.log("BaseGameMode: BALL SAVED from Trough Callback")
        self.game.set_status('Ball Saved!')

    def mode_started(self):
        pass

    def mode_stopped(self):
        pass

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.game.setPlayerState('tutorials', self.tut_status)
        self.game.setPlayerState('extra_balls_lit', self.extra_balls_lit)
        self.game.setPlayerState('extra_balls_pending', self.extra_balls_pending)
        self.game.setPlayerState('specials_lit', self.specials_lit)
        self.game.log("BaseGameMode trough changed notification ('ball_ending - again=%s, last=%s')" % (shoot_again,last_ball))
        # do the bonus here
        self.game.modes.add(self.game.bonus)
        # just as a precaution - set the multiplier back to 1 here
        self.game.multiplier = 1
        # return a special flag that says wait until I say so for the next event
        #return (False, -1)
        return 600

    def evt_game_ending(self):
        self.game.log("BaseGameMode changed notification ('game_ending')")
        self.game.displayText("GAME OVER", 'gameover')
        # play the outro song once
        self.game.sound.play_music('game_over')
        return 2

    # slings
    def sw_leftSlingshot_active(self,sw):
        print "LEFTY SLANG"
        self.sling_hit()
    def sw_rightSlingshot_active(self,sw):
        print "RIGHTY SLANG"
        self.sling_hit()
    def sling_hit(self):
        # play a sound
        self.game.sound.play('slingshot_clank')

    # music controller
    def set_music(self):
        print "SET MUSIC"
        if self.game.monger_multiball.running:
            # play the monger mb music
            song = 'monger_mb'
        elif self.game.wm_multiball.running:
            # play the war machine multiball music
            song = 'war_machine_mb'
        elif self.game.whiplash_multiball.running:
            # play the whiplash multiball music
            song = 'whiplash_mb'
        # boey trumps monger ready
        elif self.game.bogey.running:
            song = 'bogey'
        # if no multiball is running, but monger is up - that's the tune
        elif self.game.monger.status == "UP":
            song = 'monger_ready'
        # if monger isn't up, but war machine is ready, do that:
        elif self.game.warmachine.multiball_status == "READY":
            song = 'war_machine_ready'
        # last resort is the general gameplay loop
        else:
            song = 'general_gameplay'
        # turn it up, man
        print "SONG SELECTED: " + song
        self.game.sound.play_music(song,loops=-1)

    # to catch any launched ball to the pops - if the shooterlane is inactive for half second, pop the post.
    def sw_shooterLane_inactive_for_500ms(self,sw):
        self.cancel_delayed("post")
        # and fire the orbit post
        self.game.coils['orbitPost'].patter(on_time=4,off_time=4,original_on_time=20)
        # drop the post in 2 seconds
        self.delay("post",delay=2,handler=self.game.coils['orbitPost'].disable)

    # extra ball and special
    def light_extra_ball(self):
        self.extra_balls_lit += 1
        self.delay(delay=2, handler=self.voice_helper, param=['extra_ball_lit', procgame.sound.PLAY_FORCE])
        self.update_lamps()

    def collect_extra_ball(self):
        # add the extra ball
        self.extra_balls_lit -= 1
        self.extra_balls_pending += 1
        # play a sound
        self.game.sound.play('extra_ball_riff')
        # play a quote
        self.delay(delay=2 ,handler=self.voice_helper,param=['extra_ball',procgame.sound.PLAY_FORCE])
        # do some display shit?

    def light_special(self):
        self.specials_pending += 1
        self.update_lamps()

    def update_lamps(self):
        self.disable_lamps()
        if self.extra_balls_lit > 0:
            self.game.lamps['extraBall'].schedule(0x0F0F0F0F)
        if self.specials_lit > 0:
            self.game.lamps['special'].schedule(0X0F0F0F0F)
        if self.extra_balls_pending > 0:
            self.game.lamps['shootAgain'].enable()

    def disable_lamps(self):
        self.game.lamps['extraBall'].disable()
        self.game.lamps['special'].disable()

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
    def voice_helper(self,options):
        duration = self.game.sound.play_voice(options[0],action=options[1])
        return duration
