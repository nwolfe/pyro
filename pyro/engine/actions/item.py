import abc
from pyro.engine import Action, ActionResult, ItemLocation


class PickUpAction(Action):
    def __init__(self):
        Action.__init__(self)

    # TODO Do this properly; use self.actor not game.player
    # TODO Move Item#pick_up() behavior here
    def on_perform(self):
        # Pick up first item in the player's tile
        for item in self.game.stage.items:
            if item.pos == self.game.player.pos:
                item.pick_up(self.game.player)
        return ActionResult.SUCCESS


# TODO class EquipAction
# TODO class UnequipAction


class ItemAction(Action):
    __metaclass__ = abc.ABCMeta

    # TODO Remove default location value
    def __init__(self, item, location=ItemLocation.INVENTORY):
        Action.__init__(self)
        self._item = item
        self._location = location


class DropAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item):
        ItemAction.__init__(self, item)

    # TODO Move Item#drop() behavior here
    def on_perform(self):
        self._item.drop()
        return ActionResult.SUCCESS


class UseAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item, target=None):
        ItemAction.__init__(self, item)
        self._target = target

    # TODO Move Item#use() behavior here
    def on_perform(self):
        # TODO Implement the rest of this method from UseAction#onPerform()
        # TODO if item.can_equip() return alternate(EquipAction(loc, item))
        # TODO if not item.can_use() then return fail()

        # TODO Remove need for target parameter
        action = self._item.use2(self._target)

        # TODO if item.count == 0 then removeItem() else countChanged()

        return self.alternate(action)
