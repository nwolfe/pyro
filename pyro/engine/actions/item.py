import abc
import tcod as libtcod
from pyro.engine import Action, ItemLocation


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


class DropAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item):
        ItemAction.__init__(self, item)

    def on_perform(self):
        """Assumes only the player can drop items."""
        # TODO Add support for stacks of items
        self._item.owner.inventory.remove(self._item)
        self.game.stage.items.append(self._item)
        self._item.pos.copy(self._item.owner.pos)

        if self._item.is_equipped:
            self._item.is_equipped = False
            msg = 'You take off and drop the {0}.'
        else:
            msg = 'You drop the {0}.'
        self.game.log.message(msg.format(self._item.name), libtcod.yellow)
        return self.succeed()


class UseAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item, target=None):
        """Assumes only the player can use items."""
        ItemAction.__init__(self, item)
        self._target = target

    # TODO Move Item#use() behavior here
    def on_perform(self):
        # TODO Implement the rest of this method from UseAction#onPerform()
        if self._item.can_equip():
            return self.alternate(EquipAction(self._item))

        if not self._item.can_use():
            self.game.log.message("{0} can't be used.".format(self._item.name))
            return self.fail()

        # TODO Remove need for target parameter
        # TODO Add support for stacks of items
        action = self._item.use(self._target)
        self._item.owner.inventory.remove(self._item)

        return self.alternate(action)


class EquipAction(ItemAction):
    def __init__(self, equipment):
        """Assumes only the player can equip items."""
        ItemAction.__init__(self, equipment)

    def on_perform(self):
        if self._item.is_equipped:
            return self.alternate(UnequipAction(self._item))

        replaced = filter(
            lambda i: i.is_equipped and i.equip_slot == self._item.equip_slot,
            self._item.owner.inventory)
        if len(replaced) == 1:
            self.game.log.message('Unequipped {0}.'.format(replaced[0].name),
                                  libtcod.light_yellow)

        self._item.is_equipped = True
        self.game.log.message('Equipped {0} on {1}.'.format(
            self._item.name, self._item.equip_slot), libtcod.light_green)
        return self.succeed()


class UnequipAction(ItemAction):
    def __init__(self, equipment):
        """Assumes only the player can unequip items."""
        ItemAction.__init__(self, equipment)

    def on_perform(self):
        self._item.is_equipped = False
        self.game.log.message('Unequipped {0} from {1}'.format(
            self._item.name, self._item.equip_slot), libtcod.light_yellow)
        return self.succeed()
