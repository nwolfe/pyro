

class Target:
    def __init__(self, actor=None, position=None):
        self.actor = actor
        self.position = position

    @property
    def pos(self):
        if self.actor:
            return self.actor.pos
        else:
            return self.position
