import component as libcomp
import libtcodpy as libtcod


class Grass(libcomp.Component):
    def __init__(self, is_crushed=False, standing_glyph=":", crushed_glyph="."):
        self.is_crushed = is_crushed
        self.standing_glyph = standing_glyph
        self.crushed_glyph = crushed_glyph

    def crush(self):
        self.is_crushed = True
        self.owner.glyph = self.crushed_glyph
        self.owner.game.map[self.owner.x][self.owner.y].block_sight = False
        libtcod.map_set_properties(self.owner.game.fov_map,
                                   self.owner.x, self.owner.y, True, True)
