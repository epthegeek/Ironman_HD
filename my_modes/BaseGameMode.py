import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class BaseGameMode(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(BaseGameMode, self).__init__(game=game, priority=5, mode_type=AdvancedMode.Game)
        self.black = self.game.animations['black']

    # player added event
    def evt_player_added(self, player):
        # Play the player added noise
        self.game.sound.play('game_start')
        # Stores/sets data for the player for the game
        # bonus multiplier
        #player.setState('bonus_x', 0)
        # ironman targets start blank
        player.setState('im_left_targets', [False,False,False,False])
        player.setState('im_right_targets', [False,False,False])
        # set the completion total to 0
        player.setState('im_targets_completions',0)
        player.setState('fast_scoring_runs',0)
        player.setState('target_virgin', True)
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
        player.setState('monger_status', "OPEN")
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
        player.setState('whiplash_hits_for_mb',5)
        player.setState('whiplash_mb_count',0)
        player.setState('whiplash_status', "OPEN")
        player.setState('marks',0)
        player.setState('marks_finished', False)
        # for tracking not done/started/done on the 5 main mode lights
        player.setState('mode_status', [0,0,0,0,0])
        # for tracking if player has a mark level from shields
        player.setState('shield_mark',False)
        # and so on
        self.game.sound.play('start_button')

    def evt_ball_starting(self):
        self.game.sound.play_music('ball_1_shooter_lane',loops=-1)
        #self.game.ball_saver_enable(num_balls_to_save=1, time=5, now=True, allow_multiple_saves=False,callback=self.ballsaved)
        self.bonus_x = 0

    def ballsaved(self):
        self.game.log("BaseGameMode: BALL SAVED from Trough Callback")
        self.game.displayText('Ball Saved!')

    def mode_started(self):
        pass

    def mode_stopped(self):
        pass

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.game.sound.stop_music()
        self.game.log("BaseGameMode trough changed notification ('ball_ending - again=%s, last=%s')" % (shoot_again,last_ball))
        return 2

    def evt_game_ending(self):
        self.game.log("BaseGameMode changed notification ('game_ending')")
        self.game.displayText("GAME OVER", 'gameover')
        return 2

    # slings
    def sw_leftSlingshot_active(self,sw):
        self.sling_hit()
    def sw_rightSlingshot_active(self,sw):
        self.sling_hit()
    def sling_hit(self):
        # play a sound
        self.game.sound.play('slingshot_clank')
