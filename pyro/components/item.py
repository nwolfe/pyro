import abc
import tcod as libtcod
from pyro.component import Component


class ItemUse:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def use(self, action, actor, ui):
        pass


class SpellItemUse(ItemUse):
    def __init__(self, spell):
        self.spell = spell

    def use(self, action, actor, ui):
        return self.spell.player_cast(action, actor, ui)


class Item(Component):
    def __init__(self, on_use=None):
        Component.__init__(self, component_type=Item)
        self.on_use = on_use
        self.item_owner = None

    def pick_up(self, item_owner):
        inventory = item_owner.game_object.component(Inventory)
        if inventory is None:
            return False

        # Add to owner's inventory and remove from the map
        if inventory.is_full():
            if item_owner == self.owner.game.player.actor:
                msg = 'Your inventory is full, cannot pick up {0}.'
                self.owner.game.log.message(msg.format(self.owner.name), libtcod.red)
            return False
        else:
            self.item_owner = item_owner
            inventory.add_item(self.owner)
            if self.owner in self.owner.game.objects:
                self.owner.game.objects.remove(self.owner)
            if self.player_owned():
                self.owner.game.log.message('You picked up a {0}!'.format(self.owner.name),
                                            libtcod.green)
            return True

    def drop(self):
        # Remove from the inventory and add to the map.
        # Place at owner's coordinates.
        self.item_owner.game_object.component(Inventory).remove_item(self.owner)
        self.owner.game.objects.append(self.owner)
        self.owner.pos.x = self.item_owner.pos.x
        self.owner.pos.y = self.item_owner.pos.y
        if self.player_owned():
            self.owner.game.log.message('You dropped a {0}.'.format(self.owner.name),
                                        libtcod.yellow)

    def use(self, action, ui):
        # Call the use_fn if we have one
        if self.on_use is None:
            self.owner.game.log.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.on_use.use(action, self.item_owner, ui)
            if result != 'cancelled':
                self.item_owner.game_object.component(Inventory).remove_item(self.owner)

    def player_owned(self):
        return self.item_owner == self.owner.game.player.actor


class Equipment(Item):
    """An object that can be equipped, yielding bonuses. Automatically adds
    the Item component."""

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Item.__init__(self)
        self.type = Equipment
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False
        self.item_owner = None

    def set_owner(self, game_object):
        Item.set_owner(self, game_object)
        self.owner.components[Item] = self

    def pick_up(self, item_owner):
        if Item.pick_up(self, item_owner):
            if get_equipped_in_slot(item_owner, self.slot) is None:
                self.equip(item_owner)

    def drop(self):
        self.unequip()
        Item.drop(self)

    def use(self, action, ui):
        self.toggle_equip(self.item_owner)

    def toggle_equip(self, item_owner):
        if self.is_equipped:
            self.unequip()
        else:
            self.equip(item_owner)

    def equip(self, item_owner):
        """Equip object and show a message about it."""
        self.item_owner = item_owner
        replacing = get_equipped_in_slot(item_owner, self.slot)
        if replacing is not None:
            replacing.unequip()
        self.is_equipped = True
        if self.player_owned():
            msg = 'Equipped {0} on {1}.'.format(self.owner.name, self.slot)
            self.owner.game.log.message(msg, libtcod.light_green)

    def unequip(self):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        if self.player_owned():
            self.owner.game.log.message('Unequipped {0} from {1}.'.format(
                self.owner.name, self.slot), libtcod.light_yellow)


class Inventory(Component):
    def __init__(self, items=None):
        Component.__init__(self, component_type=Inventory)
        self.items = items
        if items is None:
            self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def is_full(self):
        return len(self.items) >= 26


def get_equipped_in_slot(item_owner, slot):
    inventory = item_owner.game_object.component(Inventory)
    if inventory:
        for obj in inventory.items:
            equipment = obj.component(Equipment)
            if equipment and equipment.slot == slot and equipment.is_equipped:
                return equipment
    return None


def get_all_equipped(item_owner):
    inventory = item_owner.game_object.component(Inventory)
    equipped = []
    if inventory:
        for item in inventory.items:
            equipment = item.component(Equipment)
            if equipment and equipment.is_equipped:
                equipped.append(equipment)
    return equipped
