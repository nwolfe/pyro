from pyro.component import Component
from pyro.components import Movement


class Projectile(Component):
    def __init__(self, source, on_hit_fn):
        Component.__init__(self, component_type=Projectile)
        self.source = source
        self.on_hit_fn = on_hit_fn

    def set_owner(self, game_object):
        Component.set_owner(self, game_object)
        game_object.x = self.source.x
        game_object.y = self.source.y

    def destroy(self):
        self.owner.remove_from_game()

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
            self.owner.component(Movement).move_astar(
                self.target.x, self.target.y, passthrough=True)


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
            self.owner.component(Movement).move_astar(
                self.target_x, self.target_y, passthrough=True)
