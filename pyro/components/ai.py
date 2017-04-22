import tcod as libtcod
import pyro.astar
import pyro.direction
from pyro.component import Component
from pyro.spell import SpellType
from pyro.engine.actions import AttackAction, WalkAction
from pyro.utilities import blocked
from pyro.settings import SPELL_CONFUSE_TURNS


def new(name, spells=None):
    if 'aggressive' == name:
        behavior = Aggressive()
    elif 'aggressive_spellcaster' == name:
        behavior = AggressiveSpellcaster()
    elif 'passive_aggressive' == name:
        behavior = PassiveAggressive()
    elif 'confused' == name:
        behavior = Confused()
    else:
        raise Exception('Unknown AI: {}'.format(name))
    return AI(behavior, spells)


class AI(Component):
    def __init__(self, behavior=None, spells=None):
        Component.__init__(self, component_type=AI)
        self.behavior = behavior
        if spells:
            self.__spells = {SpellType.ATTACK: [], SpellType.HEAL: []}
            for spell in spells:
                self.__spells[spell.type].append(spell)
        else:
            self.__spells = None

    def take_turn(self, action):
        """Perform a single game turn."""
        return self.behavior.take_turn(action, self)

    def confuse(self, num_turns):
        old_behavior = self.behavior
        self.behavior = Confused(old_behavior, num_turns)

    def get_spells(self, spell_type):
        return self.__spells[spell_type]

    def in_range(self, target, spell_type):
        for spell in self.__spells[spell_type]:
            if spell.in_range(self.owner, target):
                return True
        return False

    def cast_spell(self, action, spell, target):
        if SpellType.ATTACK == spell.type:
            # Only 40% chance to hit
            if libtcod.random_get_int(0, 1, 5) <= 2:
                damage = spell.cast(action, self.owner.actor, target)
                msg = 'The {0} strikes you with a {1}! You take {2} damage.'
                msg = msg.format(self.owner.name, spell.name, damage)
                self.owner.game.log.message('- ' + msg, libtcod.red)
            else:
                msg = 'The {0} casts a {1} but it fizzles!'
                msg = msg.format(self.owner.name, spell.name)
                self.owner.game.log.message(msg)
        elif SpellType.HEAL == spell.type:
            spell.cast(action, self.owner.actor, target)
            msg = 'The {0} heals itself!'.format(self.owner.name)
            self.owner.game.log.message(msg)


class BehaviorStrategy:
    def take_turn(self, action, ai):
        pass


class Aggressive(BehaviorStrategy):
    def take_turn(self, action, ai):
        monster = ai.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Move towards player if far away
            if monster.pos.distance_to(player.pos) >= 2:
                direction = pyro.astar.astar(ai.owner.game, monster.pos, player.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif player.hp > 0:
                return AttackAction(player)


class AggressiveSpellcaster(BehaviorStrategy):
    def take_turn(self, action, ai):
        monster = ai.owner
        player = monster.game.player
        if monster.game.map.is_in_fov(monster.pos.x, monster.pos.y):
            # Heal yourself if damaged
            if monster.actor.hp < monster.actor.max_hp:
                heals = ai.get_spells(SpellType.HEAL)
                if len(heals) > 0:
                    ai.cast_spell(action, heals[0], ai.owner)
                    return

            # Move towards player if far away
            if not ai.in_range(player, SpellType.ATTACK):
                direction = pyro.astar.astar(ai.owner.game, monster.pos, player.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif player.hp > 0:
                attacks = ai.get_spells(SpellType.ATTACK)
                if len(attacks) > 0:
                    random_attack = attacks[libtcod.random_get_int(0, 0, len(attacks)-1)]
                    ai.cast_spell(action, random_attack, player)


class PassiveAggressive(BehaviorStrategy):
    def take_turn(self, action, ai):
        # Become aggressive if we're damaged
        if ai.owner.actor.hp < ai.owner.actor.max_hp:
            ai.behavior = Aggressive()

        # 25% chance to move one square in a random direction
        elif libtcod.random_get_int(0, 1, 4) == 1:
            direction = pyro.direction.random()
            if not blocked(ai.owner.game, ai.owner.pos.plus(direction)):
                return WalkAction(direction)


class Confused(BehaviorStrategy):
    def __init__(self, restore_ai=None, num_turns=SPELL_CONFUSE_TURNS):
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self, action, ai):
        if self.restore_ai is None or self.num_turns > 0:
            self.num_turns -= 1
            # Move in a random direction
            direction = pyro.direction.random()
            if not blocked(ai.owner.game, ai.owner.pos.plus(direction)):
                return WalkAction(direction)
        else:
            # Restore normal AI
            ai.strategy = self.restore_ai
            msg = 'The {0} is no longer confused!'.format(ai.owner.name)
            ai.owner.game.log.message(msg, libtcod.red)
