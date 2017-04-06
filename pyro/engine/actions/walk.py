from pyro.components import Fighter, Door, Grass, Movement
from pyro.engine import Action, ActionResult
from pyro.engine.actions import AttackAction


class WalkAction(Action):
    def __init__(self, direction):
        Action.__init__(self)
        self.direction = direction

    def on_perform(self):
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
        else:
            door = None
            grass = None
            for game_object in self.game.objects:
                if game_object.component(Door):
                    if game_object.pos.equal_to(x, y):
                        door = game_object.component(Door)
                elif game_object.component(Grass):
                    if game_object.pos.equal_to(x, y):
                        if not game_object.component(Grass).is_crushed:
                            grass = game_object.component(Grass)

                if door and grass:
                    break

            movement = self.game.player.component(Movement)
            moved = movement.move(self.direction.x, self.direction.y) if movement else False
            if moved:
                if grass:
                    grass.crush()
            else:
                if door:
                    return self.alternate(OpenDoorAction(door))
        return ActionResult.SUCCESS


class OpenDoorAction(Action):
    def __init__(self, door):
        Action.__init__(self)
        self.door = door

    def on_perform(self):
        self.door.open()
        return ActionResult.SUCCESS


class CloseDoorAction(Action):
    def on_perform(self):
        x = self.game.player.pos.x
        y = self.game.player.pos.y
        for game_object in self.game.objects:
            if game_object.component(Door):
                other_x = game_object.pos.x
                other_y = game_object.pos.y
                close_x = (other_x == x or other_x == x-1 or other_x == x+1)
                close_y = (other_y == y or other_y == y-1 or other_y == y+1)
                player_on_door = (other_x == x and other_y == y)
                if close_x and close_y and not player_on_door:
                    game_object.component(Door).close()
                    break
        return ActionResult.SUCCESS

