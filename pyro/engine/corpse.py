import tcod as libtcod
from pyro.engine.glyph import Glyph


class CorpseType:
    MONSTER = None
    HERO = None
    def __init__(self, glyph):
        self.glyph = glyph

CorpseType.MONSTER = CorpseType(Glyph('%', libtcod.dark_red))
CorpseType.HERO = CorpseType(Glyph('%', libtcod.dark_red))


class Corpse:
    def __init__(self, type_, name, position):
        self.type = type_
        self.name = name
        self.pos = position


def for_monster(monster):
    name = 'Remains of {0}'.format(monster.name)
    return Corpse(CorpseType.MONSTER, name, monster.pos)


def for_hero(hero):
    name = 'Remains of {0}'.format(hero.name)
    return Corpse(CorpseType.HERO, name, hero.pos)
