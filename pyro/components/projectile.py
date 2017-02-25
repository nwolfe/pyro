from pyro.component import Component


class Projectile(Component):
    def __init__(self, source, on_hit_fn):
        Component.__init__(self)
        self.source = source
        self.on_hit_fn = on_hit_fn

    def initialize(self, owner):
        Component.initialize(self, owner)
        owner.x = self.source.x
        owner.y = self.source.y

    def destroy(self):
        self.owner.game.objects.remove(self.owner)

    def tick(self):
        pass


class TargetProjectile(Projectile):
    def __init__(self, source, target, on_hit_fn):
        Projectile.__init__(self, source, on_hit_fn)
        self.target = target

    def tick(self):
        if self.owner.x == self.target.x and self.owner.y == self.target.y:
            self.on_hit_fn(self.source, self.target)
            self.destroy()
        else:
            self.owner.move_astar(self.target.x, self.target.y, passthrough=True)


class PositionProjectile(Projectile):
    def __init__(self, source, target_x, target_y, on_hit_fn):
        Projectile.__init__(self, source, on_hit_fn)
        self.target_x = target_x
        self.target_y = target_y

    def tick(self):
        if self.owner.x == self.target_x and self.owner.y == self.target_y:
            self.on_hit_fn(self.source, self.target_x, self.target_y)
            self.destroy()
        else:
            self.owner.move_astar(self.target_x, self.target_y, passthrough=True)
