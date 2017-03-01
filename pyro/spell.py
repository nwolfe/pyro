

class Spell:
    def __init__(self, name, spell_range, strength):
        self.name = name
        self.range = spell_range
        self.strength = strength

    def initialize_monster(self):
        pass

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass
