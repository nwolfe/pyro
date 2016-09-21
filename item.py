import libtcodpy as libtcod
import component as libcomp


class Item(libcomp.Component):
    def __init__(self, use_fn=None):
        self.use_fn = use_fn
        self.item_owner = None

    def pick_up(self, game):
        # Add to player's inventory and remove from the map
        if len(game.inventory) >= 26:
            game.message('Your inventory is full, cannot pick up {0}.'.format(
                self.owner.name), libtcod.red)
        else:
            self.item_owner = game.player
            game.inventory.append(self.owner)
            game.objects.remove(self.owner)
            game.message('You picked up a {0}!'.format(self.owner.name),
                         libtcod.green)
            # Special case: automatically equip if slot is empty
            equipment = self.owner.components.get(Equipment)
            if equipment and get_equipped_in_slot(equipment.slot, game) is None:
                equipment.equip(game)

    def drop(self, game):
        # Remove from the inventory and add to the map.
        # Place at player's coordinates.
        game.inventory.remove(self.owner)
        game.objects.append(self.owner)
        self.owner.x = game.player.x
        self.owner.y = game.player.y
        # Special case: unequip before dropping
        equipment = self.owner.components.get(Equipment)
        if equipment:
            equipment.unequip(game)
        game.message('You dropped a {0}.'.format(self.owner.name),
                     libtcod.yellow)

    def use(self, game, ui):
        # Call the use_fn if we have one
        equipment = self.owner.components.get(Equipment)
        if equipment:
            # Special case: the "use" action is to equip/unequip
            equipment.toggle_equip(game)
        elif self.use_fn is None:
            game.message('The {0} cannot be used.'.format(self.owner.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.use_fn(self.item_owner, game, ui)
            if result != 'cancelled':
                game.inventory.remove(self.owner)


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
        item = Item()
        item.initialize(object)
        object.components[Item] = item

    def toggle_equip(self, game):
        if self.is_equipped:
            self.unequip(game)
        else:
            self.equip(game)

    def equip(self, game):
        """Equip object and show a message about it."""
        replacing = get_equipped_in_slot(self.slot, game)
        if replacing is not None:
            replacing.unequip(game)
        self.is_equipped = True
        game.message('Equipped {0} on {1}.'.format(self.owner.name, self.slot),
                     libtcod.light_green)

    def unequip(self, game):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        game.message('Unequipped {0} from {1}.'.format(self.owner.name,
                                                       self.slot),
                     libtcod.light_yellow)


def get_equipped_in_slot(slot, game):
    for obj in game.inventory:
        item = obj.components.get(Equipment)
        if item and item.slot == slot and item.is_equipped:
            return item
    return None


def get_all_equipped(obj, game):
    if obj == game.player:
        equipped = []
        for item in game.inventory:
            equipment = item.components.get(Equipment)
            if equipment and equipment.is_equipped:
                equipped.append(equipment)
        return equipped
    else:
        return []
