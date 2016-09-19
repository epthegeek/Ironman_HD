import procgame.game
from procgame.game import Mode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random

class MBSwitchStop(procgame.game.Mode):

    def __init__(self,game):
        super(MBSwitchStop, self).__init__(game=game, priority=48)
        self.myID = "MBSwitchStop"