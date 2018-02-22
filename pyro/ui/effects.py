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


class ActorEffect(Effect):
    """Renders a colored character over the top of the actor."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, actor):
        self.actor = actor
        self._frame = 0

    def update(self, game):
        self._frame += 1
        return self._frame < self.num_frames()

    def render(self, game, ui):
        char = self.char(self._frame)
        color = self.color(self._frame)
        x, y = self.actor.pos.x, self.actor.pos.y
        libtcod.console_set_default_foreground(ui.console, color)
        libtcod.console_put_char(ui.console, x, y, char, libtcod.BKGND_NONE)

    @abc.abstractmethod
    def num_frames(self):
        pass

    @abc.abstractmethod
    def char(self, frame):
        pass

    @abc.abstractmethod
    def color(self, frame):
        pass


class HitEffect(ActorEffect):
    def num_frames(self):
        return 4

    def char(self, frame):
        return '*'

    def color(self, frame):
        return libtcod.dark_red


class HealEffect(ActorEffect):
    def num_frames(self):
        return 8

    def char(self, frame):
        return '+'

    def color(self, frame):
        # Alternate between white and green for a cool visual effect
        if frame <= 2:
            return libtcod.white
        elif frame <= 4:
            return libtcod.green
        elif frame <= 6:
            return libtcod.white
        else:
            return libtcod.green


class BoltEffect(Effect):
    def __init__(self):
        Effect.__init__(self)
