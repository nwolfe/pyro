from pyro.component import Component


class Grass(Component):
    def __init__(self, is_crushed=False, standing_glyph=":", crushed_glyph="."):
        Component.__init__(self, component_type=Grass)
        self.is_crushed = is_crushed
        self.standing_glyph = standing_glyph
        self.crushed_glyph = crushed_glyph

    def crush(self):
        self.is_crushed = True
        self.owner.glyph = self.crushed_glyph
        self.owner.game.map.unblock_vision(self.owner.x, self.owner.y)
