import pyro.component as libcomp
import libtcodpy as libtcod


class Door(libcomp.Component):
    def __init__(self, is_open=False, opened_glyph='-', closed_glyph='+'):
        libcomp.Component.__init__(self)
        self.is_open = is_open
        self.opened_glyph = opened_glyph
        self.closed_glyph = closed_glyph

    def open(self):
        self.is_open = True
        self.owner.blocks = False
        self.owner.glyph = self.opened_glyph
        self.owner.game.map[self.owner.x][self.owner.y].blocked = False
        self.owner.game.map[self.owner.x][self.owner.y].block_sight = False
        libtcod.map_set_properties(self.owner.game.fov_map,
                                   self.owner.x, self.owner.y, True, True)

    def close(self):
        self.is_open = False
        self.owner.blocks = True
        self.owner.glyph = self.closed_glyph
        self.owner.game.map[self.owner.x][self.owner.y].blocked = True
        self.owner.game.map[self.owner.x][self.owner.y].block_sight = True
        libtcod.map_set_properties(self.owner.game.fov_map,
                                   self.owner.x, self.owner.y, False, False)
