import libtcodpy as libtcod
from pyro.components.ai import AI
from pyro.components.spellcaster import Spellcaster
from pyro.components.fighter import Fighter


class AggressiveSpellcaster(AI):
    def take_turn(self):
        monster = self.owner
        player = monster.game.player
        if libtcod.map_is_in_fov(monster.game.fov_map, monster.x, monster.y):
            # Move towards player if far away
            if not monster.component(Spellcaster).in_range(player):
                monster.move_astar(player)

            # Close enough, attack! (If the player is still alive)
            elif player.component(Fighter).hp > 0:
                monster.component(Spellcaster).cast_spell([player])
