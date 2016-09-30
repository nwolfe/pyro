import libtcodpy as libtcod
import component as libcomp


class Item(libcomp.Component):
    def __init__(self, use_fn=None):
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, item_owner, game):
        inventory = item_owner.component(Inventory)
        if inventory is None:
            return False
        else:
            inventory = inventory.items

        # Add to owner's inventory and remove from the map
        if len(inventory) >= 26:
            if item_owner == game.player:
                msg = 'Your inventory is full, cannot pick up {0}.'
                game.message(msg.format(self.owner.name), libtcod.red)
            return False
        else:
            self.item_owner = item_owner
            inventory.append(self.owner)
            game.objects.remove(self.owner)
            if item_owner == game.player:
                game.message('You picked up a {0}!'.format(self.owner.name),
                             libtcod.green)
            return True

    def drop(self, game):
        # Remove from the inventory and add to the map.
        # Place at owner's coordinates.
        inventory = self.item_owner.component(Inventory).items
        inventory.remove(self.owner)
        game.objects.append(self.owner)
        self.owner.x = self.item_owner.x
        self.owner.y = self.item_owner.y

    def use(self, game, ui):
        # Call the use_fn if we have one
        if self.use_fn is None:
            game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.use_fn(self.item_owner, game, ui)
            if result != 'cancelled':
                inventory = self.item_owner.component(Inventory).items
                inventory.remove(self.owner)


class Equipment(Item):
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
        self.owner.components[Item] = self

    def toggle_equip(self, item_owner, game):
        if self.is_equipped:
            self.unequip(game)
        else:
            self.equip(item_owner, game)

    def equip(self, item_owner, game):
        """Equip object and show a message about it."""
        self.item_owner = item_owner
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
        if self.item_owner == game.player:
            game.message('Unequipped {0} from {1}.'.format(self.owner.name,
                                                           self.slot),
                         libtcod.light_yellow)

    def pick_up(self, item_owner, game):
        # Automatically equip if slot is empty
        if Item.pick_up(self, item_owner, game):
            if get_equipped_in_slot(item_owner, self.slot) is None:
                self.equip(item_owner, game)

    def drop(self, game):
        # Unequip before dropping
        Item.drop(self, game)
        self.unequip(game)
        if self.item_owner == game.player:
            game.message('You dropped a {0}.'.format(self.owner.name),
                         libtcod.yellow)

    def use(self, game, ui):
        self.toggle_equip(self.item_owner, game)



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
