import logging
import procgame
import procgame.game
import procgame.dmd
from procgame.game import SkeletonGame
from procgame import *
import os
from procgame.modes import Attract
from procgame.game.skeletongame import run_proc_game

import my_modes
from my_modes import BaseGameMode
from my_modes import Ramps
from my_modes import IronmanTargets
from my_modes import Shields
from my_modes import Drones
from my_modes import Whiplash
from my_modes import Pops
from my_modes import Marks
from my_modes import WarMachine
from my_modes import IronMonger
from my_modes import SwitchFilter
from my_modes import Bogey

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s -%(levelname)s - %(message)s")
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))

logging.getLogger('game.driver').setLevel(logging.INFO)
logging.getLogger('game.vdriver').setLevel(logging.INFO)

class IMGame(SkeletonGame):
    def __init__(self):
        # required definitions
        self.curr_file_path = curr_file_path
        self.trough_count = 4
        
        super(IMGame, self).__init__('config/im_machine.yaml',self.curr_file_path)
       
        self.base_game_mode = BaseGameMode(game=self) # pri 5
        self.ramps = Ramps(game=self) # pri 10
        self.im_targets = IronmanTargets(game=self) # pri 10
        self.shields = Shields(game=self) # pri 10
        self.drones = Drones(game=self) # pri 10
        self.whiplash = Whiplash(game=self) # pri 10
        self.pops = Pops(game=self) # pri 10
        self.warmachine = WarMachine(game=self) # pri 10
        self.monger = IronMonger(game=self)

        self.bogey = Bogey(game=self) # pri 15
        self.mark = Marks(game=self) # pri 10

        self.switch_filter = SwitchFilter(game=self) # pri 900


        self.reset()


    def reset(self):
        # reset the monger toy?
        super(IMGame,self).reset()
        self.start_attract_mode()

## the following just set things up such that you can run Python ExampleGame.py
## and it will create an instance of the correct game objct and start running it!

if __name__ == '__main__':
    # change T2Game to be the class defined in this file!
    run_proc_game(IMGame)

