import libtcodpy as libtcod
import pyro.component as libcomp


class Item(libcomp.Component):
    def __init__(self, use_fn=None):
        libcomp.Component.__init__(self)
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, item_owner):
        inventory = item_owner.component(Inventory)
        if inventory is None:
            return False
        else:
            inventory = inventory.items

        # Add to owner's inventory and remove from the map
        if len(inventory) >= 26:
            if item_owner == self.owner.game.player:
                msg = 'Your inventory is full, cannot pick up {0}.'
                self.owner.game.message(msg.format(self.owner.name), libtcod.red)
            return False
        else:
            self.item_owner = item_owner
            inventory.append(self.owner)
            self.owner.game.objects.remove(self.owner)
            if self.player_owned():
                self.owner.game.message('You picked up a {0}!'.format(
                    self.owner.name), libtcod.green)
            return True

    def drop(self):
        # Remove from the inventory and add to the map.
        # Place at owner's coordinates.
        inventory = self.item_owner.component(Inventory).items
        inventory.remove(self.owner)
        self.owner.game.objects.append(self.owner)
        self.owner.x = self.item_owner.x
        self.owner.y = self.item_owner.y
        if self.player_owned():
            self.owner.game.message('You dropped a {0}.'.format(self.owner.name),
                                    libtcod.yellow)

    def use(self, ui):
        # Call the use_fn if we have one
        if self.use_fn is None:
            self.owner.game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.use_fn(self.item_owner, self.owner.game, ui)
            if result != 'cancelled':
                inventory = self.item_owner.component(Inventory).items
                inventory.remove(self.owner)

    def player_owned(self):
        return self.item_owner == self.owner.game.player


class Equipment(Item):
    """An object that can be equipped, yielding bonuses. Automatically adds
    the Item component."""

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Item.__init__(self)
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False
        self.item_owner = None

    def initialize(self, game_object):
        self.owner = game_object
        self.owner.components[Item] = self

    def pick_up(self, item_owner):
        if Item.pick_up(self, item_owner):
            if get_equipped_in_slot(item_owner, self.slot) is None:
                self.equip(item_owner)

    def drop(self):
        self.unequip()
        Item.drop(self)

    def use(self, ui):
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
            self.owner.game.message(msg, libtcod.light_green)

    def unequip(self):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        if self.player_owned():
            self.owner.game.message('Unequipped {0} from {1}.'.format(
                self.owner.name, self.slot), libtcod.light_yellow)


class Inventory(libcomp.Component):
    def __init__(self, items=None):
        libcomp.Component.__init__(self)
        self.items = items
        if items is None:
            self.items = []


def get_equipped_in_slot(item_owner, slot):
    inventory = item_owner.component(Inventory)
    if inventory:
        for obj in inventory.items:
            equipment = obj.component(Equipment)
            if equipment and equipment.slot == slot and equipment.is_equipped:
                return equipment
    return None


def get_all_equipped(item_owner):
    inventory = item_owner.component(Inventory)
    equipped = []
    if inventory:
        for item in inventory.items:
            equipment = item.component(Equipment)
            if equipment and equipment.is_equipped:
                equipped.append(equipment)
    return equipped
