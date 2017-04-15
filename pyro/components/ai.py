import pyro.astar
from pyro.component import Component


class AI(Component):
    def __init__(self):
        Component.__init__(self, component_type=AI)

    def take_turn(self, action):
        """Perform a single game turn."""
        pass

    def move_astar(self, player):
        direction = pyro.astar.astar(self.owner.game, self.owner.pos, player.pos)
        self.move(direction)

    def move(self, direction):
        new_pos = self.owner.pos.plus(direction)
        if not self.owner.game.is_blocked(new_pos):
            self.owner.pos = new_pos
