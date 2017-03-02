

class Spell:
    def __init__(self, name):
        self.name = name

    def configure(self, settings):
        pass

    def configure_monster_defaults(self):
        pass

    def in_range(self, caster, target):
        pass

    def cast(self, caster, target):
        pass

    def player_cast(self, player, game, ui):
        pass
