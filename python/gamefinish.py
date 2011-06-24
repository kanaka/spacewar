"gamefinish handler. just lets our stars trickle"

import pygame
import gfx, var, snd


class GameFinish:
    def __init__(self, prevhandler):
        self.prevhandler = prevhandler
        self.ticks = 17
        self.started = 0

    def input(self, i):
        pass

    def event(self, e):
        pass

    def run(self):
        gfx.updatestars(self.background, gfx)
        self.ticks -= 1
        if not self.started:
            self.started = 1
            if snd.music:
                snd.music.fadeout(15*var.clockticks)

        if not self.ticks:
            gfx.surface.fill(0)
            pygame.display.update()
            #pygame.time.delay(200)
            var.handler = self.prevhandler

    def background(self, area):
        return gfx.surface.fill((0, 0, 0), area)

