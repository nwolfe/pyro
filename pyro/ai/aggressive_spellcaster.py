import tcod as libtcod
import pyro.astar
from pyro.components import AI, Spellcaster
from pyro.spell import SpellType
from pyro.engine.actions import WalkAction


class AggressiveSpellcaster(AI):
    def take_turn(self, action):
        monster = self.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Heal yourself if damaged
            if monster.actor.hp < monster.actor.max_hp:
                heals = self.owner.component(Spellcaster).get_spells(SpellType.HEAL)
                if len(heals) > 0:
                    self.owner.component(Spellcaster).cast_spell(action, heals[0], self.owner)
                    return

            # Move towards player if far away
            if not monster.component(Spellcaster).in_range(player, SpellType.ATTACK):
                direction = pyro.astar.astar(self.owner.game, monster.pos, player.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif player.actor.hp > 0:
                attacks = self.owner.component(Spellcaster).get_spells(SpellType.ATTACK)
                if len(attacks) > 0:
                    random_attack = attacks[libtcod.random_get_int(0, 0, len(attacks)-1)]
                    self.owner.component(Spellcaster).cast_spell(action, random_attack, player)
