

MIN_SPEED = 0
NORMAL_SPEED = 3
MAX_SPEED = 5

ACTION_COST = 12
ENERGY_GAINS = [
    2,   # 1/3 normal speed
    3,   # 1/2 normal speed
    4,
    6,   # normal speed
    9,
    12,  # 2x normal speed
]


def ticks_at_speed(speed):
    return ACTION_COST / ENERGY_GAINS[NORMAL_SPEED + speed]


class Energy:
    def __init__(self):
        self.energy = 0

    def can_take_turn(self):
        return self.energy >= ACTION_COST

    def gain(self, speed):
        self.energy += ENERGY_GAINS[speed]
        return self.can_take_turn()

    def spend(self):
        self.energy -= ACTION_COST
