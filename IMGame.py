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
from my_modes import FastScoring
from my_modes import Shields
from my_modes import Drones
from my_modes import Whiplash
from my_modes import Pops
from my_modes import Marks
from my_modes import WarMachine
from my_modes import IronMonger
from my_modes import MongerToy
from my_modes import SwitchFilter
from my_modes import Bogey
from my_modes import MongerMultiball
from my_modes import WhiplashMultiball
from my_modes import WarMachineMultiball
from my_modes import Skillshot
from my_modes import MBSwitchStop

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s -%(levelname)s - %(message)s")
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))

logging.getLogger('game.driver').setLevel(logging.INFO)
logging.getLogger('game.vdriver').setLevel(logging.INFO)

class IMGame(SkeletonGame):
    def __init__(self):
        # required definitions
        self.curr_file_path = curr_file_path
        self.trough_count = 4
        self.giState = "OFF"
        
        super(IMGame, self).__init__('config/im_machine.yaml',self.curr_file_path)
       
        self.base = BaseGameMode(game=self) # pri 5

        self.fast_scoring = FastScoring(game=self) # pri 9

        self.pops = Pops(game=self) # pri 10
        self.ramps = Ramps(game=self) # pri 11
        self.shields = Shields(game=self) # pri 11

        self.bogey = Bogey(game=self) # pri 12

        self.im_targets = IronmanTargets(game=self) # pri 15
        self.drones = Drones(game=self) # pri 15
        self.whiplash = Whiplash(game=self) # pri 15

        self.warmachine = WarMachine(game=self) # pri 16

        self.monger = IronMonger(game=self) # pri 17

        self.monger_toy = MongerToy(game=self) # pri 20

        self.mb_switch_stop = MBSwitchStop(game=self) # pri 40

        self.mark = Marks(game=self) # pri 45

        self.whiplash_multiball = WhiplashMultiball(game=self) # pri 49
        self.wm_multiball = WarMachineMultiball(game=self) # pri 50
        self.monger_multiball = MongerMultiball(game=self) # pri 51

        self.skillshot = Skillshot(game=self)

        self.switch_filter = SwitchFilter(game=self) # pri 900


        self.reset()


    def reset(self):
        # reset the monger toy?
        super(IMGame,self).reset()
        # turn on the GI
        self.gi_control("ON")
        self.start_attract_mode()

    ## GI LAMPS

    def gi_control(self, state):
        if state == "OFF":
            self.giState = "OFF"
            self.lamps['playfieldGI'].disable()
        else:
            self.giState = "ON"
            self.lamps['playfieldGI'].enable()


## the following just set things up such that you can run Python ExampleGame.py
## and it will create an instance of the correct game objct and start running it!

if __name__ == '__main__':
    # change T2Game to be the class defined in this file!
    run_proc_game(IMGame)

