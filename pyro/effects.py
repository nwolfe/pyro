

class Effect:
    def __init__(self):
        pass

    def update(self, game):
        pass

    def render(self, game, ui):
        pass


class BoltEffect(Effect):
    def __init__(self):
        Effect.__init__(self)


