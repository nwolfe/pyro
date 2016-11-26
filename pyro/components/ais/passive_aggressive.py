import libtcodpy as libtcod
import components.ai as libai
import components.ais.aggressive as libagg


class PassiveAggressive(libai.AI):
    """Neutral, until the player attacks. May wander in a random direction."""

    def take_damage(self, damage):
        self.owner.set_component(libai.AI, libagg.Aggressive())

    def take_turn(self):
        # 25% chance to move one square in a random direction
        if libtcod.random_get_int(0, 1, 4) == 1:
            self.owner.move(libtcod.random_get_int(0, -1, 1),
                            libtcod.random_get_int(0, -1, 1))
