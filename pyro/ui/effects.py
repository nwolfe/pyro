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


class PositionEffect(Effect):
    """Renders a colored character over the top of the position."""
    __metaclass__ = abc.ABCMeta

    def __init__(self, position):
        self._position = position
        self._frame = 0

    def update(self, game):
        self._frame += 1
        return self._frame < self.num_frames()

    def render(self, game, ui):
        char = self.char(self._frame)
        color = self.color(self._frame)
        x, y = self._position.x, self._position.y
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


class BoltEffect(PositionEffect):
    def num_frames(self):
        return 2

    def char(self, frame):
        return '*'

    def color(self, frame):
        return libtcod.blue


class HitEffect(PositionEffect):
    def __init__(self, target):
        PositionEffect.__init__(self, target.pos)

    def num_frames(self):
        return 4

    def char(self, frame):
        return '*'

    def color(self, frame):
        return libtcod.dark_red


class HealEffect(PositionEffect):
    def __init__(self, target):
        PositionEffect.__init__(self, target.pos)

    def num_frames(self):
        return 8

    def char(self, frame):
        return '+'

    def color(self, frame):
        # Alternate between white and green for a cool visual effect
        return [
            libtcod.white,
            libtcod.white,
            libtcod.green,
            libtcod.green,
            libtcod.white,
            libtcod.white,
            libtcod.green,
            libtcod.green,
        ][frame]


class ConfuseEffect(PositionEffect):
    def __init__(self, target):
        PositionEffect.__init__(self, target.pos)

    def num_frames(self):
        return 4

    def char(self, frame):
        return '?'

    def color(self, frame):
        return [
            libtcod.green,
            libtcod.white,
            libtcod.blue,
            libtcod.yellow,
        ][frame]


