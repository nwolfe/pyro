from pyro.component import Component
from pyro.components import Movement


class Projectile(Component):
    def __init__(self, source, on_hit_fn):
        Component.__init__(self, component_type=Projectile)
        self.source = source
        self.on_hit_fn = on_hit_fn

    def set_owner(self, game_object):
        Component.set_owner(self, game_object)
        game_object.pos.x = self.source.pos.x
        game_object.pos.y = self.source.pos.y

    def destroy(self):
        self.owner.game.remove_object(self.owner)

    def tick(self):
        pass


class TargetProjectile(Projectile):
    def __init__(self, source, target, on_hit_fn):
        Projectile.__init__(self, source, on_hit_fn)
        self.target = target

    def tick(self):
        if self.owner.pos.equals(self.target.pos):
            self.on_hit_fn(self.source, self.target)
            self.destroy()
        else:
            self.owner.component(Movement).move_astar(
                self.target.pos.x, self.target.pos.y, passthrough=True)


class PositionProjectile(Projectile):
    def __init__(self, source, target_x, target_y, on_hit_fn):
        Projectile.__init__(self, source, on_hit_fn)
        self.target_x = target_x
        self.target_y = target_y

    def tick(self):
        if self.owner.pos.equal_to(self.target_x, self.target_y):
            self.on_hit_fn(self.source, self.target_x, self.target_y)
            self.destroy()
        else:
            self.owner.component(Movement).move_astar(
                self.target_x, self.target_y, passthrough=True)
