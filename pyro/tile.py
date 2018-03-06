from collections import namedtuple
import libtcodpy as libtcod
from pyro.engine.glyph import glyph
from pyro.settings import COLOR_LIGHT_GROUND, COLOR_DARK_GROUND, COLOR_LIGHT_WALL, COLOR_DARK_WALL, COLOR_LIGHT_GRASS


_Appearance = namedtuple('Appearance', 'lit unlit')


class _TileType:
    FLOOR = None
    WALL = None
    STAIRS = None
    TALL_GRASS = None
    CRUSHED_GRASS = None
    OPEN_DOOR = None
    CLOSED_DOOR = None
    def __init__(self, appearance, passable, transparent, is_exit=False, always_visible=False):
        self.appearance = appearance
        self.passable = passable
        self.transparent = transparent
        self.is_exit = is_exit
        self.always_visible = always_visible
        self.opens_to = None
        self.closes_to = None
        self.steps_to = None


def _open_tile(lit, unlit):
    """A passable, transparent tile"""
    return _TileType(_Appearance(lit, unlit), passable=True, transparent=True)


def _solid_tile(lit, unlit):
    """"An impassable, opaque tile"""
    return _TileType(_Appearance(lit, unlit), passable=False, transparent=False)


def _fog_tile(lit, unlit):
    """"A passable, opaque tile"""
    return _TileType(_Appearance(lit, unlit), passable=True, transparent=False)


def _exit_tile(lit, unlit):
    """A passable, transparent tile marked as an exit"""
    return _TileType(_Appearance(lit, unlit), passable=True, transparent=True, is_exit=True, always_visible=True)


class Tile:
    TYPE_FLOOR = _open_tile(glyph(None, COLOR_LIGHT_GROUND),
                            glyph(None, COLOR_DARK_GROUND))
    TYPE_WALL = _solid_tile(glyph(None, COLOR_LIGHT_WALL),
                            glyph(None, COLOR_DARK_WALL))
    TYPE_STAIRS = _exit_tile(glyph('>', libtcod.white, COLOR_LIGHT_GROUND),
                             glyph('>', libtcod.white, COLOR_DARK_GROUND))
    TYPE_CRUSHED_GRASS = _open_tile(glyph('.', libtcod.green, COLOR_LIGHT_GROUND),
                                    glyph('.', COLOR_DARK_GROUND))
    TYPE_TALL_GRASS = _fog_tile(glyph(':', libtcod.green, COLOR_LIGHT_GRASS),
                                glyph(':', COLOR_DARK_GROUND))
    TYPE_CLOSED_DOOR = _solid_tile(glyph('+', libtcod.white, COLOR_LIGHT_WALL),
                                   glyph('+', libtcod.white, COLOR_DARK_WALL))
    TYPE_OPEN_DOOR = _open_tile(glyph('-', libtcod.white, COLOR_LIGHT_GROUND),
                                glyph('-', libtcod.white, COLOR_DARK_GROUND))
    TYPE_TALL_GRASS.steps_to = TYPE_CRUSHED_GRASS
    TYPE_OPEN_DOOR.closes_to = TYPE_CLOSED_DOOR
    TYPE_CLOSED_DOOR.opens_to = TYPE_OPEN_DOOR

    def __init__(self):
        self.type = Tile.TYPE_WALL
        self.explored = False

    @property
    def passable(self):
        return self.type.passable

    @property
    def transparent(self):
        return self.type.transparent
