from pyro.direction import Direction
from pyro.engine import Action, ActionResult
from pyro.engine.actions import AttackAction
from pyro.utilities import blocked


class WalkAction(Action):
    def __init__(self, direction):
        Action.__init__(self)
        self.direction = direction

    def on_perform(self):
        # Do nothing if we're not moving anywhere
        if self.direction == Direction.NONE:
            return ActionResult.SUCCESS

        # See if there is an actor there
        new_pos = self.actor.pos.plus(self.direction)
        target = None
        for actor in self.game.actors:
            if actor.pos.equals(new_pos):
                target = actor
                break

        if target and target != self.actor:
            return self.alternate(AttackAction(target))

        # See if it's a door
        if self.game.map.tile(new_pos).type.opens_to:
            return self.alternate(OpenDoorAction(new_pos))

        # Try moving there
        if blocked(self.game, new_pos):
            return ActionResult.FAILURE

        self.actor.pos = new_pos
        self.game.map.dirty_visibility()

        # Step on the tile (i.e. tall grass becomes crushed grass)
        tile = self.game.map.tile(new_pos)
        if tile.type.steps_to:
            tile.type = tile.type.steps_to

        return ActionResult.SUCCESS


class OpenDoorAction(Action):
    def __init__(self, position):
        Action.__init__(self)
        self.position = position

    def on_perform(self):
        tile = self.game.map.tile(self.position)
        tile.type = tile.type.opens_to
        self.game.map.dirty_visibility()
        return ActionResult.SUCCESS


class CloseDoorAction(Action):
    def __init__(self, position):
        Action.__init__(self)
        self.position = position

    def on_perform(self):
        for direction in Direction.ALL:
            pos = self.position.plus(direction)
            tile = self.game.map.tile(pos)
            if tile.type.closes_to:
                if not blocked(self.game, pos):
                    tile.type = tile.type.closes_to
                    self.game.map.dirty_visibility()
                    break
        return ActionResult.SUCCESS
