import abc
import tcod as libtcod
from pyro.engine import Action, ItemLocation


class ItemAction(Action):
    __metaclass__ = abc.ABCMeta

    # TODO Remove default location value
    def __init__(self, item, location=ItemLocation.INVENTORY):
        Action.__init__(self)
        self.item = item
        self._location = location


class PickUpAction(ItemAction):
    def __init__(self, item):
        ItemAction.__init__(self, item, ItemLocation.GROUND)

    def on_perform(self):
        """Assumes only the player can pick up items."""
        # TODO Add support for stacks of items
        owner = self.game.player
        if len(owner.inventory) >= 26:
            return self.fail("{1} [don't|doesn't] have room for {2}.", self.actor, self.item)
        else:
            self.item.owner = owner
            owner.inventory.append(self.item)
            if self.item in self.game.stage.items:
                self.game.stage.items.remove(self.item)
            return self.succeed('{1} pick[s] up {2}.', self.actor, self.item)


class DropAction(ItemAction):
    # TODO Location parameter
    def __init__(self, item):
        ItemAction.__init__(self, item)

    def on_perform(self):
        """Assumes only the player can drop items."""
        # TODO Add support for stacks of items
        self.item.owner.inventory.remove(self.item)
        self.game.stage.items.append(self.item)
        self.item.pos.copy(self.item.owner.pos)

        if self.item.is_equipped:
            self.item.is_equipped = False
            msg = 'You take off and drop the {0}.'
        else:
            msg = 'You drop the {0}.'
        self.game.log.message(msg.format(self.item.name), libtcod.yellow)
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
        if self.item.can_equip():
            return self.alternate(EquipAction(self.item))

        if not self.item.can_use():
            self.game.log.message("{0} can't be used.".format(self.item.name))
            return self.fail()

        # TODO Remove need for target parameter
        # TODO Add support for stacks of items
        action = self.item.use(self._target)
        self.item.owner.inventory.remove(self.item)

        return self.alternate(action)


class EquipAction(ItemAction):
    def __init__(self, equipment):
        """Assumes only the player can equip items."""
        ItemAction.__init__(self, equipment)

    def on_perform(self):
        if self.item.is_equipped:
            return self.alternate(UnequipAction(self.item))

        replaced = filter(
            lambda i: i.is_equipped and i.equip_slot == self.item.equip_slot,
            self.item.owner.inventory)
        if len(replaced) == 1:
            self.game.log.message('Unequipped {0}.'.format(replaced[0].name),
                                  libtcod.light_yellow)

        self.item.is_equipped = True
        self.game.log.message('Equipped {0} on {1}.'.format(
            self.item.name, self.item.equip_slot), libtcod.light_green)
        return self.succeed()


class UnequipAction(ItemAction):
    def __init__(self, equipment):
        """Assumes only the player can unequip items."""
        ItemAction.__init__(self, equipment)

    def on_perform(self):
        self.item.is_equipped = False
        self.game.log.message('Unequipped {0} from {1}'.format(
            self.item.name, self.item.equip_slot), libtcod.light_yellow)
        return self.succeed()
