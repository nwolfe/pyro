import math


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def copy(self, other):
        self.x = other.x
        self.y = other.y

    def clone(self):
        return Position(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    def equals(self, x, y):
        return self.x == x and self.y == y

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def plus(self, direction):
        return Position(self.x + direction.x, self.y + direction.y)
