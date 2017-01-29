from pyro.component import Component
from pyro.settings import *


class Experience(Component):
    def __init__(self, xp=0, level=0):
        Component.__init__(self)
        self.xp = xp
        self.level = level

    def required_for_level_up(self):
        return LEVEL_UP_BASE + self.level * LEVEL_UP_FACTOR

    def can_level_up(self):
        return self.xp <= self.required_for_level_up()

    def level_up(self):
        required = self.required_for_level_up()
        self.level += 1
        self.xp -= required
