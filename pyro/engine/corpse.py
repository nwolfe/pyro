from collections import namedtuple
import libtcodpy as libtcod
from pyro.engine.glyph import glyph


Corpse = namedtuple('Corpse', 'type name pos')

_CorpseType = namedtuple('CorpseType', 'glyph')

_TYPE_MONSTER = _CorpseType(glyph('%', libtcod.dark_red))
_TYPE_HERO = _CorpseType(glyph('%', libtcod.dark_red))


def for_monster(monster):
    name = 'Remains of {0}'.format(monster.name)
    return Corpse(_TYPE_MONSTER, name, monster.pos)


def for_hero(hero):
    name = 'Remains of {0}'.format(hero.name)
    return Corpse(_TYPE_HERO, name, hero.pos)
