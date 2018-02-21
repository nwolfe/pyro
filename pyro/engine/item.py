import tcod as libtcod
from pyro.position import Position
from pyro.spell import CastResult
from pyro.engine import Action


class Item:
    # TODO Change on_use from a Spell to a more-general Action
    def __init__(self, name, glyph, on_use=None, equip_slot=None):
        """An Item can be either usable or equipment, but not both.
        For a usable item, provide a Spell for on_use.
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

    def use(self, target):
        """Returns an Action."""
        return ItemActionAdapter(self, target)


# TODO Probably only able to get rid of this class once we redo the
# TODO targeting system again and/or always consume items regardless
# TODO of success/failure/invalid-target
class ItemActionAdapter(Action):
    def __init__(self, item, target):
        Action.__init__(self)
        self._item = item
        self._target = target

    def on_perform(self):
        """Removes the item from the inventory if the on_use succeeded."""
        # Destroy after use, unless it was cancelled for some reason
        # TODO This "destroy" behavior should live in UseAction
        result = self._item.on_use.cast(self, self._item.owner, self._target)
        cancelled = result.type == CastResult.TYPE_CANCEL
        invalid_target = result.type == CastResult.TYPE_INVALID_TARGET
        if not cancelled and not invalid_target:
            self._item.owner.inventory.remove(self._item)
            return self.succeed()
        elif invalid_target:
            self.game.log.message('Invalid target.', libtcod.orange)
        return self.fail()
