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
        # TODO Implement the rest of this method from UseAction#onPerform()
        # TODO if item.can_equip() return alternate(EquipAction(loc, item))
        # TODO if not item.can_use() then return fail()

        # TODO Remove need for target parameter
        action = self._item.use2(self._target)

        # TODO if item.count == 0 then removeItem() else countChanged()

        return self.alternate(action)
