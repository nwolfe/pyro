import tcod as libtcod


class Effect:
    def __init__(self):
        pass

    def update(self, game):
        pass

    def render(self, game, ui):
        pass


class HitEffect(Effect):
    def __init__(self, actor):
        Effect.__init__(self)
        self.actor = actor
        self.frame = 0

    def update(self, game):
        self.frame += 1
        return self.frame < 23

    def render(self, game, ui):
        libtcod.console_set_default_foreground(ui.console, libtcod.red)
        libtcod.console_put_char(ui.console, self.actor.pos.x, self.actor.pos.y, '-', libtcod.BKGND_NONE)


class BoltEffect(Effect):
    def __init__(self):
        Effect.__init__(self)
