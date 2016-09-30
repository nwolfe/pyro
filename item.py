import libtcodpy as libtcod
import component as libcomp


class Item(libcomp.Component):
    def __init__(self, use_fn=None):
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, item_owner, game):
        inventory = item_owner.component(Inventory)
        if inventory is None:
            return
        else:
            inventory = inventory.items

        # Add to owner's inventory and remove from the map
        if len(inventory) >= 26:
            if item_owner == game.player:
                msg = 'Your inventory is full, cannot pick up {0}.'
                game.message(msg.format(self.owner.name), libtcod.red)
        else:
            self.item_owner = item_owner
            inventory.append(self.owner)
            game.objects.remove(self.owner)
            if item_owner == game.player:
                game.message('You picked up a {0}!'.format(self.owner.name),
                             libtcod.green)
            # Special case: automatically equip if slot is empty
            equipment = self.owner.component(Equipment)
            if equipment and get_equipped_in_slot(item_owner, equipment.slot) is None:
                equipment.equip(item_owner, game)

    def drop(self, game):
        # Remove from the inventory and add to the map.
        # Place at owner's coordinates.
        inventory = self.item_owner.component(Inventory).items
        inventory.remove(self.owner)
        game.objects.append(self.owner)
        self.owner.x = self.item_owner.x
        self.owner.y = self.item_owner.y
        # Special case: unequip before dropping
        equipment = self.owner.component(Equipment)
        if equipment:
            equipment.unequip(game)
        if self.item_owner == game.player:
            game.message('You dropped a {0}.'.format(self.owner.name),
                         libtcod.yellow)

    def use(self, game, ui):
        # Call the use_fn if we have one
        equipment = self.owner.component(Equipment)
        if equipment:
            # Special case: the "use" action is to equip/unequip
            equipment.toggle_equip(self.item_owner, game)
        elif self.use_fn is None:
            game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.use_fn(self.item_owner, game, ui)
            if result != 'cancelled':
                inventory = self.item_owner.component(Inventory).items
                inventory.remove(self.owner)


class Equipment(libcomp.Component):
    """An object that can be equipped, yielding bonuses. Automatically adds
    the Item component."""

    def __init__(self, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False

    def initialize(self, object):
        self.owner = object
        self.owner.set_component(Item, Item())

    def toggle_equip(self, item_owner, game):
        if self.is_equipped:
            self.unequip(game)
        else:
            self.equip(item_owner, game)

    def equip(self, item_owner, game):
        """Equip object and show a message about it."""
        self.owner.component(Item).item_owner = item_owner
        replacing = get_equipped_in_slot(item_owner, self.slot)
        if replacing is not None:
            replacing.unequip(game)
        self.is_equipped = True
        if item_owner == game.player:
            msg = 'Equipped {0} on {1}.'.format(self.owner.name, self.slot)
            game.message(msg, libtcod.light_green)

    def unequip(self, game):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        item_owner = self.owner.component(Item).item_owner
        if item_owner == game.player:
            game.message('Unequipped {0} from {1}.'.format(self.owner.name,
                                                           self.slot),
                         libtcod.light_yellow)


class Inventory(libcomp.Component):
    def __init__(self, items=[]):
        self.items = items


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
