

class SpellType:
    ATTACK = 'attack'
    HEAL = 'heal'


class Spell:
    def __init__(self, name, spell_type):
        self.name = name
        self.type = spell_type

    def configure(self, settings):
        pass

    def in_range(self, caster, target):
        pass

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass
