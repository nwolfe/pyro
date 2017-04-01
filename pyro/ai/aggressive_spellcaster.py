import tcod as libtcod
from pyro.components import AI, Spellcaster, Fighter, Movement
from pyro.spell import SpellType


class AggressiveSpellcaster(AI):
    def take_turn(self):
        monster = self.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Heal yourself if damaged
            if monster.component(Fighter).hp < monster.component(Fighter).max_hp():
                heals = self.owner.component(Spellcaster).get_spells(SpellType.HEAL)
                if len(heals) > 0:
                    self.owner.component(Spellcaster).cast_spell(heals[0], self.owner)
                    return

            # Move towards player if far away
            if not monster.component(Spellcaster).in_range(player, SpellType.ATTACK):
                movement = monster.component(Movement)
                if movement:
                    movement.move_astar(player.pos.x, player.pos.y)

            # Close enough, attack! (If the player is still alive)
            elif player.component(Fighter).hp > 0:
                attacks = self.owner.component(Spellcaster).get_spells(SpellType.ATTACK)
                if len(attacks) > 0:
                    random_attack = attacks[libtcod.random_get_int(0, 0, len(attacks)-1)]
                    self.owner.component(Spellcaster).cast_spell(random_attack, player)
