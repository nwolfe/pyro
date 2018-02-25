

class Target:
    def __init__(self, actor=None, position=None):
        self.actor = actor
        self.position = position

    @property
    def pos(self):
        if self.actor:
            return self.actor.pos
        else:
            return self.position


class TargetRequire:
    """Declares target requirements for an Item, Spell, etc."""
    
    NONE = None
    SELF = None
    SELECT = None

    TYPE_NONE = 'none'
    TYPE_SELF = 'self'
    TYPE_SELECT = 'select'
    TYPE_NEAREST = 'nearest'

    def __init__(self, type_, range_=0, not_found_message=None):
        self.type = type_
        self.range = range_
        self.not_found_message = not_found_message

TargetRequire.NONE = TargetRequire(TargetRequire.TYPE_NONE)
TargetRequire.SELF = TargetRequire(TargetRequire.TYPE_SELF)
TargetRequire.SELECT = TargetRequire(TargetRequire.TYPE_SELECT)
