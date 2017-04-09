

class Direction:
    NONE = None
    NORTH = None
    NORTHEAST = None
    EAST = None
    SOUTHEAST = None
    SOUTH = None
    SOUTHWEST = None
    WEST = None
    NORTHWEST = None
    ALL = None

    def __init__(self, x, y):
        self.x, self.y = x, y


Direction.NONE = Direction(0, 0)
Direction.NORTH = Direction(0, -1)
Direction.NORTHEAST = Direction(1, -1)
Direction.EAST = Direction(1, 0)
Direction.SOUTHEAST = Direction(1, 1)
Direction.SOUTH = Direction(0, 1)
Direction.SOUTHWEST = Direction(-1, 1)
Direction.WEST = Direction(-1, 0)
Direction.NORTHWEST = Direction(-1, -1)
Direction.ALL = [Direction.NORTH, Direction.NORTHEAST,
                 Direction.EAST, Direction.SOUTHEAST,
                 Direction.SOUTH, Direction.SOUTHWEST,
                 Direction.WEST, Direction.NORTHWEST]
