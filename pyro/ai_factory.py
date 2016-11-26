from components.ais.aggressive import *
from components.ais.aggressive_spellcaster import *
from components.ais.passive_aggressive import *
from components.ais.confused import *


def aggressive():
    return Aggressive()


def aggressive_spellcaster():
    return AggressiveSpellcaster()


def passive_aggressive():
    return PassiveAggressive()


def confused():
    return Confused()
