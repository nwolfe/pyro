from pyro.components import Fighter, Movement
from pyro.direction import Direction
from pyro.engine import Action, ActionResult
from pyro.engine.actions import AttackAction


class WalkAction(Action):
    def __init__(self, direction):
        Action.__init__(self)
        self.direction = direction

    def on_perform(self):
        # See if there is an actor there
        x = self.game.player.pos.x + self.direction.x
        y = self.game.player.pos.y + self.direction.y
        target = None
        for game_object in self.game.objects:
            if game_object.component(Fighter):
                if game_object.pos.equal_to(x, y):
                    target = game_object
                    break

        if target and target != self.actor:
            return self.alternate(AttackAction(target))

        # See if it's a door
        if self.game.map.tiles[x][y].type.opens_to:
            return self.alternate(OpenDoorAction(x, y))

        # Try moving there
        movement = self.game.player.component(Movement)
        if movement.move(self.direction.x, self.direction.y):
            # Step on the tile (i.e. tall grass becomes crushed grass)
            tile = self.game.map.tiles[x][y]
            if tile.type.steps_to:
                tile.type = tile.type.steps_to
                self.game.map.unblock_vision(x, y)

        return ActionResult.SUCCESS


class OpenDoorAction(Action):
    def __init__(self, x, y):
        Action.__init__(self)
        self.x, self.y = x, y

    def on_perform(self):
        tile = self.game.map.tiles[self.x][self.y]
        tile.type = tile.type.opens_to
        self.game.map.unblock_vision(self.x, self.y)
        return ActionResult.SUCCESS


class CloseDoorAction(Action):
    def on_perform(self):
        for direction in Direction.ALL:
            x = self.game.player.pos.x + direction.x
            y = self.game.player.pos.y + direction.y
            tile = self.game.map.tiles[x][y]
            if tile.type.closes_to:
                tile.type = tile.type.closes_to
                self.game.map.block_vision(x, y)
                break
        return ActionResult.SUCCESS
