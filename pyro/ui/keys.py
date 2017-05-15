

def key_for_int(ordinal):
    index = ordinal - ord('a')
    if 0 <= index < 26:
        return _LETTER_KEYS[index]
    else:
        return None


class Key:
    A = None
    B = None
    C = None
    D = None
    E = None
    F = None
    G = None
    H = None
    I = None
    J = None
    K = None
    L = None
    M = None
    N = None
    O = None
    P = None
    Q = None
    R = None
    S = None
    T = None
    U = None
    V = None
    W = None
    X = None
    Y = None
    Z = None

    UP = None
    DOWN = None
    LEFT = None
    RIGHT = None

    ENTER = None
    ESCAPE = None

    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

    @property
    def ord(self):
        if len(self._name) == 1:
            return ord(self._name)
        else:
            return -1


Key.A = Key('a')
Key.B = Key('b')
Key.C = Key('c')
Key.D = Key('d')
Key.E = Key('e')
Key.F = Key('f')
Key.G = Key('g')
Key.H = Key('h')
Key.I = Key('i')
Key.J = Key('j')
Key.K = Key('k')
Key.L = Key('l')
Key.M = Key('m')
Key.N = Key('n')
Key.O = Key('o')
Key.P = Key('p')
Key.Q = Key('q')
Key.R = Key('r')
Key.S = Key('s')
Key.T = Key('t')
Key.U = Key('u')
Key.V = Key('v')
Key.W = Key('w')
Key.X = Key('x')
Key.Y = Key('y')
Key.Z = Key('z')

Key.UP = Key('up')
Key.DOWN = Key('down')
Key.LEFT = Key('left')
Key.RIGHT = Key('right')

Key.ENTER = Key('enter')
Key.ESCAPE = Key('escape')


_LETTER_KEYS = [
    Key.A,
    Key.B,
    Key.C,
    Key.D,
    Key.E,
    Key.F,
    Key.G,
    Key.H,
    Key.I,
    Key.J,
    Key.K,
    Key.L,
    Key.M,
    Key.N,
    Key.O,
    Key.P,
    Key.Q,
    Key.R,
    Key.S,
    Key.T,
    Key.U,
    Key.V,
    Key.W,
    Key.X,
    Key.Y,
    Key.Z
]


