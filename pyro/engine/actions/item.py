from pyro.engine import Action, ActionResult


class PickUpAction(Action):
    def __init__(self):
        Action.__init__(self)

    # TODO Do this properly; use self.actor not game.player
    def on_perform(self):
        # Pick up first item in the player's tile
        for item in self.game.stage.items:
            if item.pos == self.game.player.pos:
                item.pick_up(self.game.player)
        return ActionResult.SUCCESS


class DropAction(Action):
    def __init__(self, item):
        Action.__init__(self)
        self.item = item

    def on_perform(self):
        self.item.drop()
        return ActionResult.SUCCESS


class UseAction(Action):
    def __init__(self, item, target=None):
        Action.__init__(self)
        self._item = item
        self._target = target

    def on_perform(self):
        self._item.use(self, self._target)
        return ActionResult.SUCCESS

