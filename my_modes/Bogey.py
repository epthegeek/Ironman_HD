import procgame.game
from procgame.game import AdvancedMode
from procgame import dmd

import pygame
from pygame.locals import *
from pygame.font import *

class Bogey(procgame.game.AdvancedMode):

    def __init__(self,game):
        super(Bogey, self).__init__(game=game, priority=12,mode_type=AdvancedMode.Manual)
        self.myID = "Bogey"
        self.running = False
        self.bogey_lamps = [self.game.lamps['leftRamp100k'],
                            self.game.lamps['leftRamp200k'],
                            self.game.lamps['leftRamp300k'],
                            self.game.lamps['leftRamp400k'],
                            self.game.lamps['rightRamp100k'],
                            self.game.lamps['rightRamp200k'],
                            self.game.lamps['rightRamp300k'],
                            self.game.lamps['rightRamp400k'],
                            self.game.lamps['leftOrbitArrow'],
                            self.game.lamps['leftRampArrow'],
                            self.game.lamps['rightRampArrow'],
                            self.game.lamps['rightOrbitArrow']]
        self.bogey_clips = ['bogey_hit_1',
                            'bogey_hit_2',
                            'bogey_hit_3',
                            'bogey_hit_4',
                            'bogey_hit_5',
                            'bogey_hit_6',
                            'bogey_hit_7',
                            'bogey_hit_8',
                            'bogey_hit_9',
                            'bogey_hit_10',
                            'bogey_hit_11',
                            'bogey_hit_12',
                            'bogey_hit_13',
                            'bogey_hit_14',
                            'bogey_hit_15',
                            'bogey_hit_16',
                            'bogey_hit_17',
                            'bogey_hit_18',
                            'bogey_hit_19',]
        back = dmd.FrameLayer(opaque=True,frame=self.game.animations['bogey_backdrop'].frames[0])
        top1 = dmd.HDTextLayer(930,110,self.game.fonts['bebas180'],"center",line_color=[64,64,64],line_width=6, interior_color=[192,192,192])
        top1.set_text("WE'VE")
        top2 = dmd.HDTextLayer(930,285,self.game.fonts['bebas180'],"center", line_color=[64,64,64],line_width=6, interior_color=[192,192,192])
        top2.set_text("GOT  A")
        top3 = dmd.HDTextLayer(930, 460, self.game.fonts['bebas180'], "center", line_color=[64, 64, 64], line_width=6,interior_color=[192, 192, 192])
        top3.set_text("BOGEY")
        self.timer_layer = dmd.HDTextLayer(1800,110,self.game.fonts['bebas500'],"right",line_color=[64,64,64],line_width=4,interior_color=[192,192,192])
        bottom1 = dmd.HDTextLayer(930,110,self.game.fonts['bebas180'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        bottom1.set_text("SHOOT")
        bottom2 = dmd.HDTextLayer(930,285,self.game.fonts['bebas180'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        bottom2.set_text("LIT")
        bottom3 = dmd.HDTextLayer(930,460,self.game.fonts['bebas180'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        bottom3.set_text("ARROWS")
        page1 = dmd.GroupedLayer(1920,800,[back,top1,top2,top3,self.timer_layer])
        page2 = dmd.GroupedLayer(1920,800,[back,top2,top3,self.timer_layer])
        page3 = dmd.GroupedLayer(1920,800,[back,top3,self.timer_layer])
        page4 = dmd.GroupedLayer(1920,800,[back,self.timer_layer])
        page5 = dmd.GroupedLayer(1920,800,[back,bottom1,self.timer_layer])
        page6 = dmd.GroupedLayer(1920,800,[back,bottom1,bottom2,self.timer_layer])
        page7 = dmd.GroupedLayer(1920,800,[back,bottom1,bottom2,bottom3,self.timer_layer])
        page8 = dmd.GroupedLayer(1920,800,[back,bottom2,bottom3,self.timer_layer])
        page9 = dmd.GroupedLayer(1920,800,[back,bottom3,self.timer_layer])
        page10 = dmd.GroupedLayer(1920,800,[back,top1,self.timer_layer])
        page11 = dmd.GroupedLayer(1920,800,[back,top1,top2,self.timer_layer])
        self.main_layer = dmd.ScriptedLayer(1920,800,[{'seconds':1, 'layer':page1},
                                                      {'seconds': 0.2, 'layer': page2},
                                                      {'seconds': 0.2, 'layer': page3},
                                                      {'seconds': 0.5, 'layer': page4},
                                                      {'seconds': 0.2, 'layer': page5},
                                                      {'seconds': 0.2, 'layer': page6},
                                                      {'seconds': 1, 'layer': page7},
                                                      {'seconds': 0.2, 'layer': page8},
                                                      {'seconds': 0.2, 'layer': page9},
                                                      {'seconds': 0.5, 'layer': page4},
                                                      {'seconds': 0.2, 'layer': page10},
                                                      {'seconds': 0.2, 'layer': page11}])
        self.bogey_award_text = dmd.HDTextLayer(1920/2,150,self.game.fonts['default'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        self.bogey_award_score = dmd.HDTextLayer(1920/2,300,self.game.fonts['main_score'],"center",line_color=[64,64,0],line_width=6,interior_color=[192,192,0])
        self.bogey_award_score_dim = dmd.HDTextLayer(1920/2,300,self.game.fonts['main_score'],"center",line_color=[16,16,0],line_width=6,interior_color=[64,64,0])
        self.flash_text = dmd.ScriptedLayer(1920,800,[{'seconds':0.2,'layer':self.bogey_award_score},{'seconds':0.2,'layer':self.bogey_award_score_dim}])

    def evt_ball_starting(self):
        self.wipe_delays()


    def mode_started(self):
        self.running = True
        # set the timer value TODO: adust for settings later
        self.timer_value = 41
        # set the point value
        self.point_value = 500000
        self.running = True
        # tally the shots
        self.shots = 0
        self.clip_index = 0
        self.total = 0
        # flash the arrows and ramps
        self.update_lamps()
        # change the music
        self.game.base.set_music()
        # play the audio bit

        self.start_bogey_display()
        # update the lamps
        self.update_lamps()

    def mode_stopped(self):
        self.running = False

    def evt_ball_ending(self,(shoot_again,last_ball)):
        if self.running:
            self.end_bogey()

    def sw_leftRampExit_active(self, sw):
        self.bogey_hit()
        return procgame.game.SwitchStop

    def sw_rightRampExit_active(self, sw):
        self.bogey_hit()
        return procgame.game.SwitchStop

    def start_bogey_display(self):
        # do the display
        anim = self.game.animations['bogey_start_movie']
        anim.reset()
        text = dmd.HDTextLayer(1920/2,20,self.game.fonts['default'],"center",line_color=[32,32,0],line_width=4,interior_color=[255,0,0])
        text.set_text("BOGEY SPOTTED")
        text.blink_frames = 8
        text.blink_frames_counter = 8
        self.layer = dmd.GroupedLayer(1920,800,[anim,text])
        if self.game.mark.player_mark < 6:
            self.game.mark.player_mark += 1
            self.game.mark.score()
            self.delay("display",delay=3,handler=self.game.mark.completed,param=self.get_going)
        else:
            self.delay("display",delay=3,handler=self.get_going)
        # start the timer in 3 seconds regardless fo what the display is doing
        self.delay(delay=3,handler=self.timer)

    def get_going(self):
        self.mode_display()

    def bogey_hit(self):
        self.cancel_delayed("display")
        self.add_text("")
        # score the points
        points = self.point_value
        self.game.score(points)
        self.total += points
        # count the shot
        self.shots += 1
        # increase the value if needed
        self.increase_point_value()
        # sounds and whatnot
        # Do the display
        # reset the anim layer
        anim = self.game.animations[self.bogey_clips[self.clip_index]]
        anim.reset()
        self.increase_index()
        self.layer = dmd.GroupedLayer(1920,800,[anim,self.bogey_award_text,self.flash_text])
        # clear after time
        self.delay("display",delay = 3,handler=self.mode_display)
        self.delay("display",delay = 1.4,handler=self.add_text,param=self.game.score_display.format_score(points))

    def increase_index(self):
        if self.clip_index < 18:
            self.clip_index += 1

    def timer(self):
        if self.timer_value >= 1:
            self.timer_value -= 1
            if self.timer_value <= 9:
                string = "0" + str(self.timer_value)
            else:
                string = str(self.timer_value)
            self.timer_layer.set_text(":" + string)
            if self.timer_value > 0:
                self.delay("timer",delay=1,handler=self.timer)
            else:
                self.delay("timer",delay=1,handler=self.end_bogey)
        else:
            pass

    def add_time(self):
        # just in case it's the last second - cancel the delay to avoid ending
        self.cancel_delayed("timer")
        # adding 20 seconds to the timer
        self.timer_value += 20
        # schedule new timer delay
        self.delay(delay=1,handler=self.timer)

    def end_bogey(self):
        self.game.ramps.ramp_stage = [0,0]
        bg = self.game.animations['bright_clouds']
        text = dmd.HDTextLayer(1920/2,50,self.game.fonts['default'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        text.set_text("WE'VE GOT A BOGEY")
        text2 = dmd.HDTextLayer(1920/2,175,self.game.fonts['default'],"center",line_color=[64,0,0],line_width=6,interior_color=[192,0,0])
        text2.set_text("TOTAL:")
        score = dmd.HDTextLayer(1920/2,325,self.game.fonts['main_score'],"center",line_color=[64,64,0],line_width=6,interior_color=[192,192,0])
        score.set_text(self.game.score_display.format_score(self.total))
        self.layer = dmd.GroupedLayer(1920,800,[bg,text,text2,score])
        self.running = False
        # reset the ramps status
        self.game.ramps.bogey_status = "OPEN"
        self.game.base.set_music()
        self.delay(delay=3,handler=self.unload)
        # update the ramp lamps
        self.game.ramps.update_lamps()

    def mode_display(self):
        self.layer = self.main_layer

    def increase_point_value(self):
        # if we're not at a million
        if self.point_value < 1000000:
            # increase by 100k
            self.point_value += 100000

    def add_text(self,points):
        if points == "":
            title = ""
        else:
            title = "BOGEY AWARD"
        self.bogey_award_text.set_text(title)
        self.bogey_award_score.set_text(str(points))
        self.bogey_award_score_dim.set_text(str(points))

    def update_lamps(self):
        self.bogey_lamps[0].schedule(0X000F000F)
        self.bogey_lamps[1].schedule(0x00F000F0)
        self.bogey_lamps[2].schedule(0x0F000F00)
        self.bogey_lamps[3].schedule(0xF000F000)

        self.bogey_lamps[4].schedule(0X000F000F)
        self.bogey_lamps[5].schedule(0x00F000F0)
        self.bogey_lamps[6].schedule(0x0F000F00)
        self.bogey_lamps[7].schedule(0xF000F000)

        self.bogey_lamps[8].schedule(0x00FF00FF)
        self.bogey_lamps[9].schedule(0x00FF00FF)
        self.bogey_lamps[10].schedule(0x00FF00FF)
        self.bogey_lamps[11].schedule(0x00FF00FF)

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
