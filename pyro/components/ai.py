import pyro.component as libcomp


class AI(libcomp.Component):
    def __init__(self):
        libcomp.Component.__init__(self)

    def take_turn(self):
        """Perform a single game turn."""
        return

    def take_damage(self, damage):
        """Called by the Fighter component when the owner takes damage."""
        return
