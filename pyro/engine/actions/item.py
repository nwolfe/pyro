import abc
import tcod as libtcod
from pyro.engine import Action, ItemLocation
from pyro.engine.item import Equipment


class ItemAction(Action):
    __metaclass__ = abc.ABCMeta

    # TODO Remove default location value
    def __init__(self, item, location=ItemLocation.INVENTORY):
        Action.__init__(self)
        self._item = item
        self._location = location


class PickUpAction(ItemAction):
    def __init__(self, item):
        ItemAction.__init__(self, item, ItemLocation.GROUND)

    def on_perform(self):
        """Assumes only the player can pick up items."""
        # TODO Add support for stacks of items
        owner = self.game.player
        if len(owner.inventory) >= 26:
            msg = 'Your inventory is full, cannot pick up {0}.'
            self.game.log.message(msg.format(self._item.name), libtcod.red)
            return self.fail()
        else:
            self._item.owner = owner
            owner.inventory.append(self._item)
            if self._item in self.game.stage.items:
                self.game.stage.items.remove(self._item)
            self.game.log.message('You picked up a {0}!'.format(self._item.name),
                                  libtcod.green)
            return self.succeed()


# TODO class EquipAction
# TODO class UnequipAction


class DropAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item):
        ItemAction.__init__(self, item)

    def on_perform(self):
        """Assumes only the player can drop items."""
        # TODO Add support for dropping equipped items
        # TODO Add support for stacks of items
        self._item.owner.inventory.remove(self._item)
        self.game.stage.items.append(self._item)
        self._item.pos.copy(self._item.owner.pos)

        # TODO Get rid of Equipment class and the need for this
        if isinstance(self._item, Equipment):
            self._item.unequip()

        self.game.log.message('You dropped a {0}.'.format(self._item.name),
                              libtcod.yellow)
        return self.succeed()


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
