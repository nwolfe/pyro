from pyro.component import Component


class Door(Component):
    def __init__(self, is_open=False, opened_glyph='-', closed_glyph='+'):
        Component.__init__(self, component_type=Door)
        self.is_open = is_open
        self.opened_glyph = opened_glyph
        self.closed_glyph = closed_glyph

    def open(self):
        self.is_open = True
        self.owner.blocks = False
        self.owner.glyph = self.opened_glyph
        self.owner.game.game_map.unblock_movement(self.owner.x, self.owner.y)
        self.owner.game.game_map.unblock_vision(self.owner.x, self.owner.y)

    def close(self):
        self.is_open = False
        self.owner.blocks = True
        self.owner.glyph = self.closed_glyph
        self.owner.game.game_map.block_movement(self.owner.x, self.owner.y)
        self.owner.game.game_map.block_vision(self.owner.x, self.owner.y)
