from pyro.component import Component


class Physics(Component):
    def __init__(self, blocks=False):
        Component.__init__(self, component_type=Physics)
        self.blocks = blocks
