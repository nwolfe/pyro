from pyro.components import Fighter, Door, Grass, Movement
from pyro.engine.actions import Action, ActionResult, AttackAction


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


