import abc
import tcod as libtcod
from pyro.position import Position


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


class Item:
    def __init__(self, name, glyph, on_use=None):
        self.name = name
        self.glyph = glyph
        self.pos = Position()
        self.on_use = on_use
        self.owner = None

    def pick_up(self, owner):
        if owner.inventory is None:
            return False

        if len(owner.inventory) >= 26:
            if owner == self.owner.game.player:
                msg = 'Your inventory is full, cannot pick up {0}.'
                self.owner.game.log.message(msg.format(self.name), libtcod.red)
            return False
        else:
            # Add to owner's inventory and remove from the map
            self.owner = owner
            owner.inventory.append(self)
            if self in self.owner.game.items:
                self.owner.game.items.remove(self)
            if self.player_owned():
                self.owner.game.log.message('You picked up a {0}!'
                                            .format(self.name), libtcod.green)
            return True

    def drop(self):
        # Remove from the inventory and add to the map.
        # Place at owner's coordinates.
        self.owner.inventory.remove(self)
        self.owner.game.items.append(self)
        self.pos.x = self.owner.pos.x
        self.pos.y = self.owner.pos.y
        if self.player_owned():
            self.owner.game.log.message(
                'You dropped a {0}.'.format(self.name), libtcod.yellow)

    def use(self, action, ui):
        # Call the use_fn if we have one
        if self.on_use is None:
            self.owner.game.log.message(
                'The {0} cannot be used.'.format(self.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            result = self.on_use.use(action, self.owner, ui)
            if result != 'cancelled':
                self.owner.inventory.remove(self)

    def player_owned(self):
        return self.owner == self.owner.game.player


class Equipment(Item):
    """An object that can be equipped, yielding bonuses. Automatically adds
    the Item component."""

    def __init__(self, name, glyph, slot, power_bonus=0, defense_bonus=0, max_hp_bonus=0):
        Item.__init__(self, name, glyph)
        self.type = Equipment
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus
        self.is_equipped = False

    def pick_up(self, owner):
        if Item.pick_up(self, owner):
            if get_equipped_in_slot(owner, self.slot) is None:
                self.equip(owner)

    def drop(self):
        self.unequip()
        Item.drop(self)

    def use(self, action, ui):
        self.toggle_equip()

    def toggle_equip(self):
        if self.is_equipped:
            self.unequip()
        else:
            self.equip(self.owner)

    def equip(self, owner):
        """Equip object and show a message about it."""
        self.owner = owner
        replacing = get_equipped_in_slot(owner, self.slot)
        if replacing is not None:
            replacing.unequip()
        self.is_equipped = True
        if self.player_owned():
            msg = 'Equipped {0} on {1}.'.format(self.name, self.slot)
            self.owner.game.log.message(msg, libtcod.light_green)

    def unequip(self):
        """Unequip object and show a message about it."""
        if not self.is_equipped:
            return
        self.is_equipped = False
        if self.player_owned():
            self.owner.game.log.message('Unequipped {0} from {1}.'.format(
                self.name, self.slot), libtcod.light_yellow)


def get_equipped_in_slot(item_owner, slot):
    if item_owner.inventory:
        for obj in item_owner.inventory:
            if isinstance(obj, Equipment):
                if obj.slot == slot and obj.is_equipped:
                    return obj
    return None


def get_all_equipped(item_owner):
    equipped = []
    if item_owner.inventory:
        for item in item_owner.inventory:
            if isinstance(item, Equipment):
                if item.is_equipped:
                    equipped.append(item)
    return equipped