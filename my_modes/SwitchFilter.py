import procgame.game
from procgame.game import AdvancedMode

import pygame
from pygame.locals import *
from pygame.font import *

class SwitchFilter(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(SwitchFilter, self).__init__(game=game, priority=900, mode_type=AdvancedMode.Game)
        self.myID = "SwitchFilter"

        # add the rules for any switch tagged bonus
        for sw in self.game.switches.items_tagged('Bonus'):
            self.add_switch_handler(name=sw.name, event_type="active", delay=None,handler=self.register)
        # all the switches have default point values that get added to any game scoring
        self.point_values ={'leftTargetI':1130,
                           'leftTargetR':1130,
                           'leftTargetO':1130,
                           'leftTargetN':1130,
                           'rightTargetM':1130,
                           'rightTargetA':1130,
                           'rightTargetN':1130,
                           'rightReturnLane':1090,
                           'leftReturnLane':1090,
                           'topRightLane':2560,
                           'topLeftLane':2560,
                            'rightOutLane':10000,
                            'leftOutLane':10000,
                            'droneTarget0':1110,
                            'droneTarget1':1110,
                            'droneTarget2':1110,
                            'droneTarget3':1110,
                            'leftRampEnter':560,
                            'rightRampEnter':560,
                            'leftRampExit':1170,
                            'rightRampExit':1170,
                            'rightSpinner':2590,
                            'leftSpinner':2590,
                            'centerSpinner':2590,
                            'leftSlingshot':440,
                            'rightSlingshot':440,
                            'rightOrbit':1220,
                            'leftOrbit':1220,
                            'leftJetBumper':170,
                            'rightJetBumper':170,
                            'bottomJetBumper':170,
                            'warMachineOpto':1510,
                            'whiplashLeft':1080,
                            'whiplashRight':1080}


    # at ball start, set the last switch and total switches to blanks
    def evt_ball_starting(self):
        self.last_switch = None
        self.total = 0

    def register(self,sw):
        # count the switch
        self.total += 1
        # score default points for the switch if there are any
        if self.point_values[sw.name]:
            self.game.score(self.point_values[sw.name])
            # if fast scoring is running, score the point value per switch also
            if self.game.fast_scoring.running:
                self.game.fast_scoring.switch_hit()
        # set the last hit switch
        self.last_switch = sw.name
