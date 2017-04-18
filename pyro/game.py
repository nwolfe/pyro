

class Game:
    def __init__(self, state, map, objects, player, log, dungeon_level):
        self.state = state
        self.map = map
        self.objects = objects
        self.player = player
        self.log = log
        self.dungeon_level = dungeon_level
        self.actors = None
