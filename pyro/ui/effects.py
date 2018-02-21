import abc
import tcod as libtcod


class Effect:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update(self, game):
        pass

    @abc.abstractmethod
    def render(self, game, ui):
        pass


class HitEffect(Effect):
    def __init__(self, actor):
        Effect.__init__(self)
        self.actor = actor
        self.frame = 0

    def update(self, game):
        self.frame += 1
        return self.frame < 4

    def render(self, game, ui):
        x, y = self.actor.pos.x, self.actor.pos.y
        libtcod.console_set_default_foreground(ui.console, libtcod.dark_red)
        libtcod.console_put_char(ui.console, x, y, '*', libtcod.BKGND_NONE)


class HealEffect(Effect):
    def __init__(self, actor):
        Effect.__init__(self)
        self._actor = actor
        self._frame = 0

    def update(self, game):
        self._frame += 1
        return self._frame < 8

    def render(self, game, ui):
        # Alternate between white and green for a cool visual effect
        if self._frame <= 2:
            color = libtcod.white
        elif self._frame <= 4:
            color = libtcod.green
        elif self._frame <= 6:
            color = libtcod.white
        else:
            color = libtcod.green

        x, y = self._actor.pos.x, self._actor.pos.y
        libtcod.console_set_default_foreground(ui.console, color)
        libtcod.console_put_char(ui.console, x, y, '+', libtcod.BKGND_NONE)


class BoltEffect(Effect):
    def __init__(self):
        Effect.__init__(self)
