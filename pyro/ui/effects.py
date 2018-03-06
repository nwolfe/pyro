import abc
import libtcodpy as libtcod
from pyro.engine.element import Elements
from pyro.engine import Event


def add_effects(effects, event):
    if Event.TYPE_HIT == event.type:
        effects.append(HitEffect(event.actor))
    elif Event.TYPE_HEAL == event.type:
        effects.append(HealEffect(event.actor))
    elif Event.TYPE_CONFUSE == event.type:
        effects.append(ConfuseEffect(event.actor))
    elif Event.TYPE_BOLT == event.type:
        effects.append(BoltEffect(event.position, event.element))


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
        # TODO are we accidentally skipping frame 0?
        self._frame = 0

    def update(self, game):
        # TODO are we accidentally skipping frame 0?
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


_ELEMENTS = {
    Elements.LIGHTNING: [['*'], [libtcod.blue]],
    Elements.FIRE:      [['o'], [libtcod.red]]
}


class BoltEffect(PositionEffect):
    def __init__(self, position, element):
        PositionEffect.__init__(self, position)
        self._element = _ELEMENTS[element]

    def num_frames(self):
        return 2

    def char(self, frame):
        chars = self._element[0]
        return chars[frame % len(chars)]

    def color(self, frame):
        colors = self._element[1]
        return colors[frame % len(colors)]


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


