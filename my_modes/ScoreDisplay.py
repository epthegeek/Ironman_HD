import pinproc
import struct
import time
import os
import locale
import procgame.game
from procgame import dmd
from procgame.game import AdvancedMode

class ScoreLayer(dmd.GroupedLayer):
    def __init__(self, width, height, mode):
        super(ScoreLayer, self).__init__(width, height, mode)
        self.mode = mode
    def next_frame(self):
        """docstring for next_frame"""
        # Setup for the frame.
        self.mode.update_layer()
        return super(ScoreLayer, self).next_frame()

class ScoreDisplay(procgame.game.AdvancedMode):
    score_muted = False

    def __init__(self, game):
        super(ScoreDisplay, self).__init__(game=game, priority=0, mode_type=AdvancedMode.System)
        self.myID = "ScoreDisplay"

        self.layer = ScoreLayer(self.game.dmd.width, self.game.dmd.height, self)
        self.layer.layers = list()
        # build all the basic layers to be used
        # main score
        self.main_score = dmd.HDTextLayer(1125,
                                          310,
                                          self.game.fonts['main_score'],
                                          "center",
                                          vert_justify="center",
                                          line_color=(0, 0, 0),
                                          line_width=9,
                                          interior_color=(255, 224, 0))
        self.main_score.set_text("00")
        # 1p score
        self.p1_score = dmd.HDTextLayer(200,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.p1_score.set_text("00")
        # ball number for 1p
        self.ball_number = dmd.HDTextLayer(200,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.player_number = dmd.HDTextLayer(200,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.info_toggle = dmd.ScriptedLayer(500,
                                             100,
                                             [{'layer': self.ball_number,'seconds': 1},{'layer': self.player_number,'seconds': 1}],
                                             )
        # 2p score
        self.p2_score = dmd.HDTextLayer(400,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.p2_score.set_text("00")
        # 3p score
        self.p3_score = dmd.HDTextLayer(600,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.p3_score.set_text("00")
        # 4p score
        self.p4_score = dmd.HDTextLayer(1654,
                                        100,
                                        self.game.fonts['bebas80'],
                                        "center",
                                        vert_justify="center",
                                        line_color=(0,0,0),
                                        line_width=4,
                                        interior_color=(255,224,0))
        self.p4_score.set_text("00")
        self.score_layers = [self.p1_score,self.p2_score,self.p3_score,self.p4_score]
        # switches
        self.switches = dmd.HDTextLayer(340,
                                        232,
                                        self.game.fonts['ptsans24'],
                                        "right",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.switches.set_text("0")
        # ramps
        self.ramps = dmd.HDTextLayer(340,
                                        270,
                                        self.game.fonts['ptsans24'],
                                        "right",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.ramps.set_text("0")
        # duration
        self.duration = dmd.HDTextLayer(340,
                                        310,
                                        self.game.fonts['ptsans24'],
                                        "right",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.duration.set_text("0")

        # extra balls
        self.extra_balls = dmd.HDTextLayer(340,
                                        350,
                                        self.game.fonts['ptsans24'],
                                        "right",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.extra_balls.set_text("0")

        # warnings
        self.warnings = dmd.HDTextLayer(340,
                                        390,
                                        self.game.fonts['ptsans24'],
                                        "right",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.warnings.set_text("0")

        # recon image
        # recon text
        self.recon_text = dmd.HDTextLayer(400,
                                        680,
                                        self.game.fonts['default'],
                                        "left",
                                        vert_justify="center",
                                        line_color=(255,255,255),
                                        line_width=0,
                                        interior_color=(255,255,255))
        self.recon_text.set_text("3 MORE DRONES FOR WAR MACHINE")

        self.last_num_players = 0
        self.last_player_idx = 0
        self.last_score = 0
        self.last_ball_num = -1

        # set up the backdrop
        self.set_backdrop()
        # set up the layers
        self.set_layers_list()

    def set_backdrop(self):
        players = len(self.game.players)
        if players <= 1:
            backdrop = "1p_score_backdrop"
        elif players == 2:
            backdrop = "2p_score_backdrop"
        elif players == 3:
            backdrop = "3p_score_backdrop"
        else:
            backdrop = "4p_score_backdrop"

        self.backdrop_layer = dmd.FrameLayer(frame=self.game.animations[backdrop].frames[0])

    def set_layers_list(self):
        print "Doing set layers list"
        my_layers = [self.backdrop_layer,
                             self.main_score,
                             self.switches,
                             self.ramps,
                             self.duration,
                             self.warnings,
                             self.extra_balls,
                             self.recon_text]
        players = len(self.game.players)
        print "Players is now " + str(players)
        if players <= 1:
            # set the position of main score
            self.main_score.set_target_position(1125,310)
            self.main_score.y = 310
            self.p1_score.set_target_position(200,100)
            self.p1_score.x = 200
            my_layers.append(self.p1_score)
        elif players == 2:
            # set the position of the main score
            self.main_score.set_target_position(1125,370)
            self.main_score.y = 370
            # set the position of p1 score
            self.p1_score.set_target_position(497,100)
            self.p1_score.x = 497
            self.p2_score.set_target_position(1422,100)
            self.p2_score.x = 1422
            my_layers.append(self.p1_score)
            my_layers.append(self.p2_score)
        elif players == 3:
            self.main_score.set_target_position(1125,370)
            self.main_score.y = 370
            self.p1_score.set_target_position(343,100)
            self.p1_score.x = 343
            self.p2_score.set_target_position(960,100)
            self.p2_score.x = 960
            self.p3_score.set_target_position(1578,100)
            self.p3_score.x = 1578
            my_layers.append(self.p1_score),
            my_layers.append(self.p2_score),
            my_layers.append(self.p3_score)
        else:
            self.main_score.set_target_position(1125,370)
            self.main_score.y = 370
            self.p1_score.set_target_position(266,100)
            self.p1_score.x = 266
            self.p2_score.set_target_position(738,100)
            self.p2_score.x = 738
            self.p3_score.set_target_position(1200,100)
            my_layers.append(self.p1_score),
            my_layers.append(self.p2_score),
            my_layers.append(self.p3_score),
            my_layers.append(self.p4_score)

        self.layer.layers = my_layers

    def format_score(self, score):
        """Returns a string representation of the given score value.
        Override to customize the display of numeric score values."""
        if score == 0:
            return '00'
        else:
            return locale.format("%d", score, True)


    def update_layer(self):
        """Called by the layer to update the score layer for the present game state."""

        if (self.score_muted):
            return

            # check if we have any changes before we go on...
        # note, self.game.ball == 0 indicates no game in play; set to -1
        # to ensure the layer is updated once when first launched
        updates_needed = (self.last_ball_num != self.game.ball) or \
                         (self.game.current_player() is not None) and \
                         ((self.last_num_players != len(self.game.players)) \
                          or (self.last_player_idx != self.game.current_player_index) \
                          or (self.last_score != self.game.current_player().score))

        if (not updates_needed):
            return

        # if player count has changed, reset the stuff
        if len(self.game.players) > self.last_num_players:
            self.set_backdrop()
            self.set_layers_list()

        if self.game.current_player() == None:
            active_score = 0  # Small hack to make *something* show up on startup.
        else:
            active_score = self.game.current_player().score

        current_ball = "BALL " + str(self.game.ball)
        # set the main score window to the active score
        self.main_score.set_text(self.format_score(active_score))

        for i in range(len(self.game.players[:4])):  # Limit to first 4 players for now.
            if self.game.current_player_index == i:
                self.score_layers[i].set_text("PLAYER " + str(i + 1))
            else:
                score = self.game.players[i].score
                self.score_layers[i].set_text(self.format_score(score))


        # record these changes for next time
        self.last_ball_num = self.game.ball
        self.last_num_players = len(self.game.players)
        self.last_player_idx = self.game.current_player_index
        self.last_score = 0

        if (self.game.current_player() is not None):
            self.last_score = self.game.current_player().score


    def mute_score(self, muted):
        self.score_muted = muted
        self.single_player_layers.enabled = not (muted)
        self.multiplayer_layers.enabled = not (muted)


    def mode_started(self):
        pass


    def mode_stopped(self):
        pass
