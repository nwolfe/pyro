from pyro.components import AI, Fighter


class Aggressive(AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self, action):
        monster = self.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Move towards player if far away
            if monster.pos.distance_to(player.pos) >= 2:
                self.move_astar(player)

            # Close enough, attack! (If the player is still alive)
            elif player.component(Fighter).hp > 0:
                monster.component(Fighter).attack(action, player)
