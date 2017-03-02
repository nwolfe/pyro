

class Spell:
    def __init__(self, name, spell_range, strength):
        self.name = name
        self.range = spell_range
        self.strength = strength

    def configure(self, settings):
        self.range = settings.get('range', self.range)
        self.strength = settings.get('strength', self.strength)

    def configure_monster_defaults(self):
        pass

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass
