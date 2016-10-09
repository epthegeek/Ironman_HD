import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *
import random
from procgame import dmd

class Bonus(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Bonus, self).__init__(game=game, priority=51,mode_type=AdvancedMode.Manual)
        self.myID = "Bonus Tally"
        # background image
        self.top_line = dmd.HDTextLayer(1920 / 2, 20, self.game.fonts['default'], "center", line_color=(0, 0, 0), line_width=3,interior_color=(224, 224, 224))
        self.points_line = dmd.HDTextLayer(1920 / 2, 200, self.game.fonts['main_score'], "center", line_color=(0, 0, 0), line_width=6,interior_color=(224, 128, 32))
        backdrop = self.game.animations['bonus_backdrop']
        self.combined = dmd.GroupedLayer(1920,800, [backdrop, self.top_line, self.points_line], opaque = True)

    def mode_started(self):
        # set the top line to bonus with bonus x
        if self.game.base.bonus_x > 1:
            multiplier = " " + str(self.game.base.bonus_x) + "X"
        else:
            multiplier = ""
        self.top_line.set_text("BONUS" + multiplier)
        # figure out 1/20th of the bonus total and set the points to that
        # bonus is 125k * ball + switches total * 670
        self.bonus_total = ((125000 * self.game.ball) + (self.game.switch_filter.total * 670))
        self.increment = self.bonus_total // 20
        self.partial_total = self.increment
        self.points_line.set_text(self.game.score_display.format_score(self.increment))
        # start the music
        self.game.sound.play_music('bonus')
        # set the layer
        self.layer = self.combined
        # start the count up of the numbers
        self.counter = 0
        self.count_up()

    def count_up(self):
        self.partial_total += self.increment
        self.points_line.set_text(self.game.score_display.format_score(self.partial_total))
        self.counter += 1
        if self.counter == 19:
            self.finish_up()
        else:
            self.delay(delay=0.1,handler=self.count_up)

    def finish_up(self):
        # play the chord
        self.game.sound.play('bonus_chord')
        # stop the music
        self.game.sound.stop_music()
        # change the title line
        self.top_line.set_text("BONUS TOTAL:")
        # change the points total
        points = (self.bonus_total * self.game.base.bonus_x)
        self.game.score(points)
        self.points_line.set_text(self.game.score_display.format_score(points))
        # delay for a bit, then close out
        self.delay(delay = 2,handler=self.shutdown)

    def shutdown(self):
        self.game.base.force_event_next()
        self.unload()


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
