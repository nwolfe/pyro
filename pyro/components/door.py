from pyro.component import Component
from pyro.components import Graphics, Physics


class Door(Component):
    def __init__(self, is_open=False, opened_glyph='-', closed_glyph='+'):
        Component.__init__(self, component_type=Door)
        self.is_open = is_open
        self.opened_glyph = opened_glyph
        self.closed_glyph = closed_glyph

    def open(self):
        self.is_open = True
        self.owner.component(Physics).blocks = False
        self.owner.component(Graphics).glyph = self.opened_glyph
        self.owner.game.map.unblock_movement(self.owner.pos.x, self.owner.pos.y)
        self.owner.game.map.unblock_vision(self.owner.pos.x, self.owner.pos.y)

    def close(self):
        self.is_open = False
        self.owner.component(Physics).blocks = True
        self.owner.component(Graphics).glyph = self.closed_glyph
        self.owner.game.map.block_movement(self.owner.pos.x, self.owner.pos.y)
        self.owner.game.map.block_vision(self.owner.pos.x, self.owner.pos.y)
