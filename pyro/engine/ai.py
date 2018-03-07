import libtcodpy as libtcod
import pyro.astar
import pyro.direction
from pyro.spell import Spell
from pyro.target import Target
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


class AI:
    def __init__(self, behavior=None, spells=None):
        self.monster = None
        self.behavior = behavior
        if spells:
            self.__spells = {Spell.TYPE_ATTACK: [], Spell.TYPE_HEAL: []}
            for spell in spells:
                self.__spells[spell.type].append(spell)
        else:
            self.__spells = None

    def take_turn(self):
        """Perform a single game turn."""
        return self.behavior.take_turn(self)

    def took_damage(self, action, damage, attacker):
        self.behavior.took_damage(action, damage, attacker, self)

    def confuse(self, num_turns):
        old_behavior = self.behavior
        self.behavior = Confused(old_behavior, num_turns)

    def get_spells(self, spell_type):
        return self.__spells[spell_type]

    def in_range(self, target, spell_type):
        target = Target(actor=target)
        for spell in self.__spells[spell_type]:
            if spell.in_range(self.monster, target):
                return True
        return False

    def cast_spell(self, spell, target):
        target = Target(actor=target)
        if Spell.TYPE_ATTACK == spell.type:
            # TODO move hit chance and messaging into Spell.cast()
            # Only 40% chance to hit
            if libtcod.random_get_int(0, 1, 5) <= 2:
                self.monster.game.log.message2('{1} casts a %s' %
                                               spell.name, self.monster)
                return spell.cast(target)
            else:
                self.monster.game.log.message2('{1} casts a %s but it fizzles!' %
                                               spell.name, self.monster)
        elif Spell.TYPE_HEAL == spell.type:
            self.monster.game.log.message2('{1} heals {2 him}self!', self.monster, self.monster)
            return spell.cast(target)


class BehaviorStrategy:
    def take_turn(self, ai):
        pass

    def took_damage(self, action, damage, attacker, ai):
        pass


class Aggressive(BehaviorStrategy):
    def __init__(self, target=None):
        self.target = target

    def take_turn(self, ai):
        target = self.target if self.target else ai.monster.game.player
        if ai.monster.game.stage.map.is_in_fov(ai.monster.pos):
            # Move towards player if far away
            if ai.monster.pos.distance_to(target.pos) >= 2:
                direction = pyro.astar.astar(ai.monster.game, ai.monster.pos, target.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif target.is_alive():
                return AttackAction(target)


# TODO Return a new CastAction so it's just like returning a WalkAction or AttackAction?
class AggressiveSpellcaster(BehaviorStrategy):
    def take_turn(self, ai):
        player = ai.monster.game.player
        if ai.monster.game.stage.map.is_in_fov(ai.monster.pos):
            # Heal yourself if damaged
            if ai.monster.hp < ai.monster.max_hp:
                heals = ai.get_spells(Spell.TYPE_HEAL)
                if len(heals) > 0:
                    return ai.cast_spell(heals[0], ai.monster)

            # Move towards player if far away
            if not ai.in_range(player, Spell.TYPE_ATTACK):
                direction = pyro.astar.astar(ai.monster.game, ai.monster.pos, player.pos)
                return WalkAction(direction)

            # Close enough, attack! (If the player is still alive)
            elif player.is_alive():
                attacks = ai.get_spells(Spell.TYPE_ATTACK)
                if len(attacks) > 0:
                    random_attack = attacks[libtcod.random_get_int(0, 0, len(attacks)-1)]
                    return ai.cast_spell(random_attack, player)


class PassiveAggressive(BehaviorStrategy):
    def take_turn(self, ai):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            direction = pyro.direction.random()
            if not blocked(ai.monster.game, ai.monster.pos.plus(direction)):
                return WalkAction(direction)

    def took_damage(self, action, damage, attacker, ai):
        # Become aggressive if we're attacked
        ai.behavior = Aggressive(target=attacker)


class Confused(BehaviorStrategy):
    def __init__(self, restore_ai=None, num_turns=SPELL_CONFUSE_TURNS):
        self.restore_ai = restore_ai
        self.num_turns = num_turns

    def take_turn(self, ai):
        if self.restore_ai is None or self.num_turns > 0:
            self.num_turns -= 1
            # Move in a random direction
            direction = pyro.direction.random()
            if not blocked(ai.monster.game, ai.monster.pos.plus(direction)):
                return WalkAction(direction)
        else:
            # Restore normal AI
            ai.behavior = self.restore_ai
            ai.monster.game.log.message2('{1} is no longer confused!', ai.monster)
