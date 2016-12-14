import libtcodpy as libtcod
import pyro.components.ai as libai
import pyro.components.fighter as libfighter
import pyro.components.spellcaster as libcast


class AggressiveSpellcaster(libai.AI):
    def take_turn(self):
        monster = self.owner
        player = monster.game.player
        if libtcod.map_is_in_fov(monster.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if not monster.component(libcast.Spellcaster).in_range(player):
                monster.move_astar(player)

            # Close enough, attack! (If the player is still alive)
            elif player.component(libfighter.Fighter).hp > 0:
                monster.component(libcast.Spellcaster).cast_spell([player])
