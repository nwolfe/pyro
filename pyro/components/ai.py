from pyro.component import Component


class AI(Component):
    def __init__(self):
        Component.__init__(self, component_type=AI)

    def take_turn(self):
        """Perform a single game turn."""
        return

    def take_damage(self, damage):
        """Called by the Fighter component when the owner takes damage."""
        return
