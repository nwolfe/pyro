import pyro.astar
from pyro.components import AI
from pyro.engine.actions import AttackAction, WalkAction


class Aggressive(AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self, action):
        monster = self.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Move towards player if far away
            if monster.pos.distance_to(player.pos) >= 2:
                direction = pyro.astar.astar(self.owner.game, monster.pos, player.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif player.hp > 0:
                return AttackAction(player.actor)
