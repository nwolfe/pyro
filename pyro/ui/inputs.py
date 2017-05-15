

class Input:
    ENTER = None
    EXIT = None

    NORTH = None
    SOUTH = None
    EAST = None
    WEST = None

    HERO_INFO = None
    DROP = None
    REST = None
    PICKUP = None
    INVENTORY = None
    CLOSE_DOOR = None

    def __init__(self, name):
        self._name = name


Input.ENTER = Input('enter')
Input.EXIT = Input('exit')

Input.NORTH = Input('north')
Input.SOUTH = Input('south')
Input.EAST = Input('east')
Input.WEST = Input('west')

Input.HERO_INFO = Input('hero info')
Input.DROP = Input('drop')
Input.REST = Input('rest')
Input.PICKUP = Input('pickup')
Input.INVENTORY = Input('inventory')
Input.CLOSE_DOOR = Input('close door')
