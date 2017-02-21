from pyro.component import Component


class Projectile(Component):
    def __init__(self, source, target, on_hit_fn):
        Component.__init__(self)
        self.source = source
        self.target = target
        self.on_hit_fn = on_hit_fn

    def initialize(self, owner):
        Component.initialize(self, owner)
        owner.x = self.source.x
        owner.y = self.source.y

    def tick(self):
        if self.owner.x == self.target.x and self.owner.y == self.target.y:
            self.on_hit_fn(self.target)
            self.owner.game.objects.remove(self.owner)
        else:
            self.owner.move_astar(self.target, passthrough=True)
