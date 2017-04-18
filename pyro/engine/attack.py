import tcod as libtcod
from pyro.engine import Event, EventType


class Hit:
    def perform(self, action, attacker, defender, can_miss=True):
        if can_miss:
            if libtcod.random_get_int(0, 1, 10) == 1:
                msg = '{0} attacks {1} but misses!'.format(attacker.name, defender.name)
                action.game.log.message(msg)
                return

        damage = attacker.power - defender.defense

        if damage > 0:
            msg = '{0} attacks {1} for {2} hit points.'.format(
                attacker.name, defender.name, damage)
            if attacker.game_object == action.game.player:
                action.game.log.message(msg, libtcod.light_green)
            else:
                action.game.log.message('- ' + msg, libtcod.light_red)
            defender.take_damage(action, damage, attacker)
        else:
            msg = '{0} attacks {1} but it has no effect!'.format(
                attacker.name, defender.name)
            action.game.log.message(msg)

        action.add_event(Event(EventType.HIT, actor=defender))
