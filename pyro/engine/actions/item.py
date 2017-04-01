from pyro.components import Item
from pyro.engine.actions import Action, ActionResult


class PickUpAction(Action):
    def __init__(self):
        Action.__init__(self)

    # TODO Do this properly; use self.actor not game.player
    def on_perform(self):
        # Pick up first item in the player's tile
        for go in self.game.objects:
            item = go.component(Item)
            if item:
                if go.pos.equals(self.game.player.pos):
                    item.pick_up(self.game.player)
        return ActionResult.SUCCESS
