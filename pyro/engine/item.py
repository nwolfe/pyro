import abc
import tcod as libtcod
from pyro.position import Position
from pyro.spell import CastResult
from pyro.engine import Action


# Hauberk notes:
# - The Item's "on_use" behavior is an Action, returned by use()


class ItemUse:
    __metaclass__ = abc.ABCMeta

    def requires_target(self):
        return False

    @abc.abstractmethod
    def use(self, action, actor, target=None):
        pass


class SpellItemUse(ItemUse):
    def __init__(self, spell):
        self.spell = spell

    def requires_target(self):
        return self.spell.requires_target()

    def use(self, action, actor, target=None):
        return self.spell.cast(action, actor, target)


class Item:
    def __init__(self, name, glyph, on_use=None, equip_slot=None):
        """An Item can be either usable or equipment, but not both.
        For a usable item, provide an ItemUse.
        For equipment, provide an equip slot string."""
        self.name = name
        self.glyph = glyph
        self.pos = Position()
        self.on_use = on_use
        self.owner = None
        self.equip_slot = equip_slot
        self.power_bonus = 0
        self.defense_bonus = 0
        self.max_hp_bonus = 0
        self.is_equipped = False

    def can_equip(self):
        return self.equip_slot is not None

    def can_use(self):
        return self.on_use is not None

    def __str__(self):
        if self.is_equipped:
            return "{0} (on {1})".format(self.name, self.equip_slot)
        else:
            return self.name

    def requires_target(self):
        return self.on_use is not None and self.on_use.requires_target()

    # TODO Move behavior into UseAction
    def use(self, action, target=None):
        # Call the use_fn if we have one
        if self.on_use is None:
            self.owner.game.log.message('The {0} cannot be used.'.format(self.name))
        else:
            # Destroy after use, unless it was cancelled for some reason
            # TODO This "destroy" behavior should live in UseAction
            result = self.on_use.use(action, self.owner, target)
            cancelled = result.type == CastResult.TYPE_CANCEL
            invalid_target = result.type == CastResult.TYPE_INVALID_TARGET
            if not cancelled and not invalid_target:
                self.owner.inventory.remove(self)
                return True
            elif invalid_target:
                self.owner.game.log.message('Invalid target.', libtcod.orange)
        return False

    # TODO Replace use() with this action-based implementation
    def use2(self, target):
        """Returns an Action."""
        return ItemAdapter(self, target)


# TODO Delete class once Item.use2() takes over Item.use()
class ItemAdapter(Action):
    def __init__(self, item, target):
        Action.__init__(self)
        self.item = item
        self.target = target

    def on_perform(self):
        if self.item.use(self, self.target):
            return self.succeed()
        else:
            return self.fail()


def get_equipped_in_slot(item_owner, slot):
    if item_owner.inventory:
        for item in item_owner.inventory:
            if item.is_equipped and item.equip_slot == slot:
                return item
    return None


def get_all_equipped(item_owner):
    equipped = []
    if item_owner.inventory:
        for item in item_owner.inventory:
            if item.is_equipped:
                equipped.append(item)
    return equipped
