import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class BaseGameMode(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(BaseGameMode, self).__init__(game=game, priority=5, mode_type=AdvancedMode.Game)
        self.black = self.game.animations['black']

    def evt_game_starting(self):
        print "GAME STARTING WOOT WOOT"
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
        player.setState('whiplash_hits_for_mb',4)
        player.setState('whiplash_mb_count',0)
        player.setState('whiplash_status', "OPEN")
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
        # and so on
        self.game.sound.play('start_button')
        # call a lamp update?
        self.game.update_lamps()

    def evt_ball_starting(self):
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
        self.bonus_x = 0
        # load the skill shot
        self.game.modes.add(self.game.skillshot)
        self.modes_this_ball = [0,0,0,0,0]
        self.tut_status = self.game.getPlayerState('tutorials')

    def ballsaved(self):
        self.game.log("BaseGameMode: BALL SAVED from Trough Callback")
        self.game.displayText('Ball Saved!')

    def mode_started(self):
        pass

    def mode_stopped(self):
        pass

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.game.sound.stop_music()
        self.game.setPlayerState('tutorials', self.tut_status)
        self.game.log("BaseGameMode trough changed notification ('ball_ending - again=%s, last=%s')" % (shoot_again,last_ball))
        return 2

    def evt_game_ending(self):
        self.game.log("BaseGameMode changed notification ('game_ending')")
        self.game.displayText("GAME OVER", 'gameover')
        # play the outro song once
        self.game.sound.play_music('game_over')
        return 2

    # slings
    def sw_leftSlingshot_active(self,sw):
        self.sling_hit()
    def sw_rightSlingshot_active(self,sw):
        self.sling_hit()
    def sling_hit(self):
        # play a sound
        self.game.sound.play('slingshot_clank')

    # music controller
    def set_music(self):
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
        self.game.sound.play_music(song,loops=-1)