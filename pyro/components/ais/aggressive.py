import libtcodpy as libtcod
import components.ai as libai
import components.fighter as libfighter


class Aggressive(libai.AI):
    """Pursue and attack the player once in sight."""

    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(monster.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if monster.distance_to(monster.game.player) >= 2:
                monster.move_astar(monster.game.player)

            # Close enough, attack! (If the player is still alive)
            elif monster.game.player.component(libfighter.Fighter).hp > 0:
                monster.component(libfighter.Fighter).attack(monster.game.player)
