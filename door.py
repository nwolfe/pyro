import component as libcomp
import libtcodpy as libtcod


class Door(libcomp.Component):
    def __init__(self, is_open=False, opened_char='-', closed_char='+'):
        self.is_open = is_open
        self.opened_char = opened_char
        self.closed_char = closed_char

    def open(self):
        self.is_open = True
        self.owner.blocks = False
        self.owner.char = self.opened_char
        self.owner.game.map[self.owner.x][self.owner.y].blocked = False
        self.owner.game.map[self.owner.x][self.owner.y].block_sight = False
        libtcod.map_set_properties(self.owner.game.fov_map,
                                   self.owner.x, self.owner.y, True, True)

    def close(self):
        self.is_open = False
        self.owner.blocks = True
        self.owner.char = self.closed_char
        self.owner.game.map[self.owner.x][self.owner.y].blocked = True
        self.owner.game.map[self.owner.x][self.owner.y].block_sight = True
        libtcod.map_set_properties(self.owner.game.fov_map,
                                   self.owner.x, self.owner.y, False, False)
