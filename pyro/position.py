import math


class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def equals(self, other):
        return self.x == other.x and self.y == other.y

    def equal_to(self, x, y):
        return self.x == x and self.y == y

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def plus(self, direction):
        return Position(self.x + direction.x, self.y + direction.y)
